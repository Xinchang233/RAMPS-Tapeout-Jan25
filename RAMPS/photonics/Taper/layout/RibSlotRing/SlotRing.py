from layout.SimpleRingBusCouplerTB.FullEtchRing import FullEtchRing
from layout.Round.Round import Round


class SlotRing(FullEtchRing):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        FullEtchRing.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    def draw_layout(self):
        """Draw the outer ring RX layer """
        outer_ring_params = dict(layer=self.ring_params['layer'], r_out=self.ring_params['outer_rout'],
                                 ring_width=self.ring_params['outer_ring_width'], resolution=0.001)

        outer_ring_temp = self.new_template(params=outer_ring_params, temp_cls=Round)
        self.add_instance(master=outer_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )

        """Draw the outer ring RX+KG layer """
        rout = self.ring_params['outer_rout'] + self.ring_params['outer_ring_width']
        outer_ring_params = dict(layer=self.ring_params['partial_ring_layer'], r_out=rout,
                                 ring_width=self.ring_params['outer_ring_width'], resolution=0.001)

        outer_ring_temp = self.new_template(params=outer_ring_params, temp_cls=Round)
        self.add_instance(master=outer_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )


        """Draw the inner ring RX layer """
        rout = self.ring_params['outer_rout'] - self.ring_params['outer_ring_width'] - self.ring_params['gap']
        inner_ring_params = dict(layer=self.ring_params['layer'], r_out=rout,
                                 ring_width=self.ring_params['inner_ring_width'], resolution=0.001)

        inner_ring_temp = self.new_template(params=inner_ring_params, temp_cls=Round)
        self.add_instance(master=inner_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )

        """Draw the inner ring RX+KG layer """
        rout = self.ring_params['outer_rout'] - self.ring_params['outer_ring_width'] - self.ring_params['gap'] - self.ring_params['inner_ring_width']
        inner_ring_params = dict(layer=self.ring_params['partial_ring_layer'], r_out=rout,
                                 ring_width=self.ring_params['inner_ring_width'], resolution=0.001)

        inner_ring_temp = self.new_template(params=inner_ring_params, temp_cls=Round)
        self.add_instance(master=inner_ring_temp, loc=(0, 0), orient="R0", unit_mode=False, )
