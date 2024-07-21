
from .. import utils
from ..core.globals import __GLOBALS__
from ..core import const as __CONSTANTS__

import bpy, gpu, blf, bmesh, mathutils
from gpu_extras.batch import batch_for_shader

from gpu.types import GPUBatch, GPUVertBuf, GPUUniformBuf

from bpy_extras.view3d_utils import location_3d_to_region_2d

#
# ---------------------------------------------------------------- HELPERS
# 

class VisualizerData():
  region= None
  rv3d= None
  bm= None
  jinfo= None

vis_data= VisualizerData()

def update_visualizer_data(context):
  global vis_data

  vis_data.region, vis_data.rv3d = utils.view3d_get(context)

  if not vis_data.region or not vis_data.rv3d: return False
  if context.object.mode != 'OBJECT' and context.object.mode != 'EDIT': return False
    
  obj = context.active_object
  if not utils.is_object_mesh(obj) or not utils.is_object_jbeam(obj) or not obj.select_get(): return False

  vis_data.bm= utils.get_active_object_bmesh(context).copy()
  vis_data.jinfo= utils.create_jbeam_info(vis_data.bm)
  return True

def get_color(basecol):
  return (basecol, [v*2+.75 for v in basecol], [1,1,1,1])

def split_vert_selection(verts):

  global vis_data
  select, active= utils.get_vert_selection(vis_data.jinfo)
  verts= [v for v in verts if not v in vis_data.jinfo.select_verts]

  return verts, select, active

def split_edge_selection(edges):

  global vis_data
  select, active= utils.get_edge_selection(vis_data.jinfo)
  edges= [e for e in edges if not e in vis_data.jinfo.select_edges]

  return edges, select, active

#
# ---------------------------------------------------------------- NODE VIS
# 

def _render_node_points(zmode, size, buf_pos, buf_color):
  
  gpu.state.point_size_set(size)
  gpu.state.depth_mask_set(False)
  gpu.state.blend_set('ALPHA')
  gpu.state.depth_test_set('ALWAYS' if zmode == 0 else 'LESS_EQUAL')

  vert_buf= GPUVertBuf(__GLOBALS__.flat_shader_vertformat, len(buf_pos))
  vert_buf.attr_fill('pos', buf_pos)
  vert_buf.attr_fill('color', buf_color)

  batch= GPUBatch(type='POINTS', buf=vert_buf)
  batch.draw(__GLOBALS__.flat_shader)

  if zmode == 2:

    buf_color_b= []

    for j in range(len(buf_color)):
      lcolor_b= [*buf_color[j]]
      lcolor_b[0]*=.625
      lcolor_b[1]*=.625
      lcolor_b[2]*=.625
      lcolor_b[3]*=.25
      buf_color_b.append(lcolor_b)
  
    gpu.state.depth_test_set('GREATER')

    vert_buf= GPUVertBuf(__GLOBALS__.flat_shader_vertformat, len(buf_pos))
    vert_buf.attr_fill('pos', buf_pos)
    vert_buf.attr_fill('color', buf_color_b)

    batch= GPUBatch(type='POINTS', buf=vert_buf)
    batch.draw(__GLOBALS__.flat_shader)

def draw_nodevis(context):
  
  jbtools= context.scene.jbtools
  if not __GLOBALS__.jbeam_nodevis_renderer_running or not 'P' in jbtools.jbeam_nodevis_mode: return
  if not update_visualizer_data(context): return
  
  global vis_data
  _render_color= 'C' in jbtools.jbeam_nodevis_mode

  matrix= bpy.context.object.matrix_world

  edges= [*vis_data.bm.edges]
  verts= [*vis_data.bm.verts]
  for v in verts: 
    v.co= matrix @ v.co

  # setup POINTS
  psize_base= jbtools.jbeam_nodevis_size

  psize= [
    psize_base,
    psize_base*1.2 + 3
  ]

  v_normal, v_select, v_active= split_vert_selection(verts)
  node_color_default= get_color(jbtools.jbeam_nodevis_color)

  #point_color= [
  #  pcolor,
  #]

  buf_pos= []
  buf_color= []
    
  zmode= jbtools.jbeam_nodevis_ztest

  # render
  for v in v_normal:
    buf_pos.append(v.co)
    buf_color.append(node_color_default[0])

  _render_node_points(zmode, psize[0], buf_pos, buf_color)
  
  if v_select or v_active:
  
    buf_pos= []
    buf_color= []

    if v_select:
      for v in v_select:
        buf_pos.append(v.co)
        buf_color.append(node_color_default[1])

    if v_active:
      buf_pos.append(v_active.co)
      buf_color.append(node_color_default[2])

    _render_node_points(zmode, psize[1], buf_pos, buf_color)

#
# ---------------------------------------------------------------- NODE TEXT VIS
# 

