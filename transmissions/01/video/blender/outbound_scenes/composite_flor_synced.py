import numpy as np, glob, os, sys, math
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter
W,H=480,270
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
flower=sorted(glob.glob('/tmp/anim/bloom/raw/f*.png'))
humo=sorted(glob.glob('/tmp/anim/humo/raw/f*.png'))
warp=sorted(glob.glob('/tmp/anim/warp/grim/f*.png'))
NF=len(flower); NH=len(humo); NW=len(warp)
yy,xx=np.mgrid[0:H,0:W].astype(float); cx,cy=W/2,H/2
R=np.sqrt(((xx-cx)/(H/2))**2+((yy-cy)/(H/2))**2)
# control track real para latir con la musica
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/outbound.npz')
cfps=int(ctrl['fps']); onset=ctrl['onset']
SEC0=263.0          # inicio ventana bloom (humo todavia)
FPS=24; SEC_DUR=58.0; COMP=int(SEC_DUR*FPS)   # +material para que el fade flor->estelas complete
OPEN_END=150        # en el render de la flor: <=150 apertura, >150 viento
# tiempos: PUM ~s16 (280 swell), pleno ~s40 (303, cerca swell 300), estelas hacia el boundary 312
S_OPEN0=34.0; S_OPEN1=45.0; S_OUT=999.0; OUT_DUR=6.0   # apertura a 4:52 (sigue cerrada antes). fade flor->estelas = en el ensamble
def onset_at(s):
    i=int((SEC0+s)*cfps); i=max(0,min(len(onset)-1,i)); return float(onset[i])
os.makedirs('/tmp/anim/florseq/grim',exist_ok=True)
for old in glob.glob('/tmp/anim/florseq/grim/f*.png'): os.remove(old)

def light(s):
    puls=1.0+0.30*onset_at(s)
    if s<10.0:  return 0.16*ease(s/8.0)*puls, 0.12               # punto difuso que late con la musica
    if s<12.0:  p=ease((s-10.0)/2.0); return (0.16+0.84*p), 0.12+1.28*p   # PUM a 4:33 (273s)
    if s<17.0:  return 1.0+0.08*math.sin((s-12.0)*2.2), 1.36     # HOLD: la luz FLUCTUA antes de bajar
    p=ease((s-17.0)/12.0); return max(0.0,1.0*(1-p)), 1.36        # disipa LENTO

def fidx(s):
    if s<S_OPEN0: return 12
    # apertura LINEAL y pareja (sin doble-ease que la trababa al inicio)
    if s<S_OPEN1: return int(12 + (s-S_OPEN0)/(S_OPEN1-S_OPEN0)*(OPEN_END-12))
    return int(min(NF-1, OPEN_END + (s-S_OPEN1)/(SEC_DUR-S_OPEN1)*(NF-1-OPEN_END)))   # abierta + viento

for cf in range(COMP):
    s=cf/FPS
    img=np.asarray(Image.open(flower[fidx(s)]).convert('RGB'),float)
    if s<S_OPEN0+2:
        hi=min(NH-1, cf//3)                                       # humo lento sin wrap
        hu=np.asarray(Image.open(humo[hi]).convert('RGB'),float)
        cop=1.0-ease((s-26.0)/5.0)                                # nubes se despejan 26-31s (luz dura mas)
        img=img*(1-cop)+hu*cop
    amp,rad=light(s)
    if amp>0.001:
        glow=amp*np.exp(-(R/rad)**1.7); glow=gaussian_filter(glow,14.0)
        glow=glow/(glow.max()+1e-9)*amp*1.7
        img=img+glow[...,None]*np.array([0.55,1.0,0.66])*255
    out=grim(np.clip(img,0,255).astype(np.uint8), scale=1.0, bright=1.0, grain_amt=2.0, gamma=1.3).astype(float)
    if s>S_OUT:
        wi=min(NW-1,int((s-S_OUT)*FPS))
        wfr=np.asarray(Image.open(warp[wi]).convert('RGB').resize((W,H)),float)
        prog=ease((s-S_OUT)/OUT_DUR)
        base=out*(1-prog); out=255-(255-base)*(255-wfr*prog)/255.0   # estelas por screen, sin pelota
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'/tmp/anim/florseq/grim/f{cf:03d}.png')
print('FLOR SYNCED DONE', COMP)
