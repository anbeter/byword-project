import unicodedata
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint, Min
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.byword.services.text_mask import replace_marked_words
from apps.byword.validators import validate_image_extension


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
    subtitle = models.CharField(max_length=150,default="Word search")
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

    docx_subtitle = "Word Search"
    docx_fields = (
        {
            # "field": "png",
            "field": "__object__",
            "renderer": "wordsearch_image",
        },
    )

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
            # return f"{self.lesson.number} - {lesson_name}"
            return (self.subtitle or f"{self.lesson.number} - {lesson_name}")
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

    text = models.CharField(max_length=50)
    normalized = models.CharField(max_length=50, editable=False)

    def clean(self):

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
    subtitle = models.CharField(max_length=150,default="Scrambled words")
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
    # attribute_docx = (
    #     "texto_embaralhado",
    # )
    docx_subtitle = "Scramble Words"
    docx_fields = (
        {
            "field": "texto_embaralhado",
            "renderer": "scramble_table",
        },
    )

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
        # return self.get_display_title()
        return (self.subtitle or self.get_display_title())


class Music(models.Model):
    number_lesson = models.PositiveIntegerField(unique=True)
    subtitle = models.CharField(max_length=150,default="Music")
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

    attribute_docx = (
        "title",
        "author",
        "lyrics_spaces",
    )
    docx_fields = (
        {
            "field": "title",
            "renderer": "title_right",
        },
        {
            "field": "lyrics_spaces",
            "renderer": "text",
        },
    )

    class Meta:
        unique_together = ("lesson", "title", "author")
        verbose_name = "Music"
        verbose_name_plural = "Music"

    def __str__(self):
        # return self.subtitle
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
    subtitle = models.CharField(max_length=150,default="Lesson Text")
    text = models.TextField()

    def __str__(self):
        # return self.subtitle
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
    subtitle = models.CharField(max_length=150,default="Vocabulary")
    created_at = models.DateTimeField(auto_now_add=True)
    docx_subtitle = "Vocabulary"
    docx_fields = (
        {
            "field": "vocabulary_table",
            "renderer": "dictionary_table",
        },
    )

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

class Reference(models.Model):
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="references"
    )
    reference = models.CharField(max_length=250)
    book = models.CharField(max_length=50,null=True, blank=True)
    chapter = models.PositiveIntegerField(null=True, blank=True)
    verse = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subtitle = models.CharField(max_length=150,null=True, blank=True)
    docx_subtitle = None
    docx_fields = (
        {
            "field": "reference",
            "renderer": "reference_right",
        },
    )

    class Meta:
        ordering = ["lesson__number", "book", "chapter", "verse"]

    # def save(self, *args, **kwargs):
    #     # self.subtitle = self.reference
    #     super().save(*args, **kwargs)

    def __str__(self):
        # return self.reference
        return (self.subtitle or self.reference)


class Verse(models.Model):
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="verses"
    )
    reference = models.ForeignKey(
        "Reference",
        on_delete=models.CASCADE,
        related_name="verses"
    )
    subtitle = models.CharField(max_length=150,default="Write the Verse")
    number = models.PositiveIntegerField()
    original_text = models.TextField()
    masked_text = models.TextField(blank=True, editable=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    docx_subtitle = "Write the Verse"
    docx_fields = (
    {
        "field": "original_text",
        "renderer": "text",
        "transform": "clean_text",
    },
        {
            "field": "masked_text",
            "renderer": "text",
        },
    )
    class Meta:
        ordering = ["reference", "number"]

    def save(self, *args, **kwargs):
        self.masked_text = replace_marked_words(
            self.original_text
        )

        super().save(*args, **kwargs)

    def __str__(self):
        # return (f"{self.reference} - Verse {self.number}")
        # return (f"{self.lesson} or 'Reference' ")
        return (f"{self.reference} - Verse {self.original_text}")


class CompleteTheSentence(models.Model):
    lesson = models.ForeignKey(
        "Lesson",
        on_delete=models.CASCADE,
        related_name="complete_sentences"
    )
    subtitle = models.CharField(max_length=150,default="Complete the sentences")
    sentences = models.TextField()
    sentences_mask = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="statics/activity/img/",
        validators=[validate_image_extension],
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    attribute_docx = (
        "image",
        "sentences_mask",
    )
    docx_fields = (
        {
            "field": "image",
            "renderer": "image",
            "width": 5.5,
        },
        {
            "field": "sentences_mask",
            "renderer": "text",
        },
    )

    class Meta:
        verbose_name = "Complete the Sentence"
        verbose_name_plural = "Complete the Sentences"
        ordering = ["lesson", "subtitle"]

    def save(self, *args, **kwargs):
        from apps.byword.services.text_mask import (
            replace_marked_words
        )
        self.sentences_mask = (
            replace_marked_words(
                self.sentences
            )
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Lesson {self.lesson.number} - "
            f"{self.subtitle}"
        )


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
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="items"
    )
    order = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True,null=True)
    content_object = GenericForeignKey("content_type","object_id")
    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "activity",
                    "content_type",
                    "object_id",
                ],
                name="unique_activity_item"
            )
        ]

    def __str__(self):
        if self.object_id and self.content_object:
            return (
                f"{self.content_type} - "
                f"{self.content_object}"
            )
        return (
            f"{self.content_type} - ALL"
        )

class Crossword(models.Model):

    docx_subtitle = "Crossword"

    docx_fields = (
        {
            "field": "image",
            "renderer": "image",
            "width": 6,
        },
    )