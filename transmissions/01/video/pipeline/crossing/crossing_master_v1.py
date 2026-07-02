import numpy as np, glob, os
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== CROSSING — primera aproximacion del video entero (13:00) =====
# Sync/estructura tomados del shader original (render.py): fases, SHADOW_TRAJ, opacidades,
# eventos de luz. Humo (Blender loop) + sombra difusa + DELIRADA Mandelbrot en el agujero.
W,H=640,360; asp=W/H; FPS=24; DUR=780.0; N=int(DUR*FPS)
OUT='/Users/emilianomettini/crossing_work/master_frames'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
def fnum(p): return int(os.path.basename(p)[1:-4])
HUMO=sorted(glob.glob('/Users/emilianomettini/crossing_work/humo_loop/f*.png'),key=fnum)
DEL =sorted(glob.glob('/Users/emilianomettini/crossing_work/mandel_delirium/f*.png'),key=fnum)
LH=len(HUMO); LD=len(DEL)
print('humo',LH,'delirium',LD)
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
cfps=int(ctrl['fps']); flux=ctrl['flux']; low=ctrl['rms_low']; air=ctrl['rms_air']
def cn(a): a=np.asarray(a,float); return (a-a.min())/(np.ptp(a)+1e-9)
flux=cn(flux); low=cn(low); air=cn(air)
def cval(arr,f): i=int(f/FPS*cfps); return float(arr[max(0,min(len(arr)-1,i))])
# ---- sync keys del original (t en minutos) ----
SHADOW_TRAJ=[(0,0.15,0.15),(0.5,0.20,0.18),(1.0,0.28,0.22),(1.5,0.36,0.27),(2.0,0.44,0.32),
 (2.5,0.50,0.36),(4.3,0.56,0.40),(6.3,0.58,0.42),(8.0,0.60,0.44),(10.5,0.66,0.50),(13.0,0.74,0.58)]
SHADOW_OP=[(0,0.55),(1.5,0.60),(3.0,0.65),(4.3,0.72),(5.3,0.52),(6.3,0.58),(8.0,0.48),(10.5,0.38),(13.0,0.22)]
PALETTE=[(0,0.068,0.160,0.092),(1.5,0.077,0.180,0.102),(3,0.060,0.150,0.085),(4.3,0.036,0.095,0.054),
 (6.3,0.031,0.088,0.050),(7.3,0.078,0.170,0.098),(10.5,0.060,0.142,0.082),(13,0.054,0.130,0.075)]
def lin(keys,t,ncol):
    ts=[k[0] for k in keys]
    if t<=ts[0]: return keys[0][1:]
    if t>=ts[-1]: return keys[-1][1:]
    for i in range(len(ts)-1):
        if ts[i]<=t<=ts[i+1]:
            a=(t-ts[i])/(ts[i+1]-ts[i]); return tuple(keys[i][1+j]+(keys[i+1][1+j]-keys[i][1+j])*a for j in range(ncol))
    return keys[-1][1:]
def phase(tm):
    # liso, nebula, fractales (del original)
    if tm<2.0: return (1,0,0)
    if tm<2.5: k=(tm-2.0)/0.5; return (1-k,k,0)
    if tm<4.0: return (0,1,0)
    if tm<4.5: k=(tm-4.0)/0.5; return (0,1-k,k)
    if tm<6.5: return (0,0,1)
    if tm<8.5: k=(tm-6.5)/2.0; return (k,0,1-k)
    return (1,0,0)
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
yy,xx=np.mgrid[0:H,0:W].astype(float)
r_c=np.sqrt(((xx-W/2)/(H/2))**2+((yy-H/2)/(H/2))**2)
def ellipse(cx,cy,rx,ry,rot):
    X=(xx/W-cx)*asp; Y=(yy/H-cy); c,s=np.cos(rot),np.sin(rot); Xr=X*c-Y*s; Yr=X*s+Y*c
    return np.exp(-((Xr/rx)**2+(Yr/ry)**2))
