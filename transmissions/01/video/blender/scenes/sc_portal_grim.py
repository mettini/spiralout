import bpy, math, os, sys
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
S=setup(samples=64, exposure=-0.5); S.cycles.device='CPU'
# atmosfera densa = vortice murky (disuelve los shards limpios)
wv=S.world.node_tree; wout=wv.nodes['World Output']; wvs=wv.nodes.new('ShaderNodeVolumeScatter')
wvs.inputs['Density'].default_value=0.03; wvs.inputs['Color'].default_value=(0.05,0.18,0.10,1); wvs.inputs['Anisotropy'].default_value=0.6
wv.links.new(wvs.outputs['Volume'], wout.inputs['Volume'])
def roughen(ob,st=0.25):
    sub=ob.modifiers.new("s",'SUBSURF'); sub.levels=1; sub.render_levels=2
    tex=bpy.data.textures.new(f"t{ob.name}",'CLOUDS'); tex.noise_scale=0.35
    d=ob.modifiers.new("d",'DISPLACE'); d.texture=tex; d.strength=st; d.texture_coords='LOCAL'
gmat,_=emission_mat('pg',(0.10,0.42,0.20,1),1.8); amat,_=emission_mat('pa',(0.5,0.38,0.14,1),1.5)
for ring in range(7):
    z=-ring*2.2; rad=1.2+ring*0.5; rot=ring*0.4
    for k in range(10):
        a=k/10*2*math.pi+rot
        bpy.ops.mesh.primitive_cone_add(radius1=0.30, depth=1.2, location=(math.cos(a)*rad,math.sin(a)*rad,z))
        sh=bpy.context.active_object; sh.rotation_euler=(math.pi/2,0,a+math.pi/2)
        sh.data.materials.append(amat if k%5==0 else gmat); roughen(sh,0.18)
# core volumetrico al fondo
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.1, subdivisions=3, location=(0,0,-16))
c=bpy.context.active_object
cm=bpy.data.materials.new('core'); cm.use_nodes=True; ct=cm.node_tree; ct.nodes.clear()
cout=ct.nodes.new('ShaderNodeOutputMaterial'); cpv=ct.nodes.new('ShaderNodeVolumePrincipled')
ctc=ct.nodes.new('ShaderNodeTexCoord'); cmp=ct.nodes.new('ShaderNodeMapping'); cmp.inputs['Location'].default_value=(-0.5,-0.5,-0.5)
ct.links.new(ctc.outputs['Generated'],cmp.inputs['Vector'])
cvl=ct.nodes.new('ShaderNodeVectorMath'); cvl.operation='LENGTH'; ct.links.new(cmp.outputs['Vector'],cvl.inputs[0])
cfa=ct.nodes.new('ShaderNodeMapRange'); cfa.inputs['From Max'].default_value=0.5; cfa.inputs['To Min'].default_value=3.0; cfa.inputs['To Max'].default_value=0.0
ct.links.new(cvl.outputs['Value'],cfa.inputs['Value']); ct.links.new(cfa.outputs['Result'],cpv.inputs['Density'])
cpv.inputs['Emission Strength'].default_value=10.0; cpv.inputs['Emission Color'].default_value=(0.10,0.5,0.22,1)
ct.links.new(cpv.outputs['Volume'],cout.inputs['Volume']); c.data.materials.append(cm)
bpy.ops.object.camera_add(location=(0,0,2)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=24
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=10.0; cam.data.dof.aperture_fstop=1.8
os.makedirs('/tmp/scenes',exist_ok=True)
S.render.filepath='/tmp/scenes/portal_grim_raw.png'; bpy.ops.render.render(write_still=True); print('DONE')
