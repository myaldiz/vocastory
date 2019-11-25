from django.contrib import admin

from .models import Word, WordSet, Sentence, Story
from .models import StoryReview

admin.site.register(Word)
admin.site.register(WordSet)
admin.site.register(Sentence)
admin.site.register(Story)
admin.site.register(StoryReview)
