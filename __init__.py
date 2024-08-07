bl_info = {
  "name": "Sopze's Jbeam Tools",
  "description": "A few Jbeam tools to make working with Nodes/Beams less tedious.",
  "author": "Sergio 'Sopze' del Pino",
  "version": (0, 2, 0),
  "blender": (4, 0, 0),
  "location": "3D View > Toolbox",
  "category": "Util"
}

from .ops import ops
from .core import globals
from . import props
from .ui import ui

def register():
  ops.register()
  props.register()
  ui.register()

def unregister():
  ops.unregister()
  props.unregister()
  ui.unregister()

  del globals.__GLOBALS__

if __name__ == '__main__':
  register()
