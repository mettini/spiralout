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
S.view_settings.view_transform='Filmic'; S.view_settings.look='None'; S.view_settings.exposure=-0.2
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.002,0.008,0.004,1)

# ---- TUBO: camara adentro, paredes emisivas con ANILLOS + ruido (orgánico) ----
bpy.ops.mesh.primitive_cylinder_add(radius=3.4, depth=90, vertices=128, location=(0,0,-43))
tube=bpy.context.active_object; bpy.ops.object.shade_smooth()
# romper la pared limpia (displacement MAS fuerte = nervaduras irregulares, no liso)
sub=tube.modifiers.new('sub','SUBSURF'); sub.levels=2; sub.render_levels=3
tex=bpy.data.textures.new('tubedisp','CLOUDS'); tex.noise_scale=0.35; tex.noise_depth=6
dis=tube.modifiers.new('disp','DISPLACE'); dis.texture=tex; dis.strength=1.0; dis.texture_coords='LOCAL'; dis.mid_level=0.5
tex2=bpy.data.textures.new('tubedisp2','CLOUDS'); tex2.noise_scale=0.12; tex2.noise_depth=5
dis2=tube.modifiers.new('disp2','DISPLACE'); dis2.texture=tex2; dis2.strength=0.4; dis2.texture_coords='LOCAL'; dis2.mid_level=0.5

tm=bpy.data.materials.new('tube'); tm.use_nodes=True; tn=tm.node_tree; tn.nodes.clear()
to=tn.nodes.new('ShaderNodeOutputMaterial'); em=tn.nodes.new('ShaderNodeEmission')
tc=tn.nodes.new('ShaderNodeTexCoord'); sep=tn.nodes.new('ShaderNodeSeparateXYZ')
tn.links.new(tc.outputs['Object'], sep.inputs['Vector'])
# DISTORSION del eje Z por noise -> anillos IRREGULARES (no periodicos perfectos = no fake)
dnoi=tn.nodes.new('ShaderNodeTexNoise'); dnoi.inputs['Scale'].default_value=1.3; dnoi.inputs['Detail'].default_value=8.0; dnoi.inputs['Roughness'].default_value=0.7
tn.links.new(tc.outputs['Object'], dnoi.inputs['Vector'])
dwarp=tn.nodes.new('ShaderNodeMath'); dwarp.operation='MULTIPLY'; dwarp.inputs[1].default_value=6.0
tn.links.new(dnoi.outputs['Fac'], dwarp.inputs[0])
zf=tn.nodes.new('ShaderNodeMath'); zf.operation='MULTIPLY'; zf.inputs[1].default_value=3.0
tn.links.new(sep.outputs['Z'], zf.inputs[0])
zadd=tn.nodes.new('ShaderNodeMath'); zadd.operation='ADD'           # Z*freq + warp = anillos ondulados
tn.links.new(zf.outputs['Value'], zadd.inputs[0]); tn.links.new(dwarp.outputs['Value'], zadd.inputs[1])
zsin=tn.nodes.new('ShaderNodeMath'); zsin.operation='SINE'; tn.links.new(zadd.outputs['Value'], zsin.inputs[0])
zb=tn.nodes.new('ShaderNodeMath'); zb.operation='MULTIPLY_ADD'; zb.inputs[1].default_value=0.5; zb.inputs[2].default_value=0.5
tn.links.new(zsin.outputs['Value'], zb.inputs[0])
zsharp=tn.nodes.new('ShaderNodeMath'); zsharp.operation='POWER'; zsharp.inputs[1].default_value=2.5
tn.links.new(zb.outputs['Value'], zsharp.inputs[0])
# TEXTURA DE PARED fuerte (rocas/detalle entre anillos, no liso)
wall=tn.nodes.new('ShaderNodeTexNoise'); wall.inputs['Scale'].default_value=9.0; wall.inputs['Detail'].default_value=14.0; wall.inputs['Roughness'].default_value=0.78
tn.links.new(tc.outputs['Object'], wall.inputs['Vector'])
comb=tn.nodes.new('ShaderNodeMath'); comb.operation='MULTIPLY'      # anillos modulados por la pared (rompe regularidad)
tn.links.new(zsharp.outputs['Value'], comb.inputs[0]); tn.links.new(wall.outputs['Fac'], comb.inputs[1])
wmul=tn.nodes.new('ShaderNodeMath'); wmul.operation='MULTIPLY'; wmul.inputs[1].default_value=0.40  # detalle de pared entre anillos
tn.links.new(wall.outputs['Fac'], wmul.inputs[0])
finadd=tn.nodes.new('ShaderNodeMath'); finadd.operation='ADD'
tn.links.new(comb.outputs['Value'], finadd.inputs[0]); tn.links.new(wmul.outputs['Value'], finadd.inputs[1])
base=tn.nodes.new('ShaderNodeMath'); base.operation='MULTIPLY_ADD'; base.inputs[1].default_value=1.5; base.inputs[2].default_value=0.07
tn.links.new(finadd.outputs['Value'], base.inputs[0])
em.inputs['Color'].default_value=(0.06,0.34,0.16,1)
tn.links.new(base.outputs['Value'], em.inputs['Strength'])
tn.links.new(em.outputs['Emission'], to.inputs['Surface'])
tube.data.materials.append(tm)

