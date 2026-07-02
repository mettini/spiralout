import bpy, math, os
# ===== CROSSING escena 1: humo/nebula verde anegrado + sombra-figura (alien/persona) =====
# Reusa el humo volumetrico de outbound (a_humo) re-tenido a verde anegrado (mas oscuro),
# con una FIGURA oscura (cuerpo + cabeza) ENTRE las capas de humo = sombra perturbante.
S=bpy.context.scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
S.render.engine='CYCLES'; S.cycles.device='CPU'
S.cycles.samples=int(os.environ.get('BL_SAMPLES',48)); S.cycles.use_denoising=True
try: S.cycles.volume_bounces=2
except: pass
S.render.resolution_x=int(os.environ.get('BL_W',960)); S.render.resolution_y=int(os.environ.get('BL_H',540))
S.render.image_settings.file_format='PNG'
S.view_settings.view_transform='Filmic'; S.view_settings.exposure=-2.0   # ANEGRADO (muy oscuro, drowned)
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0006,0.003,0.0018,1)  # casi negro verdoso

# ---- HUMO volumetrico (cubo) verde anegrado ----
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
dens=hn.nodes.new('ShaderNodeMath'); dens.operation='MULTIPLY'; dens.inputs[1].default_value=0.85  # vela los bordes de la figura
hn.links.new(ramp.outputs['Color'], dens.inputs[0]); hn.links.new(dens.outputs['Value'], pv.inputs['Density'])
pv.inputs['Color'].default_value=(0.05,0.105,0.072,1)      # verde PETROLEO desaturado (drowned)
pv.inputs['Emission Strength'].default_value=0.016
pv.inputs['Emission Color'].default_value=(0.06,0.17,0.10,1)
pv.inputs['Anisotropy'].default_value=0.45
hn.links.new(pv.outputs['Volume'], ho.inputs['Volume']); hum.data.materials.append(hm)

# ---- SOMBRA-FIGURA: cuerpo (elipsoide vertical) + cabeza (esfera) ----
# Material oscuro absorbente -> dentro del humo lee como silueta/sombra perturbante.
def dark_mat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new('ShaderNodeOutputMaterial'); b=nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value=(0.004,0.012,0.007,1)   # casi negro verdoso
    b.inputs['Roughness'].default_value=1.0
    try: b.inputs['Specular IOR Level'].default_value=0.0
    except: pass
    nt.links.new(b.outputs['BSDF'], o.inputs['Surface']); return m
import os as _os2
if not _os2.environ.get('NOFIG'):
  fig=dark_mat('figura')
  FX,FY=-1.7, 2.6     # mas adentro del humo (y mayor) -> bordes velados
  # TORSO: alargado, angosto arriba, leve ensanche abajo. Inclinado (inquietud).
  bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(FX, FY, 0.1)); body=bpy.context.active_object
  body.scale=(0.52, 0.42, 2.55); bpy.ops.object.shade_smooth(); body.data.materials.append(fig)
  body.rotation_euler=(math.radians(4),0,math.radians(-7))   # leve lean = perturbador
  # CUELLO largo (alien)
  bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(FX-0.12, FY, 2.35)); neck=bpy.context.active_object
  neck.scale=(0.6,0.6,1.2); bpy.ops.object.shade_smooth(); neck.data.materials.append(fig)
  # CABEZA: ovalada/alargada (alien), chica, ligeramente ladeada
  bpy.ops.mesh.primitive_uv_sphere_add(radius=0.46, location=(FX-0.18, FY, 3.05)); head=bpy.context.active_object
  head.scale=(0.72,0.78,1.18); bpy.ops.object.shade_smooth(); head.data.materials.append(fig); head.rotation_euler=(0,math.radians(8),0)
  # HOMBRO insinuado (uno solo, asimetrico = inquietud, NO peon simetrico)
  bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(FX+0.45, FY, 1.75)); sh=bpy.context.active_object
  sh.scale=(0.9,0.45,0.5); bpy.ops.object.shade_smooth(); sh.data.materials.append(fig); sh.rotation_euler=(0,0,math.radians(-22))

# ---- CONTRALUZ: el humo brilla DETRAS de la figura -> la figura queda como SILUETA oscura ----
# luz principal detras de la figura (y>fig), apuntando hacia la camara: glow del humo, figura negra
bpy.ops.object.light_add(type='AREA', location=(-1.0, 9.0, 1.4)); bk=bpy.context.active_object
bk.data.energy=5200.0; bk.data.color=(0.5,0.92,0.62); bk.data.size=11.0
bk.rotation_euler=(math.radians(-90),0,0)   # mira hacia -y (camara)
# fill lateral MUY tenue: apenas insinua el borde de la figura, sin iluminarla de frente
bpy.ops.object.light_add(type='AREA', location=(-8,-2,3)); fl=bpy.context.active_object
fl.data.energy=350.0; fl.data.color=(0.4,0.85,0.55); fl.data.size=7.0
fl.rotation_euler=(math.radians(70),0,math.radians(-55))

bpy.ops.object.camera_add(location=(0,-12,0.9)); cam=bpy.context.active_object
cam.rotation_euler=(math.radians(88),0,0); S.camera=cam; cam.data.lens=40

out=os.environ.get('OUT','/Users/emilianomettini/crossing_work/_still_humo_sombra.png')
os.makedirs(os.path.dirname(out),exist_ok=True)
S.render.filepath=out
bpy.ops.render.render(write_still=True)
print('STILL DONE', out)
