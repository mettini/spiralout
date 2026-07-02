import numpy as np, glob, os
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== Preview HQ 1080: humo + SOMBRA VISIBLE (difusa pero perceptible) =====
W,H=1920,1080; asp=W/H; FPS=24; S=W/640.0   # factor de escala vs el test 640
HUMO=sorted(glob.glob('/Users/emilianomettini/crossing_work/humo_hq/f*.png'),key=lambda p:int(os.path.basename(p)[1:-4]))
N=len(HUMO)
OUT='/Users/emilianomettini/crossing_work/hq_frames'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
cfps=int(ctrl['fps']); flux=ctrl['flux']; low=ctrl['rms_low']
from scipy.ndimage import uniform_filter1d
def cn(a): a=np.asarray(a,float); return (a-a.min())/(np.ptp(a)+1e-9)
# SUAVIZAR FUERTE la reactividad (ventana ~2.5s) -> la sombra NO tiembla (no tubo fluorescente)
flux=uniform_filter1d(cn(flux), int(cfps*2.5)); low=uniform_filter1d(cn(low), int(cfps*2.5))
flux=cn(flux); low=cn(low)
START_S=60.0
def cval(arr,f): i=int((START_S+f/FPS)*cfps); return float(arr[max(0,min(len(arr)-1,i))])
yy,xx=np.mgrid[0:H,0:W].astype(float)
def ell(cx,cy,rx,ry,rot=0.0):
    X=(xx/W-cx)*asp; Y=(yy/H-cy); c,s=np.cos(rot),np.sin(rot); Xr=X*c-Y*s; Yr=X*s+Y*c
    return np.exp(-((Xr/rx)**2+(Yr/ry)**2))
# anti-banding estatico (sigmas escalados a 1080)
_rng=np.random.default_rng(7)
_nlow=gaussian_filter(_rng.random((H,W)),40*S); _nlow-=_nlow.mean()
_nmid=gaussian_filter(_rng.random((H,W)),12*S); _nmid-=_nmid.mean()
_atmo=(_nlow*0.55+_nmid*0.45); _atmo/=(np.abs(_atmo).max()+1e-9)
_grain=_rng.random((H,W))-0.5
for f in range(N):
    t=START_S+f/FPS; tm=t/60.0
    plate=np.asarray(Image.open(HUMO[f]).convert('RGB'),float)
    fl=cval(flux,f); lo=cval(low,f)
    # posicion (SHADOW_TRAJ ~1:00): deriva lenta
    cx=0.36+0.02*(f/N); cy=0.30+0.01*(f/N)
    breath=1.0+0.04*lo+0.015*fl                          # respira LENTO y poco (ya suavizado)
    rx=(0.15+0.008*np.sin(t*0.22))*breath; ry=(0.26+0.012*np.sin(t*0.16))*breath; rot=0.05*np.sin(t*0.12)
    m=np.maximum(ell(cx,cy-0.16*ry/0.26,rx*0.72,ry*0.55,rot), ell(cx,cy+0.22*ry/0.26,rx*0.82,ry*0.88,rot))
    m=gaussian_filter(m,18*S); m=m/(m.max()+1e-9)        # difusa pero VISIBLE
    strength=0.82*(0.97+0.06*fl); darkfloor=0.16         # presencia estable (no tiembla)
    out=plate*(1.0-(m*strength)*(1.0-darkfloor))[...,None]
    # leve permeacion alrededor de la figura
    spread=gaussian_filter(m,60*S); spread/= (spread.max()+1e-9)
    out=out*(1.0-spread*0.12)[...,None]
    # anti-banding
    lum=out.mean(2)/255.0; aamp=0.05+(0.22-0.05)*np.clip((0.30-lum)/0.26,0,1)
    out=out*(1.0+_atmo[...,None]*aamp[...,None]) + _grain[...,None]*5.5
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(f'{OUT}/f{f:04d}.png')
print('HQ FRAMES DONE',N)
