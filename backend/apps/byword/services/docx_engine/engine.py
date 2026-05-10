from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from apps.byword.services.docx_engine.registry import DOCX_RENDERERS
from apps.byword.models import Dictionary

from apps.byword.services.docx_activity import (
    add_subtitle,
)
from apps.byword.services.docx_engine.transforms import (
    DOCX_TRANSFORMS,
)

def generate_activity_docx_v2(activity):
    print(DOCX_RENDERERS)
    doc = Document()
    lesson = activity.lesson
    title = doc.add_heading(
        f"Lesson {lesson.number} - {lesson.name}",
        level=1
    )
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for item in activity.items.order_by("order"):
        model = item.content_type.model_class()
        
        if model == Dictionary:
            queryset = (
                model.objects
                .filter(
                    occurrences__lesson=lesson
                )
                .distinct()
            )
        else:
            queryset = model.objects.filter(
                lesson=lesson
            )


        if not queryset.exists():
            continue
        # subtitle = getattr(
        #     model,
        #     "docx_subtitle",
        #     None
        # )
        # if subtitle:
        #     add_subtitle(doc, subtitle)
        model_subtitle = getattr(
            model,
            "docx_subtitle",
            None
        )
        if model == Dictionary:
            renderer = DOCX_RENDERERS[
                "dictionary_table"
            ]
            renderer(
                doc,
                queryset,
                {}
            )
            continue


        for obj in queryset:
            subtitle = getattr(
                obj,
                "subtitle",
                model_subtitle
            )
            if subtitle:
                add_subtitle(
                    doc,
                    subtitle
                )

            for field_config in model.docx_fields:
                field_name = field_config["field"]
                # renderer_name = field_config["type"]
                renderer_name = field_config["renderer"]
                # value = getattr(
                #     obj,
                #     field_name,
                #     None
                # )
                if field_name == "__object__":
                    value = obj
                else:
                    value = getattr(
                        obj,
                        field_name,
                        None
                    )

                transform_name = field_config.get(
                    "transform"
                )
                if transform_name:
                    transform_function = DOCX_TRANSFORMS[
                        transform_name
                    ]
                    value = transform_function(value)
                print("*******************************")
                print("RENDERERS:", DOCX_RENDERERS.keys())
                print("RENDERER_NAME:", renderer_name)
                print("2222222222222222222*************")
                renderer = DOCX_RENDERERS[
                    renderer_name
                ]
                renderer(
                    doc,
                    value,
                    field_config
                )
    return doc