import bpy, math, os, sys
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
S=setup(samples=40, exposure=0.7, bg=(0.02,0.035,0.008,1))   # +luz fuerte (afuera = emerger)
S.cycles.device='CPU'
import os as _o
S.render.resolution_x=int(_o.environ.get('BL_W',480)); S.render.resolution_y=int(_o.environ.get('BL_H',270))
if _o.environ.get('BL_SAMPLES'): S.cycles.samples=int(_o.environ['BL_SAMPLES'])
# AFUERA: humo ambar + haces de luz (god rays)
bpy.ops.mesh.primitive_cube_add(size=30, location=(0,0,0)); hum=bpy.context.active_object
hm=bpy.data.materials.new('humo'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
ho=hn.nodes.new('ShaderNodeOutputMaterial'); pv=hn.nodes.new('ShaderNodeVolumePrincipled')
tc=hn.nodes.new('ShaderNodeTexCoord'); mapn=hn.nodes.new('ShaderNodeMapping')
hn.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
nz=hn.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=9.0
hn.links.new(mapn.outputs['Vector'], nz.inputs['Vector'])
rr=hn.nodes.new('ShaderNodeValToRGB'); rr.color_ramp.elements[0].position=0.5; rr.color_ramp.elements[1].position=0.66
hn.links.new(nz.outputs['Fac'],rr.inputs['Fac'])
dm=hn.nodes.new('ShaderNodeMath'); dm.operation='MULTIPLY'; dm.inputs[1].default_value=0.7  # densidad media = los haces SE VEN
hn.links.new(rr.outputs['Color'],dm.inputs[0]); hn.links.new(dm.outputs['Value'],pv.inputs['Density'])
pv.inputs['Color'].default_value=(0.45,0.32,0.08,1); pv.inputs['Anisotropy'].default_value=0.5
hn.links.new(pv.outputs['Volume'],ho.inputs['Volume']); hum.data.materials.append(hm)
spots=[]
for i,(x,rz) in enumerate([(-7,-35),(6,30),(-1,8)]):
    bpy.ops.object.light_add(type='SPOT', location=(x,-9,7)); sp=bpy.context.active_object
    sp.data.energy=75000; sp.data.color=(1.0,0.75,0.30); sp.data.spot_size=math.radians(35); sp.data.spot_blend=0.5  # haces fuertes
    sp.rotation_euler=(math.radians(55),0,math.radians(rz)); spots.append((sp,rz))
bpy.ops.object.camera_add(location=(0,-10,1)); cam=bpy.context.active_object
cam.rotation_euler=(math.radians(86),0,0); S.camera=cam; cam.data.lens=38
import sys
outdir='/tmp/anim/afuera/raw'; N=120
for a in sys.argv:
    if a.isdigit(): N=int(a)
    if a.startswith('OUT='): outdir=a.split('=')[1]
os.makedirs(outdir, exist_ok=True)
for f in range(N):
    u=f/(N-1)
    mapn.inputs['Location'].default_value=(u*0.18, -u*0.10, u*0.22)  # humo deriva LENTA
    cam.location=(0+0.2*math.sin(u*math.pi*0.7), -10+u*0.35, 1.0+0.1*u)
    for j,(sp,rz) in enumerate(spots):
        sp.rotation_euler=(math.radians(55),0,math.radians(rz+3*math.sin(u*math.pi+j)))  # haces oscilan lento
    S.render.filepath=f'{outdir}/f{f:03d}.png'
    bpy.ops.render.render(write_still=True)
    if f%20==0: print('afuera',f)
print('AFUERA DONE')
