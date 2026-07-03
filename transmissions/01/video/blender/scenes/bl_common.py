# helpers comunes para las escenas
import bpy, math
def setup(samples=80, exposure=0.0, bg=(0.003,0.011,0.006,1)):
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
    S.cycles.samples=samples; S.cycles.use_denoising=True
    S.render.resolution_x=960; S.render.resolution_y=540
    S.render.image_settings.file_format='PNG'
    S.view_settings.view_transform='Filmic'; S.view_settings.exposure=exposure
    S.world.use_nodes=True
    S.world.node_tree.nodes['Background'].inputs[0].default_value=bg
    return S
def emission_mat(name, color, strength):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new('ShaderNodeOutputMaterial'); e=nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value=color; e.inputs['Strength'].default_value=strength
    nt.links.new(e.outputs['Emission'], o.inputs['Surface'])
    return m, e
