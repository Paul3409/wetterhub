from pathlib import Path
import json

import netCDF4  # noqa: F401  # NetCDF-Backend für xarray
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import xarray as xr

BASE_DIR = Path(__file__).resolve().parent
DATA_DIRS = (BASE_DIR, BASE_DIR / "data")
CONFIG_PATH = BASE_DIR / "design_config.json"

EUROPE_LAT = (35.0, 65.0)
EUROPE_LON = (-10.0, 30.0)

FILE_CANDIDATES = {
    "prmsl": ("prmsl.mon.mean.nc", "prmsl.nc"),
    "air": ("air.2m.mon.mean.nc", "air.mon.mean.nc", "air.2m.nc"),
}

VAR_CANDIDATES = {
    "prmsl": ("prmsl", "slp", "msl", "pres"),
    "air": ("air", "t2m", "tmp", "temperature", "t"),
}

NOAA_DOWNLOAD_URLS = {
    "prmsl": (
        "https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/"
        "Monthlies/miscSI-MO/prmsl.mon.mean.nc"
    ),
    "air": (
        "https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/"
        "Monthlies/2mSI-MO/air.2m.mon.mean.nc"
    ),
}

NOAA_CATALOG = "https://psl.noaa.gov/data/gridded/data.20thC_ReanV3.html"

MONATE = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}


def load_design_config() -> dict:
    if not CONFIG_PATH.is_file():
        st.error(
            f"Die Datei `{CONFIG_PATH.name}` fehlt. "
            "Bitte die Design- und Legenden-Einstellungen dort ablegen."
        )
        st.stop()

    with CONFIG_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def find_nc_file(param_key: str) -> Path | None:
    for directory in DATA_DIRS:
        if not directory.is_dir():
            continue
        for name in FILE_CANDIDATES[param_key]:
            path = directory / name
            if path.is_file():
                return path
    return None


def show_missing_file_error(param_key: str, expected_names: tuple[str, ...]) -> None:
    expected = " oder ".join(f"`{name}`" for name in expected_names)
    folders = " oder ".join(f"`{d}`" for d in DATA_DIRS)
    url = NOAA_DOWNLOAD_URLS[param_key]
    st.error(
        f"Keine lokale NetCDF-Datei gefunden ({expected}). "
        f"Lege die Datei in {folders} ab."
    )
    st.markdown(
        f"""
**NOAA 20th Century Reanalysis (V3), Monatswerte 1836–2015**

1. Übersicht: [{NOAA_CATALOG}]({NOAA_CATALOG})
2. Direkter Download: [{url}]({url})

Die Dateien sind groß (oft mehrere hundert MB). Nach dem Download
diese App neu laden.
"""
    )
    st.stop()


def _first_name(ds: xr.Dataset, candidates: tuple[str, ...], kind: str) -> str:
    names = set(map(str, list(ds.coords) + list(ds.dims) + list(ds.data_vars)))
    for name in candidates:
        if name in names:
            return name
    raise KeyError(
        f"Keine {kind}-Koordinate gefunden. Vorhanden: {sorted(names)}"
    )


def _normalize_longitude(ds: xr.Dataset, lon_name: str) -> xr.Dataset:
    lon = ds[lon_name]
    if float(lon.max()) > 180:
        ds = ds.assign_coords({lon_name: (((lon + 180) % 360) - 180)})
        ds = ds.sortby(lon_name)
    return ds


def _lat_slice(ds: xr.Dataset, lat_name: str) -> slice:
    lat_min, lat_max = EUROPE_LAT
    lat = ds[lat_name]
    if lat.size >= 2 and float(lat[0]) > float(lat[-1]):
        return slice(lat_max, lat_min)
    return slice(lat_min, lat_max)


def _pick_data_var(ds: xr.Dataset, param_key: str) -> str:
    for name in VAR_CANDIDATES[param_key]:
        if name in ds.data_vars:
            return name
    data_vars = [name for name in ds.data_vars if name not in ("time_bnds", "lat_bnds", "lon_bnds")]
    if not data_vars:
        raise KeyError("Die NetCDF-Datei enthält keine Datenvariable.")
    return data_vars[0]


