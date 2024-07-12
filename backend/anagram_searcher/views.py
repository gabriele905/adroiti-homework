from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.anagram_searcher.models import Word
from backend.anagram_searcher.serializers import AnagramSerializer


class WordsView(APIView):
    def post(self, request, format=None):
        words = request.data.get('words')

        if not words:
            return Response({'error': 'No words provided'}, status.HTTP_400_BAD_REQUEST)

        Word.add_list_of_words(words)

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        Word.objects.all().delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class WordsDetailView(APIView):
    def delete(self, request, word, format=None):
        Word.objects.filter(word=word).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AnagramView(APIView):
    def get(self, request, word, format=None):
        limit = int(request.query_params.get('limit', Word.objects.all().count()))

        return Response(
            AnagramSerializer(
                Word.objects.filter(
                    canonical_form=''.join(sorted(word))
                ).exclude(word=word).values_list('word', flat=True)[:limit]
            ).data
        )
