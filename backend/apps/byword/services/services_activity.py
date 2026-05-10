from django.contrib.contenttypes.models import ContentType

from apps.byword.models import (
    Activity,
    ActivityItem,
    Dictionary,
    ScrambleWord,
    WordSearch,
    Music,
    CompleteTheSentence,
)


def create_default_activity(lesson):
    activity = Activity.objects.create(lesson=lesson)

    defaults = [
        (Dictionary, 1),
        (ScrambleWord, 2),
        (WordSearch, 3),
        (CompleteTheSentence, 4)
        (Music, 7),
    ]

    for model_class, order in defaults:
        content_type = ContentType.objects.get_for_model(model_class)

        ActivityItem.objects.create(
            activity=activity,
            order=order,
            content_type=content_type,
        )

    return activity