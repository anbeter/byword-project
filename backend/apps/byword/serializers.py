from rest_framework import serializers
from .models import WordSearch, Word


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'text']


class WordSearchSerializer(serializers.ModelSerializer):
    words = WordSerializer(many=True, read_only=True)

    class Meta:
        model = WordSearch
        fields = [
            'id',
            'name',
            'rows',
            'cols',
            'grid',
            'solution',
            'words'
        ]