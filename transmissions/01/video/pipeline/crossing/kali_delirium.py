import numpy as np, os, glob
from PIL import Image
from scipy.ndimage import uniform_filter1d
# ===== KALISET DELIRIO full-length (4:30->7:30) verde+negro + BLOOM DE COLOR por audio en el pico =====
BASE_W,BASE_H=1280,720; SS=2; W,H=BASE_W*SS,BASE_H*SS; asp=W/H
FPS=12; DUR=180.0; NF=int(FPS*DUR)   # 2160 frames, se frame-doublea a 24 en el composite
OUT='/Users/emilianomettini/crossing_work/kali_delirium'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
T0=270.0   # 4:30 (inicio fractales)
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
cfps=int(ctrl['fps']); rms=ctrl['rms']
rms_n=(rms-rms.min())/(np.ptp(rms)+1e-9); rms_s=uniform_filter1d(rms_n,int(cfps*1.5))
def rms_at(t): i=int(t*cfps); return float(rms_s[max(0,min(len(rms_s)-1,i))])
yy,xx=np.mgrid[0:H,0:W].astype(float)
ux=(xx/W-0.5)*2.0*asp; uy=(yy/H-0.5)*2.0
green=np.array([0.10,0.34,0.18]); hot=np.array([0.45,0.78,0.52])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
vel=np.ones(NF); ramp=int(2.2*FPS)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
def hsv2rgb(h,s,v):
    h6=(h%1.0)*6; c=v*s; x=c*(1-np.abs(h6%2-1)); m=v-c
    r=np.zeros_like(h6); g=np.zeros_like(h6); b=np.zeros_like(h6)
    for cond,(rr,gg,bb) in [((h6<1),(c,x,0)),((h6>=1)&(h6<2),(x,c,0)),((h6>=2)&(h6<3),(0,c,x)),
                            ((h6>=3)&(h6<4),(0,x,c)),((h6>=4)&(h6<5),(x,0,c)),((h6>=5),(c,0,x))]:
        r=np.where(cond,rr,r); g=np.where(cond,gg,g); b=np.where(cond,bb,b)
    return np.stack([r+m,g+m,b+m],-1)
for f in range(NF):
    p=peff[f]; t=T0+f/FPS
    zoom=1.4*(0.16/1.4)**p
    Cx=0.72+0.18*np.sin(p*6.28*0.5+0.3); Cy=0.40+0.30*np.sin(p*6.28*0.37)
    rot=p*0.5; c,s=np.cos(rot),np.sin(rot)
    px=(ux*c-uy*s)*zoom; py=(ux*s+uy*c)*zoom
    trap=np.full((H,W),1e9); glow=np.zeros((H,W)); itn=np.zeros((H,W)); N=16
    for i in range(N):
        d=px*px+py*py+1e-9; px=np.abs(px)/d-Cx; py=np.abs(py)/d-Cy
        r=np.sqrt(px*px+py*py); nt=np.abs(r-0.6)
        upd=nt<trap; itn[upd]=i; trap=np.minimum(trap,nt)
        glow+=np.exp(-3.5*np.abs(px))*np.exp(-3.5*np.abs(py))
    stru=np.exp(-trap*7.0); g=np.clip(glow/N*1.5,0,1)
    val=np.power(np.clip(stru*0.85+g*0.5,0,1),1.35)
    # base VERDE+NEGRO
    col=green[None,None,:]*val[...,None]+(hot-green)[None,None,:]*(val*val)[...,None]
    # BLOOM DE COLOR en el pico (audio): solo cuando rms alto, mezcla hacia hue ciclante
    ramt=rms_at(t)
    cb=np.clip((ramt-0.42)/0.55,0,1)            # bloom mas GRADUAL y sostenido (entra antes, dura mas)
    if cb>0.02:
        # hue casi UNIFORME con deriva LENTA en el tiempo (cambios extendidos, no rainbow rapido)
        hue=(0.32 + p*0.28 + 0.07*(itn/N))%1.0
        colc=hsv2rgb(hue, 0.60, val)
        col=col*(1-cb*0.75)+colc*(cb*0.75)
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((BASE_W,BASE_H),Image.LANCZOS).save(f'{OUT}/f{f:04d}.png')
    if f%120==0: print('kali_del',f,'t',f'{t:.0f}s','colorbloom',round(cb,2))
print('KALI DELIRIUM DONE',NF)
