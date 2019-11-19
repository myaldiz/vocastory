from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import Story, Sentence, WordSet
from .forms import SentenceInputForm


def review_story(request, story_id):
    try:
        story = Story.objects.get(pk=story_id)

        context = {'story': story, 'story_text': story.get_text()}


    except Story.DoesNotExist:
        raise Http404("Story does not exists!!")

    return render(request, 'review_mode/review_story.html', context)


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


def read_story(request, story_id):
    return HttpResponse('Read/Select how to continue!')


def write_story(request, story_id):
    try:
        story = Story.objects.get(pk=story_id)
        last_two = story.get_last_two()
        context = {
            'story': story,
            'story_last_two': last_two,
            'input_form': SentenceInputForm(),
        }
    except Story.DoesNotExist:
        raise Http404("Story does not exists!!")

    if request.method == 'GET':
        return render(request, 'writers_mode/write_story.html', context)
    elif request.method == 'POST':
        form = SentenceInputForm(request.POST)
        if form.is_valid():
            context['candidate_sentence'] = form.cleaned_data['sentence']
            return render(request, 'writers_mode/submitted.html', context)
        else:
            raise Http404("Invalid form!!")
