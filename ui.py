
from . import utils
from .globals import __GLOBALS__

import bpy, bmesh

class VIEW3D_PT_soputils_main_panel(bpy.types.Panel):
  bl_label = 'Sopze'
  bl_space_type = 'VIEW_3D'
  bl_region_type= 'UI'
  bl_category = 'Sopze'

  def draw(self, context):
    sopu= context.scene.sopu
    
    obj= context.active_object

    if utils.is_object_mesh(obj):

      self.layout.label(text="JBeam:")

      col= self.layout.column(translate=False)

      _mode_object= context.object.mode == 'OBJECT'
      _mode_edit= context.object.mode == 'EDIT'

      jbeam= utils.is_object_jbeam(obj)

      if _mode_object or _mode_edit:
        
        if not jbeam:
          col.operator("soputils.jbeam_data_create", text="Create JBeam Part")
        else:
          col.operator("soputils.jbeam_data_remove", text="Remove JBeam Part")

      if jbeam:

        bm= utils.get_active_object_bmesh(context)
        jinfo= utils.create_bmesh_jbeam_info(bm)

        _beam= jinfo.hist_type == 'BEAM'
        _node= jinfo.hist_type == 'NODE'

        __GLOBALS__.selection_edge= _beam
        __GLOBALS__.selection_vert= _node

        if _mode_edit:

          # copy nodes/beams
          row= col.row()
          row.operator("soputils.jbeam_copyvertex", text="Copy Node" if _beam or jinfo.hist_single else "Copy Nodes")
          row.operator("soputils.jbeam_copyedge", text="Copy Beam" if _node or jinfo.hist_single else "Copy Beams")

          row= col.row()
          if _node:
            row.prop(sopu, 'jbeam_active_node_name')

          col.separator()
        
        bm.free()
        
      # show node names
      col.prop(sopu, 'jbeam_vertices_show')

      col.separator()

def register():
  bpy.utils.register_class(VIEW3D_PT_soputils_main_panel)

def unregister():
  bpy.utils.unregister_class(VIEW3D_PT_soputils_main_panel)
