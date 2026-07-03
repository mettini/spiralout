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
S.cycles.samples=140; S.cycles.use_denoising=True
try: S.cycles.volume_bounces=2
except: pass
S.render.resolution_x=960; S.render.resolution_y=540
S.render.image_settings.file_format='PNG'
# NO AgX (desatura el verde a blanco) -> Filmic
S.view_settings.view_transform='Filmic'; S.view_settings.look='None'; S.view_settings.exposure=-0.25
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.004,0.014,0.008,1)

# luz que maneja los rayos
bpy.ops.object.light_add(type='POINT', location=(0,0,-26)); pl=bpy.context.active_object
pl.data.energy=38000.0; pl.data.color=(0.4,1.0,0.55); pl.data.shadow_soft_size=2.0

# ---- OCCLUDER: disco con tiras RADIALES irregulares (los rayos son su sombra) ----
bpy.ops.mesh.primitive_circle_add(radius=14, fill_type='NGON', location=(0,0,-15))
occ=bpy.context.active_object
om=bpy.data.materials.new('occ'); om.use_nodes=True; on=om.node_tree; on.nodes.clear()
oo=on.nodes.new('ShaderNodeOutputMaterial'); mix=on.nodes.new('ShaderNodeMixShader')
tr=on.nodes.new('ShaderNodeBsdfTransparent'); sh=on.nodes.new('ShaderNodeBsdfDiffuse'); sh.inputs['Color'].default_value=(0,0,0,1)
otc=on.nodes.new('ShaderNodeTexCoord'); osep=on.nodes.new('ShaderNodeSeparateXYZ')
on.links.new(otc.outputs['Object'], osep.inputs['Vector'])
oang=on.nodes.new('ShaderNodeMath'); oang.operation='ARCTAN2'
on.links.new(osep.outputs['Y'], oang.inputs[0]); on.links.new(osep.outputs['X'], oang.inputs[1])
oN=on.nodes.new('ShaderNodeMath'); oN.operation='MULTIPLY'; oN.inputs[1].default_value=105.0  # cantidad de rayos
on.links.new(oang.outputs['Value'], oN.inputs[0])
osin=on.nodes.new('ShaderNodeMath'); osin.operation='SINE'; on.links.new(oN.outputs['Value'], osin.inputs[0])
# irregularidad: noise modula el umbral -> rayos de ancho variable
onoi=on.nodes.new('ShaderNodeTexNoise'); onoi.inputs['Scale'].default_value=4.0
on.links.new(otc.outputs['Object'], onoi.inputs['Vector'])
othr=on.nodes.new('ShaderNodeMath'); othr.operation='GREATER_THAN'
oadd=on.nodes.new('ShaderNodeMath'); oadd.operation='SUBTRACT'; oadd.inputs[0].default_value=0.2
on.links.new(onoi.outputs['Fac'], oadd.inputs[1])
on.links.new(osin.outputs['Value'], othr.inputs[0]); on.links.new(oadd.outputs['Value'], othr.inputs[1])
# fac=1 -> transparente (deja pasar luz = rayo), fac=0 -> opaco (sombra)
on.links.new(othr.outputs['Value'], mix.inputs[0])
on.links.new(sh.outputs['BSDF'], mix.inputs[1]); on.links.new(tr.outputs['BSDF'], mix.inputs[2])
on.links.new(mix.outputs['Shader'], oo.inputs['Surface'])
occ.data.materials.append(om)

# ---- MEDIO: domain con scatter anisotrópico (los rayos se ven acá) ----
bpy.ops.mesh.primitive_cube_add(size=44, location=(0,0,-18))
dom=bpy.context.active_object
dm=bpy.data.materials.new('dom'); dm.use_nodes=True; dn=dm.node_tree; dn.nodes.clear()
do=dn.nodes.new('ShaderNodeOutputMaterial'); dsc=dn.nodes.new('ShaderNodeVolumeScatter')
dsc.inputs['Color'].default_value=(0.06,0.30,0.14,1); dsc.inputs['Density'].default_value=0.11
dsc.inputs['Anisotropy'].default_value=0.66
dn.links.new(dsc.outputs['Volume'], do.inputs['Volume'])
dom.data.materials.append(dm)

bpy.ops.object.camera_add(location=(0,0,-4)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=30
outdir='/tmp/tunel_stills15'; os.makedirs(outdir, exist_ok=True)
for i,z in enumerate((-4.0,-8.0,-12.0)):
    cam.location=(0,0,z)
    S.render.filepath=f'{outdir}/t{i}.png'
    bpy.ops.render.render(write_still=True); print('tunel',i)
print('DONE')
