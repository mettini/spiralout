import bpy, math, os
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'
try:
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='METAL'; p.get_devices()
    for d in p.devices: d.use=True
    S.cycles.device='GPU'
except Exception as e: print('gpu',e)
S.cycles.samples=44; S.cycles.use_denoising=True
import os as _o
S.render.resolution_x=int(_o.environ.get('BL_W',960)); S.render.resolution_y=int(_o.environ.get('BL_H',540))
if _o.environ.get('BL_SAMPLES'): S.cycles.samples=int(_o.environ['BL_SAMPLES'])
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='AgX'; S.view_settings.exposure=-0.5   # +luz (no tan oscuro)
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0,0.0,0.0,1)

# backdrop nebulosa + estrellas
bpy.ops.mesh.primitive_uv_sphere_add(radius=24, segments=64, ring_count=32)
sky=bpy.context.active_object; bpy.ops.object.shade_smooth()
sm=bpy.data.materials.new('sky'); sm.use_nodes=True; sn=sm.node_tree; sn.nodes.clear()
so=sn.nodes.new('ShaderNodeOutputMaterial'); sem=sn.nodes.new('ShaderNodeEmission')
stc=sn.nodes.new('ShaderNodeTexCoord')
neb=sn.nodes.new('ShaderNodeTexNoise'); neb.inputs['Scale'].default_value=2.2; neb.inputs['Detail'].default_value=8.0; neb.inputs['Roughness'].default_value=0.7
nr=sn.nodes.new('ShaderNodeValToRGB')
nr.color_ramp.elements[0].position=0.45; nr.color_ramp.elements[0].color=(0,0,0,1)
nr.color_ramp.elements[1].position=0.72; nr.color_ramp.elements[1].color=(0.03,0.18,0.09,1)
star=sn.nodes.new('ShaderNodeTexNoise'); star.inputs['Scale'].default_value=60.0; star.inputs['Detail'].default_value=2.0
sr=sn.nodes.new('ShaderNodeValToRGB')
sr.color_ramp.elements[0].position=0.72; sr.color_ramp.elements[0].color=(0,0,0,1)
sr.color_ramp.elements[1].position=0.78; sr.color_ramp.elements[1].color=(0.5,0.7,0.55,1)
addsky=sn.nodes.new('ShaderNodeMixRGB'); addsky.blend_type='ADD'
sn.links.new(stc.outputs['Generated'], neb.inputs['Vector'])
sn.links.new(stc.outputs['Generated'], star.inputs['Vector'])
sn.links.new(neb.outputs['Fac'], nr.inputs['Fac']); sn.links.new(star.outputs['Fac'], sr.inputs['Fac'])
sn.links.new(nr.outputs['Color'], addsky.inputs[1]); sn.links.new(sr.outputs['Color'], addsky.inputs[2])
sn.links.new(addsky.outputs['Color'], sem.inputs['Color'])
sem.inputs['Strength'].default_value=1.7   # +nebula (era 1.4)
sn.links.new(sem.outputs['Emission'], so.inputs['Surface'])
sky.data.materials.append(sm)

