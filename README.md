# OGD Graz Tools

Tools for OGD-Graz


## Download WMS-Tiles


### Basic Usage
```bash
./ogd-graz/src/download_wms_tiles.py \\
  --url="https://geodaten.graz.at/arcgis/services/OGD/Hintergrundkarte_Hintergrundkarte_OGD/MapServer/WmsServer" \\
  --min-zoom=12 \\ 
  --max-zoom=19 \\
  --tile-dir="tiles"
  --overwrite
```

### OGD-Graz WMS URLs
* Basiskarte: https://geodaten.graz.at/arcgis/services/OGD/Hintergrundkarte_Hintergrundkarte_OGD/MapServer/WmsServer
* Baugrundkarte: https://geodaten.graz.at/arcgis/services/OGD/BAUGRUNDKARTE_WMS/MapServer/WmsServer
* Orthofoto 2015: https://geodaten.graz.at/arcgis/services/OGD/LUFTBILD_WMS/MapServer/WmsServer
* Orthofoto 2011: https://geodaten.graz.at/arcgis/services/OGD/Orthofoto_2011_WMS/MapServer/WmsServer

### Cleanup
* **list_html_files.sh**: list wrongly downloaded HTML files. 
* **delete_html_files.sh**: delete wrongly downloaded HTML files.

## License
This software is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see [gpl](www.gnu.org/licenses/).

## Contact
Please use the contact-form provided by github.

