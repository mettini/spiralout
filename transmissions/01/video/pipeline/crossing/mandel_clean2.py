import numpy as np, os, glob
from PIL import Image
from scipy.ndimage import gaussian_filter
# ===== Mandelbrot NATIVO 1080 + denoise dirigido (flujos suaves crispos, polvo -> negro) =====
W,H=1920,1080; asp=W/H
NF=int(os.environ.get('NF','144'))
OUT='/Users/emilianomettini/crossing_work/mandel_clean2'; os.makedirs(OUT,exist_ok=True)
for o in glob.glob(OUT+'/f*.png'): os.remove(o)
PX,PY=-0.743643887037151, 0.131825904205330
S0=1.3; SEND=4e-3
dark=np.array([0.05,0.080,0.062]); bright=np.array([0.235,0.330,0.275])
def ease(x): x=max(0.,min(1.,x)); return x*x*(3-2*x)
vel=np.ones(NF); ramp=int(2.2*24)
for i in range(min(ramp,NF)): vel[i]=ease(i/ramp)
peff=np.cumsum(vel); peff=peff/peff[-1]
yy,xx=np.mgrid[0:H,0:W].astype(float); u=(xx/W-0.5)*2*asp; v=(yy/H-0.5)*2
for f in range(NF):
    p=peff[f]; scale=S0*(SEND/S0)**p
    rot=p*0.6+0.06*np.sin(p*6.28)
    maxi=int(140+260*p)
    c,s=np.cos(rot),np.sin(rot); ur=u*c-v*s; vr=u*s+v*c
    X=PX+ur*scale; Y=PY+vr*scale; C=X+1j*Y
    Z=np.zeros_like(C); SN=np.full(C.shape,np.nan); mask=np.ones(C.shape,bool)
    for i in range(maxi):
        Z[mask]=Z[mask]*Z[mask]+C[mask]; esc=np.abs(Z)>128.0; just=esc&mask
        if i>3: SN[just]=i+1-np.log2(np.log2(np.abs(Z[just])+1e-9)+1e-9)
        mask[just]=False
        if i%40==0 and not mask.any(): break
    interior=mask
    SNf=np.nan_to_num(SN, nan=maxi)
    # DENOISE DIRIGIDO: varianza local de SN -> donde hay polvo (alta varianza) baja el brillo
    mean=gaussian_filter(SNf,2.0); var=gaussian_filter(SNf*SNf,2.0)-mean*mean
    smooth=np.exp(-np.clip(var,0,None)/3.0)        # 1=flujo suave, 0=polvo ruidoso
    band=0.5+0.5*np.cos(6.2831*SNf*0.40 + p*3.5)
    frac=np.clip(SNf/max(maxi,1),0,1)
    col=dark+(bright-dark)*(np.power(frac,0.62)[...,None])
    col=col*(0.55+0.45*band)[...,None]
    col=col*smooth[...,None]                        # el polvo -> oscuro; los flujos quedan
    col[interior]=dark*0.45
    Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).save(f'{OUT}/f{f:04d}.png')
    if f%24==0: print('clean2',f,'scale',f'{scale:.1e}','iter',maxi)
print('CLEAN2 DONE',NF)
