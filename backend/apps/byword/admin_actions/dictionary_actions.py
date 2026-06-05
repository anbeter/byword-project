from django.contrib import messages

from apps.byword.services.syllables import (
    separate_syllables,
)

from apps.byword.services.pronunciation import (
    fetch_pronunciation,
)

from apps.byword.services.tts import (
    generate_pronunciation_audio,
)

def fill_syllable_separation(
    modeladmin,
    request,
    queryset
):
    updated = 0
    not_found = []

    for obj in queryset:

        if obj.syllable_separation:
            continue

        try:
            syllables = separate_syllables(
                obj.verb_en
            )

            if syllables:
                obj.syllable_separation = syllables

                obj.save(update_fields=[
                    "syllable_separation"
                ])

                updated += 1

            else:
                not_found.append(obj.verb_en)

        except Exception:
            not_found.append(obj.verb_en)

    if not_found:
        modeladmin.message_user(
            request,
            f"Not found: {', '.join(not_found)}",
            level=messages.WARNING
        )

    modeladmin.message_user(
        request,
        f"{updated} syllable separations updated.",
        level=messages.SUCCESS
    )


fill_syllable_separation.short_description = (
    "Fill syllable separation"
)


def fill_pronunciation(
    modeladmin,
    request,
    queryset
):
    updated = 0
    not_found = []

    for obj in queryset:

        if obj.pronunciation:
            continue

        try:
            pronunciation = fetch_pronunciation(
                obj.verb_en
            )

            if pronunciation:
                obj.pronunciation = pronunciation

                obj.save(update_fields=[
                    "pronunciation"
                ])

                updated += 1

            else:
                not_found.append(obj.verb_en)

        except Exception:
            not_found.append(obj.verb_en)

    if not_found:
        modeladmin.message_user(
            request,
            f"Not found: {', '.join(not_found)}",
            level=messages.WARNING
        )

    modeladmin.message_user(
        request,
        f"{updated} pronunciations updated.",
        level=messages.SUCCESS
    )


fill_pronunciation.short_description = (
    "Fill pronunciation"
)


def generate_audio(modeladmin,request,queryset):
    updated = 0
    not_found = []

    for obj in queryset:
        try:
            result = (
                generate_pronunciation_audio(
                    obj
                )
            )
            if result:
                updated += 1
            else:
                not_found.append(
                    obj.verb_en
                )
        except Exception:
            not_found.append(
                obj.verb_en
            )

    if not_found:
        modeladmin.message_user(
            request,
            f"Not found: {', '.join(not_found)}",
            level=messages.WARNING
        )

    modeladmin.message_user(
        request,
        f"{updated} audios generated.",
        level=messages.SUCCESS
    )