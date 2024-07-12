from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    canonical_form = models.CharField(max_length=100, db_index=True)

    @staticmethod
    def add_list_of_words(words):
        if not words:
            return

        Word.objects.bulk_create(
            [Word(word=word, canonical_form=''.join(sorted(word)).lower()) for word in words],
            ignore_conflicts=True
        )