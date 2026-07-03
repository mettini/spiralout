import sys, os, glob
sys.path.insert(0,'/Users/emilianomettini/git/spiralout/transmissions/01/video/blender')
from grim_post import grim
from PIL import Image
import numpy as np
raw, out = sys.argv[1], sys.argv[2]
bright=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
grain =float(sys.argv[4]) if len(sys.argv)>4 else 7.0
gamma =float(sys.argv[5]) if len(sys.argv)>5 else 1.35
os.makedirs(out, exist_ok=True)
for fp in sorted(glob.glob(f'{raw}/f*.png'), key=lambda p:int(os.path.basename(p)[1:-4])):
    arr=np.asarray(Image.open(fp).convert('RGB'))
    Image.fromarray(grim(arr, scale=1.0, bright=bright, grain_amt=grain, gamma=gamma)).save(os.path.join(out, os.path.basename(fp)))
print('POST DONE', raw, 'bright',bright,'grain',grain,'gamma',gamma)
