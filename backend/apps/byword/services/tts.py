from io import BytesIO

from django.core.files.base import (
    ContentFile
)

from django.utils.text import slugify

from gtts import gTTS


def generate_pronunciation_audio(
    dictionary_obj
):

    word = (
        dictionary_obj.verb_en.strip()
    )

    filename = (
        f"{slugify(word)}.mp3"
    )

    mp3_fp = BytesIO()

    tts = gTTS(
        text=word,
        lang="en",
        slow=False,
    )

    tts.write_to_fp(mp3_fp)

    mp3_fp.seek(0)

    dictionary_obj.pronunciation_audio.save(
        filename,
        ContentFile(mp3_fp.read()),
        save=True
    )

    return (
        dictionary_obj.pronunciation_audio
    )