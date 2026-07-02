import numpy as np, sys, os
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter
W,H=3840,2160; cx,cy=W/2,H/2
yy,xx=np.mgrid[0:H,0:W].astype(float)
X0=(xx-cx)/(H/2); Y0=(yy-cy)/(H/2)
# TEXTURA DE PARED tileable (roca organica): noise multi-octava
rng=np.random.default_rng(4); TW,TH=512,512
base=np.zeros((TH,TW))
for oc,(sc,amp) in enumerate([(8,1.0),(16,0.5),(32,0.25),(64,0.12)]):
    n=rng.random((sc,sc)); n=np.asarray(Image.fromarray((n*255).astype(np.uint8)).resize((TW,TH),Image.BICUBIC),float)/255
    base+=n*amp
base=(base-base.min())/(base.max()-base.min())
# tile vertical (v) y horizontal (u) para continuidad
base=np.vstack([base,base[::-1]]); base=np.hstack([base,base[:,::-1]])  # mirror tile
BTH,BTW=base.shape
def frame(t):
    entry=0.34+0.66*min(1.0,(t/2.6))**0.7   # entrada: tunel arranca CHICO/lejos (boca con luz) y CRECE = volamos hacia adentro
    X=X0/entry; Y=Y0/entry
    r=np.sqrt(X*X+Y*Y)+1e-4; th=np.arctan2(Y,X)
    u=((th+0.12*np.sin(t*0.4))/(2*np.pi))%1.0   # rotacion lenta inmersiva
    _u0=(th/(2*np.pi))%1.0                 # angular (pared alrededor)
    v=(0.35/r + t*0.24)                  # scroll mas lento (viaje pausado)
    ui=((u*BTW*1.0)%BTW).astype(int)
    vi=((v*BTH*0.9)%BTH).astype(int)
    wall=base[vi,ui]
    # relieve: 2da capa de textura a otra escala (detalle)
    vi2=((v*BTH*2.3+30)%BTH).astype(int); ui2=((u*BTW*2.0)%BTW).astype(int)
    wall=wall*0.7+base[vi2,ui2]*0.3
    wall=np.clip((wall-0.5)*1.3+0.5,0,1)
    # iluminacion: paredes se oscurecen hacia el fondo (r chico) + luz al fondo
    depth=np.clip(r*1.7,0.12,1)           # cerca=claro
    img=wall*depth*1.7+wall*0.15        # paredes mas visibles
    # luz de fondo va POST-grim
    img=gaussian_filter(img,0.8)
    img=np.clip(img,0,1.6)/1.6
    deep=np.array([0.02,0.06,0.035]); brite=np.array([0.16,0.55,0.28])  # verde grim roca
    rgb=np.clip(deep+(brite-deep)*img[...,None],0,1)*255
    g=grim(rgb.astype(np.uint8), scale=1.0, grain_amt=2.0, gamma=1.32).astype(float)
    core=gaussian_filter(np.exp(-(r/0.11)**2),22)      # fantasmal: mas ancho + muy difuso
    halo=gaussian_filter(np.exp(-(r/0.26)**2),30)
    core/=core.max()+1e-9; halo/=halo.max()+1e-9
    g=g+core[...,None]*np.array([0.85,1.0,0.92])*255*0.85 + halo[...,None]*np.array([0.45,0.7,0.55])*255*0.6  # fantasmal (mas tenue)
    return np.clip(g,0,255).astype(np.uint8)
import glob
os.makedirs('/Users/emilianomettini/outbound_work/_tnp',exist_ok=True)
for o in glob.glob('/Users/emilianomettini/outbound_work/_tnp/f*.png'): os.remove(o)
for f in range(120):
    Image.fromarray(frame(f/24.0)).save('/Users/emilianomettini/outbound_work/_tnp/f%03d.png'%f)
print('CLIP 4K DONE 120')
