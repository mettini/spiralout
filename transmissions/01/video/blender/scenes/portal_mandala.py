import numpy as np, sys
from PIL import Image
W,H=960,540
rot=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
yy,xx=np.mgrid[0:H,0:W].astype(np.float64)
x=(xx-W/2)/(H/2); y=(yy-H/2)/(H/2)
r=np.sqrt(x*x+y*y); th=np.arctan2(y,x)+rot
def ring(c,w): return np.exp(-((r-c)/w)**2)
def pet(N,sh,ph=0): return np.clip(np.cos(N*th+ph),0,1)**sh
# detalle fractal sutil (sacred geometry)
frac=np.zeros_like(r)
for o in range(4):
    f=1.8**o; frac+=(1/f)*np.cos((8*f)*th+r*10*f-rot*2)
frac=0.5+0.4*(frac-frac.min())/(np.ptp(frac)+1e-9)
m=np.zeros_like(r)
m+=ring(0.16,0.04)*1.0
m+=ring(0.26,0.035)*pet(12,3)*1.3
m+=ring(0.30,0.02)*0.6
m+=ring(0.42,0.045)*pet(24,4,0.13)*1.1
m+=ring(0.50,0.02)*0.7
m+=ring(0.60,0.045)*pet(16,5)*1.0
m+=ring(0.70,0.03)*pet(48,6)*0.7
m+=ring(0.80,0.04)*pet(32,7,0.2)*0.6
m+=ring(0.90,0.02)*0.4
m+=np.exp(-r*7.5)*1.5            # iris/tercer ojo
m*=frac                          # fractal modula todo
m*=np.clip(1.1-r*0.7,0,1)        # falloff suave
m=np.clip(m,0,1.7)
deep=np.array([0.02,0.10,0.05]); brite=np.array([0.22,0.66,0.36])
col=np.clip(deep+(brite-deep)*m[...,None],0,1)
Image.fromarray((col*255).astype(np.uint8)).save(sys.argv[1])
print('ok')
