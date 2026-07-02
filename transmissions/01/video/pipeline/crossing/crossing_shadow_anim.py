import numpy as np, glob, os, sys
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== Compositor sombra animada sobre el humo (escena 1 test) =====
W,H=640,360; asp=W/H; FPS=24
HUMO=sorted(glob.glob('/Users/emilianomettini/crossing_work/humo_anim/f*.png'))
N=len(HUMO)
OUTDIR='/Users/emilianomettini/crossing_work/scene1_frames'; os.makedirs(OUTDIR,exist_ok=True)
for o in glob.glob(OUTDIR+'/f*.png'): os.remove(o)
# control track de crossing
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
cfps=int(ctrl['fps']); flux=ctrl['flux']; low=ctrl['rms_low']
def cnorm(a):
    a=np.asarray(a,float); return (a-a.min())/(np.ptp(a)+1e-9)
flux=cnorm(flux); low=cnorm(low)
def cval(arr,f):
    i=int(f/FPS*cfps); i=max(0,min(len(arr)-1,i)); return float(arr[i])
yy,xx=np.mgrid[0:H,0:W].astype(float)
def ell(cx,cy,rx,ry,rot=0.0):
    X=(xx/W-cx)*asp; Y=(yy/H-cy)
    c,s=np.cos(rot),np.sin(rot); Xr=X*c-Y*s; Yr=X*s+Y*c
    return np.exp(-((Xr/rx)**2+(Yr/ry)**2))
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
# ---- ANTI-BANDING ESTATICO (tecnica del shader original): low+mid freq + grano fino, FIJO ----
_rng=np.random.default_rng(7)
_nlow=gaussian_filter(_rng.random((H,W)),40); _nlow=_nlow-_nlow.mean()
_nmid=gaussian_filter(_rng.random((H,W)),12); _nmid=_nmid-_nmid.mean()
_atmo=(_nlow*0.55+_nmid*0.45); _atmo=_atmo/(np.abs(_atmo).max()+1e-9)
_grain=(_rng.random((H,W))-0.5)   # estatico (no per-frame = no GOP-pumping en YouTube)
for f in range(N):
    t=f/FPS; u=t/ (N/FPS)            # 0..1 a lo largo del clip
    plate=np.asarray(Image.open(HUMO[f]).convert('RGB'),float)
    fl=cval(flux,f); lo=cval(low,f)
    # ---- DERIVA: la sombra entra arriba-izquierda y cruza lento hacia el centro ----
    cx=0.30+0.16*u + 0.012*np.sin(t*0.5)
    cy=0.34+0.10*u + 0.010*np.sin(t*0.37+1.0)
    # ---- MORPH de forma (masa amorfa que cambia lento) + breathing por audio ----
    breath=1.0+0.10*lo+0.06*fl
    rx=(0.16+0.02*np.sin(t*0.6))*breath
    ry=(0.24+0.03*np.sin(t*0.43+2.0))*breath
    rot=0.12*np.sin(t*0.3)
    # masa AMORFA difusa: apenas una presencia vertical (NO forma humana marcada)
    m=np.maximum.reduce([
        ell(cx,cy-0.16*ry/0.24,rx*0.70,ry*0.55,rot),   # parte alta difusa
        ell(cx,cy+0.22*ry/0.24,rx*0.80,ry*0.85,rot)])  # cuerpo difuso
    m=gaussian_filter(m,30); m=m/(m.max()+1e-9)        # MUCHO blur = ambiguo, no humano
    # ---- presencia de la sombra (mas sutil, el negro fuerte se guarda para el climax) ----
    pres=0.38+0.22*ease(u)                       # menos presencia que antes
    strength=pres*(0.95+0.20*fl)                 # vibra con el flux
    darkfloor=0.40                               # mas alto = menos negro
    out=plate*(1.0-(m*strength)*(1.0-darkfloor))[...,None]
    # permeacion LEVE (no toma tanto negro todavia; el grande va al climax mas adelante)
    permeate=ease((u-0.30)/0.70)*0.20*(0.9+0.2*lo)
    spread=gaussian_filter(m,75); spread=spread/(spread.max()+1e-9)
    glob_dark=(0.4*permeate + 0.6*permeate*spread)
    out=out*(1.0-glob_dark*0.5)[...,None]
    # ---- ANTI-BANDING: atmosfera estructural (mas en darks) + grano fino estatico ----
    lum=out.mean(2)/255.0
    aamp=0.05+(0.22-0.05)*np.clip((0.30-lum)/0.26,0,1)
    out=out*(1.0+_atmo[...,None]*aamp[...,None])
    out=out+_grain[...,None]*7.0
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(f'{OUTDIR}/f{f:04d}.png')
print('SCENE1 FRAMES DONE', N)
