import bpy, math, os
# Humo verde anegrado ANIMADO (deriva) — para la escena 1 de crossing. Solo humo (la sombra va en post).
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='CPU'
S.cycles.samples=int(os.environ.get('BL_SAMPLES',28)); S.cycles.use_denoising=True
try: S.cycles.volume_bounces=2
except: pass
S.render.resolution_x=int(os.environ.get('BL_W',640)); S.render.resolution_y=int(os.environ.get('BL_H',360))
S.render.image_settings.file_format='PNG'; S.render.image_settings.color_depth='8'
try: S.render.dither_intensity=2.0
except: pass
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=-2.0
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0006,0.003,0.0018,1)

bpy.ops.mesh.primitive_cube_add(size=30, location=(0,0,0)); hum=bpy.context.active_object
hm=bpy.data.materials.new('humo'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
ho=hn.nodes.new('ShaderNodeOutputMaterial'); pv=hn.nodes.new('ShaderNodeVolumePrincipled')
tc=hn.nodes.new('ShaderNodeTexCoord'); mapn=hn.nodes.new('ShaderNodeMapping')
hn.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
n1=hn.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=2.0; n1.inputs['Detail'].default_value=11.0; n1.inputs['Roughness'].default_value=0.70
hn.links.new(mapn.outputs['Vector'], n1.inputs['Vector'])
ramp=hn.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=0.52; ramp.color_ramp.elements[0].color=(0,0,0,1)
ramp.color_ramp.elements[1].position=0.68; ramp.color_ramp.elements[1].color=(1,1,1,1)
hn.links.new(n1.outputs['Fac'], ramp.inputs['Fac'])
dens=hn.nodes.new('ShaderNodeMath'); dens.operation='MULTIPLY'; dens.inputs[1].default_value=0.85
hn.links.new(ramp.outputs['Color'], dens.inputs[0]); hn.links.new(dens.outputs['Value'], pv.inputs['Density'])
pv.inputs['Color'].default_value=(0.05,0.105,0.072,1)
pv.inputs['Emission Strength'].default_value=0.016
pv.inputs['Emission Color'].default_value=(0.06,0.17,0.10,1)
pv.inputs['Anisotropy'].default_value=0.45
hn.links.new(pv.outputs['Volume'], ho.inputs['Volume']); hum.data.materials.append(hm)

bpy.ops.object.light_add(type='AREA', location=(-1.0,9.0,1.4)); bk=bpy.context.active_object
bk.data.energy=5200.0; bk.data.color=(0.5,0.92,0.62); bk.data.size=11.0; bk.rotation_euler=(math.radians(-90),0,0)
bpy.ops.object.light_add(type='AREA', location=(-8,-2,3)); fl=bpy.context.active_object
fl.data.energy=1400.0; fl.data.color=(0.42,0.85,0.56); fl.data.size=13.0; fl.rotation_euler=(math.radians(70),0,math.radians(-55))
bpy.ops.object.camera_add(location=(0,-12,0.9)); cam=bpy.context.active_object
cam.rotation_euler=(math.radians(88),0,0); S.camera=cam; cam.data.lens=40

import sys, numpy as np
outdir=os.environ.get('OUT','/Users/emilianomettini/crossing_work/humo_anim'); N=int(os.environ.get('NF','144'))
os.makedirs(outdir, exist_ok=True)
# ---- DERIVA atada a la MUSICA (rms), GLACIAL: el humo avanza al ritmo del track ----
ctrl=np.load('/Users/emilianomettini/git/spiralout/transmissions/01/video/control/crossing.npz')
rms=ctrl['rms']; cfps=int(ctrl['fps']); rms_n=(rms-rms.min())/(np.ptp(rms)+1e-9)
START_S=float(os.environ.get('START_S','0')); RATE=float(os.environ.get('DRIFT','0.00018'))
cum=0.0; drift=[]
for f in range(N):
    ci=int((START_S+f/24.0)*cfps); ci=min(ci,len(rms_n)-1)
    cum+=rms_n[ci]*RATE; drift.append(cum)
for f in range(N):
    dx=drift[f]
    mapn.inputs['Location'].default_value=(dx*1.0, dx*0.62, dx*0.30)   # deriva glacial atada al rms
    S.render.filepath=f'{outdir}/f{f:04d}.png'
    bpy.ops.render.render(write_still=True)
    if f%24==0: print('humo',f,'drift',round(dx,4))
print('HUMO ANIM DONE', N)
