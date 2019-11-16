from django.contrib import admin

from .models import Word, WordSet, Sentence, Story

admin.site.register(Word)
admin.site.register(WordSet)
admin.site.register(Sentence)
admin.site.register(Story)
