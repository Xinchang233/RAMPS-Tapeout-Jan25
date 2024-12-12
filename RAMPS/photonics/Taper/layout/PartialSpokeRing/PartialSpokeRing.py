import BPG
import warnings
import math
from layout.SimpleRing.SimpleRing import SimpleRing



class PartialSpokeRing(BPG.PhotonicTemplateBase):
    """
  
    """
    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        BPG.PhotonicTemplateBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        
        ## 1. Ring parameters
            # Required
        self.ring_layer = self.params['ring_layer']
        self.port_layer = self.params['port_layer']
        self.r_out = self.params['r_out']
        self.ring_width = self.params['ring_width']
            # Optional
        self.r_eff = self.params['r_eff']
        
        ## 2. Spokes
        self.outer_layer = self.params['outer_layer']
        self.spoke_width = self.params['spoke_width']
        self.l_outer = self.params['l_outer']
        self.l_inner = self.params['l_inner']
        self.a_s = self.params['a_s']
        self.a_e = self.params['a_e']
        self.N = self.params['N']
        self.n = self.params['n']
               
        # Check parameter validity
        
        if self.a_s >= self.a_e :
            raise ValueError('start angle "a_s" should be smaller that end angle "a_e"')
        
        if (self.r_eff-0.5*self.spoke_width) <= (self.r_out-self.ring_width) :
            raise ValueError('Spokes exceed inner ring boundary, use a smaller spoke width, or use another effective radius')
        
        if (self.r_eff+0.5*self.spoke_width) >= (self.r_out) :
            raise ValueError('Spokes exceed outer ring boundary, use a smaller spoke width, or use another effective radius')

       

    @classmethod
    
    def get_default_param_values(cls):
        return dict(
            ring_layer=None,
            port_layer=None,
            r_out=None,
            ring_width=None,
            r_eff = None,
            
            outer_layer = None,
            spoke_width = None,
            l_outer = None,
            l_inner = None,
            a_s = 0,
            a_e = 45,
            N = 22,
            n = 100
            
            
        )

    
    
    def get_params_info(cls):  # Returns definition of the parameters.
        return dict(
            ring_layer='ring layer',
            port_layer='ring port layer',
            r_out='outer radius of ring',
            ring_width='width of ring',
            r_eff = 'effective radius of ring, should be given by mode solver',
            
            outer_layer = 'outer spoke layer',
            spoke_width = 'width of the spokes in the ring',
            l_outer = 'outer buff for the spoke',
            l_inner = 'inner buff for the spoke',
            a_s = 'starting angle of spokes, in degrees',
            a_e = 'end angle of spokes, in degrees',
            N = 'number of spokes, should be integer',
            n = 'number of points in each spoke, default 100'
        )

    def draw_layout(self):

        i = 1
        k = 1
        a_s = self.a_s * math.pi/180
        a_e = self.a_e * math.pi/180
        x = []
        y = []
        theta = (a_e-a_s)/(2*self.N)
        da = theta/self.n
        # point = []
        
        while i <= self.N :
            x.append((self.r_eff-0.5*self.spoke_width) * math.cos(a_s+2*(i-1)*theta))
            y.append((self.r_eff-0.5*self.spoke_width) * math.sin(a_s+2*(i-1)*theta))
            k = k + 1
            
            j = 1
            while j <= self.n :
                x.append((self.r_eff-0.5*self.spoke_width) * math.cos(a_s+2*(i-1)*theta+j*da))
                y.append((self.r_eff-0.5*self.spoke_width) * math.sin(a_s+2*(i-1)*theta+j*da))
                k = k + 1
                j = j + 1
                
            x.append((self.r_eff+0.5*self.spoke_width) * math.cos(a_s+(2*i-1)*theta))
            y.append((self.r_eff+0.5*self.spoke_width) * math.sin(a_s+(2*i-1)*theta))
            k = k + 1
            
            j = 1
            while j <= self.n :
                x.append((self.r_eff+0.5*self.spoke_width) * math.cos(a_s+(2*i-1)*theta+j*da))
                y.append((self.r_eff+0.5*self.spoke_width) * math.sin(a_s+(2*i-1)*theta+j*da))
                k = k + 1
                j = j + 1              
            i = i + 1
            
        x.append((self.r_out+self.l_outer) * math.cos(a_s+2*self.N*theta))
        y.append((self.r_out+self.l_outer) * math.sin(a_s+2*self.N*theta))
        k = k + 1
        
        x.append((self.r_out+self.l_outer) * math.cos(a_s))
        y.append((self.r_out+self.l_outer) * math.sin(a_s))
        # k = k + 1
        
        
        self.add_polygon(
                layer=self.outer_layer,
                points=[(x[t], y[t]) for t in range(k)],
                resolution=self.grid.resolution,
                unit_mode=False
            ) 

            
        self.add_round(layer=self.ring_layer,
                       resolution=self.grid.resolution,
                       center=(0, 0),
                       rin=self.r_out - self.ring_width,
                       rout=self.r_out)
        
       
