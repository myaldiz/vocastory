from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import Story, Sentence, WordSet
from accounts.models import CustomUser
from .forms import SentenceInputForm
from django.db import models


def home_view(request):
    """
    This creates the home view when first
    enter to the website
    """
    top_stories = Story.get_top_stories_ordered()
    top_word_sets = WordSet.get_top_wordsets_ordered()

    top_story_info = [
        (s.num_stars, s.title, s.get_text())
        for s in top_stories
    ]
    context = {
        'top_story_info': top_story_info,
        'top_word_sets': top_word_sets,
    }
    return render(request, 'home.html', context)


def mypage_view(request):
    """
    Stories user is part of and word-sets user created are shown
    :param request:
    :return:
    """
    user = CustomUser.objects.get(pk=request.user.id)
    stories = user.get_stories()\
        .annotate(num_stars=models.Count('starred_users'))\
        .order_by('-num_stars')
    story_info = [(s.num_stars, s.title, s.get_text()) for s in stories]
    word_sets = user.created_word_sets\
        .annotate(num_stars=models.Count('starred_users'))\
        .order_by('-num_stars')
    context = {
        'story_info': story_info,
        'word_sets': word_sets,
    }
    return render(request, 'my_page.html', context)


def starred_page_view(request):
    """
    Stories user is part of and word-sets user created are shown
    :param request:
    :return:
    """
    user = CustomUser.objects.get(pk=request.user.id)
    stories = user.starred_stories\
        .annotate(num_stars=models.Count('starred_users'))\
        .order_by('-num_stars')
    story_info = [(s.num_stars, s.title, s.get_text()) for s in stories]
    word_sets = user.starred_word_sets\
        .annotate(num_stars=models.Count('starred_users'))\
        .order_by('-num_stars')
    context = {
        'story_info': story_info,
        'word_sets': word_sets,
    }
    return render(request, 'starred_page.html', context)


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
