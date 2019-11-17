from django.shortcuts import render
from django.http import HttpResponse
from .models import Sentence, WordSet

from django.http import Http404

def browse_word_sets(request):
    word_sets = WordSet.objects.all()

    context = {'word_sets': word_sets}
    return render(request, 'browse_mode/index.html', context)


def browse_story_list(request, wordset_id):
    try:
        word_set = WordSet.objects.get(pk=wordset_id)
        story_list = word_set.story_set.all()
        context = {'word_set': word_set, 'story_list': story_list}

    except WordSet.DoesNotExist:
        raise Http404("Sentence does not exists!!")

    return render(request, 'browse_mode/browse_story.html', context)
