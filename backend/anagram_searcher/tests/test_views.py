from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from backend.anagram_searcher.models import Word


class WordsApiViewTestCase(TestCase):
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

    def test_delete_all_words(self):
        self.assertEqual(1, Word.objects.all().count())

        response = self.client.delete('/words/')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Word.objects.all().count())


class WordsDetailApiViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.word = Word.objects.create(word='read', canonical_form='ader')

    def test_delete_one_word(self):
        self.assertEqual(1, Word.objects.all().count())

        response = self.client.delete(f'/words/{self.word.word}/')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Word.objects.all().count())


class AnagramApiViewTestCase(TestCase):
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
