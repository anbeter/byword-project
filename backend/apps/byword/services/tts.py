from pathlib import Path

from django.conf import settings
from django.utils.text import slugify

from gtts import gTTS


def generate_pronunciation_audio(dictionary_obj):
    if dictionary_obj.pronunciation_audio:
        return dictionary_obj.pronunciation_audio
    try:
        word = dictionary_obj.verb_en.strip()
        filename = slugify(word)
        relative_path = (
            f"pronunciations/{filename}.mp3"
        )
        full_path = (
            Path(settings.MEDIA_ROOT)
            / relative_path
        )
        full_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        tts = gTTS(
            text=word,
            lang="en",
            slow=False,
        )
        tts.save(str(full_path))

        dictionary_obj.pronunciation_audio = (
            relative_path
        )

        dictionary_obj.save(
            update_fields=[
                "pronunciation_audio"
            ]
        )

        return dictionary_obj.pronunciation_audio

    except Exception:
        return None