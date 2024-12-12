from BPG.gds.io import GDSImport
from BPG import PhotonicTemplateBase
from pathlib import Path

from abc import abstractmethod


class FoundryImport(PhotonicTemplateBase):
    """
    Instantiate a Foundry pcell (exported as GDS) with no_dataprep and
    other markup applied
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

        self.input_gds_filename = self.params['input_gds_filename']
        self.version_dir = self.params['version_dir']

        self.gds_instance = None

    @classmethod
    def get_params_info(cls):
        return dict(
            input_gds_filename='Input filename of gds cell to import',
            version_dir='Directory of PDK version',
        )

    @classmethod
    def get_default_param_values(cls):
        return dict(
#            version_dir='V0.5_2.0',
            version_dir='V0.9_0.1',
        )

    def add_gds_layout(self):
        master_gds = self.new_template(
            params=dict(
                gds_path=str(Path(__file__).parent / self.version_dir / self.input_gds_filename)
            ),
            temp_cls=GDSImport
        )

        self.gds_instance = self.add_instance(
            master=master_gds,
            loc=(0, 0),
            orient='R0',
        )

    @abstractmethod
    def draw_layout(self):
        pass
