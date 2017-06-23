import os
import shutil


def rename_file(instance, field_name, new_name, allow_missing_file=False):
    field = getattr(instance, field_name)
    current_name, extension = os.path.splitext(field.name)

    new_name_with_extension = '{}{}'.format(new_name, extension)
    try:
        shutil.move(field.path, new_name_with_extension)
    except FileNotFoundError:
        if not allow_missing_file:
            raise
        print('Skipped missing file', field.path)
    initial_path = os.path.dirname(field.name)
    field.name = os.path.join(initial_path, new_name_with_extension)
    instance.save()
    return new_name_with_extension
