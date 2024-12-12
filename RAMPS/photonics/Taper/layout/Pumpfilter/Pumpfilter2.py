import BPG
import importlib
from Photonic_Core_Layout.AdiabaticPaths.AdiabaticPaths import AdiabaticPaths
from Photonic_Core_Layout.WaveguideBase.WaveguideBase import WaveguideBase
from Photonic_Core_Layout.Taper.LinearTaper import LinearTaper

# changed "layout" -> "quantum_photon_pair_generator.github.equip01.EquipRow_v1_BWRC"
from quantum_photon_pair_generator.github.equip01.EquipRow_v1_BWRC.ArbitraryOrderRingFilter.ArbitraryOrderRingFilter import ArbitraryOrderRingFilter

from copy import deepcopy

class Pumpfilter2(BPG.PhotonicTemplateBase):
    """
    This class creates an unbalanced MZI with an input and output rac coupler.
    Parameters
    ----------
    rac_params : dict
        dict of parameters to be sent to the directional coupler master

    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self.signal_filter_params=self.params['signal_filter_params']
        self.idler_filter_params = self.params['idler_filter_params']

        # Master declaration

        self.filters_master = dict()
        self.wgs_master = dict()

        # Instances declaration
        self.filters = dict()
        self.wgs = dict()


    @classmethod
    def get_params_info(cls) -> dict:
        return dict(input_length='input length',signal_filter_params='signal filter params filter',
        idler_filter_params='idler filter params filter',R90='Radius90dg',output_space='output ports space',R90t='Radius90dg output',R180='Radius180dg',extra_length='extra_length',taper_in_width='taper_in_width',taper_length='taper_length')

    @classmethod
    def get_default_param_values(cls) -> dict:
        return dict(input_length=None,
            signal_filter_params=None,
            idler_filter_params=None,
            R90=None,output_space=None,R90t=None,R180=None,extra_length=None,taper_in_width=None,taper_length=None
        )

    def draw_layout(self) -> None:
        self.create_inputbus()
        self.pace_inputbus()
        self.create_singal_filter()
        self.create_idler_filter()
        self.place_signal_filter()
        self.place_midbus()
        self.place_idler_filter()
        self.create_outputbus()
        self.place_outputbus()
        self.create_outputbusexit()
        self.place_outputbusexit()

    def create_inputbus(self) -> None:
        R1=self.signal_filter_params['arb_ring_params']['wg_in_params']['length']
        R2=self.idler_filter_params['arb_ring_params']['wg_in_params']['length']
        R2b = self.idler_filter_params['arb_ring_params']['wg_out_params']['length']
        R90=self.params['R90']
        L0=self.params['output_space']
        R90b=L0+R2b/2+R90-R2/2
        L2=2*R2+2*R90b-R1
        L1=(R1+L2)/2.0-R90
        layersi=self.signal_filter_params['arb_ring_params']['wg_in_params']['layer']
        buswgwidth=self.signal_filter_params['arb_ring_params']['wg_in_params']['width']
        wgparams = dict(layer=layersi,
                        width=buswgwidth, points=[(0.0, 0.0), (self.params['input_length'], 0.0)])
        self.wgs_master['input'] = self.new_template(params=wgparams, temp_cls=WaveguideBase)

        params = dict(layer=layersi,
                  port_layer=['si_full_free', 'port'],
                  x_start=0.0, y_start=0.0,
                  angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                  show_plot=False, show_plot_labels=False)

        size_90_bend = R90
        arc_params = [
            dict(arc_type="90_bend", size=size_90_bend, turn_left=True,
                width=buswgwidth)]
        params['arc_params'] = arc_params
        self.wgs_master['bend_90_1_2'] = self.new_template(params=params, temp_cls=AdiabaticPaths)

        wgparams2 = dict(layer=layersi,
                        width=buswgwidth,
                        points=[(0.0, 0.0), (L1, 0.0)])
        self.wgs_master['wg_2_3'] = self.new_template(params=wgparams2, temp_cls=WaveguideBase)

        wgparams3 = dict(layer=layersi,
                         width=buswgwidth,
                         points=[(0.0, 0.0), (L2, 0.0)])
        self.wgs_master['wg_5_6'] = self.new_template(params=wgparams3, temp_cls=WaveguideBase)

        params3 = deepcopy(params)
        size_180_bend  = self.params['R180']

        arc_params2 = [
            dict(arc_type="180_bend", size=size_180_bend, turn_left=False,
                 width=buswgwidth)]
        params3['arc_params'] = arc_params2
        self.wgs_master['bend_180_3_4'] = self.new_template(params=params3, temp_cls=AdiabaticPaths)

        params4 = dict(layer=layersi,
                      port_layer=['si_full_free', 'port'],
                      x_start=0.0, y_start=0.0,
                      angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                      show_plot=False, show_plot_labels=False)

        size_90_bendb = R90b
        arc_paramsb = [
            dict(arc_type="90_bend", size=size_90_bendb, turn_left=True,
                 width=buswgwidth)]
        params4['arc_params'] = arc_paramsb
        self.wgs_master['bend_90_pump'] = self.new_template(params=params4, temp_cls=AdiabaticPaths)

    def pace_inputbus(self) -> None:
        self.wgs['input'] = self.add_instance(self.wgs_master['input'],
                                                      loc=(0, 0),
                                                      orient='R0')
        self.extract_photonic_ports(
            inst=self.wgs['input'],
            port_names=['PORT0'],
            port_renaming={'PORT0': 'PORT_IN'},
            show=False)

        self.wgs['bend_90_1_2'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_1_2'],
                                                                   instance_port_name='PORT_IN',
                                                                   self_port=self.wgs['input']['PORT1'],
                                                                   reflect=False)
        self.wgs['wg_2_3'] = self.add_instance_port_to_port(inst_master=self.wgs_master['wg_2_3'],
                                                                 instance_port_name='PORT0',
                                                                 self_port=self.wgs['bend_90_1_2']['PORT_OUT'],
                                                                 reflect=False)
        self.wgs['bend_180_3_4'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_180_3_4'],
                                                                 instance_port_name='PORT_IN',
                                                                 self_port=self.wgs['wg_2_3']['PORT1'],
                                                                 reflect=False)

    def create_singal_filter(self) -> None:
        self.filters_master['signal'] = self.new_template(params=self.signal_filter_params['arb_ring_params'],
                                                                   temp_cls=ArbitraryOrderRingFilter)

    def create_idler_filter(self) -> None:
        self.filters_master['idler'] = self.new_template(params=self.idler_filter_params['arb_ring_params'],
                                                          temp_cls=ArbitraryOrderRingFilter)

    def place_signal_filter(self) -> None:
        self.filters['signal']=self.add_instance_port_to_port(inst_master=self.filters_master['signal'],
                                                                            instance_port_name='PORT_IN',
                                                                            self_port=self.wgs['bend_180_3_4']['PORT_OUT'],
                                                                            reflect=False)
    def place_midbus(self) -> None:
        self.wgs['wg_5_6'] = self.add_instance_port_to_port(inst_master=self.wgs_master['wg_5_6'],
                                                            instance_port_name='PORT0',
                                                            self_port=self.filters['signal']['PORT_THROUGH'],
                                                            reflect=False)
        self.wgs['bend_180_6_7'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_180_3_4'],
                                                            instance_port_name='PORT_IN',
                                                            self_port=self.wgs['wg_5_6']['PORT1'],
                                                            reflect=True)

    def place_idler_filter(self) -> None:
        self.filters['idler'] = self.add_instance_port_to_port(inst_master=self.filters_master['idler'],
                                                                    instance_port_name='PORT_IN',
                                                                    self_port=self.wgs['bend_180_6_7']['PORT_OUT'],
                                                                    reflect=True)

    def create_outputbus(self) -> None:
        layersi=self.signal_filter_params['arb_ring_params']['wg_in_params']['layer']
        buswgwidth=self.signal_filter_params['arb_ring_params']['wg_in_params']['width']

        params = dict(layer=layersi,
                  port_layer=['si_full_free', 'port'],
                  x_start=0.0, y_start=0.0,
                  angle_start=0.0, radius_threshold=1.5, curvature_rate_threshold=0.7, merge_arcs=False,
                  show_plot=False, show_plot_labels=False)

        size_90_bend = self.params['R90t']
        arc_params = [
            dict(arc_type="90_bend", size=size_90_bend, turn_left=True,
                width=buswgwidth)]
        params['arc_params'] = arc_params
        self.wgs_master['bend_90_out'] = self.new_template(params=params, temp_cls=AdiabaticPaths)

        taperparam = dict(width0=self.params['taper_in_width'],
                          width1=buswgwidth,
                          length=self.params['taper_length'],
                          layer=layersi)
        self.wgs_master['tapers'] = self.new_template(params=taperparam, temp_cls=LinearTaper)
        taperparam2 = dict(width0=self.params['taper_in_width'],
                          width1=buswgwidth,
                          length=self.params['taper_length'],
                          layer=layersi)
        self.wgs_master['taperi'] = self.new_template(params=taperparam2, temp_cls=LinearTaper)

    def place_outputbus(self) -> None:
        self.wgs['bend_90_9_10'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_pump'],
                                                            instance_port_name='PORT_IN',
                                                            self_port=self.filters['idler']['PORT_THROUGH'],
                                                            reflect=True)
        self.wgs['bend_90_out_top'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_out'],
                                                                  instance_port_name='PORT_IN',
                                                                  self_port=self.filters['idler']['PORT_DROP'],
                                                                  reflect=True)
        self.wgs['bend_90_idler'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_1_2'],
                                                            instance_port_name='PORT_IN',
                                                            self_port=self.filters['idler']['PORT_RED'],
                                                            reflect=True)

        self.wgs['bend_90_out_bot'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_out'],
                                                                     instance_port_name='PORT_IN',
                                                                     self_port=self.filters['signal']['PORT_DROP'],
                                                                     reflect=False)
        self.wgs['bend_90_signal'] = self.add_instance_port_to_port(inst_master=self.wgs_master['bend_90_1_2'],
                                                                   instance_port_name='PORT_IN',
                                                                   self_port=self.filters['signal']['PORT_RED'],
                                                                   reflect=False)
        self.wgs['tapers'] = self.add_instance_port_to_port(inst_master=self.wgs_master['tapers'],
                                                                     instance_port_name='PORT1',
                                                                     self_port=self.wgs['bend_90_out_top']['PORT_OUT'],
                                                                     reflect=False)
        self.wgs['taperi'] = self.add_instance_port_to_port(inst_master=self.wgs_master['taperi'],
                                                                    instance_port_name='PORT1',
                                                                    self_port=self.wgs['bend_90_out_bot']['PORT_OUT'],
                                                                    reflect=False)

    def create_outputbusexit(self) -> None:
        layersi = self.signal_filter_params['arb_ring_params']['wg_in_params']['layer']
        buswgwidth = self.signal_filter_params['arb_ring_params']['wg_in_params']['width']
        xl=self.params['extra_length']
        xf=self.wgs['bend_90_idler']._photonic_port_list['PORT_OUT'].center[0]+xl
        xp=self.wgs['bend_90_9_10']._photonic_port_list['PORT_OUT'].center[0]
        xs=self.wgs['bend_90_signal']._photonic_port_list['PORT_OUT'].center[0]
        wgparams = dict(layer=layersi,
                        width=buswgwidth, points=[(0.0, 0.0), (xf-xp, 0.0)])
        self.wgs_master['outputpump'] = self.new_template(params=wgparams, temp_cls=WaveguideBase)
        wgparams2 = dict(layer=layersi,
                        width=buswgwidth, points=[(0.0, 0.0), (xf - xs, 0.0)])
        self.wgs_master['outputsig'] = self.new_template(params=wgparams2, temp_cls=WaveguideBase)
        wgparams3 = dict(layer=layersi,
                        width=buswgwidth, points=[(0.0, 0.0), (xl, 0.0)])
        self.wgs_master['outputidler'] = self.new_template(params=wgparams3, temp_cls=WaveguideBase)

    def place_outputbusexit(self) -> None:
        self.wgs['outputpump'] = self.add_instance_port_to_port(inst_master=self.wgs_master['outputpump'],
                                                                    instance_port_name='PORT0',
                                                                    self_port=self.wgs['bend_90_9_10']['PORT_OUT'],
                                                                    reflect=False)
        self.wgs['outputsig'] = self.add_instance_port_to_port(inst_master=self.wgs_master['outputsig'],
                                                                instance_port_name='PORT0',
                                                                self_port=self.wgs['bend_90_signal']['PORT_OUT'],
                                                                reflect=False)
        self.wgs['outputidler'] = self.add_instance_port_to_port(inst_master=self.wgs_master['outputidler'],
                                                                instance_port_name='PORT0',
                                                                self_port=self.wgs['bend_90_idler']['PORT_OUT'],
                                                                reflect=False)
        self.extract_photonic_ports(
            inst=self.wgs['outputpump'],
            port_names=['PORT1'],
            port_renaming={'PORT1': 'PORT_OUT_P'},
            show=False)

        self.extract_photonic_ports(
            inst=self.wgs['outputsig'],
            port_names=['PORT1'],
            port_renaming={'PORT1': 'PORT_OUT_S'},
            show=False)

        self.extract_photonic_ports(
            inst=self.wgs['outputidler'],
            port_names=['PORT1'],
            port_renaming={'PORT1': 'PORT_OUT_I'},
            show=False)