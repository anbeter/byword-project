import unicodedata
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint, Min
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Lesson(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=70)

    def __str__(self):
        return f"Lesson {self.number} - {self.name}"

    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)

    #     if is_new:
    #         from .models import Activity
    #         Activity.objects.create(lesson=self)

class WordSearch(models.Model):
    name = models.CharField(max_length=100)
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wordsearches"
    )

    rows = models.PositiveIntegerField(default=14)
    cols = models.PositiveIntegerField(default=14)

    grid = models.JSONField(null=True, blank=True)
    solution = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rows < 5 or self.cols < 5:
            raise ValidationError("Grid mínimo é 5x5")

        if self.rows > 50 or self.cols > 50:
            raise ValidationError("Grid máximo é 50x50")

    class Meta:
        verbose_name = "Word Search"
        verbose_name_plural = "Word Search"

    def __str__(self):
        if self.lesson:
            lesson_name = self.lesson.name or "Unnamed"
            return f"{self.lesson.number} - {lesson_name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.rows:
            self.rows = 15
        if not self.cols:
            self.cols = 15

        self.full_clean()
        super().save(*args, **kwargs)


def normalize(word: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', word)
        if unicodedata.category(c) != 'Mn'
    )

class Word(models.Model):
    wordsearch = models.ForeignKey(
        'WordSearch',
        related_name='words',
        on_delete=models.CASCADE
    )

    text = models.CharField(max_length=50)          # (com acento)
    normalized = models.CharField(max_length=50, editable=False)  # sem acento

    def clean(self):
        # if not self.wordsearch_id:
        #     return
        if not self.wordsearch:
            raise ValidationError("WordSearch não definido.")

        word = self.text.strip()

        if not word.isalpha():
            raise ValidationError(
                f'A palavra "{word}" deve conter apenas letras.'
            )

        max_size = max(self.wordsearch.rows, self.wordsearch.cols)

        if len(word) > max_size:
            raise ValidationError(
                f'A palavra "{word}" excede o tamanho máximo ({max_size}).'
            )

    def save(self, *args, **kwargs):
        # 🔥 NORMALIZAÇÃO PRINCIPAL CAIXA ALTA
        self.text = self.text.strip().upper()
        #Retirando acentos, caso necessário utilizar
        self.normalized = normalize(self.text)

        self.full_clean()

        super().save(*args, **kwargs)


    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['wordsearch', 'text'],
                name='unique_word_per_wordsearch'
            )
        ]


class ScrambleWord(models.Model):
    titulo = models.CharField(max_length=70, null=True, blank=True)
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scramblewords"
    )
    texto_original = models.CharField(max_length=270)
    texto_embaralhado = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Scramble Words"
        verbose_name_plural = "Scramble Words"

    def save(self, *args, **kwargs):
        from .scrambleword.engine import embaralhar_texto

        self.texto_embaralhado = embaralhar_texto(self.texto_original)
        super().save(*args, **kwargs)
    
    def get_display_title(self):
        if self.lesson:
            return f"{self.lesson.number} - {self.lesson.name}"
        return self.titulo or "Scramble avulso"

    def __str__(self):
        return self.get_display_title()


class Music(models.Model):
    number_lesson = models.PositiveIntegerField(unique=True)
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="musics"
    )

    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150, blank=True, null=True)

    youtube_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)

    lyrics = models.TextField()
    lyrics_spaces = models.TextField(blank=True)

    class Meta:
        unique_together = ("lesson", "title", "author")
        verbose_name = "Music"
        verbose_name_plural = "Music"

    def __str__(self):
        return f"{self.title} - {self.author or ''}".strip()

    def generate_lyrics_spaces(self):
        def replace(match):
            word = match.group(1)
            size = (len(word) * 2) + 2
            return "_" * size

        return re.sub(r"\*(.*?)\*", replace, self.lyrics)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Music.objects.get(pk=self.pk)
            old_text = old.lyrics
        else:
            old_text = ""

        self.lyrics_spaces = self.generate_lyrics_spaces()

        super().save(*args, **kwargs)

        from apps.byword.services.dictionary import sync_dictionary

        sync_dictionary(
            old_text=old_text,
            new_text=self.lyrics,
            instance=self,
            origin="music",
            lesson=self.lesson,
        )


class LessonText(models.Model):
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="texts"
    )
    title = models.CharField(max_length=150)
    text = models.TextField()

    def __str__(self):
        return f"Lesson {self.lesson.number} - {self.lesson.number}"

    def get_pages(self):
        return self.text.split("#")

    def save(self, *args, **kwargs):
        is_update = self.pk is not None

        old_text = None
        if is_update:
            old = LessonText.objects.get(pk=self.pk)
            old_text = old.text

        super().save(*args, **kwargs)

        from apps.byword.services.dictionary import sync_dictionary

        sync_dictionary(
            instance=self,
            new_text=self.text,
            old_text=old_text,
            origin="lesson_text",
            lesson=self.lesson,
        )


class Dictionary(models.Model):
    verb_en = models.CharField(max_length=150, unique=True)
    translation = models.CharField(max_length=270, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dictionary"
        verbose_name_plural = "Dictionary"

    def __str__(self):
        return self.verb_en


class DictionaryOccurrence(models.Model):
    dictionary = models.ForeignKey(
        Dictionary,
        on_delete=models.CASCADE,
        related_name="occurrences"
    )
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="dictionary_occurrences"
    )

    origin = models.CharField(max_length=20)  # "music" / "lesson_text"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("dictionary", "content_type", "object_id")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.dictionary} ({self.origin})"


class Activity(models.Model):
    lesson = models.OneToOneField(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="activity"
    )

    @property
    def title(self):
        return f"Lesson {self.lesson.number} - {self.lesson.name}"

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lesson {self.lesson.number} - {self.lesson.name}"


class ActivityItem(models.Model):
    class ItemType(models.TextChoices):
        # BIBLE_REFERENCE = "bible_reference", "Bible Reference"
        DICTIONARY = "dictionary", "Dictionary"
        SCRAMBLE = "scramble", "Scramble Words"
        WORDSEARCH = "wordsearch", "Word Search"
        # VERSE = "verse", "Verse"
        # COMPLETE = "complete", "Complete the Sentences"
        # REWRITE = "rewrite", "Rewrite the Sentences"
        MUSIC = "music", "Music"

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="items"
    )

    order = models.PositiveIntegerField()

    # 🔥 ligação genérica (qualquer modelo)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )


    class Meta:
        ordering = ["order"]
        unique_together = ("activity", "order")

    def __str__(self):
        return f"{self.activity} - ({self.order}) {self.content_type}"