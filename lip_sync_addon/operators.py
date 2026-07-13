import bpy
from . import properties as props
from . import lip_sync_core as core


class HIPPO_LIPSYNC_OT_init_mapping(bpy.types.Operator):
    """Initialize the lip sync mapping table on the active mesh."""

    bl_idname = "hippo_lipsync.init_mapping"
    bl_label = "Init Mapping"
    bl_description = "Create an empty mapping table (A-K) on the selected mesh"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

    def execute(self, context):
        obj = context.active_object
        props.init_lip_sync_map(obj.data)
        self.report({'INFO'}, "Lip sync mapping initialised")
        return {'FINISHED'}


class HIPPO_LIPSYNC_OT_clear_mapping(bpy.types.Operator):
    """Clear all phoneme-to-shape-key mapping entries."""

    bl_idname = "hippo_lipsync.clear_mapping"
    bl_label = "Clear Mapping"
    bl_description = "Reset all mapping entries to empty"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        props.clear_lip_sync_map(obj.data)
        self.report({'INFO'}, "Mapping cleared")
        return {'FINISHED'}


class HIPPO_LIPSYNC_OT_select_file(bpy.types.Operator):
    """Open a file browser to choose a lip sync file (JSON or TSV)."""

    bl_idname = "hippo_lipsync.select_file"
    bl_label = "Browse File"
    bl_description = "Select a lip-sync file (Rhubarb JSON or Cherry TSV)"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore

    filter_glob: bpy.props.StringProperty(
        default="*.json;*.tsv",
        options={'HIDDEN'},
    )  # type: ignore

    def execute(self, context):
        context.scene.lipsync.json_file_path = self.filepath
        ext = self.filepath.split('.')[-1].upper()
        self.report({'INFO'}, f"File selected: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class HIPPO_LIPSYNC_OT_apply_lip_sync(bpy.types.Operator):
    """Parse the selected file and write shape-key keyframes to the timeline."""

    bl_idname = "hippo_lipsync.apply_lip_sync"
    bl_label = "Apply to Timeline"
    bl_description = "Read the lip sync file (JSON or TSV), compute keyframes, and apply to shape keys"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return False
        if not context.scene.lipsync.json_file_path:
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        scene = context.scene

        # ── Read mapping ───────────────────────────────────────────────
        mapping = props.get_lip_sync_map(obj.data)
        # Allow operation even if some mappings are missing — only skip if ALL are empty
        if not any(mapping.values()):
            self.report(
                {'WARNING'}, "No mappings set. Please configure the mapping table first.")
            return {'CANCELLED'}

        # ── Parse file (auto-detect JSON or TSV) ───────────────────────
        file_path = scene.lipsync.json_file_path
        try:
            mouth_cues = core.parse_lip_sync_file(file_path)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to parse file: {e}")
            return {'CANCELLED'}

        if not mouth_cues:
            self.report({'WARNING'}, "No mouth cues found in the file")
            return {'CANCELLED'}

        # ── Apply ──────────────────────────────────────────────────────
        core.apply_lip_sync_to_mesh(obj, mouth_cues, mapping)

        non_x_count = len([c for c in mouth_cues if c.get('value') != 'X'])
        self.report({'INFO'}, f"Lip sync applied ({non_x_count} non-X cues)")
        return {'FINISHED'}


class HIPPO_LIPSYNC_OT_clear_animation(bpy.types.Operator):
    """Remove all shape-key f-curves from the active mesh."""

    bl_idname = "hippo_lipsync.clear_animation"
    bl_label = "Clear Animation"
    bl_description = "Delete all shape-key animation keyframes"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        core.clear_shape_key_animation(obj)
        self.report({'INFO'}, "Shape key animation cleared")
        return {'FINISHED'}


# ── Registration ───────────────────────────────────────────────────────────

classes = [
    HIPPO_LIPSYNC_OT_init_mapping,
    HIPPO_LIPSYNC_OT_clear_mapping,
    HIPPO_LIPSYNC_OT_select_file,
    HIPPO_LIPSYNC_OT_apply_lip_sync,
    HIPPO_LIPSYNC_OT_clear_animation,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
