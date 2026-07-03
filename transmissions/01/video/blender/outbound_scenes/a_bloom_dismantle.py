import bpy, math, os, sys, random
random.seed(7)
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
S=setup(samples=40, exposure=-0.35)
S.cycles.device='CPU'
import os as _o
S.render.resolution_x=int(_o.environ.get('BL_W',960)); S.render.resolution_y=int(_o.environ.get('BL_H',540))
if _o.environ.get('BL_SAMPLES'): S.cycles.samples=int(_o.environ['BL_SAMPLES'])

# ---- BACKDROP: campo de estrellas + nebulosa (fondo negro con estrellas) ----
bpy.ops.mesh.primitive_uv_sphere_add(radius=40, segments=64, ring_count=32)
sky=bpy.context.active_object; bpy.ops.object.shade_smooth()
sm=bpy.data.materials.new('sky'); sm.use_nodes=True; sn=sm.node_tree; sn.nodes.clear()
so=sn.nodes.new('ShaderNodeOutputMaterial'); sem=sn.nodes.new('ShaderNodeEmission')
stc=sn.nodes.new('ShaderNodeTexCoord')
neb=sn.nodes.new('ShaderNodeTexNoise'); neb.inputs['Scale'].default_value=2.0; neb.inputs['Detail'].default_value=8.0; neb.inputs['Roughness'].default_value=0.7
nr=sn.nodes.new('ShaderNodeValToRGB')
nr.color_ramp.elements[0].position=0.45; nr.color_ramp.elements[0].color=(0,0,0,1)
nr.color_ramp.elements[1].position=0.74; nr.color_ramp.elements[1].color=(0.02,0.13,0.07,1)
star=sn.nodes.new('ShaderNodeTexNoise'); star.inputs['Scale'].default_value=80.0; star.inputs['Detail'].default_value=2.0
sr=sn.nodes.new('ShaderNodeValToRGB')
sr.color_ramp.elements[0].position=0.73; sr.color_ramp.elements[0].color=(0,0,0,1)
sr.color_ramp.elements[1].position=0.79; sr.color_ramp.elements[1].color=(0.55,0.75,0.6,1)
addsky=sn.nodes.new('ShaderNodeMixRGB'); addsky.blend_type='ADD'
sn.links.new(stc.outputs['Generated'], neb.inputs['Vector']); sn.links.new(stc.outputs['Generated'], star.inputs['Vector'])
sn.links.new(neb.outputs['Fac'], nr.inputs['Fac']); sn.links.new(star.outputs['Fac'], sr.inputs['Fac'])
sn.links.new(nr.outputs['Color'], addsky.inputs[1]); sn.links.new(sr.outputs['Color'], addsky.inputs[2])
sn.links.new(addsky.outputs['Color'], sem.inputs['Color']); sem.inputs['Strength'].default_value=1.5
sn.links.new(sem.outputs['Emission'], so.inputs['Surface']); sky.data.materials.append(sm)

def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)

# ---- malla de PETALO curvado+ahuecado (no esfera aplastada) ----
def petal_mesh(name):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=7, y_subdivisions=16, size=1.0)
    o=bpy.context.active_object; o.name=name; me=o.data
    for v in me.vertices:
        x,y,z=v.co
        yn=y+0.5                              # 0(base)..1(punta)
        w=math.sin(max(0.001,yn)*math.pi)**0.55   # ancho: angosto base, ancho medio, punta fina
        nx=x*w*1.1
        bow=0.55*(yn**2)                      # se curva hacia adelante (la punta cae)
        cup=1.1*(x*w)**2                      # ahuecado (bordes suben) = volumen real
        v.co=(nx, yn, bow+cup)               # base en y=0, punta en y~1
    bpy.ops.object.shade_smooth()
    return o

