import bpy, math, os
# ===== CROSSING escena 2: AGUJERO NEGRO = ESFERA real con el fractal proyectado encima =====
# La esfera ES la bola del agujero negro (se ve redonda por shading+fresnel). El Mandelbrot
# (colores del original) se PROYECTA sobre la esfera (Window) -> se ve sobre la bola.
# Luz difusa detras (area+haze) = profundidad. Sin rim neon.
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='GPU'
try:
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='METAL'; p.get_devices()
    for d in p.devices: d.use=True
except Exception as e: print('gpu',e)
S.cycles.samples=int(os.environ.get('BL_SAMPLES',128)); S.cycles.use_denoising=True
S.render.resolution_x=int(os.environ.get('BL_W',960)); S.render.resolution_y=int(os.environ.get('BL_H',540))
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=-0.8
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0,0.0,0.0,1)
MAND=os.environ.get('MAND','/Users/emilianomettini/crossing_work/_mandelbrot.png')

# ---- ESFERA = la bola del agujero negro ----
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, segments=128, ring_count=64, location=(0,0,0))
sph=bpy.context.active_object; bpy.ops.object.shade_smooth()
sm=bpy.data.materials.new('hole'); sm.use_nodes=True; nt=sm.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial')
mix=nt.nodes.new('ShaderNodeMixShader')
# base oscura (cuerpo del agujero)
dark=nt.nodes.new('ShaderNodeBsdfPrincipled'); dark.inputs['Base Color'].default_value=(0.004,0.012,0.008,1); dark.inputs['Roughness'].default_value=1.0
# fractal proyectado (Window = plano desde camara) -> se ve sobre la bola
em=nt.nodes.new('ShaderNodeEmission')
tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(MAND); tex.extension='EXTEND'
tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping')
mp.inputs['Location'].default_value=(0.5,0.5,0.0)  # centrar
mp.inputs['Scale'].default_value=(0.42,0.42,1.0)   # encuadre del fractal en la bola
# Window coords centradas
sub=nt.nodes.new('ShaderNodeVectorMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=(0.5,0.5,0.0)
nt.links.new(tc.outputs['Window'], sub.inputs[0]); nt.links.new(sub.outputs['Vector'], mp.inputs['Vector'])
nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
em.inputs['Strength'].default_value=2.7
nt.links.new(tex.outputs['Color'], em.inputs['Color'])
# mezcla: el fractal emite, la base oscura debajo. Fresnel oscurece el borde (volumen de bola)
fres=nt.nodes.new('ShaderNodeFresnel'); fres.inputs['IOR'].default_value=1.3
nt.links.new(fres.outputs['Fac'], mix.inputs['Fac'])   # centro=fractal, borde=oscuro -> bola
nt.links.new(em.outputs['Emission'], mix.inputs[1])
nt.links.new(dark.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
sph.data.materials.append(sm)

# ---- BACKLIGHT difuso (area + haze) = profundidad, sin rim neon ----
bpy.ops.object.light_add(type='AREA', location=(0,0,-4.5)); bk=bpy.context.active_object
bk.data.energy=1500.0; bk.data.color=(0.5,0.6,0.53); bk.data.size=2.6; bk.rotation_euler=(0,0,0)
# relleno frontal MUY tenue para que se lea la curvatura de la bola
bpy.ops.object.light_add(type='AREA', location=(-3,-2,4)); fl=bpy.context.active_object
fl.data.energy=120.0; fl.data.color=(0.4,0.6,0.45); fl.data.size=6.0; fl.rotation_euler=(math.radians(50),0,math.radians(-30))
# haze
bpy.ops.mesh.primitive_cube_add(size=22, location=(0,0,-1.5)); hz=bpy.context.active_object
hm=bpy.data.materials.new('haze'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
hoo=hn.nodes.new('ShaderNodeOutputMaterial'); vs=hn.nodes.new('ShaderNodeVolumeScatter')
vs.inputs['Color'].default_value=(0.10,0.17,0.12,1); vs.inputs['Density'].default_value=0.008
hn.links.new(vs.outputs['Volume'], hoo.inputs['Volume']); hz.data.materials.append(hm)

bpy.ops.object.camera_add(location=(0,0,9.5)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=55

out_p=os.environ.get('OUT','/Users/emilianomettini/crossing_work/_still_agujero3.png')
os.makedirs(os.path.dirname(out_p),exist_ok=True)
S.render.filepath=out_p; bpy.ops.render.render(write_still=True)
print('AGUJERO3 DONE', out_p)
