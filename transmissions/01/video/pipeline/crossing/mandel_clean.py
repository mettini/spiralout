import numpy as np, os, glob
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== Mandelbrot LIMPIO: ease-in + supersampling (AA, sin musgo) + menos iter (mas simple) =====
W,H=960,540; SS=2; cw,ch=W*SS,H*SS; asp=cw/ch
NF=int(os.environ.get('NF','240'))   # 10s @24fps (test)
OUT='/Users/emilianomettini/crossing_work/mandel_clean'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
PX,PY=-0.743643887037151, 0.131825904205330
S0=1.3; SEND=2e-3   # zoom SUAVE/no tan profundo = detalle disfrutable, no musgo
dark=np.array([0.05,0.080,0.062]); bright=np.array([0.235,0.330,0.275])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
# ease-in: velocidad de zoom arranca en 0 y sube en ~2.2s, despues constante
vel=np.ones(NF); ramp=int(2.2*24)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
yy,xx=np.mgrid[0:ch,0:cw].astype(float); u=(xx/cw-0.5)*2*asp; v=(yy/ch-0.5)*2
for f in range(NF):
    p=peff[f]
    scale=S0*(SEND/S0)**p
    rot=p*0.7 + 0.08*np.sin(p*6.28)      # rotacion mas calmada
    maxi=int(120+220*p)                   # MENOS iter (boundary mas limpio, menos musgo)
    c,s=np.cos(rot),np.sin(rot); ur=u*c-v*s; vr=u*s+v*c
    X=PX+ur*scale; Y=PY+vr*scale; C=X+1j*Y
    Z=np.zeros_like(C); SN=np.zeros(C.shape); mask=np.ones(C.shape,bool)
    for i in range(maxi):
        Z[mask]=Z[mask]*Z[mask]+C[mask]; esc=np.abs(Z)>64.0; just=esc&mask  # escape radius alto = smooth count limpio
        if i>3: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
        mask[just]=False
        if i%40==0 and not mask.any(): break
    interior=mask
    # coloreo: SOLO bandas suaves (las "olas"), sin resaltar el speckle del borde
    band=0.5+0.5*np.cos(6.2831*SN*0.42 + p*4.0)
    frac=np.clip(SN/max(maxi,1),0,1)
    col=dark+(bright-dark)*(np.power(frac,0.6)[...,None])
    col=col*(0.6+0.4*band)[...,None]
    col[interior]=dark*0.5
    # downscale SS -> AA (mata el musgo/interferencia)
    img=Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((W,H),Image.LANCZOS)
    img.save(f'{OUT}/f{f:04d}.png')
    if f%48==0: print('clean',f,'scale',f'{scale:.1e}','iter',maxi)
print('CLEAN DONE',NF)
