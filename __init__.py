bl_info = {
  "name": "Sopze's Jbeam Tools",
  "description": "few Jbeam tools to make working with Jbeams less tedious.",
  "author": "Sergio 'Sopze' del Pino",
  "version": (0, 1, 0),
  "blender": (4, 0, 0),
  "location": "3D View > Toolbox",
  "category": "Modding"
}

import bpy

def register():
  from . import ops, props, ui
  ops.register()
  props.register()
  ui.register()

def unregister():
  from . import ops, props, ui
  ops.unregister()
  props.unregister()
  ui.unregister()

if __name__ == '__main__':
  register()
