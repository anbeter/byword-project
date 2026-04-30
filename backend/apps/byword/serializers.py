from rest_framework import serializers
from .models import WordSearch, Word, ScrambleWord


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



class ScrambleWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrambleWord
        fields = [
            'id',
            'titulo',
            'texto_original',
            'texto_embaralhado',
            'criado_em'
        ]