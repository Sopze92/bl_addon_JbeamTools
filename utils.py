
from .core.globals import __GLOBALS__
from .core import const as __CONSTANTS__

import bpy, bmesh, re

# general

def get_number_safe(data):
  t= type(data)
  try:
    return data if t is int else int(data)
  except:
    pass
  return -1

# view 3d

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

# object

def get_active_object_bmesh(context):
  
  if context.object.mode == 'EDIT':
    bm= bmesh.from_edit_mesh(context.active_object.data)
  else:
    bm = bmesh.new()
    bm.from_mesh(context.active_object.data)

  return bm

def get_object_bmesh(obj):
  bm = bmesh.new()
  bm.from_mesh(obj.data)
  return bm

def is_object_mesh(obj):
  return obj and obj.type == 'MESH'

def is_object_jbeam(obj):
  return __CONSTANTS__.ATTR_JBEAM_NODES in obj.data.attributes and __CONSTANTS__.ATTR_JBEAM_BEAMS in obj.data.attributes

# jbeam info

class jbeam_info():
  select_history_mode= 'NONE'
  select_history= []
  select_history_len= 0
  select_history_single= True
  select_mode= 'NONE'
  select_verts= []
  select_verts_len= 0
  select_verts_single= True
  select_edges= []
  select_edges_len= 0
  select_edges_single= True
  #select_faces= []
  #select_faces_len= 0
  #select_faces_single= True
  select_len= 0
  select_single= True
  layer_nodes= None
  layer_beams= None

def create_jbeam_info(bmesh_):

  info= jbeam_info()

  info.layer_nodes= bmesh_.verts.layers.string.get(__CONSTANTS__.ATTR_JBEAM_NODES)
  info.layer_beams= bmesh_.edges.layers.string.get(__CONSTANTS__.ATTR_JBEAM_BEAMS)

  # normal selection
  select_mode= set()

  if 'VERT' in bmesh_.select_mode: select_mode.add('NODE')
  info.select_verts= [se for se in bmesh_.verts if se.select]
  info.select_verts_len= len(info.select_verts)
  info.select_verts_single= info.select_len < 2

  if 'EDGE' in bmesh_.select_mode: select_mode.add('BEAM')
  info.select_edges= [se for se in bmesh_.edges if se.select]
  info.select_edges_len= len(info.select_edges)
  info.select_edges_single= info.select_len < 2

  #if 'FACE' in bmesh_.select_mode: select_mode.add('FACE')
  #info.select_faces= [se for se in bmesh_.faces if se.select]
  #info.select_faces_len= len(info.select_faces)
  #info.select_faces_single= info.select_len < 2

  info.select_len= info.select_verts_len + info.select_edges_len
  info.select_single= info.select_len < 2
  info.select_mode= select_mode
  
  # selection history
  history= bmesh_.select_history

  _vert= isinstance(history.active, bmesh.types.BMVert)
  _edge= not _vert and isinstance(history.active, bmesh.types.BMEdge)

  info.select_history= history
  info.select_history_len= len(history)
  info.select_history_single= info.select_history_len < 2
  info.select_history_mode= 'NODE' if _vert else 'BEAM' if _edge else 'NONE'
  
  info.use_select= (not _vert and not _edge) or (info.select_history_len < (info.select_verts_len if _vert else info.select_edges_len))

  info.select= history if not info.use_select else ( info.select_verts if 'VERT' in bmesh_.select_mode else info.select_edges )

  return info

def get_vert_selection(jinfo):

  if jinfo.use_select or jinfo.select_history_mode == 'BEAM':

    if jinfo.select_verts_len > 0:
      select= set(jinfo.select_verts)
      return select, None
    
  elif jinfo.select_history_len > 0 and jinfo.select_history_mode == 'NODE':
    active= jinfo.select_history.active
    select= set([v for v in jinfo.select_history if v.index != active.index])
    return select, active

  return None, None

def get_edge_selection(jinfo):

  if jinfo.use_select or jinfo.select_history_mode == 'NODE':

    if jinfo.select_edges_len > 0:
      select= set(jinfo.select_edges)
      return select, None
    
  elif jinfo.select_history_len > 0:
  
    if jinfo.select_history_mode == 'BEAM':
      active= jinfo.select_history.active
      select= set([e for e in jinfo.select_history if e.index != active.index])
      return select, active

  return None, None

def get_all_vert_raw(jinfo):

  select= jinfo.use_select

  if select and jinfo.select_verts_len > 0 or jinfo.select_history_mode == 'NODE':
    return jinfo.select_verts if select else jinfo.select_history

  elif select and jinfo.select_edges_len > 0 or jinfo.select_history_mode == 'BEAM':

    selection= jinfo.select_edges if select else jinfo.select_history

    verts= set([v for e in selection for v in e.verts])
    return list(verts)

  return None

# string utils

