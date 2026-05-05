

def format_lesson_title(lesson):
    if not lesson:
        return None
    return f"{lesson.number} - {lesson.name}"