def draw_nodetextvis(context):
  
  jbtools= context.scene.jbtools
  if not __GLOBALS__.jbeam_nodevis_renderer_running or not 'T' in jbtools.jbeam_nodevis_mode: return
  if not update_visualizer_data(context): return
  
  global vis_data
  _render_color= 'C' in jbtools.jbeam_nodevis_mode

  matrix= bpy.context.object.matrix_world
  view_matrix= vis_data.rv3d.view_matrix

  verts= vis_data.bm.verts
  for v in verts: 
    v.co= matrix @ v.co

  verts.sort(key= lambda v: (view_matrix @ v.co)[2] )
  
  # setup TEXT
  bgcolor= jbtools.jbeam_nodetextvis_bgcolor
  fgcolor= jbtools.jbeam_nodetextvis_fgcolor
  
  blf.color(1, *fgcolor)

  fsize= jbtools.jbeam_nodetextvis_size
  blf.size(1, fsize)
  chw, chh= blf.dimensions(1, "x")
  chh+=4

  text_bg_verts= [ 0,0,0,0,0,0 ]
  text_bg_color= [
    bgcolor,
    bgcolor,
    bgcolor,
    bgcolor,
    bgcolor,
    bgcolor
  ]

  draw_bg= bgcolor[3] > .0
    
  # create render buffers
  for v in verts:

    npos= location_3d_to_region_2d(vis_data.region, vis_data.rv3d, v.co)

    if npos:
        
      tpos= ( npos[0]+6, npos[1]+4, 0 )

      blf.position(1, *tpos)
      label= utils.get_node_data_from_attribute(str(v[vis_data.jinfo.layer_nodes], 'utf-8'))[0]
      #label= str(v[vis_data.jinfo.layer_nodes], 'utf-8')

      if draw_bg:
        x, y, z= tpos
        w= chw*len(label)+4

        text_bg_verts[0]= text_bg_verts[5]= (x-4,   y-2)
        text_bg_verts[1]= (x+w,   y-2)
        text_bg_verts[2]= text_bg_verts[3]= (x+w,   y+chh)
        text_bg_verts[4]= (x-4,   y+chh)

        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')
        batch= batch_for_shader(__GLOBALS__.flat_shader, 'TRIS', {"pos": text_bg_verts, "color": text_bg_color})
        batch.draw(__GLOBALS__.flat_shader)

      blf.draw(1, label)

#
# ---------------------------------------------------------------- BEAM VIS
# 

def _render_beam_lines(zmode, size, buf_pos, buf_color):
        
  gpu.state.line_width_set(size)
  gpu.state.depth_mask_set(False)
  gpu.state.blend_set('ALPHA')
  gpu.state.depth_test_set('ALWAYS' if zmode == 0 else 'LESS_EQUAL')

  vert_buf= GPUVertBuf(__GLOBALS__.flat_shader_vertformat, len(buf_pos))
  vert_buf.attr_fill('pos', buf_pos)
  vert_buf.attr_fill('color', buf_color)

  batch= GPUBatch(type='LINES', buf=vert_buf)
  batch.draw(__GLOBALS__.smooth_shader)

  if zmode == 2:

    # create colors for behind part
    buf_color_b= []

    for j in range(len(buf_color)):
      lcolor_b= [*buf_color[j]]
      lcolor_b[0]*=.75
      lcolor_b[1]*=.75
      lcolor_b[2]*=.75
      lcolor_b[3]*=.25
      buf_color_b.append(lcolor_b)
  
    gpu.state.depth_test_set('GREATER')

    vert_buf= GPUVertBuf(__GLOBALS__.flat_shader_vertformat, len(buf_pos))
    vert_buf.attr_fill('pos', buf_pos)
    vert_buf.attr_fill('color', buf_color_b)

    batch= GPUBatch(type='LINES', buf=vert_buf)
    batch.draw(__GLOBALS__.smooth_shader)

def draw_beamvis(context):

  jbtools= context.scene.jbtools
  if not __GLOBALS__.jbeam_beamvis_renderer_running or not 'L' in jbtools.jbeam_beamvis_mode: return
  if not update_visualizer_data(context): return
  
  global vis_data
  _render_color= 'C' in jbtools.jbeam_beamvis_mode

  matrix= bpy.context.object.matrix_world

  edges= [*vis_data.bm.edges]
  verts= [*vis_data.bm.verts]
  for e in verts:
    e.co= matrix @ e.co

  # setup LINES
  lsize_base= jbtools.jbeam_beamvis_size

  lsize= (
    lsize_base,
    lsize_base*1.2 + 3
  )

  e_normal, e_select, e_active= split_edge_selection(edges)

  basecolor= get_color(jbtools.jbeam_beamvis_color)

  beam_color_default= (
    basecolor[0],
    basecolor[0]
  )

  buf_pos= []
  buf_color= []
    
  zmode= jbtools.jbeam_nodevis_ztest

  # render
  for e in e_normal:
    
    buf_pos.extend([v.co for v in e.verts])
    buf_color.extend(beam_color_default)

  _render_beam_lines(zmode, lsize[0], buf_pos, buf_color)

  if e_select or e_active:

    buf_pos= []
    buf_color= []
    
    beam_color= (
      basecolor[1],
      basecolor[1]
    )

    if e_select:
      for e in e_select:
        
        buf_pos.extend([v.co for v in e.verts])
        buf_color.extend(beam_color)

    if e_active:
      buf_pos.extend([v.co for v in e_active.verts])
      buf_color.extend((basecolor[2], basecolor[2]))
      
    _render_beam_lines(zmode, lsize[1], buf_pos, buf_color)
#
# ---------------------------------------------------------------- BEAM TEXT VIS
# 

def draw_beamtextvis(context):

  jbtools= context.scene.jbtools
  if not __GLOBALS__.jbeam_beamvis_renderer_running or not 'T' in jbtools.jbeam_beamvis_mode: return
  if not update_visualizer_data(context): return
  
  global vis_data
  _render_color= 'C' in jbtools.jbeam_beamvis_mode
