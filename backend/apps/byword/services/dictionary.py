import re
from django.contrib.contenttypes.models import ContentType
from apps.byword.models import Dictionary, Lesson

from django.core.cache import cache

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

    if not text:
        return set()

    # normaliza travessões
    text = text.replace("–", " ").replace("—", " ")

    # captura palavras com letras + apóstrofo interno
    words = re.findall(r"[A-Za-zÀ-ÿ']+", text)

    # lowercase final padronizado
    return {w.lower().strip() for w in words if w.strip()}


## google translate
def suggest_translation(word):
    from deep_translator import GoogleTranslator
    try:
        return GoogleTranslator(source='en', target='pt').translate(word)
    except Exception:
        return ""

def translate_word_if_needed(dictionary):
    """
    Traduz a palavra usando cache para evitar chamadas repetidas
    """

    if dictionary.translation:
        return dictionary

    cache_key = f"translate:{dictionary.verb_en.lower()}"
    cached = cache.get(cache_key)

    if cached:
        dictionary.translation = cached
        dictionary.save(update_fields=["translation"])
        return dictionary

    try:
        translation = GoogleTranslator(
            source='en',
            target='pt'
        ).translate(dictionary.verb_en)

        if translation:
            dictionary.translation = translation
            dictionary.save(update_fields=["translation"])
            cache.set(cache_key, translation, timeout=60 * 60 * 24 * 30)  # 30 dias

    except Exception:
        pass

    return dictionary

# =========================
# SYNC PRINCIPAL
# =========================
def sync_dictionary(*, old_text, new_text, instance, origin, lesson):
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
        # if not dictionary.occurrences.exists():
        if not DictionaryOccurrence.objects.filter(dictionary=dictionary).exists():
            dictionary.delete()

    # =========================
    # ADICIONAR NOVAS PALAVRAS
    # =========================
    translated_cache = {}

    for word in added_words:
        dictionary, created = Dictionary.objects.get_or_create(verb_en=word)
        # 🔥 OPCIONAL: tradução automática (DESLIGADO)
        if created:
            translate_word_if_needed(dictionary)
        # fim da tradução automática

        DictionaryOccurrence.objects.get_or_create(
            dictionary=dictionary,
            content_type=content_type,
            object_id=instance.id,
            defaults={
                "origin": origin,
                "lesson": lesson,
            }
        )
