
from .. import utils
from ..core.globals import __GLOBALS__

import bpy, blf, bmesh

#
# region ---------------------------------------------------------------- HELPERS
# 

def _get_ztest_icon(v):
  return __GLOBALS__.icons['jbeam_vis_ztest_partial' if v==2 else 'jbeam_vis_ztest_on' if v==1 else 'jbeam_vis_ztest_off'].icon_id

def _create_prop_row(element, name):
  row= element.row()
  lab= row.row()
  lab.ui_units_x=4
  lab.alignment='RIGHT'
  lab.label(text=name)
  return row.row(align=True)

def _insert_info(container, text, alignment='CENTER', active= True):
  if hasattr(text, '__iter__') and not isinstance(text, str):
    for line in text:
      row= container.row()
      row.active=active
      row.alignment=alignment
      row.scale_y= .625
      row.label(text=line)
  else:
    row= container.row()
    row.active=active
    row.alignment=alignment
    row.label(text=text)
# endregion

#
# region ---------------------------------------------------------------- DATA
# 

class VIEW3D_PT_jbeamtools_data(bpy.types.Panel):
  bl_label = 'Data'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeamTools'

  def draw(self, context):

    lay= self.layout
    
    jbtools= context.scene.jbtools
    obj= context.active_object

    _mode_object= context.object.mode == 'OBJECT'
    _mode_edit= context.object.mode == 'EDIT'

    if utils.is_object_mesh(obj):

      if not utils.is_object_jbeam(obj):
        _insert_info(lay, "Create a JBeam part to start", active= False)
        return

      bm= utils.get_active_object_bmesh(context)
      jinfo= utils.create_jbeam_info(bm)

      if _mode_edit:

        _node= context.tool_settings.mesh_select_mode[0]
        _beam= context.tool_settings.mesh_select_mode[1]

        use_select= jinfo.use_select

        __GLOBALS__.selection_edge= _beam
        __GLOBALS__.selection_vert= _node

        sel_len= jinfo.select_history_len if not use_select else jinfo.select_verts_len if _node else jinfo.select_edges_len
        sel_single= sel_len < 2

        box= lay.box()
        box.active= sel_len > 0 and (_node or _beam)

        if box.active:
          if sel_single:
            if _node:
              val= _create_prop_row(box, "Node")
              val.prop(jbtools, 'jbeam_active_node_name', text="")
            elif _beam:
              val= _create_prop_row(box, "Beam")
              val.prop(jbtools, 'jbeam_active_beam_name_a', text="")
              val.prop(jbtools, 'jbeam_active_beam_name_b', text="")
          else:
            _insert_info(box, f"{sel_len} {'Nodes' if _node else 'Beams'} selected")
        else:
          _insert_info(box, "Nothing selected", active= False)

        if _node or _beam:

          val= _create_prop_row(box, "Prefix")
          val.prop(jbtools, 'jbeam_user_prefix', text="")
          val.operator(F"jbeamtools.jbeam_prefix_getset", text="Get").setter=False
          row= val.row(align=True)
          row.operator(F"jbeamtools.jbeam_prefix_getset", text="Set").setter=True
          row.active= jbtools.jbeam_user_prefix != None and len(jbtools.jbeam_user_prefix) > 0
          val= _create_prop_row(box, "Count start")
          val.prop(jbtools, "jbeam_naming_countstart", text= "")
          val.operator(F"jbeamtools.jbeam_numeral_action", text="Count").action='CNT'
          val.operator(F"jbeamtools.jbeam_numeral_action", text="Replace").action='SET'
          row= box.row()
          row.operator(F"jbeamtools.jbeam_numeral_action", text="Invert").action='INV'
          row_= row.row(align=True)
          row_.operator(F"jbeamtools.jbeam_numeral_action", text="Count++").action='INC'
          row_.operator(F"jbeamtools.jbeam_numeral_action", text="Count--").action='DEC'
          val= _create_prop_row(box, "Side")
          val.operator(F"jbeamtools.jbeam_side_handler", text="<< L++").action='LFT'
          val.operator(F"jbeamtools.jbeam_side_handler", text="Clear").action='CLR'
          val.operator(F"jbeamtools.jbeam_side_handler", text="R++ >>").action='RGT'
          
      bm.free()
# endregion

#
# region ---------------------------------------------------------------- IN/OUT
# 

class VIEW3D_PT_jbeamtools_inout(bpy.types.Panel):
  bl_label = 'In/Out'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeamTools'

  def draw(self, context):

    lay= self.layout
    
    jbtools= context.scene.jbtools
    obj= context.active_object

    _mode_edit= context.object.mode == 'EDIT'

    if utils.is_object_mesh(obj):

      if not utils.is_object_jbeam(obj):
        _insert_info(lay, "Create a JBeam part to start", active= False)
        return
      
      if not _mode_edit:
        _insert_info(lay, "Actions require Edit Mode", active= False)
        return
      
      bm= utils.get_active_object_bmesh(context)
      jinfo= utils.create_jbeam_info(bm)

      _node= context.tool_settings.mesh_select_mode[0]
      _beam= context.tool_settings.mesh_select_mode[1]

      use_select= jinfo.use_select

      sel_len= jinfo.select_len if use_select else jinfo.select_history_len
      sel_single= sel_len < 2

      # copy nodes/beams
      box= lay.box()
      box.active= sel_len > 0 and (_node or _beam)

      if box.active:
        _mode= "vertex" if _node else "edge"
        _optext=("Copy Node" if sel_single else "Copy Nodes") if _node else ("Copy Beam" if sel_single else "Copy Beams")
        
        box.label(text="With selection order:")

        if use_select:
          _insert_info(box, [
            "Warning: Selection history was compromised",
            "User selection order is unpredictable"
          ], active= False)

        row= box.row(align=True)
        row.operator(F"jbeamtools.jbeam_copy{_mode}", text=_optext).sorting='RAW'
        row.operator(F"jbeamtools.jbeam_copy{_mode}", text="Copy reverse").sorting='INV'
        
        box.label(text="Copy sorted:")

        grid= box.grid_flow(columns=2, even_columns=True, align=True)
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="L>R-Asc").sorting='ALS'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="L>R-Desc").sorting='DLS'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="R>L-Asc").sorting='ARS'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="R>L-Desc").sorting='DRS'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="Asc-L>R").sorting='ALN'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="Desc-L>R").sorting='DLN'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="Asc-R>L").sorting='ARN'
        grid.operator(F"jbeamtools.jbeam_copy{_mode}", text="Desc-R>L").sorting='DRN'
        
      else:
        _insert_info(box, "Select Nodes/Beams to show actions", active= False)
    
      bm.free()
