
from .. import utils
from ..jbeam import visualizer
from ..core.globals import __GLOBALS__
from ..core import const as __CONSTANTS__

import bpy, bmesh

from bpy.props import BoolProperty, StringProperty

#
# ---------------------------------------------------------------- OPERATORS :: NODE RENDERER
#   

class JBEAMTOOLS_SCENE_OT_jbeam_nodevis_renderer(bpy.types.Operator):
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

#
# ---------------------------------------------------------------- OPERATORS :: BEAM RENDERER
#   

class JBEAMTOOLS_SCENE_OT_jbeam_beamvis_renderer(bpy.types.Operator):
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

#
# ---------------------------------------------------------------- OPERATORS :: CREATE JBEAM DATA EDGES
#   

class JBEAMTOOLS_OBJECT_OT_jbeam_data_create(bpy.types.Operator):
  """Create object's JBeam data"""
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
      jinfo= utils.create_jbeam_info(bm)

      _layer_nodes= jinfo.layer_nodes

      for v in bm.verts:  
        v[_layer_nodes]= bytes(f"n{v.index}|n|{v.index}|", 'utf-8')
      
      if context.object.mode == 'OBJECT':
        bm.to_mesh(obj.data)
      
      bm.free()

    return {'FINISHED'}

#
# ---------------------------------------------------------------- OPERATORS :: REMOVE JBEAM DATA EDGES
#   
  
class JBEAMTOOLS_OBJECT_OT_jbeam_data_remove(bpy.types.Operator):
  """Remove object's JBeam data"""
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

#
# ---------------------------------------------------------------- OPERATORS :: NODE PREFIX GET/SET
#   
  
class JBEAMTOOLS_OBJECT_OT_jbeam_prefix_getset(bpy.types.Operator):
  """Set/Get current selection node prefix from/to user variable holder"""
  bl_idname = "jbeamtools.jbeam_prefix_getset"
  bl_label = "Set/Get Node selection prefix"
  bl_options = {'REGISTER', 'UNDO'}

  setter: BoolProperty(default= False)
  
  @classmethod
  def poll(cls, context):
    if context.object.mode != 'EDIT': return False
    obj= context.active_object
    return utils.is_object_mesh(obj) and utils.is_object_jbeam(obj)

  def execute(self, context):
    
    jbtools= context.scene.jbtools

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_jbeam_info(bm)

    if not self.setter:
      jbtools.jbeam_user_prefix= utils.get_selection_prefix(jinfo) or "n"
    
    else:
      utils.set_selection_prefix(jinfo, jbtools.jbeam_user_prefix)

    return {'FINISHED'}

#
# ---------------------------------------------------------------- OPERATORS :: NODE NUMERAL ACTIONS
#   
  
