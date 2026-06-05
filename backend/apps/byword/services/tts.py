from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.utils.text import slugify

from gtts import gTTS


def generate_pronunciation_audio(dictionary_obj):
    if dictionary_obj.pronunciation_audio:
        return dictionary_obj.pronunciation_audio
    try:
        word = (
            dictionary_obj.verb_en.strip()
        )
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
        tts = gTTS(text=word,lang="en",slow=False,)
        tts.save(str(full_path))
        with open(full_path, "rb") as f:
            dictionary_obj.pronunciation_audio.save(
                f"{filename}.mp3",
                File(f),
                save=True
            )
        return (
            dictionary_obj.pronunciation_audio
        )
    except Exception as e:
        print(e)
        return None