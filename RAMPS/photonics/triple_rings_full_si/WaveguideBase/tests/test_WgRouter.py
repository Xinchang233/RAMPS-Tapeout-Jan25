import BPG
from Photonic_Core_Layout.WaveguideBase.WgRouter import WgRouter


class WgRouterTester(BPG.PhotonicTemplateBase):
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        return dict()

    def draw_layout(self):

        # ------------- Basic component route tests -------------

        self.add_photonic_port(name='init0',
                               center=(0, 0),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('init0'),
                          layer=('SI', 'drawing'))
        (router
         .add_straight_wg(length=10.0)
         .add_90_bend(bend_params=dict(bend_type='circular', radius=5.0), direction='right')
         .add_90_bend(bend_params=dict(bend_type='circular', radius=5.0), direction='right'))

        # ------------- Cardinal route tests -------------
        # Stairstep route test
        self.add_photonic_port(name='init1',
                               center=(0, 10),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('init1'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2.0),
                               points=[
                                   (5, 15),
                                   (10, 20),
                                   (15, 25)
                               ])

        # Co-linear starting point test
        self.add_photonic_port(name='init2',
                               center=(0, 30),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('init2'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[
                                   (5, 30),
                                   (10, 30),
                                   (15, 30),
                                   (15, 35)
                               ])

        # ------------- L-route tests from Cardinal Router -------------
        # Left/Right routes
        self.add_photonic_port(name='RightDown',
                               center=(30, 0),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('RightDown'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(35, -5)])

        self.add_photonic_port(name='RightUp',
                               center=(30, 10),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('RightUp'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(35, 15)])

        self.add_photonic_port(name='LeftDown',
                               center=(30, 20),
                               orient='R0',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('LeftDown'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(25, 15)])

        self.add_photonic_port(name='LeftUp',
                               center=(30, 30),
                               orient='R0',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('LeftUp'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(25, 35)])

        # Up/Down routes
        self.add_photonic_port(name='UpRight',
                               center=(50, 0),
                               orient='R270',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('UpRight'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(55, 5)])

        self.add_photonic_port(name='UpLeft',
                               center=(50, 10),
                               orient='R270',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('UpLeft'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(45, 15)])

        self.add_photonic_port(name='DownRight',
                               center=(50, 20),
                               orient='R90',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('DownRight'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(55, 15)])

        self.add_photonic_port(name='DownLeft',
                               center=(50, 30),
                               orient='R90',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('DownLeft'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[(45, 25)])

        # These cases must fail!!
        self.add_photonic_port(name='FailUpLeft',
                               center=(60, 10),
                               orient='R270',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('FailUpLeft'),
                          layer=('SI', 'drawing'))
        try:
            router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                                   points=[(65, 5)])
        except ValueError:
            assert True
        else:
            assert False

        self.add_photonic_port(name='FailDownRight',
                               center=(60, 20),
                               orient='R90',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('FailDownRight'),
                          layer=('SI', 'drawing'))
        try:
            router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                                   points=[(55, 25)])
        except ValueError:
            assert True
        else:
            assert False

        # ------------- Relative point bend tests -------------
        self.add_photonic_port(name='Relative_point_test',
                               center=(70, 0),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('Relative_point_test'),
                          layer=('SI', 'drawing'))
        router.cardinal_router(bend_params=dict(bend_type='circular', radius=2),
                               points=[
                                   (5, 15),
                                   (10, 20),
                                   (15, 25)
                               ],
                               relative_coords=True)

        # ------------- Default bend settings tests -------------
        self.add_photonic_port(name='Default_Bend_Params',
                               center=(90, 0),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('Default_Bend_Params'),
                          layer=('SI', 'drawing'))

        router.set_default_bend_params(
            bend_params=dict(
                bend_type='euler',
                radius=3,
                euler_percent=1
            )
        )
        router.cardinal_router(
                               points=[
                                   (5, 0),
                                   (10, 10),
                                   (15, 25)
                               ],
                               relative_coords=True)

        # ------------- Switching defaults bend settings tests -------------
        self.add_photonic_port(name='Switch_bend_params',
                               center=(90, 40),
                               orient='R180',
                               width=1.0,
                               layer='SI')
        router = WgRouter(gen_cls=self,
                          init_port=self.get_photonic_port('Switch_bend_params'),
                          layer=('SI', 'drawing'))

        router.set_default_bend_params(
            bend_params=dict(
                bend_type='euler',
                radius=3,
                euler_percent=1
            )
        )
        router.cardinal_router(
            points=[
                (5, 0),
                (10, 10),
                (15, 25)
            ],
            relative_coords=True)
        router.cardinal_router(
            points=[
                (5, 0),
                (10, 10),
                (15, -25)
            ],
            relative_coords=True,
            bend_params=dict(
                bend_type='circular',
                radius=4
            )
        )
        router.cardinal_router(
            points=[
                (5, 0),
                (10, -10),
                (15, -25)
            ],
            relative_coords=True)


def test_router_base():
    spec_file = 'Photonic_Core_Layout/WaveguideBase/specs/wgrouter.yaml'
    plm = BPG.PhotonicLayoutManager(spec_file)
    plm.generate_content()
    plm.generate_gds()
    # plm.generate_flat_content()
    # plm.generate_flat_gds()
    # plm.generate_lsf()


if __name__ == '__main__':
    test_router_base()
