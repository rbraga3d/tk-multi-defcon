import maya.cmds as cmds
import sgtk


def resolve_image_file_prefix(engine, image_file_prefix):
    context = engine.context

    if context.entity["type"] == "Asset":
        # Replace {Shot} token with {Asset} token and
        # remove {Sequence} token, if context is Asset.
        tmp_string = image_file_prefix.replace("{Sequence}", "").replace("__", "_")
        tmp_string = tmp_string.replace("{Shot}", "{Asset}")

        image_file_prefix = tmp_string


    keys = {
        "Project": sgtk.StringKey("Project"),
        "Step": sgtk.StringKey("Step"),
        "Sequence": sgtk.StringKey("Sequence"),
        "Shot": sgtk.StringKey("Shot"),
        "Asset": sgtk.StringKey("Asset"),
        "sg_asset_type": sgtk.StringKey("sg_asset_type"),
        "version": sgtk.IntegerKey("version", format_spec="03")
    }


    work_file_path = cmds.file(query=True, sn=True)
    work_file_norm_path = sgtk.util.ShotgunPath.normalize(work_file_path)
    work_template_path = engine.sgtk.template_from_path(work_file_norm_path)
    work_file_fields = work_template_path.get_fields(work_file_norm_path)


    fields = {
        "Project": context.project.get('name'),
        "Step": context.step.get("name"),
        "Sequence": work_file_fields.get("Sequence"),
        "Shot": work_file_fields.get("Shot"),
        "Asset": work_file_fields.get("Asset", ""),
        "sg_asset_type": work_file_fields.get("sg_asset_type"),
        "version": work_file_fields.get("version")

    }

    

    template = sgtk.TemplateString(image_file_prefix, keys)

    resolved_image_file_prefix = template.apply_fields(fields)
    return resolved_image_file_prefix


    
