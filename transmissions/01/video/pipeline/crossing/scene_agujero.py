import bpy, math, os
# ===== CROSSING escena 2: AGUJERO NEGRO real + Mandelbrot adentro =====
# Disco negro (se ve lo redondo por el rim verde tenue) con el fractal Mandelbrot
# glowing en el centro. Camara de frente (luego se acerca = entrar al agujero).
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='GPU'
try:
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='METAL'; p.get_devices()
    for d in p.devices: d.use=True
except Exception as e: print('gpu',e)
S.cycles.samples=int(os.environ.get('BL_SAMPLES',64)); S.cycles.use_denoising=True
S.render.resolution_x=int(os.environ.get('BL_W',960)); S.render.resolution_y=int(os.environ.get('BL_H',540))
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=-0.7
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0,0.0,0.0,1)  # negro

MAND=os.environ.get('MAND','/Users/emilianomettini/crossing_work/_mandelbrot.png')

# ---- DISCO con el Mandelbrot (emission) en el centro del agujero ----
bpy.ops.mesh.primitive_circle_add(radius=2.0, vertices=128, fill_type='NGON', location=(0,0,0))
disc=bpy.context.active_object
# UV para mapear la imagen
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.uv.smart_project(); bpy.ops.object.mode_set(mode='OBJECT')
dm=bpy.data.materials.new('mand'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.clear()
do=dn.nodes.new('ShaderNodeOutputMaterial'); em=dn.nodes.new('ShaderNodeEmission')
tex=dn.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(MAND)
tc=dn.nodes.new('ShaderNodeTexCoord'); dn.links.new(tc.outputs['Generated'], tex.inputs['Vector'])
em.inputs['Strength'].default_value=2.2
dn.links.new(tex.outputs['Color'], em.inputs['Color'])
# fade radial: el fractal se oscurece hacia el borde (entra en el negro del agujero)
geo=dn.nodes.new('ShaderNodeNewGeometry')
# usar distancia al centro via Generated (0..1) -> mezclar emission con negro en el borde
sep=dn.nodes.new('ShaderNodeVectorMath'); sep.operation='DISTANCE'; sep.inputs[1].default_value=(0.5,0.5,0.0)
dn.links.new(tc.outputs['Generated'], sep.inputs[0])
ramp=dn.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=0.30; ramp.color_ramp.elements[0].color=(1,1,1,1)
ramp.color_ramp.elements[1].position=0.50; ramp.color_ramp.elements[1].color=(0,0,0,1)
dn.links.new(sep.outputs['Value'], ramp.inputs['Fac'])
mul=dn.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=2.2
dn.links.new(ramp.outputs['Color'], mul.inputs[0])
dn.links.new(mul.outputs['Value'], em.inputs['Strength'])
dn.links.new(em.outputs['Emission'], do.inputs['Surface']); disc.data.materials.append(dm)

# ---- RIM del agujero: toro fino con emision verde tenue (se ve lo REDONDO) ----
bpy.ops.mesh.primitive_torus_add(major_radius=2.05, minor_radius=0.035, location=(0,0,-0.02))
rim=bpy.context.active_object; bpy.ops.object.shade_smooth()
rm=bpy.data.materials.new('rim'); rm.use_nodes=True; rn=rm.node_tree; rn.nodes.clear()
ro=rn.nodes.new('ShaderNodeOutputMaterial'); re=rn.nodes.new('ShaderNodeEmission')
re.inputs['Color'].default_value=(0.10,0.45,0.22,1); re.inputs['Strength'].default_value=3.0
rn.links.new(re.outputs['Emission'], ro.inputs['Surface']); rim.data.materials.append(rm)

# ---- anillo exterior negro (el cuerpo del agujero) para que el fractal quede "adentro" ----
bpy.ops.mesh.primitive_circle_add(radius=9.0, vertices=128, fill_type='NGON', location=(0,0,0.05))
outer=bpy.context.active_object
# agujero: borrar el centro -> mejor un disco negro grande detras con un hueco? simplest: plano negro con hueco via boolean
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,0,0.04)); blk=bpy.context.active_object
bm=bpy.data.materials.new('blk'); bm.use_nodes=True; bn=bm.node_tree; bn.nodes.clear()
bo=bn.nodes.new('ShaderNodeOutputMaterial'); bb=bn.nodes.new('ShaderNodeEmission')
bb.inputs['Color'].default_value=(0,0,0,1); bb.inputs['Strength'].default_value=0.0
bn.links.new(bb.outputs['Emission'], bo.inputs['Surface']); blk.data.materials.append(bm)
# hueco circular en el plano negro (boolean con cilindro)
bpy.ops.mesh.primitive_cylinder_add(radius=2.02, depth=2, location=(0,0,0.04))
cyl=bpy.context.active_object
bpy.context.view_layer.objects.active=blk
boo=blk.modifiers.new('hole','BOOLEAN'); boo.operation='DIFFERENCE'; boo.object=cyl
bpy.ops.object.modifier_apply(modifier='hole')
bpy.data.objects.remove(cyl, do_unlink=True)
bpy.data.objects.remove(outer, do_unlink=True)

bpy.ops.object.camera_add(location=(0,0,6.2)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=50

out=os.environ.get('OUT','/Users/emilianomettini/crossing_work/_still_agujero.png')
os.makedirs(os.path.dirname(out),exist_ok=True)
S.render.filepath=out; bpy.ops.render.render(write_still=True)
print('AGUJERO STILL DONE', out)
