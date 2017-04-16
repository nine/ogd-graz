# OGD Graz Tools

Tools for OGD-Graz


## Download WMS-Tiles


Basiskarte:
 
```bash
./ogd-graz/src/download_wms_tiles.py \\
  --url="https://geodaten.graz.at/arcgis/services/OGD/Hintergrundkarte_Hintergrundkarte_OGD/MapServer/WmsServer" \\
  --min-zoom=12 \\ 
  --max-zoom=19 \\
  --overwrite
```

## Links
* Basiskarte: https://geodaten.graz.at/arcgis/services/OGD/Hintergrundkarte_Hintergrundkarte_OGD/MapServer/WmsServer
* Baugrundkarte: https://geodaten.graz.at/arcgis/services/OGD/BAUGRUNDKARTE_WMS/MapServer/WmsServer
* Orthofoto 2015: https://geodaten.graz.at/arcgis/services/OGD/LUFTBILD_WMS/MapServer/WmsServer
* Orthofoto 2011: https://geodaten.graz.at/arcgis/services/OGD/Orthofoto_2011_WMS/MapServer/WmsServer
