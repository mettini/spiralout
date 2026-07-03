import numpy as np, os, sys, glob
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter
W,H=960,540
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/outbound.npz')
cfps=int(ctrl['fps']); rms=ctrl['rms']; onset=ctrl['onset']
SEC0=360.0; SEC_DUR=60.0; FPS=24; N=int(SEC_DUR*FPS)
def ctl(arr,s):
    i=int((SEC0+s)*cfps); i=max(0,min(len(arr)-1,i)); return float(arr[i])
yy,xx=np.mgrid[0:H,0:W].astype(np.float64)
X=(xx-W/2)/(H/2); Y=(yy-H/2)/(H/2); R=np.sqrt(X*X+Y*Y); TH=np.arctan2(Y,X)
_rng=np.random.default_rng(11); _neb=gaussian_filter(_rng.random((H,W)),76); _neb=(_neb-_neb.min())/(_neb.max()-_neb.min())
# fase de giro acumulada con velocidad que sube con la energia
ph=0.0; phases=[]
for f in range(N):
    e=ctl(rms,f/FPS); ph+=0.012*(0.4+1.1*e); phases.append(ph)
def mandala(f):
    s=f/FPS; e=ctl(rms,s); su=ctl(onset,s); P=phases[f]
    bri=0.65+1.0*e                                  # brillo sube con la energia
    illo=0.4+0.6*e                                  # iris con la energia
    def ring(c,w): return np.exp(-((R-c)/w)**2)
    def pet(Np,sh,ph0,spin): return np.clip(np.cos(Np*(TH+spin)+ph0),0,1)**sh
    frac=np.zeros_like(R)
    for o in range(4):
        fk=1.8**o; frac+=(1/fk)*np.cos((8*fk)*(TH+P*0.5)+R*10*fk - P*1.1)
    frac=0.5+0.4*(frac-frac.min())/(np.ptp(frac)+1e-9)
    m=np.zeros_like(R)
    m+=ring(0.16,0.04)*1.0
    m+=ring(0.26,0.035)*pet(12,3,0, P*1.4)*1.3
    m+=ring(0.30,0.02)*0.6
    m+=ring(0.42,0.045)*pet(24,4,0,-P*2.1)*1.1
    m+=ring(0.50,0.02)*0.7
    m+=ring(0.60,0.045)*pet(16,5,0, P*1.1)*1.0
    m+=ring(0.70,0.03)*pet(48,6,0,-P*1.7)*0.7
    m+=ring(0.80,0.04)*pet(32,7,0, P*0.9)*0.6
    m+=ring(0.90,0.02)*0.4
    m+=np.exp(-R*7.5)*(1.0+1.1*illo+0.5*su)
    # OJO/IRIS central que se ABRE: un anillo brillante cuyo radio dilata con la energia + respira
    ap=0.05+0.17*e + 0.025*np.sin(s*1.4)
    m+=np.exp(-((R-ap)/0.035)**2)*(1.2+1.6*e)
    m*=frac; m*=np.clip(1.15-R*0.7,0,1); m=np.clip(m*bri,0,1.9)
    deep=np.array([0.02,0.10,0.05]); brite=np.array([0.22,0.66,0.36]); nebcol=np.array([0.035,0.12,0.06])
    base=deep + _neb[...,None]*nebcol*(0.6+0.4*illo) + np.exp(-R*1.1)[...,None]*nebcol*0.8
    return (np.clip(base+(brite-deep)*m[...,None],0,1)*255).astype(np.uint8)
os.makedirs('/tmp/anim/mandala/grim',exist_ok=True)
for old in glob.glob('/tmp/anim/mandala/grim/f*.png'): os.remove(old)
for f in range(N):
    Image.fromarray(grim(mandala(f), scale=1.0, grain_amt=2.0)).save(f'/tmp/anim/mandala/grim/f{f:03d}.png')
print('MANDALA SYNCED DONE', N)
