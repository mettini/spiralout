import numpy as np, os, glob
from PIL import Image
# ===== Mandelbrot DISTANCE ESTIMATION (filamentos crispos, continuos, sin musgo/popping) =====
# DE = 2|z|ln|z| / |dz|  (Wikipedia: Plotting algorithms for the Mandelbrot set)
W,H=1920,1080; asp=W/H
NF=int(os.environ.get('NF','144'))
OUT='/Users/emilianomettini/crossing_work/mandel_de'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
PX,PY=-0.743643887037151, 0.131825904205330
S0=1.3; SEND=2e-3
deep=np.array([0.010,0.020,0.014]); mid=np.array([0.07,0.13,0.09]); bright=np.array([0.30,0.46,0.34])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
vel=np.ones(NF); ramp=int(2.2*24)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
yy,xx=np.mgrid[0:H,0:W].astype(float); u=(xx/W-0.5)*2*asp; v=(yy/H-0.5)*2
for f in range(NF):
    p=peff[f]; scale=S0*(SEND/S0)**p
    rot=p*0.6+0.05*np.sin(p*6.28)
    maxi=int(180+360*p)
    c,s=np.cos(rot),np.sin(rot); ur=u*c-v*s; vr=u*s+v*c
    X=PX+ur*scale; Y=PY+vr*scale; C=X+1j*Y
    Z=np.zeros_like(C); dZ=np.zeros_like(C); SN=np.zeros(C.shape); mask=np.ones(C.shape,bool)
    BAIL=1e6
    for i in range(maxi):
        dZ[mask]=2.0*Z[mask]*dZ[mask]+1.0
        Z[mask]=Z[mask]*Z[mask]+C[mask]
        esc=(Z.real*Z.real+Z.imag*Z.imag)>BAIL*BAIL; just=esc&mask
        if i>2: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
        mask[just]=False
        if i%40==0 and not mask.any(): break
    interior=mask
    az=np.abs(Z)+1e-12; absdz=np.abs(dZ)+1e-12
    DE=2.0*az*np.log(az)/absdz                 # distancia al borde (plano c)
    dpix=DE*H/(2.0*scale)                        # en pixeles
    # FILAMENTOS crispos: glow que cae con la distancia al borde (AA natural)
    fila=np.exp(-np.clip(dpix,0,None)/1.6)
    # flujo suave de fondo (bandas) tenue, para que no sea solo lineas sobre negro
    band=0.5+0.5*np.cos(6.2831*SN*0.30 + p*3.0)
    bg=(0.5+0.5*band)*np.exp(-np.clip(dpix,0,None)/22.0)   # halo amplio alrededor de los filamentos
    col=deep[None,None,:]+ (mid-deep)[None,None,:]*bg[...,None] + (bright-mid)[None,None,:]*fila[...,None]
    col[interior]=deep*0.5
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).save(f'{OUT}/f{f:04d}.png')
    if f%24==0: print('de',f,'scale',f'{scale:.1e}','iter',maxi)
print('DE DONE',NF)