class JBEAMTOOLS_OBJECT_OT_jbeam_numeral_action(bpy.types.Operator):
  """Execute an action on node selection numerals"""
  bl_idname = "jbeamtools.jbeam_numeral_action"
  bl_label = "Execute numeral action"
  bl_options = {'REGISTER', 'UNDO'}

  action: StringProperty("NUL")
  
  @classmethod
  def poll(cls, context):
    if context.object.mode != 'EDIT': return False
    obj= context.active_object
    return utils.is_object_mesh(obj) and utils.is_object_jbeam(obj)

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_jbeam_info(bm)

    numerals= utils.get_selection_numerals(jinfo)

    if self.action == 'CNT' or self.action == 'SET':
      jbtools= context.scene.jbtools
      v= jbtools.jbeam_naming_countstart

      if self.action == 'CNT': # soft replace

        numerals_sort= []
        nrange= range(len(numerals))

        for i in nrange:
          numerals_sort.append((numerals[i], i))

        numerals_sort.sort(key= lambda a: a[0]) # sort by numeral
        diff= v - numerals_sort[0][0]

        for i in nrange:
          numerals[numerals_sort[i][1]]+= diff

      elif self.action == 'SET': # replace (by selection order if any, name order otherwise)
        
        if not jinfo.use_select:
          for i in range(len(numerals)):
            if not numerals[i] < 0: numerals[i]= v
            else: numerals[i]= 0 # add numeral 0 if none
            v+=1
        else:
          numerals_sort= []
          nrange= range(len(numerals))

          for i in nrange:
            numerals_sort.append((numerals[i], i))

          numerals_sort.sort(key= lambda a: a[0]) # sort by numeral

          for i in nrange:
            numerals[numerals_sort[i][1]]= v+i
    
    elif self.action == 'INV': # invert numeral order

      numerals_sort= []
      numerals_sort_inv= []
      nrange= range(len(numerals))

      for i in nrange:
        numerals_sort.append((numerals[i], i))
        numerals_sort_inv.append((numerals[i], i))

      numerals_sort.sort(key= lambda a: a[0]) # sort by numeral
      numerals_sort_inv.sort(key= lambda a: a[0], reverse=True) # sort by numeral

      for i in nrange:
        numerals[numerals_sort[i][1]]= numerals_sort_inv[i][0]

    elif self.action == 'INC': # increment
      for i in range(len(numerals)):
        if not numerals[i] < 0: numerals[i]+= 1
        else: numerals[i]= 0 # add numeral 0 if none

    elif self.action == 'DEC': # decrement
      for i in range(len(numerals)):
        if numerals[i] > 0: numerals[i]-= 1
        else: numerals[i]= -1 # this removes numeral from name

    print(numerals)

    utils.set_selection_numerals(jinfo, numerals)

    return {'FINISHED'}

#
# ---------------------------------------------------------------- OPERATORS :: NODE SIDE HANDLER
#   
  
class JBEAMTOOLS_OBJECT_OT_jbeam_side_assign(bpy.types.Operator):
  """Modify current node selection side"""
  bl_idname = "jbeamtools.jbeam_side_handler"
  bl_label = "Assign node selection side"
  bl_options = {'REGISTER', 'UNDO'}

  action: StringProperty("NUL")
  
  @classmethod
  def poll(cls, context):
    if context.object.mode != 'EDIT': return False
    obj= context.active_object
    return utils.is_object_mesh(obj) and utils.is_object_jbeam(obj)

  def execute(self, context):

    bm= utils.get_active_object_bmesh(context)
    jinfo= utils.create_jbeam_info(bm)

    sides= utils.get_selection_side(jinfo)

    if sides:

      if self.action== 'CLR':
        for i in range(len(sides)):
          sides[i]=""

      else:
        sref= ['l','r'] if self.action=='LFT' else ['r','l']
        for i in range(len(sides)):
          s= sides[i]
          if sref[1] in s: sides[i]= s[1:]
          else: sides[i]= s + sref[0]

    utils.set_selection_side(jinfo, sides)

    return {'FINISHED'}

# ----------------------------- DUMMY

class JBEAMTOOLS_OT_dummy(bpy.types.Operator):
  """Dummy operator, for ui layout"""
  bl_idname = "jbeamtools.__dummy"
  bl_label = "Dummy Operator"
  
  #@classmethod
  #def poll(cls, context): return True
  def execute(self, context): print("dummy operator"); return {'FINISHED'}
  
#
# ---------------------------------------------------------------- REGISTRY
# 

classes= [
  JBEAMTOOLS_OT_dummy,
  JBEAMTOOLS_SCENE_OT_jbeam_nodevis_renderer,
  JBEAMTOOLS_SCENE_OT_jbeam_beamvis_renderer,
  JBEAMTOOLS_OBJECT_OT_jbeam_data_create,
  JBEAMTOOLS_OBJECT_OT_jbeam_data_remove,
  JBEAMTOOLS_OBJECT_OT_jbeam_prefix_getset,
  JBEAMTOOLS_OBJECT_OT_jbeam_numeral_action,
  JBEAMTOOLS_OBJECT_OT_jbeam_side_assign
]

def register():
  from . import ops_clipboard
  for cls in classes:
    bpy.utils.register_class(cls)
      
  ops_clipboard.register()

def unregister():
  from . import ops_clipboard
  for cls in classes:
    bpy.utils.unregister_class(cls)
    
  ops_clipboard.unregister()