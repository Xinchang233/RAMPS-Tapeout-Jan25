import BPG
from BPG.lumerical.testbench import LumericalTB
from BPG.geometry import CoordBase


class WaveguideModeSim(LumericalTB):
    """
    Places a simple straight waveguide as the DUT and solves for the available modes
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        LumericalTB.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    def construct_tb(self):
        center_loc = 0.5 * self.layout_params['length']
        fde = self.add_code_obj()
        fde.add_code('addfde')
        fde['solver type'] = "2D X normal"
        fde['x'] = CoordBase(center_loc).meters
        fde['y'] = 0
        fde['y span'] = CoordBase(self.params['sim_width']).meters
        fde['z'] = 0
        fde['z span'] = CoordBase(self.params['sim_height']).meters

        # Set the fde boundary conditions
        fde['y min bc'] = self.params['bc_type']
        fde['y max bc'] = self.params['bc_type']
        fde['z max bc'] = self.params['bc_type']
        fde['z min bc'] = self.params['bc_type']

        # Set the fde mesh parameters
        fde['wavelength'] = self.params['wavelength']
        fde['define y mesh by'] = "maximum mesh step"
        fde['dy'] = self.params['meshsize']
        fde['define z mesh by'] = "maximum mesh step"
        fde['dz'] = self.params['meshsize']
        fde['number of trial modes'] = self.params['n_trial_modes']

        # Run the mode simulation
        fde.add_code('findmodes')


if __name__ == '__main__':
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/WaveguideModeSim.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    plm.generate_flat_content()
    plm.generate_tb()
