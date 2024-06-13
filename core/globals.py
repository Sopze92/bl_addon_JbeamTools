import gpu

from gpu.types import GPUVertFormat

class JBEAMTOOLS_globals():
  
  active_object_tracker_running= False

  jbeam_nodevis_renderer_running= False
  jbeam_beamvis_renderer_running= False

  selection_vert= False
  selection_edge= False

  flat_shader= gpu.shader.from_builtin('FLAT_COLOR')
  smooth_shader= gpu.shader.from_builtin('SMOOTH_COLOR')

  flat_shader_vertformat = GPUVertFormat()
  flat_shader_vertformat.attr_add(id='pos',    comp_type='F32',  len=3,  fetch_mode='FLOAT')
  flat_shader_vertformat.attr_add(id='color',  comp_type='F32',  len=4,  fetch_mode='FLOAT')

  icons= {}

__GLOBALS__= JBEAMTOOLS_globals()