# endregion

#
# region ---------------------------------------------------------------- STYLE
# 

class VIEW3D_PT_jbeamtools_style(bpy.types.Panel):
  bl_label = 'Style'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeamTools'

  def draw(self, context):

    lay= self.layout
    
    jbtools= context.scene.jbtools
    obj= context.active_object
    
    # node vis settings
    lay.label(text="Node vis settings:")
    box= lay.box()

    val= _create_prop_row(box, "Vis mode:")
    val.prop(jbtools, 'jbeam_nodevis_mode', text="")

    val= _create_prop_row(box, "Point")
    val.prop(jbtools, 'jbeam_nodevis_color', text="")
    val.prop(jbtools, 'jbeam_nodevis_size', text="")
    val.prop(jbtools, 'jbeam_nodevis_ztest_cycle', icon_only=True, icon_value=_get_ztest_icon(jbtools.jbeam_nodevis_ztest))

    if 'C' in jbtools.jbeam_nodevis_mode:
      box.label(text="(overriden by current Node mode)")
    
    val= _create_prop_row(box, "Text")
    val.prop(jbtools, 'jbeam_nodetextvis_fgcolor', text="")
    val.prop(jbtools, 'jbeam_nodetextvis_bgcolor', text="")
    
    val= _create_prop_row(box, "Font size")
    val.prop(jbtools, 'jbeam_nodetextvis_size', text="", slider=True)

    # beam vis settings
    lay.label(text="Beam vis settings:")
    
    box= lay.box()
    val= _create_prop_row(box, "Vis mode:")
    val.prop(jbtools, 'jbeam_beamvis_mode', text="")

    val= _create_prop_row(box, "Line")
    val.prop(jbtools, 'jbeam_beamvis_color', text="")
    val.prop(jbtools, 'jbeam_beamvis_size', text="")
    val.prop(jbtools, 'jbeam_beamvis_ztest_cycle', icon_only=True, icon_value=_get_ztest_icon(jbtools.jbeam_beamvis_ztest))

    if 'C' in jbtools.jbeam_beamvis_mode:
      box.label(text="(color overriden by current Beam mode)")

    val= _create_prop_row(box, "Text")
    val.prop(jbtools, 'jbeam_beamtextvis_fgcolor', text="")
    val.prop(jbtools, 'jbeam_beamtextvis_bgcolor', text="")

    val= _create_prop_row(box, "Font size")
    val.prop(jbtools, 'jbeam_beamtextvis_size', text="", slider=True)
    
    _insert_info(lay, ["If you're experiencing low performance", "consider setting text BG full transparent"], active= False)
# endregion

#
# region ---------------------------------------------------------------- BLENDER
# 

class VIEW3D_PT_jbeamtools_blender(bpy.types.Panel):
  bl_label = 'Blender'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeamTools'

  def draw(self, context):

    lay= self.layout
    obj= context.active_object

    if utils.is_object_mesh(obj):
      
      _mode_object= context.object.mode == 'OBJECT'
      _mode_edit= context.object.mode == 'EDIT'

      if _mode_edit:
        
        lay.label(text="Merge:")

        row= lay.row(align=True)
        row.operator("mesh.remove_doubles", text="Merge")
        opp= row.operator("mesh.merge", text="Center")
        opp.type='CENTER'

      if _mode_object or _mode_edit:

        jbeam= utils.is_object_jbeam(obj)

        lay.label(text="General:")
        box= lay.box()
        if not jbeam: box.operator("jbeamtools.jbeam_data_create", text="Create JBeam Part")
        else: box.operator("jbeamtools.jbeam_data_remove", text="Remove JBeam Part")
# endregion

#
# region ---------------------------------------------------------------- REGISTRY
# 

classes = (
  VIEW3D_PT_jbeamtools_blender,
	VIEW3D_PT_jbeamtools_data,
	VIEW3D_PT_jbeamtools_inout,
  VIEW3D_PT_jbeamtools_style
)

icons = {
  "jbeam_vis_ztest_on",
  "jbeam_vis_ztest_off",
  "jbeam_vis_ztest_partial",
}

def register():
  import os
  import bpy.utils.previews
  for cls in classes:
    bpy.utils.register_class(cls)

  icon_collection = bpy.utils.previews.new()
  icons_dir = os.path.join(os.path.dirname(__file__), "icon")

  for icon in icons:
    icon_collection.load(icon, os.path.join(icons_dir, f"{icon}.png"), 'IMAGE')

  __GLOBALS__.icons = icon_collection

def unregister():
  import bpy.utils.previews
  for cls in classes:
    bpy.utils.unregister_class(cls)

  bpy.utils.previews.remove(__GLOBALS__.icons)
# endregion
