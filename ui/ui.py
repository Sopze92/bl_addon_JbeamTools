
from .. import utils
from ..core.globals import __GLOBALS__

import bpy, bmesh

class VIEW3D_PT_jbeamtools_main_panel(bpy.types.Panel):
  bl_label = 'JBeam Tools'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeam'

  def draw(self, context):

    lay= self.layout
    
    jbtools= context.scene.jbtools
    obj= context.active_object

    if utils.is_object_mesh(obj):

      lay.label(text="General:")

      col= lay.column(translate=False)

      _mode_object= context.object.mode == 'OBJECT'
      _mode_edit= context.object.mode == 'EDIT'

      jbeam= utils.is_object_jbeam(obj)

      if _mode_object or _mode_edit:
        
        if not jbeam: col.operator("jbeamtools.jbeam_data_create", text="Create JBeam Part")
        else: col.operator("jbeamtools.jbeam_data_remove", text="Remove JBeam Part")

      if jbeam:

        bm= utils.get_active_object_bmesh(context)
        jinfo= utils.create_bmesh_jbeam_info(bm)

        _beam= jinfo.hist_type == 'BEAM'
        _node= jinfo.hist_type == 'NODE'

        __GLOBALS__.selection_edge= _beam
        __GLOBALS__.selection_vert= _node

        if _mode_edit:

          # copy nodes/beams
          row= lay.row()
          row.operator("jbeamtools.jbeam_copyvertex", text="Copy Node" if _beam or jinfo.hist_single else "Copy Nodes")
          row.operator("jbeamtools.jbeam_copyedge", text="Copy Beam" if _node or jinfo.hist_single else "Copy Beams")

          row= lay.row()
          if _node: 
            row.prop(jbtools, 'jbeam_active_node_name', text="Name")
        
        bm.free()

def _get_ztest_icon(v):
  return __GLOBALS__.icons['jbeam_vis_ztest_partial' if v==2 else 'jbeam_vis_ztest_on' if v==1 else 'jbeam_vis_ztest_off'].icon_id

class VIEW3D_PT_jbeamtools_style_panel(bpy.types.Panel):
  bl_label = 'JBeam Style'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'JBeam'

  def draw(self, context):

    lay= self.layout
    
    jbtools= context.scene.jbtools
    obj= context.active_object
    
    # node vis settings
    box= lay.box()
    box.label(text="Node vis settings:")
    box.prop(jbtools, 'jbeam_nodevis_mode', text="Mode")

    row= box.row(align= True)
    row.label(text="Point")
    row.prop(jbtools, 'jbeam_nodevis_color', text="")
    row.prop(jbtools, 'jbeam_nodevis_size', text="")
    row.prop(jbtools, 'jbeam_nodevis_ztest_cycle', icon_only=True, icon_value=_get_ztest_icon(jbtools.jbeam_nodevis_ztest))

    if 'C' in jbtools.jbeam_nodevis_mode:
      box.label(text="(overriden by current Node mode)")

    box.prop(jbtools, 'jbeam_nodetextvis_size', text="Font size", slider=True)
    
    brow= box.row()
    rcol= brow.column()
    rcol.prop(jbtools, 'jbeam_nodetextvis_fgcolor', text="Foreground")
    
    rcol= brow.column()
    rcol.prop(jbtools, 'jbeam_nodetextvis_bgcolor', text="Background")

    # beam vis settings
    box= lay.box()
    box.label(text="Beam vis settings:")
    box.prop(jbtools, 'jbeam_beamvis_mode', text="Mode")

    row= box.row(align= True)
    row.label(text="Line")
    row.prop(jbtools, 'jbeam_beamvis_color', text="")
    row.prop(jbtools, 'jbeam_beamvis_size', text="")
    row.prop(jbtools, 'jbeam_beamvis_ztest_cycle', icon_only=True, icon_value=_get_ztest_icon(jbtools.jbeam_beamvis_ztest))

    if 'C' in jbtools.jbeam_beamvis_mode:
      box.label(text="(color overriden by current Beam mode)")

    box.prop(jbtools, 'jbeam_beamtextvis_size', text="Font size", slider=True)
    
    brow= box.row()
    rcol= brow.column()
    rcol.prop(jbtools, 'jbeam_beamtextvis_fgcolor', text="Foreground")
    
    rcol= brow.column()
    rcol.prop(jbtools, 'jbeam_beamtextvis_bgcolor', text="Background")

classes = (
	VIEW3D_PT_jbeamtools_main_panel,
  VIEW3D_PT_jbeamtools_style_panel
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
