import numpy as np, os
from PIL import Image, ImageDraw
# ===== KALISET (IFS caleidoscopico): full-screen, patrones que se repiten, psicodelico =====
# p = abs(p)/dot(p,p) - C   (iterado) -> estructura fractal que llena la pantalla
BASE=640; SS=2; W=H=BASE*SS
yy,xx=np.mgrid[0:H,0:W].astype(float)
ux=(xx/W-0.5)*2.0; uy=(yy/H-0.5)*2.0
deep=np.array([0.010,0.022,0.015]); midc=np.array([0.10,0.20,0.13]); hi=np.array([0.40,0.62,0.45])
def kali(Cx,Cy,N=14,scale=1.0):
    px=ux*scale; py=uy*scale
    trap=np.full((H,W),1e9); glow=np.zeros((H,W))
    for i in range(N):
        d=px*px+py*py+1e-9
        px=np.abs(px)/d - Cx; py=np.abs(py)/d - Cy
        r=np.sqrt(px*px+py*py)
        trap=np.minimum(trap, np.abs(r-0.7))     # orbit trap (anillo)
        glow+=np.exp(-2.5*np.abs(px))            # acumulacion suave (psicodelico)
    t=np.clip(trap*3.0,0,1); g=np.clip(glow/N*2.0,0,1)
    val=(1-t)*0.6+g*0.6
    col=deep[None,None,:]+(midc-deep)[None,None,:]*val[...,None]+(hi-midc)[None,None,:]*(g[...,None])
    img=Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).resize((BASE,BASE),Image.LANCZOS)
    return img
combos=[(0.5,0.5),(0.7,0.3),(0.86,0.0),(0.9,0.65),(0.62,0.9),(1.0,1.0)]
cols=3; rows=2
sh=Image.new('RGB',(330*cols,330*rows+rows*16),(15,15,15)); dr=ImageDraw.Draw(sh)
for i,(cx,cy) in enumerate(combos):
    im=kali(cx,cy).resize((330,330)); x=(i%cols)*330; y=(i//cols)*(330+16)+14
    sh.paste(im,(x,y)); dr.text((x+5,y-13),f"C=({cx},{cy})",fill=(255,255,0))
sh.save('/tmp/_kali_grid.png'); print('ok')
