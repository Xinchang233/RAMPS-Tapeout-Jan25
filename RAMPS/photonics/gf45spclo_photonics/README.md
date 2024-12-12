# gf45spclo_photonics

Photonics technology repo for gf45spclo

## Updating the Klayout / BPG / Cadence layermaps
Run `scripts/make_layermap.py` from within the project directory (one level above gf45spclo_photonics)

`scripts/make_layermaps.py`:
* Points to the GF-provided layermap (symlinked in gf45spclo/workspace_setup)
* Points to a via_info yaml required for BAG/BPG
* Points to a abstract_layers.layermap file which includes custom layers

To enable new layers to be used in BPG/BAG:
* Update the `source/abstract_layers.layermap` file
* Rerun `make_layermaps.py` 

Generates BAG/BPG yaml format layermaps, and Cadence layermaps

Does not affect display settings


## Updating the KLayout layerproperties
See the `display` folder's readme.md