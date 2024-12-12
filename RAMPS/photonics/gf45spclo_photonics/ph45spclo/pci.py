from .foundry_import import FoundryImport


class all_pci(FoundryImport):
	"""
	BPG wrapper around pci cell for signoff
	"""
	
	def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
		FoundryImport.__init__(self, temp_db, lib_name, params, used_names, **kwargs)

	@classmethod
	def get_params_info(cls):
		params = FoundryImport.get_params_info()
		return params

	@classmethod
	def get_default_param_values(cls):
		default_params = FoundryImport.get_default_param_values()
		default_params.update(
			dict(input_gds_filename='all_pci.gds')
		)
		return default_params

	def draw_layout(self):
		self.add_gds_layout()

