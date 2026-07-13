import bpy
from . import properties as props


class HIPPO_LIPSYNC_PT_main_panel(bpy.types.Panel):
    """Main UI panel for Hippo's Lip Sync in the 3D view sidebar."""

    bl_label = "Hippo's Lip Sync"
    bl_idname = "HIPPO_LIPSYNC_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hippo's Lip Sync"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # ── Header ─────────────────────────────────────────────────────
        if obj.type == 'MESH':
            row = layout.row()
            row.label(text="Target:", icon='MESH_DATA')
            row.label(text=obj.name)
        else:
            layout.label(text="Select a mesh object", icon='ERROR')
            return

        # ── Initialise / Clear mapping ─────────────────────────────────
        row = layout.row(align=True)
        row.operator("hippo_lipsync.init_mapping",
                     text="Init Mapping", icon='ADD')
        row.operator("hippo_lipsync.clear_mapping", text="Clear", icon='X')

        # ── Mapping table ──────────────────────────────────────────────
        has_mapping = (
            hasattr(obj.data, 'lipsync_mapping')
            and obj.data.lipsync_mapping is not None
        )

        if has_mapping:
            layout.separator()
            layout.label(text="Phoneme Mapping:",
                         icon='SHAPEKEY_DATA')

            mapping = obj.data.lipsync_mapping

            if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
                for phoneme in props.PHONEMES:
                    row = layout.row(align=True)
                    row.label(text=f"  {phoneme}")
                    prop_name = f"mapping_{phoneme}"
                    row.prop_search(
                        mapping,
                        prop_name,
                        obj.data.shape_keys,
                        "key_blocks",
                        text="",
                    )
            else:
                layout.label(text="No shape keys on this mesh", icon='ERROR')

            layout.separator()
            layout.label(text="X (silence) is auto-skipped", icon='INFO')

        # ── Generate section ───────────────────────────────────────────
        layout.separator()
        layout.separator()
        layout.label(text="Generate Lip Sync:", icon='ACTION')

        scene = context.scene
        lipsync = scene.lipsync

        layout.prop(lipsync, "json_file_path", text="")

        row = layout.row(align=True)
        row.operator("hippo_lipsync.select_file",
                     text="Browse File (JSON/TSV)", icon='FILE_FOLDER')
        row.operator("hippo_lipsync.clear_animation",
                     text="Clear", icon='TRASH')

        row = layout.row(align=True)
        row.operator("hippo_lipsync.apply_lip_sync",
                     text="Apply to Timeline", icon='PLAY')


# ── Registration ───────────────────────────────────────────────────────────

classes = [HIPPO_LIPSYNC_PT_main_panel]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
