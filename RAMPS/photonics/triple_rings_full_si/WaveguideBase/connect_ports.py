# Moving this out of phot_template, because of import loop (connect uses WgRouter, and WgRouter uses PhotTemplate classes)
# This would probably make the most sense as part of WgRouter, with some modifications/simplifications
import numpy as np
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter
# from phot_top.global_variables import LPPList_Routing


def connect_ports(InLayout, PortA, PortB, lpp_routing=None,
                  WaveguideWidth=None, TransitionLength=None  ):  
#                  lpp_routing = LPPList_Routing[0]):  
        """
        Connect two ports (PortA and PortB) with a straight waveguide, transitioning to a specified 
        WaveguideWidth if there is room for transitions, and otherwise linearly tapering directly between ports
        Returns a list of either one instance or three instances
        """
        gridres = InLayout.grid.resolution
        # print('In connect_ports, Ports: ' + str(PortA) + str(PortB))
        # print('PortA orientation: ' + str(PortA.orientation))
        # print('PortB orientation: ' + str(PortB.orientation))

        # N90degs = port_inward_in_90degs(PortA.orientation)  # ORIENTATIONS_AS_N90Degs.index(PortA.orientation)
        # nhat = [ int(np.round(np.cos( np.pi * N90degs / 2.0))), 
        #          int(np.round(np.sin( np.pi * N90degs / 2.0))) ] 
        # N90degsB = port_inward_in_90degs(PortB.orientation)  # ORIENTATIONS_AS_N90Degs.index(PortB.orientation)
        # print('nhat: ' + str(nhat))
        # print('N90degsA: ' + str(N90degs))
        # print('N90degsB: ' + str(N90degsB))
        nhatA = PortA.width_vec_unit / np.sqrt(sum([ coord**2 for coord in PortA.width_vec_unit]))
        nhatB = PortB.width_vec_unit / np.sqrt(sum([ coord**2 for coord in PortB.width_vec_unit]))
        # print('nhatA: ' + str(nhatA))
        # print('nhatB: ' + str(nhatB))

        #     # Separation from PortA to PortB along "outward" direction of PortA
        sep_vec  = (PortA.center[0] - PortB.center[0], PortA.center[1] - PortB.center[1])  # Inward: A-B
        # print('abs sep: ' + str(sep_vec))
        port_sep     = (nhatA[0] * sep_vec[0] + nhatA[1] * sep_vec[1])  # nhat inward, nhat dot (A-B) = outward
        # print('port_sep in units: ' + str( port_sep / gridres))
        # print('Port x pos in units: [%.4f,%.4f, %.4f]]' % (PortA.center_unit[0], PortB.center_unit[0], 
        #                                                    PortA.center_unit[0] - PortB.center_unit[0]))
        misalignment = sep_vec[0] * nhatA[1] - sep_vec[1] * nhatA[0]  
        misalignment = np.round(misalignment / (0.01  * gridres)) * (0.01  * gridres)
        NoMiddleWgWidth = (WaveguideWidth is None) or ((WaveguideWidth == PortB.width) and 
                                                       (WaveguideWidth == PortA.width) )


        if(np.abs(nhatA[0] * nhatB[1] - nhatA[1] * nhatB[0]  ) > 1e-4):  # ##MAGIC NUMBER
                print(nhatA)
                print(nhatB)
                raise RuntimeError('connect_ports requires that ports face each other!')
        if(port_sep < 0.0):
                raise RuntimeError('draw_straight_waveguide cannot connect two ports with negative separation')
        if(port_sep <= 10 * gridres):
            # warnings.warn('This is an awfully small waveguide...skipping')
            raise RuntimeError('draw_straight_waveguide called with no separation...how should we handle this?')

        InstanceList = []
        # Should we make a three-section Wg with transition, or simply a single wg?
        # Eventually, I would like to have transition at each A and B decided separately
        if(TransitionLength is None):
            ThreePartWg = False
        else:
            StraightLength =  np.ceil( float(port_sep - 2 * TransitionLength) / (0.01 * gridres) ) * (0.01 * gridres)
            THRESH = 1.0
            ThreePartWg = (StraightLength > THRESH * TransitionLength) and not(NoMiddleWgWidth)
        if(ThreePartWg):
            # This is just a three-section waveguide...simpler than what I did before, no?
            # BPG straight-taper-waveguide only?!
            router = WgRouter(InLayout, init_port=PortA, layer=lpp_routing, name=None)
            router.add_straight_wg(length=TransitionLength, out_width=WaveguideWidth)
            router.add_straight_wg(length=StraightLength)
            router.add_straight_wg(length=TransitionLength, out_width=PortB.width)
            
            if(misalignment != 0):
                raise RuntimeError('For now, disable s-bends in connect_with_waveguide...must be aligned')
            # add_instances_port_to_port(InLayout,
            #                        inst_master: "PhotonicTemplateBase",
            #                        instance_port_name: str,
            #                        InLayout_port: Optional[PhotonicPort] = None,
            #                        InLayout_port_name: Optional[str] = None,
            #                        instance_name: Optional[str] = None,
            #                        reflect: bool = False,
            #                        )

            # # Make a straight waveguide with StraightLength
            # master = InLayout.template_db.new_template( params={ 'Length':  StraightLength,
            #                                                  'WaveguideWidth': WaveguideWidth, 
            #                                                  'LayerPurposePairList':  lpplist  },  
            #                                         temp_cls = wg_class)
            # # Place it aligned with PortA, but pushed out by TransitionLength
            # transformB = PortA.port_to_port_cardinal_transform(master.PhotPorts[0], invertY = False, 
            #                                                    offset_outward=TransitionLength)
            # InstW = InLayout.add_instance(master, None, loc=transformB[0], orient=transformB[1], unit_mode=False)
            # InstanceList.append(InstW)
            # # # Instance waveguides between each grating port and InstW, using Path class features
            # PortW = Ports Of Instance(InstW)[0]
            # master, loc, orient, invertY, params = PortA.port_to_port_new_localphot_template(
            #     InLayout, template_class=wg_class, PortIndex=0, 
            #     params={'LayerPurposePairList':  lpplist}, 
            #     invertY=False, anotherPort=PortW)
            # InstanceList.append(InLayout.add_instance(master, None, loc=loc, orient=orient, unit_mode=False))
            # PortW = Ports Of Instance(InstW)[1]
            # master, loc, orient, invertY, params = PortB.port_to_port_new_localphot_template(
            #     InLayout, template_class=wg_class, PortIndex=0, 
            #     params={'LayerPurposePairList':  lpplist}, 
            #     invertY=False, anotherPort=PortW)
            # InstanceList.append(InLayout.add_instance(master, None, loc=loc, orient=orient, unit_mode=False))
        else: 
            if(misalignment != 0):
                router = WgRouter(InLayout, init_port=PortA, layer=lpp_routing, name=None)
                # print("In connect_ports, port_sep=%.3f, misalignment=%.3f" % (port_sep,misalignment))
                router.add_polygon_s_bend(length=np.ceil( float(port_sep) / (1.0 * gridres) ) * (1.0 * gridres), 
                                          shift_left=-misalignment, out_width=PortB.width)
            else:
                router = WgRouter(InLayout, init_port=PortA, layer=lpp_routing, name=None)
                router.add_straight_wg(length=port_sep, out_width=PortB.width)
            # # If the StraightLength is too short, simply connect with a single waveguide
            # master, loc, orient, invertY, params = PortA.port_to_port_new_localphot_template(
            #     InLayout, template_class=wg_class, PortIndex=0, 
            #     params={'LayerPurposePairList':  lpplist}, 
            #     invertY=False, anotherPort=PortB)
            # InstanceList.append(InLayout.add_instance(master, None, loc=loc, orient=orient, unit_mode=False))
        return InstanceList

