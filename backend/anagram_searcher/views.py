from django.db.models import Count, Min, Max, Avg, Q
from django.db.models.functions import Length
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
        include_proper_nouns = request.query_params.get('include_proper_nouns', 'false').lower() == 'true'

        f = Q(canonical_form=''.join(sorted(word)))

        if not include_proper_nouns:
            f &= Q(word__regex=r'^[a-z]+$')

        return Response(
            AnagramSerializer(Word.objects.filter(f).exclude(word=word).values_list('word', flat=True)[:limit]).data
        )


class CorpusStatsView(APIView):
    def get(self, request):
        total_words = Word.objects.count()
        word_length_stats = Word.objects.aggregate(
            min_length=Min(Length('word')),
            max_length=Max(Length('word')),
            average_length=Avg(Length('word'))
        )
        word_lengths = list(Word.objects.annotate(length=Length('word')).values_list('length', flat=True))
        word_lengths.sort()
        median_length = word_lengths[len(word_lengths) // 2] if word_lengths else 0

        stats = {
            'total_words': total_words,
            'min_length': word_length_stats['min_length'],
            'max_length': word_length_stats['max_length'],
            'average_length': word_length_stats['average_length'],
            'median_length': median_length,
        }
        return Response(stats, status=status.HTTP_200_OK)


class MostAnagramsView(APIView):
    def get(self, request):
        anagram_counts = Word.objects.values('canonical_form').annotate(count=Count('id')).order_by('-count')
        max_anagrams = anagram_counts[0]['count'] if anagram_counts else 0
        words_with_most_anagrams = Word.objects.filter(
            canonical_form__in=[item['canonical_form'] for item in anagram_counts if item['count'] == max_anagrams]
        ).values_list('word', flat=True)

        return Response({'words': words_with_most_anagrams}, status=status.HTTP_200_OK)


class CheckAnagramsView(APIView):
    def post(self, request, format=None):
        words = request.data.get('words', [])

        if not words:
            return Response({'error': 'No words provided'}, status.HTTP_400_BAD_REQUEST)

        canonical_forms = {''.join(sorted(word)) for word in words}

        return Response({'are_anagrams': len(canonical_forms) == 1})


class AnagramGroupView(APIView):
    def get(self, request, size, format=None):
        anagram_groups = Word.objects.values('canonical_form').annotate(count=Count('id')).filter(count__gte=size)
        groups = {
            group['canonical_form']: list(Word.objects.filter(
                canonical_form=group['canonical_form']).values_list('word', flat=True)) for group in anagram_groups
        }

        return Response(groups)


class DeleteWordView(APIView):
    def delete(self, request, word, format=None):
        Word.objects.filter(canonical_form=''.join(sorted(word))).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
