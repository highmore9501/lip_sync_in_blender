# Hippo's Lip Sync - Blender Addon
# A plugin to import Rhubarb Lip Sync JSON and drive mesh shape keys

from . import panels
from . import operators
from . import lip_sync_core
from . import properties
import importlib
bl_info = {
    "name": "Hippo's Lip Sync",
    "author": "Hippo",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "3D View > Sidebar > Hippo's Lip Sync",
    "description": "Import Rhubarb lip sync JSON and drive mesh shape keys",
    "category": "Animation",
}


modules = [properties, lip_sync_core, operators, panels]


def register():
    for mod in modules:
        importlib.reload(mod)
        if hasattr(mod, 'register'):
            mod.register()


def unregister():
    for mod in reversed(modules):
        if hasattr(mod, 'unregister'):
            mod.unregister()


if __name__ == "__main__":
    register()
