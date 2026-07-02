import numpy as np, glob, os, sys, math
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
from scipy.ndimage import gaussian_filter
# Igual que ovulo_post_sync.py pero a 1920x1080 (raw 4x de 480). Params en px escalados ~x4;
# grim scale=2.0 (balance: mantiene el grim pero deja pasar algo del detalle nativo de 1080).
BELL_EVENTS=[(39.683,1.0),(46.684,1.0),(50.196,0.55),(50.370,0.55),(50.828,0.35),(51.026,0.35),
 (51.682,0.30),(56.988,0.55),(57.185,0.55),(57.980,0.30),(59.193,0.30),(64.685,1.0),(69.416,1.0),(72.301,0.6)]
def bump(t):
    return min(1.0, sum(a*math.exp(-((t-et)/0.07)**2) for et,a in BELL_EVENTS))
def fnum(p): return int(os.path.basename(p)[1:-4])
raw=sorted(glob.glob('/tmp/anim/ov1080/raw/f*.png'), key=fnum)
out='/tmp/anim/ov1080/grim'; os.makedirs(out,exist_ok=True)
for old in glob.glob(out+'/f*.png'): os.remove(old)
H=W=None
for fp in raw:
    f=fnum(fp); t=f/24.0
    arr=np.asarray(Image.open(fp).convert('RGB'),float)
    if H is None:
        H,W,_=arr.shape; cx,cy=W*0.499,H*0.498
        yy,xx=np.mgrid[0:H,0:W].astype(float)
        R=np.sqrt(((xx-cx)/(H*0.42))**2+((yy-cy)/(H*0.42))**2)
    b=bump(t)
    if b>0.001:
        halo=gaussian_filter(np.exp(-(R/0.40)**2)*b,48.0)   # 12*4 (mismo halo a 1920)
        arr=arr+halo[...,None]*np.array([0.5,1.0,0.62])*255*1.0
    g=grim(np.clip(arr,0,255).astype(np.uint8), scale=2.0, bright=1.15, grain_amt=1.3, gamma=1.12)
    Image.fromarray(g).save(f'{out}/f{f:03d}.png')
print('OVULO 1080 POST DONE', len(raw))
