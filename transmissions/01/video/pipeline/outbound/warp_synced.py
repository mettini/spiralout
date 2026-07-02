import numpy as np, glob, os, sys
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter, uniform_filter1d
SS=2; W,H=960*SS,540*SS; cx,cy=W/2,H/2          # SUPERSAMPLING 2x -> downscale = lineas limpias
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/outbound.npz')
cfps=int(ctrl['fps']); rms=ctrl['rms']
SEC0=300.0; SEC_DUR=62.0; FPS=24; N=int(SEC_DUR*FPS)   # empieza 5:00 (fade letargico) hasta el kaleido
def ctl(arr,s):
    i=int((SEC0+s)*cfps); i=max(0,min(len(arr)-1,i)); return float(arr[i])
rng=np.random.default_rng(7); ST=420
ang=rng.uniform(0,2*np.pi,ST); u0=rng.uniform(0,1,ST); spd=rng.uniform(0.85,1.2,ST)
jit=rng.uniform(0.55,1.0,ST); hero=np.where(rng.random(ST)<0.06,2.4,1.0)
K=4.3; RMIN=2.2
yy,xx=np.mgrid[0:H,0:W]; Rn=np.sqrt(((xx-cx)/(H/2))**2+((yy-cy)/(H/2))**2)
_nz=gaussian_filter(np.random.default_rng(5).random((H,W)),7.0*SS); _nz=(_nz-_nz.min())/(_nz.max()-_nz.min())  # irregularidad del nucleo
def _ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
_rmss=uniform_filter1d(np.array([ctl(rms,f/FPS) for f in range(N)]), int(FPS*1.5))
ph=0.0; phases=[]; vel=0.45
for f in range(N):
    s=f/FPS; e=_rmss[f]
    spdmul=0.80+1.10*_ease((s-50.0)/4.0)         # acelera en ~5:50 (s50, SEC0=300); SIN frenado hasta la explosion
    target=0.020*(0.55+1.3*e)*spdmul
    vel+=(target-vel)*0.05
    ph+=vel; phases.append(ph)
os.makedirs('/tmp/anim/estelas/grim',exist_ok=True)
for old in glob.glob('/tmp/anim/estelas/grim/f*.png'): os.remove(old)
LSUB=46                                           # muchos sub-puntos = LINEA larga continua (no asterisco)
deep=np.array([0.01,0.05,0.025]); brite=np.array([0.34,0.92,0.50])
prev=None
for f in range(N):
    s=f/FPS; e=ctl(rms,s); P=phases[f]
    roll=0.04*P; a2=ang+roll; c2=np.cos(a2); s2=np.sin(a2)
    buf=np.zeros((H,W),float)
    scale=2.0+1.6*e
    for sps in range(LSUB):
        frac=sps/LSUB
        u=(u0+spd*P-frac*0.16)%1.0                # cola LARGA (estria de warp)
        rad=RMIN*np.exp(u*K)*scale
        x=cx+c2*rad*SS; y=cy+s2*rad*SS
        bright=jit*hero*(0.5+2.4*u)*(1-frac*0.78)*(0.5+0.9*e)
        m=(x>=0)&(x<W)&(y>=0)&(y<H)
        xi=x[m].astype(np.int64); yi=y[m].astype(np.int64)
        np.add.at(buf,(yi,xi),bright[m])
    buf=gaussian_filter(buf,1.4*SS)               # suaviza la linea
    buf*=2.6                                       # brillo FIJO (no auto-normalizar = estelas visibles)
    # NUCLEO FUZZY: ancho + irregular (noise) + difuso, sin saturar a disco perfecto
    ncore=np.exp(-Rn*7.0)*(0.5+0.7*_nz)           # ancho + borde irregular
    ncore=gaussian_filter(ncore,4.0*SS)
    buf+=ncore*(0.85+0.9*e)
    buf=np.clip(buf,0,1.0)
    # downscale supersampling -> limpio
    small=np.asarray(Image.fromarray((buf*255).astype(np.uint8)).resize((960,540),Image.LANCZOS),float)/255.0
    if prev is not None: small=0.72*small+0.28*prev # persistencia menor = sin fantasma/trabazon
    prev=small.copy()
    img=(np.clip(deep+(brite-deep)*small[...,None],0,1)*255).astype(np.uint8)
    Image.fromarray(grim(img, scale=1.0, grain_amt=2.0)).save(f'/tmp/anim/estelas/grim/f{f:03d}.png')
print('ESTELAS SYNCED DONE', N)
