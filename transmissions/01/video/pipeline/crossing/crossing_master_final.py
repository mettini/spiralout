import numpy as np, glob, os
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== CROSSING FINAL — video entero 1080, sync del original + fixes =====
W,H=1920,1080; asp=W/H; FPS=24; DUR=780.0; N=int(DUR*FPS); S=W/640.0
MW,MH=480,270   # mascaras (sombra) en baja-res -> upscale (rapido; son blobs blureados)
OUT='/Users/emilianomettini/crossing_work/final_frames'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
def fnum(p): return int(os.path.basename(p)[1:-4])
HUMO=sorted(glob.glob('/Users/emilianomettini/crossing_work/humo_loop_hq/f*.png'),key=fnum)
DEL =sorted(glob.glob('/Users/emilianomettini/crossing_work/kali_delirium/f*.png'),key=fnum)
LH=len(HUMO); LD=len(DEL); print('humo',LH,'delirium',LD)
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
cfps=int(ctrl['fps']); flux=ctrl['flux']; low=ctrl['rms_low']; air=ctrl['rms_air']
from scipy.ndimage import uniform_filter1d
def cn(a): a=np.asarray(a,float); return (a-a.min())/(np.ptp(a)+1e-9)
# SUAVIZAR la reactividad (ventana ~2.5s) -> la sombra NO tiembla
flux=cn(uniform_filter1d(cn(flux),int(cfps*2.5))); low=cn(uniform_filter1d(cn(low),int(cfps*2.5))); air=cn(air)
def cval(arr,f): i=int(f/FPS*cfps); return float(arr[max(0,min(len(arr)-1,i))])
SHADOW_TRAJ=[(0,0.15,0.15),(0.5,0.20,0.18),(1.0,0.28,0.22),(1.5,0.36,0.27),(2.0,0.44,0.32),
 (2.5,0.50,0.36),(4.3,0.56,0.40),(6.3,0.58,0.42),(8.0,0.60,0.44),(10.5,0.66,0.50),(13.0,0.74,0.58)]
SHADOW_OP=[(0,0.62),(1.5,0.68),(3.0,0.74),(4.3,0.80),(5.3,0.60),(6.3,0.64),(8.0,0.56),(10.5,0.46),(13.0,0.30)]
PALETTE=[(0,0.068,0.160,0.092),(1.5,0.077,0.180,0.102),(3,0.060,0.150,0.085),(4.3,0.036,0.095,0.054),
 (6.3,0.031,0.088,0.050),(7.3,0.078,0.170,0.098),(10.5,0.060,0.142,0.082),(13,0.054,0.130,0.075)]
def lin(keys,t,nc):
    ts=[k[0] for k in keys]
    if t<=ts[0]: return keys[0][1:]
    if t>=ts[-1]: return keys[-1][1:]
    for i in range(len(ts)-1):
        if ts[i]<=t<=ts[i+1]:
            a=(t-ts[i])/(ts[i+1]-ts[i]); return tuple(keys[i][1+j]+(keys[i+1][1+j]-keys[i][1+j])*a for j in range(nc))
    return keys[-1][1:]
def phase(tm):
    if tm<2.0: return (1,0,0)
    if tm<2.5: k=(tm-2.0)/0.5; return (1-k,k,0)
    if tm<4.0: return (0,1,0)
    if tm<4.5: k=(tm-4.0)/0.5; return (0,1-k,k)
    if tm<6.5: return (0,0,1)
    if tm<7.5: k=(tm-6.5)/1.0; return (k,0,1-k)   # fade fractales->liso CORTO (1min)
    return (1,0,0)
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
# grillas
yy,xx=np.mgrid[0:H,0:W].astype(float); r_c=np.sqrt(((xx-W/2)/(H/2))**2+((yy-H/2)/(H/2))**2)
myy,mxx=np.mgrid[0:MH,0:MW].astype(float)
def ell_m(cx,cy,rx,ry,rot):
    X=(mxx/MW-cx)*asp; Y=(myy/MH-cy); c,s=np.cos(rot),np.sin(rot); Xr=X*c-Y*s; Yr=X*s+Y*c
    return np.exp(-((Xr/rx)**2+(Yr/ry)**2))
