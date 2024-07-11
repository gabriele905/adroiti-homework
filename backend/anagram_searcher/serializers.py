from rest_framework import serializers


class AnagramSerializer(serializers.Serializer):
    anagrams = serializers.SerializerMethodField()

    def get_anagrams(self, obj):
        return obj
