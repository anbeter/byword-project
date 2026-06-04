from pathlib import Path

from django.conf import settings
from django.utils.text import slugify

from gtts import gTTS


def generate_pronunciation_audio(dictionary_obj,slow=False,):
    try:
        word = dictionary_obj.verb_en.strip()
        filename = slugify(word)
        if slow:
            relative_path = (
                f"pronunciations/slow/"
                f"{filename}.mp3"
            )
        else:
            relative_path = (
                f"pronunciations/"
                f"{filename}.mp3"
            )
        full_path = (
            Path(settings.MEDIA_ROOT)
            / relative_path
        )
        # já existe
        if full_path.exists():
            return relative_path
        full_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        tts = gTTS(
            text=word,
            lang="en",
            slow=slow,
        )
        tts.save(str(full_path))
        if slow:
            dictionary_obj.pronunciation_audio_slow = (
                relative_path
            )
            dictionary_obj.save(
                update_fields=[
                    "pronunciation_audio_slow"
                ]
            )
        else:
            dictionary_obj.pronunciation_audio = (
                relative_path
            )
            dictionary_obj.save(
                update_fields=[
                    "pronunciation_audio"
                ]
            )
        return relative_path
    except Exception:
        return None