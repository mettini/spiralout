import numpy as np, glob, os, sys
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter
W,H=960,540
def ease(x): x=np.clip(x,0,1); return x*x*(3-2*x)
def cl(x): return max(0.,min(1.,x))
yy,xx=np.mgrid[0:H,0:W].astype(float); X=(xx-W/2)/(H/2); Y=(yy-H/2)/(H/2)
R=np.sqrt(X*X+Y*Y); TH=np.arctan2(Y,X)
_rng=np.random.default_rng(11); _neb=gaussian_filter(_rng.random((H,W)),76); _neb=(_neb-_neb.min())/(_neb.max()-_neb.min())
def fnum(p): return int(os.path.basename(p)[1:-4])
estelas=sorted(glob.glob('/tmp/anim/estelas/grim/f*.png'), key=fnum); NE=len(estelas)
mandfr=sorted(glob.glob('/tmp/anim/mandala/grim/f*.png'), key=fnum); NM=len(mandfr)   # mandala REAL (empalme perfecto)

def mand_intensity(P):
    def ring(c,w): return np.exp(-((R-c)/w)**2)
    def pet(N,sh,sp): return np.clip(np.cos(N*(TH+sp)),0,1)**sh
    frac=np.zeros_like(R)
    for o in range(4):
        fk=1.8**o; frac+=(1/fk)*np.cos((8*fk)*(TH+P*0.5)+R*10*fk-P*1.1)
    frac=0.5+0.4*(frac-frac.min())/(np.ptp(frac)+1e-9)
    m=ring(0.16,0.04)*1.0+ring(0.26,0.035)*pet(12,3,P*1.4)*1.3+ring(0.30,0.02)*0.6
    m+=ring(0.42,0.045)*pet(24,4,-P*2.1)*1.1+ring(0.50,0.02)*0.7+ring(0.60,0.045)*pet(16,5,P*1.1)*1.0
    m+=ring(0.70,0.03)*pet(48,6,-P*1.7)*0.7+ring(0.80,0.04)*pet(32,7,P*0.9)*0.6+ring(0.90,0.02)*0.4
    m+=np.exp(-R*7.5)*1.6
    m*=frac; m*=np.clip(1.15-R*0.7,0,1); return np.clip(m,0,1.9)
deep=np.array([0.02,0.10,0.05]); brite=np.array([0.22,0.66,0.36]); nebcol=np.array([0.035,0.12,0.06])

COMP=int(12.0*24); FPS=24   # +material para que el fade kaleido->mandala complete
os.makedirs('/tmp/anim/kaleido/grim',exist_ok=True)
for old in glob.glob('/tmp/anim/kaleido/grim/f*.png'): os.remove(old)
for cf in range(COMP):
    t=cf/FPS
    # mandala DEBAJO = frames REALES del mandala_synced (empalme perfecto, mismo color/forma)
    mand_img=np.asarray(Image.open(mandfr[min(NM-1,cf)]).convert('RGB').resize((W,H)),float)
    # ESTELAS (escena anterior) que estallan en luz
    ei=min(NE-1, 1368+int(t*12)); e=np.asarray(Image.open(estelas[ei]).convert('RGB').resize((W,H)),float)   # climax estelas (~357 en timeline)
    amp=ease(cl((t-2.0)/0.9))                 # las estelas REVIENTAN en luz (PUM ~2-3s)
    rad=0.30+1.7*ease(cl((t-2.0)/1.5))
    kray=(0.5+0.5*np.cos(20*(TH+0.2*t)))**2; krings=0.5+0.5*np.cos(R*22-t*3.0)
    kal=kray*(0.4+0.6*krings)*np.exp(-(R/rad)**1.5); kal=gaussian_filter(kal,3.0); kal/=kal.max()+1e-9
    estelas_layer=e*(1+2.6*amp) + (kal*amp)[...,None]*np.array([0.6,1.0,0.7])*255*1.7  # estelas blow-out + caleido
    op=1.0-ease(cl((t-3.5)/4.7))              # la LUZ se disipa LENTO 3.5->8.2 y revela el mandala
    img=mand_img*(1-op)+estelas_layer*op       # capas YA grim-eadas (empalme consistente)
    g=img+np.random.default_rng(cf).normal(0,1,(H,W,1))*2.0   # grano ligero (sin doble-grim)
    Image.fromarray(np.clip(g,0,255).astype(np.uint8)).save(f'/tmp/anim/kaleido/grim/f{cf:03d}.png')
print('KALEIDO DONE', COMP)
