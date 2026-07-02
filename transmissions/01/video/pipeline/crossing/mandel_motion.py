import numpy as np, os, glob
from PIL import Image
# ===== Mandelbrot MOVIMIENTO: zoom LENTO por estructuras grandes + slope shading + SS2 =====
BASE_W,BASE_H=1280,720; SS=2; W,H=BASE_W*SS,BASE_H*SS; asp=W/H
NF=int(os.environ.get('NF','192'))
OUT='/Users/emilianomettini/crossing_work/mandel_motion'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
PX,PY=-0.74364388703, 0.13182590421
S0=1.6e-2; SEND=4e-3        # zoom LENTO/poco profundo -> estructuras GRANDES legibles
deep=np.array([0.010,0.022,0.015]); midc=np.array([0.10,0.17,0.12]); hi=np.array([0.34,0.50,0.38])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
vel=np.ones(NF); ramp=int(2.0*24)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
yy,xx=np.mgrid[0:H,0:W].astype(float); u=(xx/W-0.5)*2*asp; v=(yy/H-0.5)*2
for f in range(NF):
    p=peff[f]; scale=S0*(SEND/S0)**p
    rot=p*0.25
    maxi=int(260+200*p)
    c,s=np.cos(rot),np.sin(rot); ur=u*c-v*s; vr=u*s+v*c
    X=PX+ur*scale; Y=PY+vr*scale; C=X+1j*Y
    Z=np.zeros_like(C); dZ=np.zeros_like(C); SN=np.zeros(C.shape); mask=np.ones(C.shape,bool); BAIL=1e6
    for i in range(maxi):
        dZ[mask]=2.0*Z[mask]*dZ[mask]+1.0
        Z[mask]=Z[mask]*Z[mask]+C[mask]
        esc=(Z.real*Z.real+Z.imag*Z.imag)>BAIL*BAIL; just=esc&mask
        if i>2: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
        mask[just]=False
        if i%40==0 and not mask.any(): break
    interior=mask
    U=Z/(dZ+1e-12); U=U/(np.abs(U)+1e-12)
    ang=np.radians(45.0); lx,ly=np.cos(ang),np.sin(ang); hgt=1.5
    shade=np.clip((U.real*lx+U.imag*ly+hgt)/(1.0+hgt),0,1)
    az=np.abs(Z)+1e-12; absdz=np.abs(dZ)+1e-12
    DE=2.0*az*np.log(az)/absdz; dpix=DE*H/(2.0*scale); edge=np.exp(-np.clip(dpix,0,None)/2.0)
    band=0.5+0.5*np.cos(6.2831*SN*0.12 + p*2.0)
    val=(0.35+0.65*band)*shade
    col=deep[None,None,:]+(midc-deep)[None,None,:]*val[...,None]+(hi-midc)[None,None,:]*(val*edge)[...,None]
    col[interior]=deep*0.4
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((BASE_W,BASE_H),Image.LANCZOS).save(f'{OUT}/f{f:04d}.png')
    if f%24==0: print('motion',f,'scale',f'{scale:.1e}')
print('MOTION DONE',NF)
