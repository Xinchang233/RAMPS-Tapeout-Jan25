import BPG
from BPG.gds.io import GDSImport

import pdb


class JosepTaper(BPG.PhotonicTemplateBase):
    """
    wide adiabatic taper, designed by Josep
    Wavelength is selected by the parameter "wavelength"

    Params:
        wavelength : either 1300 or 1550

    Ports:
        'PORT0'
        'PORT1'
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(
            wavelength = 'either 1300 or 1550'
        )

    # @classmethod
    # def get_default_param_values(cls):
    #     return dict(
    #         gds_path='layout/Importers/Tapers/gds/taper1300.gds'
    #     )

    def draw_layout(self):

        if self.params['wavelength'] == 1300:

            import_params = { 'gds_path' : 'layout/Importers/Tapers/gds/taper1300.gds' }
            single_mode_wg_width = 0.5

        elif self.params['wavelength'] == 1550:

            import_params = { 'gds_path' : 'layout/Importers/Tapers/gds/taper1550.gds' }
            single_mode_wg_width = 0.7

        # end if else

        master = self.new_template(params=import_params, temp_cls=GDSImport)
        mast_inst = self.add_instance(master)

        # get coordinates
        bb      = mast_inst.bound_box
        center_y = ( bb.top + bb.bottom )/2.0
        left    = bb.left
        right   = bb.right


        # add port at wide end
        self.add_photonic_port(
            name='PORT0',
            orient='R0',
            center=(left, center_y),
            width=0.5,
            layer=('RX', 'port'),
            resolution=self.grid.resolution,
            unit_mode=False,
            show=False)

        # add port at narrow end
        self.add_photonic_port(
            name    = 'PORT1',
            orient  = 'R180',
            center  = (right, center_y),
            width   = single_mode_wg_width,
            layer   = ('RX', 'port'),
            resolution  = self.grid.resolution,
            unit_mode   = False,
            show        = False )

        # get length
        self.length = abs( self.get_photonic_port('PORT0').x - self.get_photonic_port('PORT1').x )

    # end draw_layout()

# end JosepTaper

# spec_file = 'layout/Importers/Gratings/specs/gc_bidir_wl1300nm_mfd5000nm.yaml'
# plm = BPG.PhotonicLayoutManager(spec_file)
# plm.generate_content()
# plm.generate_gds()
# plm.dataprep_calibre()
