
from . import utils
from .jbeam import visualizer
from .core.globals import __GLOBALS__
from .core import const as __CONSTANTS__

import bpy, bmesh
#
# ---------------------------------------------------------------- OPERATORS
# 

class JBEAMTOOLS_SCENE_OT_jbeam_nodevis_renderer(bpy.types.Operator): # ----------------------------- Jbeam Node Renderer
  """Real-time JBeam Node renderer"""
  bl_idname = "jbeamtools.jbeam_nodevis_renderer"
  bl_label = "JBeam real-time node renderer"
  _handle= None
  _handle_text= None

  def modal(self, context, event):
    if __GLOBALS__.jbeam_nodevis_renderer_running:
      return {'PASS_THROUGH'}
    self.finish(context)
    return {'FINISHED'}

  def execute(self, context):
    self._handle = bpy.types.SpaceView3D.draw_handler_add(visualizer.draw_nodevis, (context,), 'WINDOW', 'POST_VIEW')
    self._handle_text = bpy.types.SpaceView3D.draw_handler_add(visualizer.draw_nodetextvis, (context,), 'WINDOW', 'POST_PIXEL')
    return {'RUNNING_MODAL'}

  def cancel(self, context): self.finish(context)
  def finish(self, context):
    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
    bpy.types.SpaceView3D.draw_handler_remove(self._handle_text, 'WINDOW')

class JBEAMTOOLS_SCENE_OT_jbeam_beamvis_renderer(bpy.types.Operator): # ----------------------------- Jbeam Beam Renderer
  """Real-time JBeam Beam renderer"""
  bl_idname = "jbeamtools.jbeam_beamvis_renderer"
  bl_label = "JBeam real-time beam renderer"
  _handle= None
  _handle_text= None

  def modal(self, context, event):
    if __GLOBALS__.jbeam_beamvis_renderer_running:
      return {'PASS_THROUGH'}
    self.finish(context)
    return {'FINISHED'}

  def execute(self, context):
    self._handle = bpy.types.SpaceView3D.draw_handler_add(visualizer.draw_beamvis, (context,), 'WINDOW', 'POST_VIEW')
    self._handle_text = bpy.types.SpaceView3D.draw_handler_add(visualizer.draw_beamtextvis, (context,), 'WINDOW', 'POST_PIXEL')
    return {'RUNNING_MODAL'}

  def cancel(self, context): self.finish(context)
  def finish(self, context):
    bpy.types.SpaceView3D.draw_handler_remove(self._handle_text, 'WINDOW')
    
class JBEAMTOOLS_OBJECT_OT_jbeam_data_create(bpy.types.Operator): # ----------------------------- Jbeam Create GeometryNodes Modifier
  """Create object JBeam data"""
  bl_idname = "jbeamtools.jbeam_data_create"
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
  
class JBEAMTOOLS_OBJECT_OT_jbeam_data_remove(bpy.types.Operator): # ----------------------------- Jbeam Destroy GeometryNodes Modifier
  """Removes this object's JBeam data"""
  bl_idname = "jbeamtools.jbeam_data_remove"
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
    
class JBEAMTOOLS_VERTEX_OT_JbeamCopyVertices(bpy.types.Operator): # ----------------------------- Jbeam Copy Vertices as Nodes
  """Copy selected vertices (in order) as nodes for use in JBeam"""
  bl_idname = "jbeamtools.jbeam_copyvertex"
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
  
class JBEAMTOOLS_EDGE_OT_JbeamCopyEdges(bpy.types.Operator): # ----------------------------- Jbeam Copy Edges as Beams
  """Copy selected edges (in order) as beams for use in JBeam"""
  bl_idname = "jbeamtools.jbeam_copyedge"
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
  
#
# ---------------------------------------------------------------- REGISTRY
# 

classes= [
  JBEAMTOOLS_SCENE_OT_jbeam_nodevis_renderer,
  JBEAMTOOLS_SCENE_OT_jbeam_beamvis_renderer,
  JBEAMTOOLS_OBJECT_OT_jbeam_data_create,
  JBEAMTOOLS_OBJECT_OT_jbeam_data_remove,
  JBEAMTOOLS_VERTEX_OT_JbeamCopyVertices,
  JBEAMTOOLS_EDGE_OT_JbeamCopyEdges
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)