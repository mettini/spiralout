#!/usr/bin/env python3
"""grim_post.py — pase de grade GRIM reusable (reconstruido del spec en memoria
crossing_abstracts_grim_aesthetic). Black metal noruego: poco verde/desaturado,
duro/oscuro, DIFUSO (mata bordes poligonales limpios), distorsionado, grano.
Aplicar a CADA render del video. Uso: grim_post.py in.png out.png [--scale 1.0]
"""
import sys, argparse
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

def grim(img, scale=1.0, bright=1.0, grain_amt=7.0, gamma=1.35, desat=0.78):
    # bright>1.0 aclara (escenas que no deben quedar tan oscuras, ej. ovulo)
    # grain_amt: intensidad del grano (bajar en escenas oscuras que se ven "granuladas")
    # gamma: <1.35 = menos crush (mas brillo en midtones); desat: 0..1 cuanto monocromo
    h,w,_=img.shape; s=scale
    x=img.astype(np.float64)/255.0
    # 1) DESATURAR a gris-verde (poco verde, blanquecino, no lime)
    lum=(x*np.array([0.30,0.59,0.11])).sum(2,keepdims=True)
    x=lum*desat + x*(1.0-desat)              # casi monocromo
    tint=np.array([0.82,1.0,0.86])           # tinte verde sucio MUY leve sobre gris
    x=x*tint
    # 2) SOFTEN GLOBAL (difuminar = matar el borde poligonal limpio)
    blur=np.stack([gaussian_filter(x[...,c], 2.2*s) for c in range(3)],-1)
    x=x*0.45 + blur*0.55
    # 3) CRUSH / lo-fi: blacks lavados + hombro, bajo rango dinámico
    x=0.02 + 0.93*bright*np.power(np.clip(x,0,1), gamma)   # lift + gamma (milky, oscuro)
    # 4) ABERRACION CROMATICA (radial, sucia)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float64)
    cx,cy=w/2,h/2; dx=(xx-cx)/w; dy=(yy-cy)/h
    sh=0.9*s
    for c,m in ((0,1.0),(2,-1.0)):
        x[...,c]=map_coordinates(x[...,c], [yy+dy*sh*m*6, xx+dx*sh*m*6], order=1, mode='nearest')
    # 5) NEBULA: ruido baja frecuencia (atmosfera de pantano) multiplicativo
    rng=np.random.default_rng(7)
    neb=gaussian_filter(rng.random((h,w)), 40*s)
    neb=(neb-neb.min())/(neb.max()-neb.min())
    x=x*(0.82+0.18*neb[...,None])
    # 6) VIÑETA dura
    r=np.sqrt(dx*dx+dy*dy)
    vig=np.clip(1.0-np.power(r*1.35,2.2),0.15,1.0)
    x=x*vig[...,None]
    # 7) GRANO pesado (analogico) — tambien anti-banding del encoder
    grain=rng.normal(0,1,(h,w,1))*(grain_amt/255.0)
    x=x+grain
    return np.clip(x*255,0,255).astype(np.uint8)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('outp'); ap.add_argument('--scale',type=float,default=1.0)
    a=ap.parse_args()
    im=np.asarray(Image.open(a.inp).convert('RGB'))
    Image.fromarray(grim(im,a.scale)).save(a.outp)
    print('grim ->',a.outp)
