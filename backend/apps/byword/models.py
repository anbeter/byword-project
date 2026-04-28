import unicodedata
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint


class WordSearch(models.Model):
    name = models.CharField(max_length=100)

    rows = models.PositiveIntegerField(default=15)
    cols = models.PositiveIntegerField(default=15)

    grid = models.JSONField(null=True, blank=True)
    solution = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.rows < 5 or self.cols < 5:
            raise ValidationError("Grid mínimo é 5x5")

        if self.rows > 50 or self.cols > 50:
            raise ValidationError("Grid máximo é 50x50")

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

    text = models.CharField(max_length=50)          # original (com acento)
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