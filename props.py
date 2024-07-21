from .core.globals import __GLOBALS__ as globals
from . import utils

import bpy, re

from bpy.app.handlers import persistent

from bpy.props import PointerProperty
from bpy.props import BoolProperty, IntProperty, IntVectorProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty

# --------------------------- renderer togglers

@persistent
def load_handler_jbeamvis(file):
  update_beamvis_renderer_state(None, bpy.context)
  update_nodevis_renderer_state(None, bpy.context)

def update_nodevis_renderer_state(self, context):

  state= globals.jbeam_nodevis_renderer_running
  reqstate= context.scene.jbtools.jbeam_nodevis_mode != 'OFF'

  if state != reqstate:
    globals.jbeam_nodevis_renderer_running= reqstate
    if reqstate:
      bpy.ops.jbeamtools.jbeam_nodevis_renderer('INVOKE_DEFAULT')

def update_beamvis_renderer_state(self, context):

  state= globals.jbeam_beamvis_renderer_running
  reqstate= context.scene.jbtools.jbeam_beamvis_mode != 'OFF'

  if state != reqstate:
    globals.jbeam_beamvis_renderer_running= reqstate
    if reqstate:
      bpy.ops.jbeamtools.jbeam_beamvis_renderer('INVOKE_DEFAULT')

# --------------------------- other helpers

# get active node name (full)
def get_active_node_name(self):

  bm= utils.get_active_object_bmesh(bpy.context)
  jinfo= utils.create_jbeam_info(bm)

  return str(jinfo.select_history.active[jinfo.layer_nodes], 'utf-8')

# set active node name (full)
def set_active_node_name(self, value):
  utils.view3d_redraw_all(bpy.context)

  if re.match(r"^[0-z_]+$", value)[0]:
    
    bm= utils.get_active_object_bmesh(bpy.context)
    jinfo= utils.create_jbeam_info(bm)

    jinfo.select_history.active[jinfo.layer_nodes]= bytes(value, 'utf-8')

# get active beam node names (full)
def get_active_beam_node_name(self, index):

  bm= utils.get_active_object_bmesh(bpy.context)
  jinfo= utils.create_jbeam_info(bm)

  return str(jinfo.select_history.active.verts[index][jinfo.layer_nodes], 'utf-8')

# set active beam node names (full)
def set_active_beam_node_name(self, value, index):
  utils.view3d_redraw_all(bpy.context)

  if re.match(r"^[0-z_]+$", value)[0]:
    
    bm= utils.get_active_object_bmesh(bpy.context)
    jinfo= utils.create_jbeam_info(bm)

    jinfo.select_history.active.verts[index][jinfo.layer_nodes]= bytes(value, 'utf-8')

