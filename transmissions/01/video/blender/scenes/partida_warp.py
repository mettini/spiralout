import bpy, math, os, sys, random
sys.path.insert(0,'/tmp'); exec(open('/tmp/bl_common.py').read())
random.seed(7)
S=setup(samples=48, exposure=-0.2); S.cycles.device='CPU'
S.world.node_tree.nodes['Background'].inputs[0].default_value=(0.0,0.0,0.0,1)
# ESTELAS WARP: lineas emisivas radiando del centro (hiperespacio), mas largas hacia afuera
mat,e=emission_mat('streak',(0.30,0.85,0.45,1),5.0)
base=None
N=240
for i in range(N):
    a=random.uniform(0,2*math.pi); r=random.uniform(0.6,9.0)
    L=0.25+r*0.55*random.uniform(0.7,1.3)              # estela mas larga lejos = warp
    w=0.012*random.uniform(0.6,1.6)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    s=bpy.context.active_object
    s.scale=(w, L, w*0.5)
    # ubicar a mitad de la estela y orientar radialmente (eje Y = radial)
    mid=r+L*0.5
    s.location=(math.cos(a)*mid, math.sin(a)*mid, random.uniform(-0.5,0.5))
    s.rotation_euler=(0,0,a-math.pi/2)
    mm=mat.copy(); mm.node_tree.nodes['Emission'].inputs['Strength'].default_value=random.uniform(2.5,7.0)
    s.data.materials.append(mm)
# core glow
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.5, subdivisions=2, location=(0,0,0))
c=bpy.context.active_object; cm,_=emission_mat('cc',(0.5,1.0,0.6,1),7.0); c.data.materials.append(cm)
# motion blur para estirar las estelas
bpy.ops.object.camera_add(location=(0,0,8)); cam=bpy.context.active_object
cam.rotation_euler=(0,0,0); S.camera=cam; cam.data.lens=35
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=8.0; cam.data.dof.aperture_fstop=3.0
os.makedirs('/tmp/scenes',exist_ok=True)
S.render.filepath='/tmp/scenes/warp_raw.png'; bpy.ops.render.render(write_still=True); print('DONE')
