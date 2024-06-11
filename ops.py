
from . import utils
from .globals import __GLOBALS__
from . import const as __CONSTANTS__

import bpy, gpu, blf, bmesh
from gpu_extras.batch import batch_for_shader

from bpy_extras.view3d_utils import location_3d_to_region_2d

#
# ---------------------------------------------------------------- UTIL FUNCTIONS
# 

def draw_text_px(self, context):
  
  region, rv3d = utils.view3d_get(context)

  if region and rv3d:

    if not __GLOBALS__.jbeam_renderer_running: return
    if context.object.mode != 'OBJECT' and context.object.mode != 'EDIT': return
      
    obj = context.active_object
    if not utils.is_object_mesh(obj) or not utils.is_object_jbeam(obj): return

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_bmesh_jbeam_info(bm)

    _layer_nodes= jinfo.layer_nodes
    
    shader= gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("color", (.7, .7, .7, .25))
    
    _state_blend= gpu.state.blend_get()
    gpu.state.blend_set('ALPHA_PREMULT')
    
    blf.color(0, .0, .0, .0, 1.0)
    blf.size(0, 14.0)

    matrix= bpy.context.object.matrix_world

    for vert in bm.verts:

      pos = location_3d_to_region_2d(region, rv3d, matrix @ vert.co)

      if pos:
        
        pos[0]+= 8
        pos[1]+= 6

        blf.position(0, *pos, 0)

        label= str(vert[_layer_nodes], 'utf-8')
        w, h= blf.dimensions(0, label)

        rect= [
          (pos[0]-4,   pos[1]-2),
          (pos[0]+w+4, pos[1]-2),
          (pos[0]+w+4, pos[1]+h+2),
          (pos[0]+w+4, pos[1]+h+2),
          (pos[0]-4,   pos[1]+h+2),
          (pos[0]-4,   pos[1]-2)
        ]

        batch = batch_for_shader(shader, 'TRIS', {"pos": rect})
        batch.draw(shader)

        blf.draw(0, label)
      
    gpu.state.blend_set(_state_blend)
    gpu.shader.unbind()

#
# ---------------------------------------------------------------- OPERATORS
# 

class SOPUTILS_OBJECT_OT_jbeam_renderer(bpy.types.Operator): # ----------------------------- Jbeam Node Renderer
  """Real-time JBeam renderer"""
  bl_idname = "soputils.jbeam_renderer"
  bl_label = "JBeam real-time renderer"

  _handle= None

  def modal(self, context, event):
    if __GLOBALS__.jbeam_renderer_running:
      return {'PASS_THROUGH'}
    self.finish(context)
    return {'FINISHED'}

  def execute(self, context):
    args= (self, context)
    self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_px, args, 'WINDOW', 'POST_PIXEL')
    return {'RUNNING_MODAL'}

  def cancel(self, context): self.finish(context)
  def finish(self, context):
    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
    
class SOPUTILS_VERTEX_OT_JbeamCopyVertices(bpy.types.Operator): # ----------------------------- Jbeam Copy Vertices as Nodes
  """Copy selected vertices (in order) as nodes for use in JBeam"""
  bl_idname = "soputils.jbeam_copyvertex"
  bl_label = "Copy JBeam nodes"
  bl_options = {'REGISTER'}
  
  @classmethod
  def poll(cls, context):
    return __GLOBALS__.selection_vert and context.active_object.type == 'MESH'

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_bmesh_jbeam_info(bm)

    if len(jinfo.hist_len) > 0:

      _layer_nodes= jinfo.layer_nodes
      result= []

      for se in jinfo.hist_len:

        if isinstance(se, bmesh.types.BMVert):

          name= str(se[_layer_nodes], 'utf-8')
          pos= ", ".join(["{:4.2f}".format(v) for v in bm.verts[se.index].co])

          result.append(f"[\"{name}\", {pos}]")

        else:
          continue
      
      if len(result) > 0:
        context.window_manager.clipboard= '\n' + {'\n'.join(result)} + '\n'
        print(result)

      bm.free()

    else:
      print("No vertices selected.")
    return {'FINISHED'}
  
