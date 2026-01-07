# TreeMortNet

*TreeMortNet* is a Python package for predicting **individual tree mortality** from high-resolution, four-band (RGB + NIR)
NAIP imagery using polygons representing tree crowns, perhaps delineated using airborne lidar.

The package wraps a pre-trained TensorFlow model and provides a simple, file-based prediction interface.

## Requirements

- Python ≥ 3.11
- TensorFlow (CPU or GPU) ≥ 2.19
- GeoPandas / Rasterio stack
- NAIP imagery aligned with crown polygons
  - Same CRS

GPU acceleration is **optional**. CPU-only inference works well for thousands of tree crowns.

## Installation

Clone the repository and install locally:

```commandline
git clone https://github.com/mickeycampbell/TreeMortNet.git
cd TreeMortNet
pip install -e .
```

## Example Usage

The main function for applying *TreeMortNet* is `treemortnet.predict_crowns()`. It takes two inputs:
- `crowns_fp`: File path pointing to tree crown polygons in any common vector format readable by geopandas
- `naip_path`: File path pointing to NAIP imagery in any common raster format readable by rasterio

```python
from treemortnet import predict_crowns

gdf = predict_crowns(
    crowns_fp="crowns.gpkg",
    naip_path="naip.tif",
    output_fp="predictions.gpkg"
)
```

The function returns a GeoDataFrame equivalent to the input, but with two new fields appended:
- `prob_dead`: The predicted probability that a given tree crown is dead
- `pred_dead`: A binary representation of live (0) or dead (1), based on a `prob_dead` ≥ 0.5 threshold

## Notes
- Input crown polygons must be in the same CRS as the NAIP image
- Crown polygons must overlap the NAIP data

## Citation
If you use this tool, please cite:

TBD