# -*- coding: utf-8 -*-
"""
@author: bohan

Run this file to generate all the taper clip blocks
"""

 
# -------------------------------------------------------
# Import dependencies


# generate gds function
from Photonic_Layout_45SPCLO.generate_gds import generate_gds

  # -------------------------------------------------------
# Main function, call this file to generate all the taperclip test site blocks

if __name__ == '__main__':

    # lambda 1550, w1 7 um, w2 0.5 um, 71.91 um long
    spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/Taperclips/taperclip_lam1d55_W1_7_W2_0d5_L71d91_Hamming_BPG.yaml'
    generate_gds( spec_file )

    # # lambda 1550, w1 15 um, w2 0.5 um, 279.3 um long
    # spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/Taperclips/taperclip_lam1d55_W1_15_W2_0d5_L279d3_Hamming_BPG.yaml'
    # generate_gds( spec_file )
    
    # # lambda 1300, w1 13 um, w2 0.41 um, 262.5 um long
    # spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/Taperclips/taperclip_lam1d3_W1_13_W2_0d41_L262d5_Hamming_BPG.yaml'
    # generate_gds( spec_file )

    # # lambda 1300, w1 7 um, w2 0.41 um, 86.29 um long
    # spec_file = 'Photonic_Layout_45SPCLO/Taper/specs/Taperclips/taperclip_lam1d3_W1_7_W2_0d41_L86d29_Hamming_BPG.yaml'
    # generate_gds( spec_file )
# end main()


