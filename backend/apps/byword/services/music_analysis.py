import re
from apps.byword.models import Lesson, Dictionary

MAX_NEW_WORDS = 7


def normalize_word(word):
    return re.sub(r"[^a-zA-Z']", "", word.lower()).strip()

def get_ignored_words(music):
    return {
        word.strip().lower()
        for word in music.ignored_words.split()
        if word.strip()
    }

def extract_music_words(text, ignored_words=None):
    ignored_words = ignored_words or set()
    words = set()
    normalized_text = re.sub(
        r"[^a-zA-Z']",
        " ",
        text.lower(),
    )
    for raw in normalized_text.split():
        word = raw.strip()
        if word and word not in ignored_words:
            words.add(word)
    return words

def get_known_words_until_lesson(lesson_number):
    return set(
        Dictionary.objects.filter(
            occurrences__lesson__number__lte=lesson_number
        ).values_list("verb_en", flat=True)
    )


def analyze_music_by_lessons(music):
    ignored_words = get_ignored_words(music)
    music_words = extract_music_words(music.lyrics,ignored_words=ignored_words,)
    results = []
    lessons = Lesson.objects.order_by("number")
    for lesson in lessons:
        known_words = {
            word.lower().strip()
            for word in get_known_words_until_lesson(lesson.number)
        }
        new_words = sorted(music_words - known_words)
        result = {
            "lesson": lesson.number,
            "new_words_count": len(new_words),
            "new_words": new_words,
        }

        results.append(result)

        if len(new_words) <= MAX_NEW_WORDS:
            break

    return results