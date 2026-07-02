import bpy, math, os
# ===== CROSSING escena 2 (Blender, magia): AGUJERO NEGRO + Mandelbrot adentro =====
# Esfera oscura (cuerpo del agujero) + disco Mandelbrot al frente (fractal en el medio,
# VISIBLE) + backlight difuso detras (profundidad, sin rim neon) + bloom (glare) + haze.
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='GPU'
try:
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='METAL'; p.get_devices()
    for d in p.devices: d.use=True
except Exception as e: print('gpu',e)
S.cycles.samples=int(os.environ.get('BL_SAMPLES',96)); S.cycles.use_denoising=True
S.render.resolution_x=int(os.environ.get('BL_W',960)); S.render.resolution_y=int(os.environ.get('BL_H',540))
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=-0.4
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0,0.0,0.0,1)

MAND=os.environ.get('MAND','/Users/emilianomettini/crossing_work/_mandelbrot.png')

# ---- ESFERA = cuerpo del agujero negro (oscuro desaturado, casi negro verdoso) ----
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, segments=96, ring_count=48, location=(0,0,0))
sph=bpy.context.active_object; bpy.ops.object.shade_smooth()
sm=bpy.data.materials.new('hole'); sm.use_nodes=True; sn=sm.node_tree; sn.nodes.clear()
so=sn.nodes.new('ShaderNodeOutputMaterial'); sb=sn.nodes.new('ShaderNodeBsdfPrincipled')
sb.inputs['Base Color'].default_value=(0.006,0.018,0.012,1)   # casi negro desaturado
sb.inputs['Roughness'].default_value=1.0
sn.links.new(sb.outputs['BSDF'], so.inputs['Surface']); sph.data.materials.append(sm)

# ---- DISCO Mandelbrot al FRENTE de la esfera (el fractal en el medio, VISIBLE) ----
bpy.ops.mesh.primitive_circle_add(radius=1.55, vertices=128, fill_type='NGON', location=(0,0,2.02))
disc=bpy.context.active_object
dm=bpy.data.materials.new('mand'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.clear()
do=dn.nodes.new('ShaderNodeOutputMaterial'); em=dn.nodes.new('ShaderNodeEmission')
tex=dn.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(MAND)
tc=dn.nodes.new('ShaderNodeTexCoord'); dn.links.new(tc.outputs['Generated'], tex.inputs['Vector'])
em.inputs['Strength'].default_value=3.6
dn.links.new(tex.outputs['Color'], em.inputs['Color'])
dn.links.new(em.outputs['Emission'], do.inputs['Surface']); disc.data.materials.append(dm)

# ---- BACKLIGHT difuso: LUZ DE AREA detras de la esfera + haze la dispersa = halo natural ----
bpy.ops.object.light_add(type='AREA', location=(0,0,-4.5)); bk=bpy.context.active_object
bk.data.energy=2600.0; bk.data.color=(0.62,0.70,0.64); bk.data.size=3.5   # palido desaturado, sutil
bk.rotation_euler=(0,0,0)   # apunta +z (hacia camara)

# ---- HAZE volumetrico (magia/profundidad): dispersa el backlight en halo suave ----
bpy.ops.mesh.primitive_cube_add(size=22, location=(0,0,-1.5)); hz=bpy.context.active_object
hm=bpy.data.materials.new('haze'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
hoo=hn.nodes.new('ShaderNodeOutputMaterial'); vs=hn.nodes.new('ShaderNodeVolumeScatter')
vs.inputs['Color'].default_value=(0.10,0.17,0.12,1); vs.inputs['Density'].default_value=0.03
hn.links.new(vs.outputs['Volume'], hoo.inputs['Volume']); hz.data.materials.append(hm)

bpy.ops.object.camera_add(location=(0,0,11.0)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=50

# bloom se aplica en post (numpy) tras el render
out=os.environ.get('OUT','/Users/emilianomettini/crossing_work/_still_agujero_bl.png')
os.makedirs(os.path.dirname(out),exist_ok=True)
S.render.filepath=out; bpy.ops.render.render(write_still=True)
print('AGUJERO BL DONE', out)
