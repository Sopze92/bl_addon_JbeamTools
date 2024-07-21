
from .. import utils
from ..jbeam import visualizer
from ..core.globals import __GLOBALS__
from ..core import const as __CONSTANTS__

import bpy, bmesh

from bpy.props import BoolProperty, StringProperty

#
# ---------------------------------------------------------------- OPERATORS :: COPY VERTICES
#   

class JBEAMTOOLS_VERTEX_OT_JbeamCopyVertices(bpy.types.Operator):
  """Copy selected vertices (in order) as nodes for use in JBeam"""
  bl_idname = "jbeamtools.jbeam_copyvertex"
  bl_label = "Copy Nodes"
  bl_options = {'REGISTER'}

  sorting: StringProperty(default='RAW')
  
  @classmethod
  def poll(cls, context):
    return __GLOBALS__.selection_vert and context.active_object.type == 'MESH'

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_jbeam_info(bm)

    if jinfo.select_history_len > 0:

      _layer_nodes= jinfo.layer_nodes
      result= []

      elements= jinfo.select if jinfo.use_select else jinfo.select_history

      #print("use_select:", jinfo.use_select)

      for se in elements:

        if isinstance(se, bmesh.types.BMVert):

          name= utils.get_node_name_full(se[_layer_nodes])
          pos= ", ".join(["{:4.2f}".format(v) for v in bm.verts[se.index].co])

          result.append(f"[\"{name}\", {pos}]")

        else:
          continue
      
      if len(result) > 0:

        #print("sorting:", self.sorting)

        if self.sorting == 'INV':
          result.reverse()
        elif self.sorting != 'RAW':
          ascending= 'A' in self.sorting
          left_first= 'L' in self.sorting
          side_over_name= 'S' in self.sorting

          result.sort(key= lambda e: utils.sort_node(e, ascending, side_over_name, left_first))

        result_str= '\n'.join(result) 

        context.window_manager.clipboard= result_str + '\n'
        #print("node result:\n" + result_str)

      bm.free()

    else:
      print("No vertices selected.")
    return {'FINISHED'}

#
# ---------------------------------------------------------------- OPERATORS :: COPY EDGES
#   

class JBEAMTOOLS_EDGE_OT_JbeamCopyEdges(bpy.types.Operator):
  """Copy selected edges (in order) as beams for use in JBeam"""
  bl_idname = "jbeamtools.jbeam_copyedge"
  bl_label = "Copy Beams"
  bl_options = {'REGISTER'}

  sorting: StringProperty(default='RAW')
  
  @classmethod
  def poll(cls, context):
    return __GLOBALS__.selection_edge and context.active_object.type == 'MESH'

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_jbeam_info(bm)

    if jinfo.select_history_len > 0:

      _layer_nodes= jinfo.layer_nodes
      result= []
      
      elements= jinfo.select if jinfo.use_select else jinfo.select_history

      for se in elements:

        if isinstance(se, bmesh.types.BMEdge):

          names= (
            utils.get_node_name_full(se.verts[0][_layer_nodes]),
            utils.get_node_name_full(se.verts[1][_layer_nodes])
          )

          result.append(str(b"[\"%s\", \"%s\"]" % (names[0], names[1]), 'utf-8'))

        else:
          continue

      if len(result) > 0:

        if self.sorting == 'INV':
          result.reverse()
        if self.sorting != 'RAW':
          ascending= 'A' in self.sorting
          left_first= 'L' in self.sorting
          side_over_name= 'S' in self.sorting

          result.sort(key= lambda e: utils.sort_beam(e, ascending, side_over_name, left_first, False))

        result_str= '\n'.join(result) 

        context.window_manager.clipboard= result_str + '\n'
        print("beam result:\n" + result_str)
    
      bm.free()

    else:
      print("No edges selected.")
    return {'FINISHED'}
#
# ---------------------------------------------------------------- REGISTRY
# 

classes= [
  JBEAMTOOLS_VERTEX_OT_JbeamCopyVertices,
  JBEAMTOOLS_EDGE_OT_JbeamCopyEdges
]

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)