Note:

There is a silly bug in KLayout Version <0.25.8 where stipples need to be mirrored in the lyp file...

If we update to a newer KLayout, all the custom stipples in the lyp will need to be mirrored vertically.

Delete this comment if this ever happens... its a 1 time thing.

# Instructions on how to generate new display-related files

Steps 1-3 are used to remap the original IBM 12SOI colorscheme onto the current PDK's Virtuoso display.drf, 
convert that new display.drf into the Calibre DRV format, 
and finally convert the Calibre DRV format into a klayout `lyp` file. 

It is not expected that these should be run frequently.
It is much easier to manipulate the klayout `lyp` file as new abstract layers are added.

In general, because photonics layouts are generally only viewed within KLayout, we have stopped updating the Virtuoso techfiles and display.drf files. 
So as abstract layers get added, there is no need to run steps 1-3. 

TLDR:  Usually, just skip to step 4.

## 1. Remap good `display.drf` settings onto new PDK `drf`.

This only needs to be run if the PDK gets updated.
We prefer the colorscheme from the IBM 12SOI process.
This script remaps the Virtuoso display properties from 12SOI onto the current PDK.
It currently does not add in any 'custom' `drf` color packets/etc.  
Just uses what is in the files pointed to in the `__main__` method of the script.

Not expected that we will need to run this again for CLO.

To run:
(In the bag/cds workspace)

`$BAG_PYTHON gf45spclo_photonics/display/make_display_drf.py`

## 2. Generate the Calibre DRV files based on the updated `drf`

If the stipples/colors in the base `drf` change significantly, you may need to rerun this.

Not expected that we run this again for CLO. 

This is needed as a temporary step to finally export to KLayout `lyp`.


To run:
(In `gf45pclo_photoncs/display/calibreDRV`)

`source runme.sh`

## 3. Convert Calibre DRV to Klayout `lyp`

Takes the Calibre DRV files and converts them to a base KLayout `lyp` (XML) file that can finally be manipulated as we want.

To run: (In `gf45spclo_photonics/display`)

`$BAG_PYTHON calibre_to_klayout.py`

## 4. Customizing KLayout lyp file

Customizing the KLayout lyp is an iterative process that involves a combination of manual editing and script execution.

After generating/updating the layermap, edit the `gf45spclo_photonics/display/KLayout_groups.yaml` file.
All layers in the layermap must appear as an entry in this `KLayout_groups.yaml`.

Place the layers as desired in existing display groups, or create a new group if needed.

Then run (from the bag/cds workspace):

`$BAG_PYTHON gf45spclo_photonics/display/MakeKLayoutGroups.py`

This script:
* Ensures all layers in the layermap appear in the grouping file.  
  Missing layers are printed.  
  The script aborts if any layers are missing
* Ensures there are no duplicate entires in the grouping file.  
  The script aborts if this occurs.
* Reports any newly-added layers whose color and stipple may need to be updated.  
  The output is printed, and generated in `gf45spclo_photonics/display/newly_added_layers.yaml`


The script works by reading in the current KLayout layerproperties file, and parsing its layer properties entries and stipples.
It then re-groups the layers based on the grouping file, and outputs a new lyp file.

If satisfied with the new lyp, replace the old one with the new one.

To customize colors, stipples, etc, directly modify the lyp file.

If layers were recently added to the grouping file/layermap, they will be added to the output klayout lyp file.
However, these entries will use a default stipple/color, and should be updated.
A list of these layers is printed during script execution, and is also reported out in `newly_added_layers.yaml`
Go through each layer in the `newly_added_layers.yaml` file and update its properties in the output KLayout lyp as desired. 
  
  
  

### Note on Klayout Lyp Stipples:
To assign a custom stipple pattern, use `C#` where `#` is the number/order of the stipple in the bottom of the lyp file.
To use a built-in stipple, use `I#`, where `#` is 0-12.
