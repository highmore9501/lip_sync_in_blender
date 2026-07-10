import json
import bpy


# ── Utility functions ──────────────────────────────────────────────────────


def parse_lip_sync_json(json_path):
    """Parse a Rhubarb lip sync JSON file and return the mouthCues list.

    Each cue has the shape: {"start": float, "end": float, "value": str}.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('mouthCues', [])


def get_scene_fps(scene):
    """Return the effective FPS from the scene settings."""
    return scene.render.fps / scene.render.fps_base


def _calc_change_duration(start, end):
    """Compute change_duration = (end - start) / 3, capped at 0.5 s."""
    duration = (end - start) / 3.0
    return min(duration, 0.5)


# ── Core apply function ────────────────────────────────────────────────────


def apply_lip_sync_to_mesh(mesh_obj, mouth_cues, mapping, audio_offset=0):
    """Apply mouth-cue data to a mesh's shape keys by inserting keyframes.

    Args:
        mesh_obj:      The Blender mesh object (must have shape keys).
        mouth_cues:    List of dicts [{start, end, value}, ...].
        mapping:       Dict {phoneme: shape_key_name} (A-H → shape key).
        audio_offset:  Optional global frame offset (default 0).
    """
    if not mesh_obj.data.shape_keys:
        return

    scene = bpy.context.scene
    fps = get_scene_fps(scene)
    key_blocks = mesh_obj.data.shape_keys.key_blocks

    # ── Step 1: filter out X cues ──────────────────────────────────────
    non_x_cues = [c for c in mouth_cues if c.get('value') != 'X']
    if not non_x_cues:
        return

    # ── Step 2: pre-compute change_duration for each cue ───────────────
    for cue in non_x_cues:
        cue['_change_duration'] = _calc_change_duration(
            cue['start'], cue['end'])

    # ── Step 3: temporarily disable auto-keyframe ──────────────────────
    use_auto_key = scene.tool_settings.use_keyframe_insert_auto
    scene.tool_settings.use_keyframe_insert_auto = False

    # ── Step 4: iterate cues and insert keyframes ──────────────────────
    for i, cue in enumerate(non_x_cues):
        phoneme = cue['value']
        shape_key_name = mapping.get(phoneme, '')
        if not shape_key_name or shape_key_name not in key_blocks:
            continue

        start = cue['start']
        end = cue['end']
        change_dur = cue['_change_duration']

        # Determine the next cue's change_duration for fade-out
        if i + 1 < len(non_x_cues):
            next_change_dur = non_x_cues[i + 1]['_change_duration']
        else:
            next_change_dur = change_dur  # last cue uses its own

        keyblock = key_blocks[shape_key_name]

        # Frame 1 — fade-in start (value = 0.0)
        t1 = max(0.0, start - change_dur)
        f1 = int(t1 * fps) + audio_offset
        keyblock.value = 0.0
        keyblock.keyframe_insert(data_path='value', frame=f1)

        # Frame 2 — fade-in complete / hold start (value = 1.0)
        f2 = int(start * fps) + audio_offset
        keyblock.value = 1.0
        keyblock.keyframe_insert(data_path='value', frame=f2)

        # Frame 3 — hold end (value = 1.0)
        f3 = int(end * fps) + audio_offset
        keyblock.value = 1.0
        keyblock.keyframe_insert(data_path='value', frame=f3)

        # Frame 4 — fade-out complete (value = 0.0)
        t4 = end + next_change_dur
        f4 = int(t4 * fps) + audio_offset
        keyblock.value = 0.0
        keyblock.keyframe_insert(data_path='value', frame=f4)

    # ── Step 5: restore auto-keyframe setting ──────────────────────────
    scene.tool_settings.use_keyframe_insert_auto = use_auto_key


# ── Helper functions ───────────────────────────────────────────────────────


def clear_shape_key_animation(mesh_obj):
    """Remove all f-curves from the shape-key animation data."""
    if not mesh_obj.data.shape_keys:
        return
    sk = mesh_obj.data.shape_keys
    if sk.animation_data and sk.animation_data.action:
        sk.animation_data.action.fcurves.clear()
