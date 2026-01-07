"""
predict.py

Prediction functions for treemortnet final model.

Input crowns must be a file path (GeoPackage, shapefile, etc.).
"""

import os
import numpy as np
import geopandas as gpd
from shapely.geometry import box, shape
from tensorflow.keras.models import load_model
from rasterio import open as rio_open
from rasterio.mask import mask
from rasterio.features import rasterize
from rasterio.windows import Window
from PIL import Image
import importlib.resources as pkg_resources
import pathlib

# -----------------------------
# Get model path
# -----------------------------
try:
    _FINAL_MODEL_PATH = str(pkg_resources.files("treemortnet").joinpath("models/model.keras"))
except FileNotFoundError:
    raise FileNotFoundError("Cannot find the treemortnet model. Make sure the package is installed correctly.")

# -----------------------------
# Helper functions
# -----------------------------
def resize_chip(chip):
    """Resize chip (bands, H, W) → (H, W, bands)."""
    resized = [np.array(Image.fromarray(band).resize((64, 64), resample=Image.BILINEAR))
               for band in chip]
    return np.stack(resized, axis=-1)

def stretch_to_square(chip_data):
    """Stretch to 64x64 pixels."""
    return resize_chip(chip_data)

def process_crown(feature, src, naip_geom):
    """Preprocess a single crown polygon into a chip."""
    geom = shape(feature["geometry"])
    if geom is None or not geom.intersects(naip_geom):
        return None
    geom = geom.buffer(1.0)

    try:
        # rasterize / mask
        masked_chip, _ = mask(src, [geom], crop=True, filled=False)
        if isinstance(masked_chip, np.ma.MaskedArray):
            valid_mask = ~np.ma.getmaskarray(masked_chip[0])
        else:
            valid_mask = masked_chip[0] != 0
        if valid_mask.sum() < 4: 
            return None
        chip_data = masked_chip.filled(0) if isinstance(masked_chip, np.ma.MaskedArray) else masked_chip
        chip_data = chip_data[:4]  # max 4 bands
        return stretch_to_square(chip_data)
    
    except Exception as e:
        print(f"Skipping crown due to error: {e}")
        return None

# -----------------------------
# Main prediction function
# -----------------------------
def predict_crowns(crowns_fp, naip_path, output_fp=None):
    """
    Predict tree mortality for crowns (simplified, no interim files or batching).

    Parameters
    ----------
    crowns_fp : str
        File path to input crown polygons.
    naip_path : str
        File path to NAIP raster.
    output_fp : str, optional
        If provided, saves a GeoPackage with predicted attributes.

    Returns
    -------
    geopandas.GeoDataFrame
        Copy of input crowns with 'prob_dead' and 'pred_dead' columns.
    """
    if not os.path.exists(_FINAL_MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {_FINAL_MODEL_PATH}")

    model = load_model(_FINAL_MODEL_PATH, compile=False)
    crowns_gdf = gpd.read_file(crowns_fp)

    with rio_open(naip_path) as src:
        naip_geom = box(*src.bounds)
        naip_crs = src.crs

        chips, ids, geoms = [], [], []

        for idx, feature in crowns_gdf.iterrows():
            res = process_crown(feature, src, naip_geom)
            if res is None:
                continue

            chips.append(res.astype(np.float32) / 255.0)
            ids.append(feature.get("id", idx))
            geoms.append(feature.geometry)

        if not chips:
            raise ValueError("No valid crowns found for prediction.")

        # Stack all chips at once
        X = np.stack(chips)
        prob_dead = model.predict(X, verbose=0).flatten()
        pred_dead = (prob_dead >= 0.5).astype(int)

        # Create output GeoDataFrame
        output_gdf = gpd.GeoDataFrame({
            "id": ids,
            "prob_dead": prob_dead,
            "pred_dead": pred_dead,
            "geometry": geoms
        }, crs=naip_crs)

    if output_fp:
        output_gdf.to_file(output_fp, driver="GPKG", mode="w")

    return output_gdf