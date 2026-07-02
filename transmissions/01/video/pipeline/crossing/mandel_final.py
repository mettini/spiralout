import numpy as np, os
from PIL import Image
# ===== DELIRADA MANDELBROT: zoom profundo + rotacion, verde anegrado (seccion agujero) =====
W,H=960,540; asp=W/H
NF=int(os.environ.get('NF','2160'))   # 12fps * 120s
OUT='/Users/emilianomettini/crossing_work/mandel_final'; os.makedirs(OUT,exist_ok=True)
import glob
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
# punto de dive (seahorse valley deep)
PX,PY=-0.743643887037151, 0.131825904205330
S0=1.4   # escala inicial
SEND=3e-6  # escala final (zoom profundo)
dark=np.array([0.05,0.080,0.062]); bright=np.array([0.235,0.330,0.275])  # verde anegrado desat
yy,xx=np.mgrid[0:H,0:W].astype(float)
u=(xx/W-0.5)*2*asp; v=(yy/H-0.5)*2
for f in range(NF):
    p=f/(NF-1)
    scale=S0*(SEND/S0)**p                       # zoom exponencial = velocidad constante
    rot=p*1.2 + 0.15*np.sin(p*6.28*2)           # rotacion delirante
    maxi=int(200+600*p)                         # mas iteraciones al profundizar
    c,s=np.cos(rot),np.sin(rot)
    ur=u*c-v*s; vr=u*s+v*c
    X=PX+ur*scale; Y=PY+vr*scale
    C=X+1j*Y; Z=np.zeros_like(C); SN=np.zeros(C.shape); mask=np.ones(C.shape,bool)
    for i in range(maxi):
        Z[mask]=Z[mask]*Z[mask]+C[mask]; esc=np.abs(Z)>16.0; just=esc&mask
        if i>3: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
        mask[just]=False
        if i%50==0 and not mask.any(): break
    interior=mask
    band=0.5+0.5*np.cos(6.2831*SN*0.55 + p*6.0)  # bandas que corren (color cycle delirante)
    frac=np.clip(SN/max(maxi,1),0,1)
    col=dark+(bright-dark)*(np.power(frac,0.5)[...,None]); col=col*(0.5+0.5*band)[...,None]
    col[interior]=dark*0.5
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).save(f'{OUT}/f{f:04d}.png')
    if f%120==0: print('delirium',f,'scale',f'{scale:.1e}')
print('DELIRIUM DONE',NF)