class JBEAMTOOLS_Addon_Props(bpy.types.PropertyGroup):
	
  # node vis mode
  jbeam_nodevis_mode: EnumProperty(
		name= "Node vis mode", description= "Visualization mode for nodes",
    items= [
      ("OFF",   "Off",          ""), 
      ("P",     "Points",       ""),
      ("T",     "Names",        ""),
      ("PT",    "Points+Names", "")
    ],
    update= update_nodevis_renderer_state,
		default= 0
	)

  # beam vis mode
  jbeam_beamvis_mode: EnumProperty(
		name= "Beam vis mode", description= "Visualization mode for beams",
    items= [
      ("OFF",   "Off",      ""), 
      ("L",     "Normal",   "")
    ],
    update= update_beamvis_renderer_state,
		default= 0
	)

  # node vis settings
  jbeam_nodevis_color: FloatVectorProperty(
		description= "The Node color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (1.0, .6, .0, 1.0)
	)

  jbeam_nodevis_size: IntProperty(
		description= "The Node point size",
		min= 8, max= 24, subtype='PIXEL', 
    default= 8
	)

  def _get_nodevis_ztest__dummy(self): return self.jbeam_nodevis_ztest > 0
  def _cycle_nodevis_ztest(self, value):
    v= self.jbeam_nodevis_ztest
    self.jbeam_nodevis_ztest = v+1 if v < 2 else 0

  jbeam_nodevis_ztest_cycle: BoolProperty(
    description= "Cycle through ZTesting modes: Off, On, Partial",
    get=_get_nodevis_ztest__dummy, set=_cycle_nodevis_ztest,
    default= False
  )
  jbeam_nodevis_ztest: IntProperty(default= 0)

  jbeam_nodetextvis_size: IntProperty(
		description= "The Node text size",
		min= 4, soft_min= 8, soft_max= 32, max=100, subtype='PIXEL', 
    default= 14
	)

  jbeam_nodetextvis_fgcolor: FloatVectorProperty(
		description= "The Node text foreground color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (1.0, .6, .0, 1.0)
	)

  jbeam_nodetextvis_bgcolor: FloatVectorProperty(
		description= "The Node text background color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (.0, .0, .0, .45)
	)

  # beam vis settings
  jbeam_beamvis_color: FloatVectorProperty(
		description= "The Beam color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (.0, .88, .0, 1.0)
	)

  jbeam_beamvis_size: IntProperty(
		description= "The Beam line width",
		min= 1, max= 16, subtype='PIXEL', 
    default= 2
	)

  def _get_beamvis_ztest__dummy(self): return self.jbeam_beamvis_ztest > 0
  def _cycle_beamvis_ztest(self, value):
    v= self.jbeam_beamvis_ztest
    self.jbeam_beamvis_ztest = v+1 if v < 2 else 0

  jbeam_beamvis_ztest_cycle: BoolProperty(
    description= "Cycle through ZTesting modes: Off, On, Partial",
    get=_get_beamvis_ztest__dummy, set=_cycle_beamvis_ztest,
    default= False
  )
  jbeam_beamvis_ztest: IntProperty(default= 0)

  jbeam_beamtextvis_size: IntProperty(
		description= "The Beam text size",
		min= 4, soft_min= 8, soft_max= 32, max=100, subtype='PIXEL', 
    default= 14
	)

  jbeam_beamtextvis_fgcolor: FloatVectorProperty(
		description= "The Beam text foreground color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (.0, .88, .0, 1.0)
	)

  jbeam_beamtextvis_bgcolor: FloatVectorProperty(
		description= "The Beam text background color",
		min= 0, max= 1, size= 4, subtype='COLOR', 
    default= (.0, .0, .0, .0)
	)

  # jbeam node name
  jbeam_active_node_name: StringProperty(
    description= "Name of the current node", 
    options= {'TEXTEDIT_UPDATE'}, maxlen= 24, 
    get= get_active_node_name, set= set_active_node_name
  )

  # jbeam beam names
  jbeam_active_beam_name_a: StringProperty(
    description= "Name of the current beam start node", 
    options= {'TEXTEDIT_UPDATE'}, maxlen= 24, 
    get= lambda s: get_active_beam_node_name(s, 0), set= lambda s, v: set_active_beam_node_name(s, v, 0)
  )

  jbeam_active_beam_name_b: StringProperty(
    description= "Name of the current beam end node", 
    options= {'TEXTEDIT_UPDATE'}, maxlen= 24, 
    get= lambda s: get_active_beam_node_name(s, 1), set= lambda s, v: set_active_beam_node_name(s, v, 1)
  )

  jbeam_naming_countstart: IntProperty(
		description= "Starting count for renaming",
		min= 0, soft_max= 48, max=255, subtype='UNSIGNED', 
    default= 0
	)

  # prefix user value
  jbeam_user_prefix: StringProperty(
    description= "Current string to be applied as selected node's prefix", 
    options= {'TEXTEDIT_UPDATE'}, maxlen= 24,
    default= "n"
  )

#
# ---------------------------------------------------------------- REGISTRY
# 

classes = (
	JBEAMTOOLS_Addon_Props,
)

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

  bpy.types.Scene.jbtools = PointerProperty(type=JBEAMTOOLS_Addon_Props)
  bpy.app.handlers.load_post.append(load_handler_jbeamvis)

def unregister():
  for cls in classes:
    bpy.utils.unregister_class(cls)
        
  bpy.app.handlers.load_post.remove(load_handler_jbeamvis)
  del bpy.types.Scene.jbtools