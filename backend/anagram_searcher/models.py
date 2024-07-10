from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=100, unique=True)
    canonical_form = models.CharField(max_length=100, db_index=True)