@st.cache_data(show_spinner="NetCDF-Ausschnitt wird geladen …")
def load_europe_slice(
    nc_path: str, param_key: str, year: int, month: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, str]:
    """Liest nur den gewählten Monat und den Europa-Ausschnitt."""
    with xr.open_dataset(nc_path, engine="netcdf4") as ds:
        lat_name = _first_name(ds, ("lat", "latitude", "y"), "Breitengrad")
        lon_name = _first_name(ds, ("lon", "longitude", "x"), "Längengrad")
        time_name = _first_name(ds, ("time", "date"), "Zeit")
        var_name = _pick_data_var(ds, param_key)

        ds = _normalize_longitude(ds, lon_name)
        ds = ds.sel(
            {
                lat_name: _lat_slice(ds, lat_name),
                lon_name: slice(*EUROPE_LON),
            }
        )

        target = np.datetime64(f"{year}-{month:02d}")
        sliced = ds.sel({time_name: target}, method="nearest")
        da = sliced[var_name].squeeze(drop=True).load()

        lats = np.asarray(da[lat_name].values, dtype="float64")
        lons = np.asarray(da[lon_name].values, dtype="float64")
        values = np.asarray(da.values, dtype="float64")

        if time_name in da.coords:
            actual_time = str(np.datetime64(da[time_name].values, "M"))
        else:
            actual_time = f"{year}-{month:02d}"

    finite = values[np.isfinite(values)]
    if param_key == "prmsl" and finite.size and np.nanmedian(finite) > 10_000:
        values = values / 100.0
    if param_key == "air" and finite.size and np.nanmedian(finite) > 100:
        values = values - 273.15

    return lats, lons, values, var_name, actual_time


def design_for(config: dict, param_key: str) -> dict:
    if param_key in config:
        return config[param_key]
    return config


def build_map(
    lons: np.ndarray,
    lats: np.ndarray,
    values: np.ndarray,
    settings: dict,
    colorbar_title: str,
) -> go.Figure:
    zmin = float(settings["min_value"])
    zmax = float(settings["max_value"])
    step = float(settings["step_size"])
    if step <= 0:
        step = (zmax - zmin) / 10 if zmax != zmin else 1.0

    fig = go.Figure(
        data=go.Contour(
            x=lons,
            y=lats,
            z=values,
            colorscale=settings["colormap"],
            zmin=zmin,
            zmax=zmax,
            contours=dict(
                start=zmin,
                end=zmax,
                size=step,
                showlabels=True,
                labelfont=dict(size=10, color="black"),
            ),
            colorbar=dict(title=colorbar_title),
            line_smoothing=0.7,
            hovertemplate="Lon: %{x:.2f}°<br>Lat: %{y:.2f}°<br>Wert: %{z:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis_title="Längengrad",
        yaxis_title="Breitengrad",
        yaxis=dict(scaleanchor="x", scaleratio=1, range=[EUROPE_LAT[0], EUROPE_LAT[1]]),
        xaxis=dict(range=[EUROPE_LON[0], EUROPE_LON[1]]),
        height=700,
    )
    return fig


st.set_page_config(page_title="NOAA Wetterkarten-Viewer", layout="wide")
st.title("🗺️ Historischer Wetterkarten-Viewer (1836–2015)")
st.write(
    "Echte NOAA-Reanalysis-Daten (NetCDF) für Europa – "
    "Legende und Farbschema kommen aus `design_config.json`."
)

design_config = load_design_config()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    jahr = st.number_input("Jahr (1836 - 2015):", min_value=1836, max_value=2015, value=1976, step=1)
    monat_name = st.selectbox("Monat:", list(MONATE.keys()))
    monat_num = MONATE[monat_name]
    variable = st.selectbox(
        "Wetter-Parameter:",
        [
            "Sea Level Pressure (Bodendruck / Isobaren)",
            "Air Temperature (Lufttemperatur 2m)",
        ],
    )

param_key = "prmsl" if "Pressure" in variable else "air"
settings = design_for(design_config, param_key)
nc_path = find_nc_file(param_key)

if nc_path is None:
    show_missing_file_error(param_key, FILE_CANDIDATES[param_key])

st.subheader(f"Wetterlage für Europa: {monat_name} {jahr}")

try:
    lats, lons, values, var_name, actual_time = load_europe_slice(
        str(nc_path), param_key, int(jahr), int(monat_num)
    )
except Exception as exc:
    st.error(f"Die NetCDF-Datei konnte nicht gelesen werden: {exc}")
    st.stop()

unit = settings.get("unit", "")
fig = build_map(lons, lats, values, settings, unit or var_name)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    f"Quelle: NOAA 20th Century Reanalysis (V3) · Datei `{nc_path.name}` · "
    f"Variable `{var_name}` · Zeitscheibe {actual_time} · "
    f"Region Lat {EUROPE_LAT[0]}–{EUROPE_LAT[1]}°, Lon {EUROPE_LON[0]}–{EUROPE_LON[1]}° · "
    f"Colormap `{settings['colormap']}`, {settings['min_value']}–{settings['max_value']} {unit}, "
    f"Schritt {settings['step_size']}"
)
