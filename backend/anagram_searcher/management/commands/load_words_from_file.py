from django.core.management.base import BaseCommand

from backend.anagram_searcher.models import Word


class Command(BaseCommand):
    help = 'Load words from a text file into the database'

    def handle(self, *args, **kwargs):
        with open('dictionary.txt', 'r') as file:
            words = file.read().splitlines()

        Word.add_list_of_words(words)
