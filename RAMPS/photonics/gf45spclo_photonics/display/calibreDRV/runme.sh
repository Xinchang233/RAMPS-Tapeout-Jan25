#! /bin/csh -f

setenv TECHNAME 45spclo

setenv DRV_BITMAP_DIR ./bitmaps

./conv_cds_drv.pl -tech $TECHNAME -disp ../display.drf -tf ../../../gf45spclo/workspace_setup/techfile.tf -map ../../../gf45spclo/workspace_setup/layermap

cp $TECHNAME.layerprops layerprops

sed -i 's/$DRV_BITMAP_DIR/gf45spclo_photonics\/display\/calibreDRV\/bitmaps/g' layerprops





#setenv TECHNAME 45spclo
#setenv DRV_BITMAP_DIR ./bitmaps
#conv_cds_drv.pl -tech $TECHNAME -disp ../display.drf -tf ../techfile.tf -map ../layermap.layermap
#cp $TECHNAME.layerprops layerprops
#sed -i 's/$DRV_BITMAP_DIR/$PROJECT\/cad\/cds\/tech\/calibreDRV\/bitmaps/g' layerprops