# ---- LUZ AL FONDO DEL TUNEL (vanishing point) ----
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.6, subdivisions=3, location=(0,0,-84))
glow=bpy.context.active_object
gm=bpy.data.materials.new('glow'); gm.use_nodes=True; gn=gm.node_tree; gn.nodes.clear()
go=gn.nodes.new('ShaderNodeOutputMaterial'); ge=gn.nodes.new('ShaderNodeEmission')
ge.inputs['Color'].default_value=(0.4,1.0,0.55,1); ge.inputs['Strength'].default_value=22.0
gn.links.new(ge.outputs['Emission'], go.inputs['Surface']); glow.data.materials.append(gm)
bpy.ops.object.light_add(type='POINT', location=(0,0,-82)); pl=bpy.context.active_object
pl.data.energy=40000.0; pl.data.color=(0.4,1.0,0.55); pl.data.shadow_soft_size=3.0

# ---- ATMOSFERA dentro del tubo (haze -> profundidad + haz al fondo) ----
bpy.ops.mesh.primitive_cylinder_add(radius=3.2, depth=88, vertices=64, location=(0,0,-43))
haze=bpy.context.active_object
hm=bpy.data.materials.new('haze'); hm.use_nodes=True; hn=hm.node_tree; hn.nodes.clear()
ho=hn.nodes.new('ShaderNodeOutputMaterial'); vs=hn.nodes.new('ShaderNodeVolumeScatter')
vs.inputs['Color'].default_value=(0.06,0.30,0.14,1); vs.inputs['Density'].default_value=0.05; vs.inputs['Anisotropy'].default_value=0.5
hn.links.new(vs.outputs['Volume'], ho.inputs['Volume']); haze.data.materials.append(hm)

bpy.ops.object.camera_add(location=(0,0,2)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=24   # gran angular = mas inmersion
import sys
outdir='/tmp/anim/tunel/raw'; N=120
for a in sys.argv:
    if a.isdigit(): N=int(a)
    if a.startswith('OUT='): outdir=a.split('=')[1]
os.makedirs(outdir, exist_ok=True)
for f in range(N):
    u=f/(N-1)
    cam.location=(0,0, 4.5 - 82.0*u)          # viaje LARGO hacia la luz del fondo (136s)
    # vortice = ROLL lento de camara mientras volamos (el tubo no tiene occluder)
    cam.rotation_euler=(0,0, 0.6*u + 0.10*math.sin(u*math.pi*3.0))
    S.render.filepath=f'{outdir}/f{f:03d}.png'
    bpy.ops.render.render(write_still=True)
    if f%40==0: print('tunel',f)
print('TUNEL DONE')
