def create_default_activity(lesson):
    activity = Activity.objects.create(lesson=lesson)

    defaults = [
        ("dictionary", 1),
        ("scramble", 2),
        ("wordsearch", 3),
    ]

    for item_type, order in defaults:
        ActivityItem.objects.create(
            activity=activity,
            type=item_type,
            order=order,
            content_type=None,
            object_id=None
        )

    return activity