# material petalo: translucido, gradiente base->punta, leve emision
pm=bpy.data.materials.new('petal'); pm.use_nodes=True; pn=pm.node_tree; pn.nodes.clear()
po=pn.nodes.new('ShaderNodeOutputMaterial'); pb=pn.nodes.new('ShaderNodeBsdfPrincipled')
ptc=pn.nodes.new('ShaderNodeTexCoord'); psep=pn.nodes.new('ShaderNodeSeparateXYZ')
pn.links.new(ptc.outputs['Generated'], psep.inputs['Vector'])
pgrad=pn.nodes.new('ShaderNodeValToRGB')
pgrad.color_ramp.elements[0].position=0.0; pgrad.color_ramp.elements[0].color=(0.02,0.10,0.05,1)   # base oscura
pgrad.color_ramp.elements[1].position=1.0; pgrad.color_ramp.elements[1].color=(0.10,0.40,0.20,1)   # punta mas clara
pn.links.new(psep.outputs['Y'], pgrad.inputs['Fac'])
pn.links.new(pgrad.outputs['Color'], pb.inputs['Base Color'])
pb.inputs['Roughness'].default_value=0.55
try:
    pb.inputs['Subsurface Weight'].default_value=0.35
    pb.inputs['Subsurface Radius'].default_value=(0.3,0.8,0.45)
    pb.inputs['Emission Color'].default_value=(0.06,0.26,0.12,1)
    pb.inputs['Emission Strength'].default_value=0.25
except Exception as e: print('sss',e)
pn.links.new(pb.outputs['BSDF'], po.inputs['Surface'])

proto=petal_mesh('proto'); proto.data.materials.append(pm); proto.hide_render=True

# fondo dark-green (NO negro puro) -> los huecos entre petalos no se ven como agujeros
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.012,0.03,0.018,1)

# ---- rosa: anillos concentricos. MAS petalos (overlap, sin huecos). centro ELEVADO ----
petals=[]
# (count, base_radius, scale, closed_pitch, od, ring_z)  ring_z mayor adentro = centro arriba
rings=[(12,0.28,0.58,1.05,0.0,0.46),(13,0.48,0.88,1.0,0.33,0.31),
       (15,0.72,1.18,0.82,0.66,0.16),(17,1.0,1.55,0.6,1.0,0.0)]
for ri,(cnt,br,sc,cp,od,rz) in enumerate(rings):
    for k in range(cnt):
        a=k/cnt*2*math.pi + ri*0.55 + random.uniform(-0.06,0.06)
        o=proto.copy(); o.data=proto.data
        o.hide_render=False
        bpy.context.collection.objects.link(o)
        s=sc*random.uniform(0.92,1.1)
        # DE ADENTRO HACIA AFUERA: centro (od=0) abre primero, outer (od=1) ultimo
        dl=od*0.42 + (k/cnt)*0.04 + random.uniform(0,0.03)
        wph=random.uniform(0,6.28)                       # fase de viento por petalo
        wamp=random.uniform(0.010,0.045)                 # viento SUTIL (algunos un toque mas)
        petals.append(dict(o=o,a=a,br=br,s=s,cp=cp,od=od,dl=dl,rz=rz,wph=wph,wamp=wamp))

# ---- core volumetrico (LUZ que aparece en el humo, late, luego estalla al abrir) ----
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.7, subdivisions=3, location=(0,0,0.08))
core=bpy.context.active_object
cm=bpy.data.materials.new('core'); cm.use_nodes=True; ct=cm.node_tree; ct.nodes.clear()
cout=ct.nodes.new('ShaderNodeOutputMaterial'); cpv=ct.nodes.new('ShaderNodeVolumePrincipled')
cpv.inputs['Density'].default_value=9.0
cestr=ct.nodes.new('ShaderNodeValue'); cestr.outputs[0].default_value=0.0
ct.links.new(cestr.outputs[0], cpv.inputs['Emission Strength'])
cpv.inputs['Emission Color'].default_value=(0.20,0.75,0.36,1)
ct.links.new(cpv.outputs['Volume'],cout.inputs['Volume']); core.data.materials.append(cm)
# halo emisivo extra: una esferita brillante que se ve COMO LUZ a traves del humo en el acercamiento
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.22, subdivisions=2, location=(0,0,0.1))
halo=bpy.context.active_object
hm2=bpy.data.materials.new('halo'); hm2.use_nodes=True; ht=hm2.node_tree; ht.nodes.clear()
hoO=ht.nodes.new('ShaderNodeOutputMaterial'); hem=ht.nodes.new('ShaderNodeEmission')
hem.inputs['Color'].default_value=(0.4,1.0,0.55,1)
hstr=ht.nodes.new('ShaderNodeValue'); hstr.outputs[0].default_value=0.0
ht.links.new(hstr.outputs[0], hem.inputs['Strength'])
ht.links.new(hem.outputs['Emission'], hoO.inputs['Surface']); halo.data.materials.append(hm2)

