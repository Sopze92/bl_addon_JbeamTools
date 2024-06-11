from .globals import __GLOBALS__ as globals
from . import utils

import bpy, re, bmesh

from bpy.props import PointerProperty
from bpy.props import StringProperty, BoolProperty

def on_jbeam_renderer_state_changed(self, context):
  if context.scene.sopu.jbeam_vertices_show:
    globals.jbeam_renderer_running= True
    bpy.ops.soputils.jbeam_renderer('INVOKE_DEFAULT')
  else:
    globals.jbeam_renderer_running= False

def update_active_node_name(self, context):
  print("update", type(self))

def get_active_node_name(self):

  bm= utils.get_active_object_bmesh(bpy.context)
  jinfo= utils.create_bmesh_jbeam_info(bm)

  return str(jinfo.hist.active[jinfo.layer_nodes], 'utf-8')

def set_active_node_name(self, value):
  print("set", type(self))
  utils.view3d_redraw_all(bpy.context)

  if re.match(r"^[0-z_]+$", value)[0]:
    
    bm= utils.get_active_object_bmesh(bpy.context)
    jinfo= utils.create_bmesh_jbeam_info(bm)

    jinfo.hist.active[jinfo.layer_nodes]= bytes(value, 'utf-8')

class SOPUTIL_Addon_Props(bpy.types.PropertyGroup):
	
  # public
  jbeam_vertices_show: BoolProperty(
		name= "Show node names",
		description= "Show the node names in 3D viewport",
    update= on_jbeam_renderer_state_changed,
		options= set(), default= False
	)

  jbeam_active_node_name: StringProperty(
    name= "", 
    description= "Name of the current node", 
    options= {'TEXTEDIT_UPDATE'}, maxlen= 24, 
    get= get_active_node_name, set= set_active_node_name,
    update= update_active_node_name
  )

#
# ---------------------------------------------------------------- REGISTRY
# 

classes = (
	SOPUTIL_Addon_Props,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.sopu = PointerProperty(type=SOPUTIL_Addon_Props)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
		
	del bpy.types.Scene.sopu