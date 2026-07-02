import bpy, math, os
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='CPU'
S.cycles.samples=40; S.cycles.use_denoising=True
try: S.cycles.volume_bounces=2
except: pass
import os as _o
S.render.resolution_x=int(_o.environ.get('BL_W',480)); S.render.resolution_y=int(_o.environ.get('BL_H',270))
if _o.environ.get('BL_SAMPLES'): S.cycles.samples=int(_o.environ['BL_SAMPLES'])
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=0.0
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.003,0.011,0.006,1)

bpy.ops.mesh.primitive_cube_add(size=30, location=(0,0,0)); hum=bpy.context.active_object
hm=bpy.data.materials.new('humo'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
ho=hn.nodes.new('ShaderNodeOutputMaterial'); pv=hn.nodes.new('ShaderNodeVolumePrincipled')
tc=hn.nodes.new('ShaderNodeTexCoord'); mapn=hn.nodes.new('ShaderNodeMapping')
hn.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
n1=hn.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=2.3; n1.inputs['Detail'].default_value=10.0; n1.inputs['Roughness'].default_value=0.68
hn.links.new(mapn.outputs['Vector'], n1.inputs['Vector'])
ramp=hn.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=0.50; ramp.color_ramp.elements[0].color=(0,0,0,1)
ramp.color_ramp.elements[1].position=0.64; ramp.color_ramp.elements[1].color=(1,1,1,1)
hn.links.new(n1.outputs['Fac'], ramp.inputs['Fac'])
dens=hn.nodes.new('ShaderNodeMath'); dens.operation='MULTIPLY'; dens.inputs[1].default_value=0.9
hn.links.new(ramp.outputs['Color'], dens.inputs[0]); hn.links.new(dens.outputs['Value'], pv.inputs['Density'])
pv.inputs['Color'].default_value=(0.05,0.26,0.12,1)
pv.inputs['Emission Strength'].default_value=0.04
pv.inputs['Emission Color'].default_value=(0.08,0.40,0.18,1)
pv.inputs['Anisotropy'].default_value=0.4
hn.links.new(pv.outputs['Volume'], ho.inputs['Volume']); hum.data.materials.append(hm)

bpy.ops.object.light_add(type='AREA', location=(-6,-5,4)); ar=bpy.context.active_object
ar.data.energy=5000.0; ar.data.color=(0.5,1.0,0.65); ar.data.size=8.0
ar.rotation_euler=(math.radians(55),0,math.radians(-40))

bpy.ops.object.camera_add(location=(0,-12,0.8)); cam=bpy.context.active_object
cam.rotation_euler=(math.radians(88),0,0); S.camera=cam; cam.data.lens=40

import sys
outdir='/tmp/anim/humo/raw'; N=120
for a in sys.argv:
    if a.isdigit(): N=int(a)
    if a.startswith('OUT='): outdir=a.split('=')[1]
os.makedirs(outdir, exist_ok=True)
for f in range(N):
    u=f/(N-1)
    mapn.inputs['Location'].default_value=(u*0.28, u*0.18, -u*0.42)  # adveccion LENTA
    cam.location=(0,-12+u*0.5, 0.8+u*0.1)                            # deriva muy suave
    S.render.filepath=f'{outdir}/f{f:03d}.png'
    bpy.ops.render.render(write_still=True)
    if f%20==0: print('humo',f)
print('HUMO DONE')