# anti-banding estatico
_rng=np.random.default_rng(7)
_nlow=gaussian_filter(_rng.random((H,W)),40); _nlow-=_nlow.mean()
_nmid=gaussian_filter(_rng.random((H,W)),12); _nmid-=_nmid.mean()
_atmo=(_nlow*0.55+_nmid*0.45); _atmo/=(np.abs(_atmo).max()+1e-9)
_grain=_rng.random((H,W))-0.5
# delirium en campo redondo (agujero): vigneta
vig_hole=1-np.clip((r_c-0.42)/(1.15-0.42),0,1)**1.3
def humo_idx(f):
    per=2*LH-2; i=f%per; return i if i<LH else per-i
FRAC0=int(4.5*60*FPS)  # inicio fractales (4:30 con crossfade ~4:00-4:30)
for f in range(N):
    tm=f/FPS/60.0; wl,wn,wf=phase(tm); fl=cval(flux,f); lo=cval(low,f); ai=cval(air,f)
    # ---- BASE: humo (liso+nebula) ----
    hu=np.asarray(Image.open(HUMO[humo_idx(f)]).convert('RGB'),float)
    pr,pg,pb=lin(PALETTE,tm,3); tint=np.array([pr,pg,pb])/np.array([0.06,0.15,0.09])
    base=hu*tint
    if wn>0: base=base*(1.0+0.25*wn)  # nebula un poco mas activa/densa
    # ---- DELIRADA Mandelbrot en el agujero (fase fractales) ----
    if wf>0.001:
        di=min(LD-1,(f-FRAC0)//2); di=max(0,di)
        dl=np.asarray(Image.open(DEL[di]).convert('RGB').resize((W,H)),float)
        dl=dl*vig_hole[...,None]                 # dentro del campo redondo (agujero)
        # halo difuso atras (profundidad)
        halo=np.exp(-((r_c-0.55)/0.30)**2)*0.10
        dl=dl+halo[...,None]*np.array([0.14,0.17,0.15])*255
        base=base*(1-wf)+dl*wf
    out=base.copy()
    # ---- SOMBRA difusa (fade en fractales: adentro del agujero no hay sombra) ----
    sh_vis=(1.0-wf)
    if sh_vis>0.01:
        _,sx,sy=(0,)+lin(SHADOW_TRAJ,tm,2)
        op=lin(SHADOW_OP,tm,1)[0]
        breath=1.0+0.10*lo+0.06*fl
        rx=(0.15+0.02*np.sin(tm*0.6))*breath; ry=(0.24+0.03*np.sin(tm*0.43))*breath; rot=0.12*np.sin(tm*0.3)
        m=np.maximum(ellipse(sx,sy-0.16*ry/0.24,rx*0.7,ry*0.55,rot), ellipse(sx,sy+0.22*ry/0.24,rx*0.8,ry*0.85,rot))
        m=gaussian_filter(m,30); m=m/(m.max()+1e-9)
        strength=op*sh_vis*(0.9+0.2*fl); darkfloor=0.40
        out=out*(1.0-(m*strength)*(1.0-darkfloor))[...,None]
        # PERMEACION: crece hacia el climax (4:30) y en la 2da mitad recede
        perm=ease((tm-1.0)/3.3)*(1-wf)  # 0 en 1min -> 1 hacia 4:18
        if tm>6.5: perm*=max(0.0,1-(tm-6.5)/4.0)
        spread=gaussian_filter(m,75); spread/= (spread.max()+1e-9)
        glob_dark=(0.4+0.6*spread)*perm*0.35
        out=out*(1.0-glob_dark)[...,None]
    # ---- EVENTOS DE LUZ (back half): bells 10:30-12:10 sup-izq + voyager sup-der ----
    if 10.3<tm<12.2:
        bw=ease((tm-10.3)/0.5)*ease((12.2-tm)/0.5)*(0.5+0.5*ai)
        gl=np.exp(-(((xx/W-0.13))**2+((yy/H-0.18))**2)/0.10)
        out=out+gl[...,None]*np.array([0.5,1.0,0.55])*255*0.18*bw
    out=np.clip(out,0,255)
    # ---- ANTI-BANDING ----
    lum=out.mean(2)/255.0; aamp=0.05+(0.22-0.05)*np.clip((0.30-lum)/0.26,0,1)
    out=out*(1.0+_atmo[...,None]*aamp[...,None]) + _grain[...,None]*7.0
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(f'{OUT}/f{f:05d}.png')
    if f%480==0: print('master',f, f'{tm:.1f}min')
print('MASTER FRAMES DONE',N)
