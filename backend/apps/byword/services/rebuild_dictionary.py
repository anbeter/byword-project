from apps.byword.models import Music, LessonText, DictionaryOccurrence
from apps.byword.services.dictionary import sync_dictionary


def rebuild_dictionary():
    print("Cleaning occurrences...")
    DictionaryOccurrence.objects.all().delete()

    print("Rebuilding from Music...")
    for obj in Music.objects.all():
        sync_dictionary(
            instance=obj,
            new_text=obj.lyrics,
            old_text=None,
            origin="music",
            number_lesson=obj.number_lesson,
        )

    print("Rebuilding from LessonText...")
    for obj in LessonText.objects.all():
        sync_dictionary(
            instance=obj,
            new_text=obj.text,
            old_text=None,
            origin="lesson_text",
            number_lesson=obj.number_lesson,
        )

    print("Done!")