def get_node_data_from_attribute(string: str):
  """ Split the attribute into data """
  return string.split('|')

def get_node_name_full(attribute: bytes):
  """ Get full name string from attribute """
  return str(attribute, 'utf-8').split('|')[0]

def compose_node_data_raw(data:list) -> str:
  """ Create the node data to be stored in attributes """
  nstr= type(data[2]) != str
  data[2]= "" if (nstr and data[2] < 0) else str(data[2]) if nstr else data[2]
  data[0]= data[1] + data[2] + data[3]
  return '|'.join(data)

def compose_node_data(prefix:str= "n", number:int|None=-1, side:str|None="") -> str:
  """ Create the node data to be stored in attributes """
  name= prefix + n + side
  n = "" if (type(number) == int and number < 0) else number
  return name + "|" + prefix + "|" + n + "|" + side

# sortening utils

def get_name_features(name: str):
  try:
    match= re.fullmatch(r"(([A-z_]+)*(?=[0-9])([0-9]+)([A-z]|))", name)
    return match[2], match[3], match[4]
  except: pass
  return name, "", ""

def get_sortable_name(name:str, ascending:bool, side_over_name:bool, left_first:bool):
  pre, num, side= get_name_features(name)
  num= int(num) if num != "" else 100000
  
  side_priority= side.startswith("l") and left_first
  side_factor= ("0" if side_priority else "1")*len(side)

  data= []

  if side_over_name:
    data.append(side_factor)
  
  data.append(pre)

  num= str(num if ascending else 100000-num)
  if len(num) < 6: num= ("0"*(6-len(num))) + num

  data.append(num)

  if not side_over_name:
    data.append(side_factor)

  return "|".join(data)

def sort_node(element, ascending=True, side_over_name=True, left_first=True):
  name= re.search(r"[\"' ]+([A-z0-9_-]+)[\"' ],", element)[1]
  sortable_str= get_sortable_name(name, ascending, side_over_name, left_first)

  print(f"sorting node: '{name}', '{sortable_str}'")
  return sortable_str

def sort_beam(element, ascending=True, side_over_name=True, left_first=True, dest_over_src=False):
  name_a= re.search(r"[\"' ]+([A-z0-9_-]+)[\"' ],", element)[1]
  data_a= get_sortable_name(name_a, ascending, side_over_name, left_first)

  name_b= re.search(r",[\"' ]+([A-z0-9_-]+)[\"' ]", element)[1]
  data_b= get_sortable_name(name_b, ascending, side_over_name, left_first)

  sortable_str= f"{data_b}|{data_a}" if dest_over_src else f"{data_a}|{data_b}"
  
  print(f"sorting beam: '{name_a}' to '{name_b}', '{sortable_str}'")
  return sortable_str

# set prefix for current selection
def set_selection_prefix(jinfo, value):
  view3d_redraw_all(bpy.context)
  
  if re.match(r"^[A-z_]+$", value)[0]:

    verts= get_all_vert_raw(jinfo)
    if verts:

      for v in verts:
        attrdata= get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))
        attrdata[1]= value

        v[jinfo.layer_nodes]= bytes(compose_node_data_raw(attrdata), 'utf-8')

# get most used prefix in current selection
def get_selection_prefix(jinfo):

  verts= get_all_vert_raw(jinfo)

  if verts:

    prefix_list= [get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))[1] for v in verts]
    prefix_set = set(prefix_list)

    prefix_count= dict((e, prefix_list.count(e)) for e in prefix_set)
    key= max(prefix_count, key=lambda k: prefix_count[k])
    return key

  return None

# set selection numerals
def set_selection_numerals(jinfo, values):
  view3d_redraw_all(bpy.context)

  verts= get_all_vert_raw(jinfo)
  if verts:

    for i in range(len(verts)):
      v= verts[i]
      attrdata= get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))
      attrdata[2]= values[i]

      v[jinfo.layer_nodes]= bytes(compose_node_data_raw(attrdata), 'utf-8')

# get selection numerals
def get_selection_numerals(jinfo):

  verts= get_all_vert_raw(jinfo)
  values= []

  if verts:

    values= [get_number_safe(get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))[2]) for v in verts]

  return values

# set selection side
def set_selection_side(jinfo, values):
  view3d_redraw_all(bpy.context)

  verts= get_all_vert_raw(jinfo)
  if verts:

    for i in range(len(verts)):
      v= verts[i]
      attrdata= get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))
      attrdata[3]= values[i]

      v[jinfo.layer_nodes]= bytes(compose_node_data_raw(attrdata), 'utf-8')

# get selection side
def get_selection_side(jinfo):

  verts= get_all_vert_raw(jinfo)
  values= []

  if verts:

    values= [get_node_data_from_attribute(str(v[jinfo.layer_nodes], 'utf-8'))[3] for v in verts]

  return values