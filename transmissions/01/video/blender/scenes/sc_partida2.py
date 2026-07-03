import bpy, math, os, sys
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
S=setup(samples=72, exposure=-0.35); S.cycles.device='CPU'
# REMOLINO volumetrico: brazos espirales en la densidad de un volumen emisivo
bpy.ops.mesh.primitive_cylinder_add(radius=9, depth=4, location=(0,0,0)); sw=bpy.context.active_object
m=bpy.data.materials.new('swirl'); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
o=nt.nodes.new('ShaderNodeOutputMaterial'); pv=nt.nodes.new('ShaderNodeVolumePrincipled')
tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(tc.outputs['Object'],sep.inputs['Vector'])
ang=nt.nodes.new('ShaderNodeMath'); ang.operation='ARCTAN2'; nt.links.new(sep.outputs['Y'],ang.inputs[0]); nt.links.new(sep.outputs['X'],ang.inputs[1])
vlen=nt.nodes.new('ShaderNodeVectorMath'); vlen.operation='LENGTH'; nt.links.new(tc.outputs['Object'],vlen.inputs[0])
logr=nt.nodes.new('ShaderNodeMath'); logr.operation='LOGARITHM'; logr.inputs[1].default_value=2.718281828; nt.links.new(vlen.outputs['Value'],logr.inputs[0])
# fase espiral = angle*2 + log(r)*3.5  -> brazos log
ph=nt.nodes.new('ShaderNodeMath'); ph.operation='MULTIPLY_ADD'; ph.inputs[1].default_value=3.5
nt.links.new(logr.outputs['Value'],ph.inputs[0])
a2=nt.nodes.new('ShaderNodeMath'); a2.operation='MULTIPLY'; a2.inputs[1].default_value=2.0; nt.links.new(ang.outputs['Value'],a2.inputs[0])
phs=nt.nodes.new('ShaderNodeMath'); phs.operation='ADD'; nt.links.new(ph.outputs['Value'],phs.inputs[0]); nt.links.new(a2.outputs['Value'],phs.inputs[1])
sn=nt.nodes.new('ShaderNodeMath'); sn.operation='SINE'; nt.links.new(phs.outputs['Value'],sn.inputs[0])
arms=nt.nodes.new('ShaderNodeMath'); arms.operation='POWER'; arms.inputs[1].default_value=3.0
ab=nt.nodes.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; nt.links.new(sn.outputs['Value'],ab.inputs[0]); nt.links.new(ab.outputs['Value'],arms.inputs[0])
# turbulencia (ruido) para que no sea prolijo
noi=nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=2.5; noi.inputs['Detail'].default_value=9.0; nt.links.new(tc.outputs['Object'],noi.inputs['Vector'])
tmix=nt.nodes.new('ShaderNodeMath'); tmix.operation='MULTIPLY'; nt.links.new(arms.outputs['Value'],tmix.inputs[0]); nt.links.new(noi.outputs['Fac'],tmix.inputs[1])
# falloff radial (denso al centro)
fall=nt.nodes.new('ShaderNodeMapRange'); fall.inputs['From Min'].default_value=0.5; fall.inputs['From Max'].default_value=8.0; fall.inputs['To Min'].default_value=1.0; fall.inputs['To Max'].default_value=0.0
nt.links.new(vlen.outputs['Value'],fall.inputs['Value'])
dens=nt.nodes.new('ShaderNodeMath'); dens.operation='MULTIPLY'; dens.inputs[1].default_value=6.0
df=nt.nodes.new('ShaderNodeMath'); df.operation='MULTIPLY'; nt.links.new(tmix.outputs['Value'],df.inputs[0]); nt.links.new(fall.outputs['Result'],df.inputs[1])
nt.links.new(df.outputs['Value'],dens.inputs[0]); nt.links.new(dens.outputs['Value'],pv.inputs['Density'])
pv.inputs['Emission Strength'].default_value=2.5; pv.inputs['Emission Color'].default_value=(0.10,0.5,0.22,1); pv.inputs['Anisotropy'].default_value=0.4
nt.links.new(pv.outputs['Volume'],o.inputs['Volume']); sw.data.materials.append(m)
# core
bpy.ops.object.light_add(type='POINT', location=(0,0,0)); pl=bpy.context.active_object
pl.data.energy=8000; pl.data.color=(0.4,1.0,0.55); pl.data.shadow_soft_size=1.0
bpy.ops.object.camera_add(location=(0,0,11)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=42
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=11.0; cam.data.dof.aperture_fstop=2.5
os.makedirs('/tmp/scenes',exist_ok=True)
S.render.filepath='/tmp/scenes/partida_swirl_raw.png'; bpy.ops.render.render(write_still=True); print('DONE')
