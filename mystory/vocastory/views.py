from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseBadRequest

from .models import Story, Sentence, WordSet, StoryReview
from accounts.models import CustomUser
from .forms import SentenceInputForm, SentenceSelectForm, StoryRatingForm
from django.db import models


def home_view(request):
    """ C
    This creates the home view when first
    enter to the website
    """
    top_stories = Story.get_top_stories_ordered()
    top_word_sets = WordSet.get_top_wordsets_ordered()

    context = {
        'stories': top_stories,
        'word_sets': top_word_sets,
    }
    return render(request, 'home.html', context)


def mypage_view(request):
    """ C
    Stories user is part of and word-sets user created are shown
    :param request:
    :return:
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    user = get_object_or_404(CustomUser, id=request.user.id)

    context = {
        'stories': user.get_stories(),
        'word_sets': user.created_word_sets.all(),
    }
    return render(request, 'my_page.html', context)



def starred_page_view(request):
    """ C
    Stories user is part of and word-sets user created are shown
    :param request:
    :return:
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    user = CustomUser.objects.get(pk=request.user.id)

    context = {
        'stories': user.starred_stories.all(),
        'word_sets': user.starred_word_sets.all(),
    }
    return render(request, 'starred_page.html', context)


def review_story(request, story_id):
    """C
    Review page
    :param request:
    :param story_id:
    :return:
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    story = get_object_or_404(Story, id=story_id)
    user = get_object_or_404(CustomUser, id=request.user.id)
    instance = StoryReview.objects.filter(creator=user, story=story).first()
    if instance is not None:
        initial = {
            'flag': instance.flag,
            'coherence': instance.coherence,
            'creativity': instance.creativity,
            'fun': instance.fun
        }
    else:
        initial = {}

    context = {
        'story': story,
        'instance': instance,
        'rating_form': StoryRatingForm(initial=initial),
    }

    if request.method == 'GET':
        return render(request, 'review_mode/review_story.html', context)
    elif request.method == 'POST':

        form = StoryRatingForm(request.POST)

        if form.is_valid():
            flag = form.cleaned_data['flag']
            coherence = form.cleaned_data['coherence']
            creativity = form.cleaned_data['creativity']
            fun = form.cleaned_data['fun']

            context['flag'] = flag
            context['coherence'] = coherence
            context['creativity'] = creativity
            context['fun'] = fun

            # This will create the review and save it
            StoryReview.create_or_edit(
                user, story, flag,
                coherence, creativity, fun
            )

            return render(request, 'review_mode/reviewed.html', context)
        else:
            return HttpResponseBadRequest("Invalid form!!")


def browse_word_sets(request):
    """C
    Wordset browsing page
    Only shows wordsets
    :param request:
    :return:
    """
    context = {'word_sets': WordSet.objects.all()}
    return render(request, 'browse_mode/index.html', context)


def browse_story_list(request, wordset_id):
    """C
    Given wordset it shows the stories
    :param request:
    :param wordset_id:
    :return:
    """
    word_set = get_object_or_404(WordSet, id=wordset_id)
    story_list = word_set.story_set.all()
    context = {'word_set': word_set, 'story_list': story_list}

    return render(request, 'browse_mode/browse_story.html', context)


def read_story(request, story_id):
    """
    Given story id it prepares selection form
    :param request:
    :param story_id:
    :return:
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    story = get_object_or_404(Story, id=story_id)

    candidates_text = ".\n".join([i.text for i in story.get_candidate_sentences()])
    context = {
        'story': story,
        'the_candidates': candidates_text,
        'the_form': SentenceSelectForm(),
    }

    if request.method == 'GET':
        return render(request, 'readers_mode/select_sentence.html',context)
    elif request.method == 'POST':
        form = SentenceSelectForm(request.POST)
        if form.is_valid():
            candidates=story.get_candidate_sentences() 
            user = CustomUser.objects.get(pk=request.user.id)
            chosen_sentence = candidates[form.cleaned_data['int_option']-1]
            chosen_sentence.vote_sentence(user)
            context['selected_sentence'] = chosen_sentence

            # story.check_time_and_select()
            return render(request, 'readers_mode/selected.html', context)
        else:
            return HttpResponseBadRequest("Invalid form!!")


def write_story(request, story_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    story = get_object_or_404(Story, id=story_id)
    context = {
        'story': story,
        'input_form': SentenceInputForm(),
    }

    if request.method == 'GET':
        return render(request, 'writers_mode/write_story.html', context)
    elif request.method == 'POST':
        form = SentenceInputForm(request.POST)
        if form.is_valid():
            context['candidate_sentence'] = form.cleaned_data['sentence']
            current_user = CustomUser.objects.get(pk=request.user.id)
            Sentence.create(text=form.cleaned_data['sentence'], story=story, creator=current_user)
            return render(request, 'writers_mode/submitted.html', context)
        else:
            return HttpResponseBadRequest("Invalid form!!")
