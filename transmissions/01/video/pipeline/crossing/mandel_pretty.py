import numpy as np, os
from PIL import Image
# ===== Mandelbrot AGRADABLE: DE + SLOPE SHADING (relieve 3D) + supersampling fuerte =====
import os as _o; BASE_W,BASE_H=1280,720; SS=int(_o.environ.get("SS",3)); W,H=BASE_W*SS,BASE_H*SS; asp=W/H
PX,PY=-0.74364388703, 0.13182590421
scale=float(os.environ.get('SCALE','3e-3'))
maxi=int(os.environ.get('MAXI','500'))
deep=np.array([0.010,0.022,0.015]); midc=np.array([0.10,0.17,0.12]); hi=np.array([0.34,0.50,0.38])
yy,xx=np.mgrid[0:H,0:W].astype(float); u=(xx/W-0.5)*2*asp; v=(yy/H-0.5)*2
X=PX+u*scale; Y=PY+v*scale; C=X+1j*Y
Z=np.zeros_like(C); dZ=np.zeros_like(C); SN=np.zeros(C.shape); mask=np.ones(C.shape,bool); BAIL=1e6
for i in range(maxi):
    dZ[mask]=2.0*Z[mask]*dZ[mask]+1.0
    Z[mask]=Z[mask]*Z[mask]+C[mask]
    esc=(Z.real*Z.real+Z.imag*Z.imag)>BAIL*BAIL; just=esc&mask
    if i>2: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
    mask[just]=False
    if i%40==0 and not mask.any(): break
interior=mask
# --- SLOPE SHADING: normal desde u=z/dz -> relieve 3D (no plano) ---
U=Z/(dZ+1e-12); U=U/(np.abs(U)+1e-12)        # normal compleja unitaria
ang=np.radians(45.0); lx,ly=np.cos(ang),np.sin(ang); hgt=1.5
shade=(U.real*lx+U.imag*ly+hgt)/(1.0+hgt)
shade=np.clip(shade,0,1)
# --- DE para borde crispo ---
az=np.abs(Z)+1e-12; absdz=np.abs(dZ)+1e-12
DE=2.0*az*np.log(az)/absdz; dpix=DE*H/(2.0*scale)
edge=np.exp(-np.clip(dpix,0,None)/2.0)
# --- color: bandas suaves * shade (relieve) + edge highlight ---
band=0.5+0.5*np.cos(6.2831*SN*0.12)
val=(0.35+0.65*band)*shade
col=deep[None,None,:]+(midc-deep)[None,None,:]*val[...,None]+(hi-midc)[None,None,:]*(val*edge)[...,None]
col[interior]=deep*0.4
img=Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((BASE_W,BASE_H),Image.LANCZOS)
out=os.environ.get('OUT','/Users/emilianomettini/crossing_work/_mandel_pretty.png')
img.save(out); print('PRETTY DONE',out,'scale',scale)
