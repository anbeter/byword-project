from apps.byword.models import Dictionary

from apps.byword.services.syllables import (
    separate_syllables,
)

from apps.byword.services.pronunciation import (
    fetch_pronunciation,
)


def fill_dictionary_data():
    not_found = []

    queryset = Dictionary.objects.all()

    for obj in queryset:

        changed = False

        if not obj.syllable_separation:
            syllables = separate_syllables(obj.verb_en)

            if syllables:
                obj.syllable_separation = syllables
                changed = True

        if not obj.pronunciation:
            pronunciation = fetch_pronunciation(
                obj.verb_en
            )

            if pronunciation:
                obj.pronunciation = pronunciation
                changed = True
            else:
                not_found.append(obj.verb_en)

        if changed:
            obj.save()

    return not_found