# ovulo continentes + rim + beep interior
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4, segments=128, ring_count=64)
ov=bpy.context.active_object; bpy.ops.object.shade_smooth()
mat=bpy.data.materials.new('ovulo'); mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled')
tc=nt.nodes.new('ShaderNodeTexCoord'); noi=nt.nodes.new('ShaderNodeTexNoise')
noi.inputs['Scale'].default_value=3.5; noi.inputs['Detail'].default_value=12.0
ramp=nt.nodes.new('ShaderNodeValToRGB')   # continentes con MAS contraste (que se vean)
ramp.color_ramp.elements[0].position=0.36; ramp.color_ramp.elements[0].color=(0.012,0.05,0.024,1)
ramp.color_ramp.elements[1].position=0.60; ramp.color_ramp.elements[1].color=(0.20,0.56,0.28,1)
nt.links.new(tc.outputs['Object'], noi.inputs['Vector']); nt.links.new(noi.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=0.9
try:
    bsdf.inputs['Subsurface Weight'].default_value=0.1
    bsdf.inputs['Subsurface Radius'].default_value=(0.4,0.9,0.5)
except Exception as e: print('sss',e)
bsdf.inputs['Emission Color'].default_value=(0.10,0.52,0.24,1)
lw=nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.5
fres=nt.nodes.new('ShaderNodeFresnel'); fres.inputs['IOR'].default_value=1.45
rim=nt.nodes.new('ShaderNodeMath'); rim.operation='MULTIPLY'; rim.inputs[1].default_value=0.46  # +rim (era 0.35)
cen=nt.nodes.new('ShaderNodeMath'); cen.operation='POWER'; cen.inputs[1].default_value=11.0
inv=nt.nodes.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1.0
beep=nt.nodes.new('ShaderNodeValue'); beep.outputs[0].default_value=0.0
cenmul=nt.nodes.new('ShaderNodeMath'); cenmul.operation='MULTIPLY'
emadd=nt.nodes.new('ShaderNodeMath'); emadd.operation='ADD'
nt.links.new(fres.outputs['Fac'], rim.inputs[0])
nt.links.new(lw.outputs['Facing'], inv.inputs[1]); nt.links.new(inv.outputs['Value'], cen.inputs[0])
nt.links.new(cen.outputs['Value'], cenmul.inputs[0]); nt.links.new(beep.outputs[0], cenmul.inputs[1])
nt.links.new(rim.outputs['Value'], emadd.inputs[0]); nt.links.new(cenmul.outputs['Value'], emadd.inputs[1])
nt.links.new(emadd.outputs['Value'], bsdf.inputs['Emission Strength'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
ov.data.materials.append(mat)

bpy.ops.object.light_add(type='SUN', location=(2,-3,2)); sun=bpy.context.active_object
sun.data.energy=0.7; sun.data.color=(0.6,1.0,0.7); sun.rotation_euler=(math.radians(50),0,math.radians(30))  # +luz (era 0.5)
bpy.ops.object.camera_add(location=(0,-8.6,0.35)); cam=bpy.context.active_object
cam.rotation_euler=(math.radians(87),0,0); S.camera=cam; cam.data.lens=46   # mas lejos = se ve el ovulo ENTERO

import sys
outdir='/tmp/anim/ovulo/raw'; N=120
for a in sys.argv:
    if a.isdigit(): N=int(a)
    if a.startswith('OUT='): outdir=a.split('=')[1]
START=int(_o.environ.get('BL_START',0))
os.makedirs(outdir, exist_ok=True)
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
# BASE LIMPIA: glow CONSTANTE bajo (continentes visibles), SIN latido ni destellos horneados.
# Todo el sync (destellos campanita + latido + dive a 1:15) se aplica en POST (ovulo_post_sync.py).
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
# LATIDO solo del ovulo (mesh), MUY sutil. Eventos: fuertes (original) + suaves desde 0:30
HEART_STRONG=[12.254,17.252,21.995,27.249]
HEART_SOFT=[30.0,33.0,35.0,37.0,39.0,41.0,43.0,45.0,47.0,49.0,51.0,53.0,55.0,57.0,59.0,61.0,63.0,65.0,67.0,69.0,71.0]
def heart(t):
    v=0.0
    for et in HEART_STRONG: v+=1.0*math.exp(-((t-et)/0.10)**2)
    for et in HEART_SOFT:   v+=0.5*math.exp(-((t-et)/0.10)**2)
    return min(1.0,v)
# CAMARA FIJA: ovulo siempre centrado (-> destello centrado en post). Mira al origen.
cam.location=(0,-8.6,0.35); cam.rotation_euler=(math.radians(87),0,0)
for f in range(START,N):
    t=f/24.0
    hb=heart(t)
    # AGRANDADO: el ovulo crece LARGO (t=72->80.5) y MAS GRANDE (hasta 2.4x). El tunel entra ~1:18.
    dive=ease((t-72.0)/8.5)
    base=1.0+0.006*hb            # LATIDO sutil: ±0.6% SOLO el ovulo
    grow=1.0+1.4*dive            # agrandado de la transicion (max ~2.4x en 80.5)
    ov.scale=(base*grow,)*3
    ov.rotation_euler=(0,0,0.05+t*0.008)      # continentes giran lentisimo
    sky.rotation_euler=(0,0,t*0.006)          # backdrop/reflejos con movimiento lento
    beep.outputs[0].default_value=0.13 + 1.9*dive   # glow base tenue; se ilumina (la luz) al crecer
    S.render.filepath=f'{outdir}/f{f:03d}.png'
    bpy.ops.render.render(write_still=True)
    if f%60==0: print('ovulo',f)
print('OVULO DONE')
