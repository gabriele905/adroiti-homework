from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from backend.anagram_searcher.models import Word


class WordsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word = Word.objects.create(word='read', canonical_form='ader')

    def test_create_words(self):
        self.assertEqual(1, Word.objects.all().count())

        data = {
            'words': ['read', 'dear', 'dare']
        }
        response = self.client.post('/words/', data, format='json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Word.objects.all().count())

    def test_create_words_no_words_passed(self):
        data = {
            'words': []
        }
        response = self.client.post('/words/', data, format='json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('No words provided', response.data['error'])

    def test_delete_all_words(self):
        self.assertEqual(1, Word.objects.all().count())

        response = self.client.delete('/words/')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Word.objects.all().count())


class WordsDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word = Word.objects.create(word='read', canonical_form='ader')

    def test_delete_one_word(self):
        self.assertEqual(1, Word.objects.all().count())

        response = self.client.delete(f'/words/{self.word.word}/')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Word.objects.all().count())


class AnagramViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word_read = Word.objects.create(word='read', canonical_form='ader')
        self.word_dare = Word.objects.create(word='dare', canonical_form='ader')
        self.word_dear = Word.objects.create(word='dear', canonical_form='ader')
        self.word_book = Word.objects.create(word='book', canonical_form='bkoo')

    def test_get_anagram_founds_two_anagram(self):
        response = self.client.get(f'/anagrams/{self.word_read.word}/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn(self.word_dare.word, response.data['anagrams'])
        self.assertIn(self.word_dear.word, response.data['anagrams'])

    def test_get_anagram_limit_to_one_anagram(self):
        self.assertEqual(2, Word.objects.filter(
            canonical_form=self.word_read.canonical_form).exclude(word=self.word_read.word).count())

        response = self.client.get(f'/anagrams/{self.word_read.word}/?limit=1')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn(self.word_dare.word, response.data['anagrams'])
        self.assertNotIn(self.word_dear.word, response.data['anagrams'])


class CorpusStatsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word_a = Word.objects.create(word='a', canonical_form='a')
        self.word_cat = Word.objects.create(word='cat', canonical_form='act')
        self.word_book = Word.objects.create(word='book', canonical_form='bkoo')

    def test_get_corpus_stats(self):
        response = self.client.get('/corpus_stats/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(3, response.data['total_words'])
        self.assertEqual(1, response.data['min_length'])
        self.assertEqual(4, response.data['max_length'])
        self.assertEqual(8 / 3, response.data['average_length'])
        self.assertEqual(3, response.data['median_length'])


class MostAnagramsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word_read = Word.objects.create(word='read', canonical_form='ader')
        self.word_dare = Word.objects.create(word='dare', canonical_form='ader')
        self.word_dear = Word.objects.create(word='dear', canonical_form='ader')
        self.word_book = Word.objects.create(word='book', canonical_form='bkoo')

    def test_get_most_anagrams_without_limit(self):
        response = self.client.get('/most_anagrams/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(3, len(response.data['words']))
        self.assertIn(self.word_read.word, response.data['words'])
        self.assertIn(self.word_dare.word, response.data['words'])
        self.assertIn(self.word_dear.word, response.data['words'])


class CheckAnagramsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_check_anagrams_returns_true(self):
        data = {
            'words': ['read', 'dear']
        }
        response = self.client.post('/check_anagrams/', data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertTrue(response.data['are_anagrams'])

    def test_check_anagrams_returns_false(self):
        data = {
            'words': ['read', 'book']
        }
        response = self.client.post('/check_anagrams/', data, format='json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(response.data['are_anagrams'])

    def test_check_anagrams_no_words_passed(self):
        data = {
            'words': []
        }
        response = self.client.post('/check_anagrams/', data, format='json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('No words provided', response.data['error'])


class AnagramGroupViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word_read = Word.objects.create(word='read', canonical_form='ader')
        self.word_dare = Word.objects.create(word='dare', canonical_form='ader')
        self.word_dear = Word.objects.create(word='dear', canonical_form='ader')
        self.word_book = Word.objects.create(word='book', canonical_form='bkoo')

    def test_get_anagrams_group_one(self):
        response = self.client.get('/anagram_group/1/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        self.assertIn(self.word_read.canonical_form, response.data)
        self.assertIn(self.word_read.word, response.data[self.word_read.canonical_form])
        self.assertIn(self.word_dare.word, response.data[self.word_read.canonical_form])
        self.assertIn(self.word_dear.word, response.data[self.word_read.canonical_form])

        self.assertIn(self.word_book.canonical_form, response.data)
        self.assertIn(self.word_book.word, response.data[self.word_book.canonical_form])

    def test_get_anagrams_group_two(self):
        response = self.client.get('/anagram_group/2/')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

        self.assertIn(self.word_read.canonical_form, response.data)
        self.assertIn(self.word_read.word, response.data[self.word_read.canonical_form])
        self.assertIn(self.word_dare.word, response.data[self.word_read.canonical_form])
        self.assertIn(self.word_dear.word, response.data[self.word_read.canonical_form])


class DeleteWordViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word_read = Word.objects.create(word='read', canonical_form='ader')
        self.word_dare = Word.objects.create(word='dare', canonical_form='ader')
        self.word_dear = Word.objects.create(word='dear', canonical_form='ader')
        self.word_book = Word.objects.create(word='book', canonical_form='bkoo')

    def test_delete_word_deletes_all_anagrams(self):
        self.assertEqual(4, Word.objects.all().count())

        anagram = self.word_read.canonical_form

        response = self.client.delete(f'/delete_word/{self.word_read.word}/')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        self.assertEqual(1, Word.objects.all().count())
        self.assertEqual(0, Word.objects.filter(canonical_form=anagram).count())
