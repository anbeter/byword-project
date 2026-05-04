import re
from django.contrib.contenttypes.models import ContentType
from apps.byword.models import Dictionary

import re
from django.contrib.contenttypes.models import ContentType
from apps.byword.models import Dictionary, DictionaryOccurrence

from deep_translator import GoogleTranslator

# =========================
# NORMALIZAÇÃO DE TEXTO
# =========================
def normalize_word(word):
    return word.lower().strip()


def extract_words(text):
    """
    Extrai palavras ignorando:
    - pontuação
    - símbolos
    - números
    """
    STOP_WORDS = {
        "the", "a", "an", "of", "to", "in", "on", "at", "for",
        "and", "or", "but", "is", "are", "was", "were", "be",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", 
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", 
        "u", "v", "w", "x", "y", "z"
    }
    # words = re.findall(r"[a-zA-ZÀ-ÿ']+", text)
    # return set(normalize_word(w) for w in words if w)
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return {
        w for w in words
        if len(w) > 2 and w not in STOP_WORDS
    }


## google translate
def suggest_translation(word):
    from deep_translator import GoogleTranslator
    try:
        return GoogleTranslator(source='en', target='pt').translate(word)
    except Exception:
        return ""

# =========================
# SYNC PRINCIPAL
# =========================
def sync_dictionary(*, old_text, new_text, instance, origin, number_lesson):
    """
    Sincroniza o dicionário baseado na diferença entre textos
    """



    old_words = extract_words(old_text or "")
    new_words = extract_words(new_text or "")

    removed_words = old_words - new_words
    added_words = new_words - old_words

    content_type = ContentType.objects.get_for_model(instance)

    # =========================
    # REMOVER OCORRÊNCIAS
    # =========================
    for word in removed_words:
        try:
            dictionary = Dictionary.objects.get(verb_en=word)
        except Dictionary.DoesNotExist:
            continue

        # remove ocorrência dessa instância
        DictionaryOccurrence.objects.filter(
            dictionary=dictionary,
            content_type=content_type,
            object_id=instance.id
        ).delete()

        # 🔥 se não sobrou ocorrência → remove do dicionário
        if not dictionary.occurrences.exists():
            dictionary.delete()

    # =========================
    # ADICIONAR NOVAS PALAVRAS
    # =========================
    translated_cache = {}

    for word in added_words:
        dictionary, created = Dictionary.objects.get_or_create(verb_en=word)
        if len(word) <= 2:
            continue
        if word in STOP_WORDS:
            continue

        if created and not dictionary.translation:

            if word not in translated_cache:
                translated_cache[word] = suggest_translation(word)

            dictionary.translation = translated_cache[word]

        DictionaryOccurrence.objects.get_or_create(
            dictionary=dictionary,
            content_type=content_type,
            object_id=instance.id,
            defaults={
                "origin": origin,
                "number_lesson": number_lesson,
            }
        )

        if created and dictionary.translation:
            dictionary.save()