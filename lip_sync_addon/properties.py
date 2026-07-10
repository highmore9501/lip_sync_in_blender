import bpy

PHONEMES = ["A", "B", "C", "D", "E", "F", "G", "H"]


class LipSyncMappingProps(bpy.types.PropertyGroup):
    """Mapping from phoneme to shape key name, stored on mesh data."""

    mapping_A: bpy.props.StringProperty(name="A", default="")
    mapping_B: bpy.props.StringProperty(name="B", default="")
    mapping_C: bpy.props.StringProperty(name="C", default="")
    mapping_D: bpy.props.StringProperty(name="D", default="")
    mapping_E: bpy.props.StringProperty(name="E", default="")
    mapping_F: bpy.props.StringProperty(name="F", default="")
    mapping_G: bpy.props.StringProperty(name="G", default="")
    mapping_H: bpy.props.StringProperty(name="H", default="")

    def get_mapping_dict(self):
        """Return {phoneme: shape_key_name} dict."""
        return {
            "A": self.mapping_A,
            "B": self.mapping_B,
            "C": self.mapping_C,
            "D": self.mapping_D,
            "E": self.mapping_E,
            "F": self.mapping_F,
            "G": self.mapping_G,
            "H": self.mapping_H,
        }

    def set_from_dict(self, mapping_dict):
        """Set all mappings from a {phoneme: shape_key_name} dict."""
        for p in PHONEMES:
            setattr(self, f"mapping_{p}", mapping_dict.get(p, ""))


class LipSyncSceneProps(bpy.types.PropertyGroup):
    """Scene-level properties for the plugin."""

    json_file_path: bpy.props.StringProperty(
        name="JSON File",
        description="Path to Rhubarb lip sync JSON file",
        subtype='FILE_PATH',
        default="",
    )
    use_vse_offset: bpy.props.BoolProperty(
        name="Use VSE Audio Offset",
        description="Auto-detect frame offset from the first audio strip in the VSE",
        default=True,
    )


# ── Utility functions ──────────────────────────────────────────────────────


def init_lip_sync_map(mesh_data):
    """Initialize the lip_sync mapping table on mesh data (A-H all empty)."""
    if not hasattr(mesh_data, 'lipsync_mapping') or mesh_data.lipsync_mapping is None:
        mesh_data.lipsync_mapping = mesh_data.lipsync_mapping.__class__()
    for p in PHONEMES:
        setattr(mesh_data.lipsync_mapping, f"mapping_{p}", "")


def get_lip_sync_map(mesh_data):
    """Get the mapping dict {phoneme: shape_key_name} from mesh data."""
    if hasattr(mesh_data, 'lipsync_mapping') and mesh_data.lipsync_mapping is not None:
        return mesh_data.lipsync_mapping.get_mapping_dict()
    return {}


def set_mapping(mesh_data, phoneme, shape_key_name):
    """Set a single phoneme → shape_key mapping entry."""
    if phoneme in PHONEMES and hasattr(mesh_data, 'lipsync_mapping'):
        setattr(mesh_data.lipsync_mapping,
                f"mapping_{phoneme}", shape_key_name)


def get_shape_key_list(mesh_data):
    """Return a list of shape key names available on the mesh."""
    if mesh_data.shape_keys and mesh_data.shape_keys.key_blocks:
        return [kb.name for kb in mesh_data.shape_keys.key_blocks]
    return []


def clear_lip_sync_map(mesh_data):
    """Clear all mapping entries (reset to empty strings)."""
    init_lip_sync_map(mesh_data)


# ── Registration ───────────────────────────────────────────────────────────

classes = [LipSyncMappingProps, LipSyncSceneProps]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Mesh.lipsync_mapping = bpy.props.PointerProperty(
        type=LipSyncMappingProps
    )
    bpy.types.Scene.lipsync = bpy.props.PointerProperty(type=LipSyncSceneProps)


def unregister():
    del bpy.types.Mesh.lipsync_mapping
    del bpy.types.Scene.lipsync
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
