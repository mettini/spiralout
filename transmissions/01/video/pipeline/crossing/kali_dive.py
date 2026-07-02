import numpy as np, os, glob
from PIL import Image
# ===== KALISET DIVE: full-screen psicodelico, MUCHO NEGRO + estructuras verdes, zoom+morph =====
BASE_W,BASE_H=1280,720; SS=2; W,H=BASE_W*SS,BASE_H*SS; asp=W/H
NF=int(os.environ.get('NF','192'))
OUT='/Users/emilianomettini/crossing_work/kali_dive'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
yy,xx=np.mgrid[0:H,0:W].astype(float)
ux=(xx/W-0.5)*2.0*asp; uy=(yy/H-0.5)*2.0
deep=np.array([0.0,0.0,0.0]); green=np.array([0.10,0.34,0.18]); hot=np.array([0.45,0.78,0.52])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
vel=np.ones(NF); ramp=int(2.2*24)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
for f in range(NF):
    p=peff[f]
    zoom=1.4*(0.18/1.4)**p                         # zoom IN (nos metemos)
    # morph de la constante (delirio): se mueve lento entre patrones
    Cx=0.72+0.18*np.sin(p*6.28*0.5+0.3); Cy=0.40+0.30*np.sin(p*6.28*0.37)
    rot=p*0.5
    c,s=np.cos(rot),np.sin(rot)
    px=(ux*c-uy*s)*zoom; py=(ux*s+uy*c)*zoom
    trap=np.full((H,W),1e9); glow=np.zeros((H,W))
    N=16
    for i in range(N):
        d=px*px+py*py+1e-9
        px=np.abs(px)/d - Cx; py=np.abs(py)/d - Cy
        r=np.sqrt(px*px+py*py)
        trap=np.minimum(trap, np.abs(r-0.6))
        glow+=np.exp(-3.5*np.abs(px))*np.exp(-3.5*np.abs(py))
    # ALTO CONTRASTE sobre NEGRO: estructuras finas brillantes, resto negro
    stru=np.exp(-trap*7.0)                          # estructuras (orbit trap) brillantes
    g=np.clip(glow/N*1.5,0,1)
    val=np.clip(stru*0.85 + g*0.5, 0, 1)
    val=np.power(val,1.35)                          # mas negro (crush)
    col=deep[None,None,:]+(green)[None,None,:]*val[...,None]+(hot-green)[None,None,:]*(val*val)[...,None]
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((BASE_W,BASE_H),Image.LANCZOS).save(f'{OUT}/f{f:04d}.png')
    if f%24==0: print('kali',f,'zoom',f'{zoom:.2f}')
print('KALI DONE',NF)