def up(m): return np.asarray(Image.fromarray((m*255).astype('uint8')).resize((W,H),Image.BILINEAR),float)/255.0
# anti-banding estatico (1080)
_rng=np.random.default_rng(7)
_nlow=gaussian_filter(_rng.random((H,W)),40*S); _nlow-=_nlow.mean()
_nmid=gaussian_filter(_rng.random((H,W)),12*S); _nmid-=_nmid.mean()
_atmo=(_nlow*0.55+_nmid*0.45); _atmo/=(np.abs(_atmo).max()+1e-9); _grain=_rng.random((H,W))-0.5
vig_hole=1-np.clip((r_c-0.42)/(1.15-0.42),0,1)**1.3
halo_hole=np.exp(-((r_c-0.55)/0.30)**2)*0.10
def humo_idx(f):
    per=2*LH-2; i=f%per; return i if i<LH else per-i
FRAC0=int(4.5*60*FPS)
F_A=int(os.environ.get('START_F','0')); F_B=int(os.environ.get('END_F',str(N)))
for f in range(F_A,F_B):
    tm=f/FPS/60.0; wl,wn,wf=phase(tm); fl=cval(flux,f); lo=cval(low,f); ai=cval(air,f)
    hu=np.asarray(Image.open(HUMO[humo_idx(f)]).convert('RGB'),float)
    pr,pg,pb=lin(PALETTE,tm,3); tint=np.array([pr,pg,pb])/np.array([0.06,0.15,0.09])
    base=hu*tint
    if wn>0: base=base*(1.0+0.22*wn)
    if wf>0.001:
        di=min(LD-1,max(0,(f-FRAC0)//2))
        dl=np.asarray(Image.open(DEL[di]).convert('RGB').resize((W,H),Image.LANCZOS),float)  # Kaliset FULL-SCREEN
        base=base*(1-wf)+dl*wf
    out=base.copy()
    sh_vis=1.0-wf
    if sh_vis>0.01:
        _,sx,sy=(0,)+lin(SHADOW_TRAJ,tm,2); op=lin(SHADOW_OP,tm,1)[0]
        breath=1.0+0.04*lo+0.015*fl                       # respira lento y poco (estable)
        rx=(0.15+0.008*np.sin(tm*0.22))*breath; ry=(0.26+0.012*np.sin(tm*0.16))*breath; rot=0.05*np.sin(tm*0.12)
        m=np.maximum(ell_m(sx,sy-0.16*ry/0.26,rx*0.72,ry*0.55,rot), ell_m(sx,sy+0.22*ry/0.26,rx*0.82,ry*0.88,rot))
        m=gaussian_filter(m,18); m=m/(m.max()+1e-9); mU=up(m)
        strength=op*sh_vis*(0.97+0.06*fl); darkfloor=0.16
        out=out*(1.0-(mU*strength)*(1.0-darkfloor))[...,None]
        perm=ease((tm-1.0)/3.3)*sh_vis
        if tm>6.5: perm*=max(0.0,1-(tm-6.5)/2.0)
        spread=up(gaussian_filter(m,45)); spread/=(spread.max()+1e-9)
        out=out*(1.0-(0.4+0.6*spread)*perm*0.30)[...,None]
    if 10.3<tm<12.2:
        bw=ease((tm-10.3)/0.5)*ease((12.2-tm)/0.5)*(0.5+0.5*ai)
        gl=np.exp(-(((xx/W-0.13))**2+((yy/H-0.18))**2)/0.10)
        out=out+gl[...,None]*np.array([0.5,1.0,0.55])*255*0.18*bw
    out=np.clip(out,0,255)
    lum=out.mean(2)/255.0; aamp=0.05+(0.22-0.05)*np.clip((0.30-lum)/0.26,0,1)
    out=out*(1.0+_atmo[...,None]*aamp[...,None]) + _grain[...,None]*5.5
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(f'{OUT}/f{f:05d}.png')
    if f%480==0: print('final',f,f'{tm:.1f}min')
print('FINAL FRAMES DONE',N)