# luz key suave + rim
bpy.ops.object.light_add(type='AREA', location=(2.5,-2.5,4)); kl=bpy.context.active_object
kl.data.energy=900; kl.data.color=(0.7,1.0,0.8); kl.data.size=5.0
kl.rotation_euler=(math.radians(40),0,math.radians(35))
bpy.ops.object.light_add(type='AREA', location=(-3,2,1.5)); rl=bpy.context.active_object
rl.data.energy=400; rl.data.color=(0.4,0.8,0.5); rl.data.size=4.0; rl.rotation_euler=(math.radians(70),0,math.radians(-150))

bpy.ops.object.camera_add(location=(0,0,5.6)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=50   # FIJA, cenital. flor ya en su tamaño
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=5.6; cam.data.dof.aperture_fstop=3.2


# ===== DISMANTLE sobre la FLOR ORIGINAL: petalos vuelan + centro -> singularidad =====
import random as _rnd
_rnd.seed(11)
for p in petals:
    p['fly_v']=_rnd.uniform(5.0,8.5)
    p['fly_dl']=(1.0-p['od'])*0.8 + _rnd.uniform(0,0.3)   # escalonado pero terminan antes
    p['tumble']=(_rnd.uniform(-6,6),_rnd.uniform(-6,6),_rnd.uniform(-6,6))
    p['zv']=_rnd.uniform(-2.0,3.5)
# fondo TRANSPARENTE: el fondo lo pone el VIAJE (estelas) en el composite
S.render.film_transparent=True
S.render.image_settings.color_mode='RGBA'
sky.hide_render=True
halo.hide_render=True            # el halo duro era el circulo perfecto -> fuera

outdir='/tmp/anim/dismantle/raw'; os.makedirs(outdir,exist_ok=True)
import glob as _g
for old in _g.glob(outdir+'/f*.png'): os.remove(old)
N=240; HOLD=4.0; FLY_DUR=5.8
for f in range(N):
    t=f/24.0
    # estado ABIERTO + vuelo de petalos (como ya lo teniamos)
    for p in petals:
        fly=ease((t-HOLD-p['fly_dl'])/FLY_DUR)
        rad=p['br'] + fly*p['fly_v']*(1.0-0.12*fly)       # leve perdida de impulso
        # FLUTTER: balanceo lateral perpendicular + flotacion vertical (trayectoria de hoja)
        flut=0.5*math.sin(t*2.6+p['wph'])*fly
        px=-math.sin(p['a']); py=math.cos(p['a'])
        x=math.cos(p['a'])*rad + px*flut
        y=math.sin(p['a'])*rad + py*flut
        z=p['rz'] + fly*p['zv'] + 0.25*math.sin(t*1.8+p['wph'])*fly
        s=p['s']*(1.0-0.45*fly)
        p['o'].location=(x,y,z)
        p['o'].scale=(s,s*1.25,s)
        tb=p['tumble']
        # rotacion: tumble + flutter oscilante (la hoja se mece)
        p['o'].rotation_euler=(0.12+tb[0]*fly+0.3*math.sin(t*3.2+p['wph'])*fly, tb[1]*fly, p['a']-math.pi/2+tb[2]*fly)
    # CENTRO se achica a SINGULARIDAD (scale -> punto) manteniendo emision BRILLANTE
    col=ease((t-HOLD)/7.0)
    cs=1.0-0.92*col                         # se achica a un punto (NO desaparece, queda singularidad)
    core.scale=(cs,cs,cs)
    cestr.outputs[0].default_value=2.0+5.0*col   # singularidad verde (no blanco quemado)
    S.render.filepath=f'{outdir}/f{f:03d}.png'
    bpy.ops.render.render(write_still=True)
    if f%20==0: print('dismantle',f)
print('DISMANTLE DONE')
