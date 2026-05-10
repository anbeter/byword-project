from django.core.exceptions import ValidationError


def validate_image_extension(value):
    valid_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
    ]
    file_name = value.name.lower()
    if not any(
        file_name.endswith(ext)
        for ext in valid_extensions
    ):
        raise ValidationError(
            "Only JPG, JPEG and PNG files are allowed."
        )