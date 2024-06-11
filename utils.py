
from .globals import __GLOBALS__
from . import const as __CONSTANTS__

import bpy, bmesh

def get_active_object_bmesh(context):
  
  if context.object.mode == 'EDIT':
    bm= bmesh.from_edit_mesh(context.active_object.data)
  else:
    bm = bmesh.new()
    bm.from_mesh(context.active_object.data)

  return bm

def is_object_mesh(obj):
  return obj and obj.type == 'MESH'

def is_object_jbeam(obj):
  return __CONSTANTS__.ATTR_JBEAM_NODES in obj.data.attributes and __CONSTANTS__.ATTR_JBEAM_BEAMS in obj.data.attributes

class jbeam_info():
  hist= None
  hist_len= 0
  hist_type= 'NONE'
  hist_single= True
  layer_nodes= None
  layer_beams= None

def create_bmesh_jbeam_info(bm):

  info= jbeam_info()

  info.layer_nodes= bm.verts.layers.string.get(__CONSTANTS__.ATTR_JBEAM_NODES)
  info.layer_beams= bm.edges.layers.string.get(__CONSTANTS__.ATTR_JBEAM_BEAMS)

  history= bm.select_history

  _vert= isinstance(history.active, bmesh.types.BMVert)
  _edge= not _vert and isinstance(history.active, bmesh.types.BMEdge)

  info.hist= history
  info.hist_len= len(history)
  info.hist_type= 'NODE' if _vert else 'BEAM' if _edge else 'NONE'
  info.hist_single= info.hist_len < 2

  return info

def view3d_get(context):
  area= context.area
  if area.type == 'VIEW_3D':
    area.tag_redraw()
    rv3d = area.spaces[0].region_3d
    for region in area.regions:
      if region.type == 'WINDOW':
        return region, rv3d
  return None, None

def view3d_redraw_all(context):
  for area in context.window.screen.areas:
    if area.type == 'VIEW_3D':
      area.tag_redraw()