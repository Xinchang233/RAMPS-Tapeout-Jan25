import BPG

spec_file = 'layout/ArbitraryOrderRingFilter/specs/arb_order_filter.yaml'
plm = BPG.PhotonicLayoutManager(spec_file)
plm.generate_content()
plm.generate_gds()
plm.generate_flat_content()
plm.generate_flat_gds()
# plm.generate_lsf()