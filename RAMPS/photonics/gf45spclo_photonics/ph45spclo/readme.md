# ph45spclo

Folder to contain the 'blackbox' PDK photonic library components.

`current` symlink should point to latest PDK release

`*.py` files use BPG GDSImport to import the streamed-out GDS cells, and add `PhotonicPort` to the cells as needed. Also add `NoDataprep` layers.

Each PDK version folder should contain the streamed-out GDS files.