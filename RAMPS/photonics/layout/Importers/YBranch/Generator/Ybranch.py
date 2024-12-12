import BPG
from ..AdiabaticRouter.AdiabaticRouter import AdiabaticRouter
from BPG.template import PhotonicPolygon

class Ybranch(BPG.PhotonicTemplateBase):
    """ This class hard codes the shape of the optimized Y-branch for CENA tapeout
        Design is done in O-band and it is an improvement on PICO design which enables
        equal splitting on the output of the back-to-back y-branches when light is
        coupled into only a single branch """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict(

        )

    @classmethod
    def get_default_param_values(cls):
        return dict(

        )

    def draw_layout(self) -> None:
        init_port = self.add_photonic_port(name='init_port', center=(0, 0), orient='R0', width=0.36,
                                           layer=('RX', 'port'))
        Wg = AdiabaticRouter(gen_cls=self, init_port=init_port, layer=('si_full_free', 'drawing'), name='init_port2')

        Wg.add_straight_wg(length=0.5)  # add small amount of the straight wg
        Wg.add_parabolic_polygon(wout=1.4, length=1.15)
        Wg.add_straight_wg(length=0.94)
        Wg.add_straight_wg(length=0.89, width=1.04)
        Wg.add_straight_wg(length=2.62 - 0.89)

        loc_x = Wg.port.center[0]

        # add upper port
        upper_port = self.add_photonic_port(name='upper_port', center=(loc_x, 0.32), orient='R0', width=0.4,
                                                        layer=('RX', 'port'))

        upper_wg = AdiabaticRouter(gen_cls=self, init_port=upper_port, layer=('si_full_free', 'drawing'),
                                   name='upper_port')
        upper_wg.add_straight_wg(length=0.5)
        # upper_wg.add_offset_bend(offset=1, rmin=5)
        # upper_wg.add_straight_wg(length=3)

        # add lower port
        lower_port = self.add_photonic_port(name='lower_port', center=(loc_x, -0.32), orient='R0', width=0.4,
                                            layer=('RX', 'port'))

        lower_wg = AdiabaticRouter(gen_cls=self, init_port=lower_port, layer=('si_full_free', 'drawing'),
                                   name='lower_port')
        lower_wg.add_straight_wg(length=0.5)
        # lower_wg.add_offset_bend(offset=-1, rmin=5)
        # lower_wg.add_straight_wg(length=3)

        # add upper triangle
        points_upper = [[loc_x, 0.12], [loc_x, 0.12 - 0.059], [loc_x - 0.295, 0.12]]
        poly_upper = PhotonicPolygon(resolution=self.grid.resolution,
                                     layer=('si_full_free', 'drawing'),
                                     points=points_upper)

        self.add_obj(poly_upper)
        
        # add lower triangle
        points_lower = [[loc_x, -0.12], [loc_x, -0.12+0.059], [loc_x-0.295, -0.12]]
        poly_lower = PhotonicPolygon(resolution=self.grid.resolution,
                            layer=('si_full_free', 'drawing'),
                            points=points_lower)

        self.add_obj(poly_lower)