class SOPUTILS_EDGE_OT_JbeamCopyEdges(bpy.types.Operator): # ----------------------------- Jbeam Copy Edges as Beams
  """Copy selected edges (in order) as beams for use in JBeam"""
  bl_idname = "soputils.jbeam_copyedge"
  bl_label = "Copy JBeam beams"
  bl_options = {'REGISTER'}
  
  @classmethod
  def poll(cls, context):
    return __GLOBALS__.selection_edge and context.active_object.type == 'MESH'

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_bmesh_jbeam_info(bm)

    if len(jinfo.hist_len) > 0:

      _layer_nodes= jinfo.layer_nodes
      result= []

      for se in jinfo.hist:

        if isinstance(se, bmesh.types.BMEdge):

          names= (
            str(se.verts[0][_layer_nodes], 'utf-8'),
            str(se.verts[1][_layer_nodes], 'utf-8')
          )

          result.append(f"[\"{names[0]}\", \"{names[1]}\"]\n")

        else:
          continue

      if len(result) > 0:
        context.window_manager.clipboard= '\n' + {'\n'.join(result)} + '\n'
        print(result)
    
      bm.free()

    else:
      print("No edges selected.")
    return {'FINISHED'}
    
class SOPUTILS_OBJECT_OT_jbeam_data_create(bpy.types.Operator): # ----------------------------- Jbeam Create GeometryNodes Modifier
  """Create object JBeam data"""
  bl_idname = "soputils.jbeam_data_create"
  bl_label = "Create JBeam Part"
  bl_options = {'REGISTER', 'UNDO'}
  
  @classmethod
  def poll(cls, context):
    if context.object.mode != 'OBJECT' and context.object.mode != 'EDIT': return False
    obj= context.active_object
    return utils.is_object_mesh(obj) and not utils.is_object_jbeam(obj)

  def execute(self, context):

    obj= context.active_object
    attr= obj.data.attributes

    if not __CONSTANTS__.ATTR_JBEAM_BEAMS in attr: attr.new(__CONSTANTS__.ATTR_JBEAM_BEAMS, type='STRING', domain='EDGE')
    if not __CONSTANTS__.ATTR_JBEAM_NODES in attr:

      attr.new(__CONSTANTS__.ATTR_JBEAM_NODES, type='STRING', domain='POINT')

      bm= utils.get_active_object_bmesh(context)
      jinfo= utils.create_bmesh_jbeam_info(bm)

      _layer_nodes= jinfo.layer_nodes

      for v in bm.verts:
        v[_layer_nodes]= bytes(f"n{v.index}", 'utf-8')
      
      if context.object.mode == 'OBJECT':
        bm.to_mesh(obj.data)
      
      bm.free()

    return {'FINISHED'}
  
class SOPUTILS_OBJECT_OT_jbeam_data_remove(bpy.types.Operator): # ----------------------------- Jbeam Destroy GeometryNodes Modifier
  """Removes this object's JBeam data"""
  bl_idname = "soputils.jbeam_data_remove"
  bl_label = "Remove JBeam Part"
  bl_options = {'REGISTER', 'UNDO'}
  
  @classmethod
  def poll(cls, context):
    if context.object.mode != 'OBJECT' and context.object.mode != 'EDIT': return False
    obj= context.active_object
    return utils.is_object_mesh(obj) and utils.is_object_jbeam(obj)

  def execute(self, context):

    obj= context.active_object

    attr= obj.data.attributes
    if __CONSTANTS__.ATTR_JBEAM_BEAMS in attr: attr.remove(attr[__CONSTANTS__.ATTR_JBEAM_BEAMS])
    if __CONSTANTS__.ATTR_JBEAM_NODES in attr: attr.remove(attr[__CONSTANTS__.ATTR_JBEAM_NODES])
    return {'FINISHED'}

#
# ---------------------------------------------------------------- REGISTRY
# 

classes= [
  SOPUTILS_OBJECT_OT_jbeam_renderer,
  SOPUTILS_VERTEX_OT_JbeamCopyVertices,
  SOPUTILS_EDGE_OT_JbeamCopyEdges,
  SOPUTILS_OBJECT_OT_jbeam_data_create,
  SOPUTILS_OBJECT_OT_jbeam_data_remove
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)