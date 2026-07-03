import bpy, math, os, sys
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
S=setup(samples=64, exposure=-0.5)
S.cycles.device='CPU'
# atmosfera world volume
wv=S.world.node_tree; wout=wv.nodes['World Output']; wvs=wv.nodes.new('ShaderNodeVolumeScatter')
wvs.inputs['Density'].default_value=0.012; wvs.inputs['Color'].default_value=(0.05,0.16,0.09,1); wvs.inputs['Anisotropy'].default_value=0.4
wv.links.new(wvs.outputs['Volume'], wout.inputs['Volume'])

def roughen(ob, dscale=0.35):
    # MODIFICADOR displace multi-escala -> rompe la silueta poligonal (real)
    sub=ob.modifiers.new("sub",'SUBSURF'); sub.levels=2; sub.render_levels=3
    for i,(sz,st) in enumerate([(0.7,dscale),(0.25,dscale*0.45),(0.1,dscale*0.2)]):
        tex=bpy.data.textures.new(f"t_{ob.name}_{i}",'CLOUDS'); tex.noise_scale=sz; tex.noise_depth=5
        dis=ob.modifiers.new(f"disp{i}",'DISPLACE'); dis.texture=tex; dis.strength=st; dis.texture_coords='LOCAL'; dis.mid_level=0.5

petal_mat,_=emission_mat('petal',(0.10,0.34,0.17,1),1.5)
for ring,(rad,scl,off) in enumerate([(1.7,(0.18,0.95,0.07),0.0),(1.05,(0.14,0.66,0.05),0.26)]):
    for k in range(12):
        a=k/12*2*math.pi+off
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(math.cos(a)*rad,math.sin(a)*rad,0))
        p=bpy.context.active_object; bpy.ops.object.shade_smooth(); p.scale=scl; p.rotation_euler=(0,0,a+math.pi/2)
        p.data.materials.append(petal_mat); roughen(p,0.28)
# core volumetrico emisivo (sin bola)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.95, subdivisions=3, location=(0,0,0.05))
c=bpy.context.active_object
cm=bpy.data.materials.new('core'); cm.use_nodes=True; ct=cm.node_tree; ct.nodes.clear()
cout=ct.nodes.new('ShaderNodeOutputMaterial'); cpv=ct.nodes.new('ShaderNodeVolumePrincipled')
ctc=ct.nodes.new('ShaderNodeTexCoord'); cmp=ct.nodes.new('ShaderNodeMapping'); cmp.inputs['Location'].default_value=(-0.5,-0.5,-0.5)
ct.links.new(ctc.outputs['Generated'],cmp.inputs['Vector'])
cvl=ct.nodes.new('ShaderNodeVectorMath'); cvl.operation='LENGTH'; ct.links.new(cmp.outputs['Vector'],cvl.inputs[0])
cfa=ct.nodes.new('ShaderNodeMapRange'); cfa.inputs['From Max'].default_value=0.5; cfa.inputs['To Min'].default_value=3.0; cfa.inputs['To Max'].default_value=0.0
ct.links.new(cvl.outputs['Value'],cfa.inputs['Value']); ct.links.new(cfa.outputs['Result'],cpv.inputs['Density'])
cpv.inputs['Emission Strength'].default_value=5.0; cpv.inputs['Emission Color'].default_value=(0.10,0.5,0.22,1)
ct.links.new(cpv.outputs['Volume'],cout.inputs['Volume']); c.data.materials.append(cm)
bpy.ops.object.camera_add(location=(0,0,7)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=45
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=7.0; cam.data.dof.aperture_fstop=2.0
os.makedirs('/tmp/scenes',exist_ok=True)
S.render.filepath='/tmp/scenes/bloom_grim_raw.png'; bpy.ops.render.render(write_still=True); print('DONE')
