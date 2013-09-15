# OGD Graz Tools

Tools for OGD-Graz


## Download WMS-Tiles


Basiskarte:
 
```bash
./ogd-graz/src/download_wms_tiles.py \\
  --url="http://geodaten1.graz.at/ArcGIS_Graz/services/Extern/BASISKARTE_WMS/MapServer/WMSServer" \\
  --min-zoom=12 \\ 
  --max-zoom=19 \\
  --overwrite
```
