from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction

from .models import Story, Sentence, WordSet
from .models import Word, StoryReview
from .forms import SentenceInputForm, SentenceSelectForm, StoryRatingForm
from accounts.models import CustomUser

dict_engine = None


def dict(*args, **kwargs):
    """
    This method tokenizes the sentence
    """
    global dict_engine
    if dict_engine is None:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from PyDictionary import PyDictionary
            dict_engine=PyDictionary()
    return dict_engine.meaning(*args, **kwargs)


def home_view(request):
    """ C
    This creates the home view when first
    enter to the website
    """
    with transaction.atomic():
        top_stories = Story.get_top_stories_ordered()

    context = {
        'stories': top_stories,
    }
    return render(request, 'home.html', context)


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
    user = CustomUser.objects.get(pk=request.user.id)

    if request.method == 'GET':
        with transaction.atomic():
            order = story.get_candidate_index()
            form = SentenceSelectForm()
            choices = []
            for i in story.get_candidate_sentences(order):
                if i.creator != user:
                    choices.append((i.id, i.text))
            form.fields['sentence_choice'].choices = choices
            context = {'story': story, 'form': form}
            if len(form.fields['sentence_choice'].choices) != 0:
                return render(request, 'select_sentence.html', context)
            else:
                messages.info(request, 'All the sentences written by you!')

    elif request.method == 'POST':
        form = SentenceSelectForm(request.POST)
        order = int(request.POST.get("order", "-1"))
        with transaction.atomic():
            candidates = story.get_candidate_sentences(order)
            chosen_sentence = candidates.get(id=form.data['sentence_choice'])
            chosen_sentence.vote_sentence(user)
            messages.info(request, 'Your response is recorded')
            # This selects sentence is certain conditions
            # are fulfilled, and finishes the story
            story.close_sentence_poll()
            story.finish_story()

    return HttpResponseRedirect(reverse('home'))


def write_story(request, story_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    story = get_object_or_404(Story, id=story_id)
    context = {'story': story}

    if request.method == 'GET':
        context['input_form'] = SentenceInputForm()
        with transaction.atomic():
            return render(request, 'write_story.html', context)
    elif request.method == 'POST':
        order = int(request.POST.get("order", "0"))
        form = SentenceInputForm(request.POST)
        if form.is_valid():
            current_user = CustomUser.objects.get(pk=request.user.id)
            ret = Sentence.create(order=order, text=form.cleaned_data['sentence'], story=story, creator=current_user)
            context['candidate_sentence'] = ret

            if ret is None:
                messages.error(request, 'Please use the words from the word-list!')
                context['input_form'] = form
                with transaction.atomic():
                    return render(request, 'write_story.html', context)

    return HttpResponseRedirect(reverse('home'))


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
    with transaction.atomic():
        instance = StoryReview.objects.filter(creator=user, story=story).first()
    if instance is not None:
        initial = {
            'flag': instance.flag,
            'coherence': instance.coherence,
            'creativity': instance.creativity,
            'fun': instance.fun,
            'comment': instance.comment,
        }
    else:
        initial = {}

    context = {
        'story': story,
        'instance': instance,
        'rating_form': StoryRatingForm(initial=initial),
        'review_list': story.review_set.all()
    }

    if request.method == 'GET':
        return render(request, 'review_story.html', context)
    elif request.method == 'POST':

        form = StoryRatingForm(request.POST)

        if form.is_valid():
            flag = form.cleaned_data['flag']
            coherence = form.cleaned_data['coherence']
            creativity = form.cleaned_data['creativity']
            fun = form.cleaned_data['fun']
            comment = form.cleaned_data['comment']

            context['flag'] = flag
            context['coherence'] = coherence
            context['creativity'] = creativity
            context['fun'] = fun
            context['comment'] = comment

            # This will create the review and save it
            with transaction.atomic():
                StoryReview.create_or_edit(
                    user, story, flag,
                    coherence, creativity, fun, comment
                )

    return HttpResponseRedirect(reverse('home'))

@transaction.atomic
def browse_word_sets(request):
    """C
    Wordset browsing page
    Only shows wordsets
    :param request:
    :return:
    """
    context = {'word_sets': WordSet.objects.all()}
    return render(request, 'browse_mode/index.html', context)


@transaction.atomic
def browse_story_list(request, wordset_id):
    """C
    Given wordset it shows the stories
    :param request:
    :param wordset_id:
    :return:
    """
    word_set = get_object_or_404(WordSet, id=wordset_id)
    context = {'word_set': word_set, 'story_list': word_set.story_set.all()}
    return render(request, 'browse_mode/browse_story.html', context)


def show_word_meaning(request, word_id):
    word = get_object_or_404(Word, id=word_id)
    meaning = dict(word.text)
    return render(request, 'show_meaning.html', {"word": word, "word_info": meaning})


@transaction.atomic
def swap_like_wordset(request, wordset_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Please login first!!")

    wordset = get_object_or_404(WordSet, id=wordset_id)
    current_user = CustomUser.objects.get(pk=request.user.id)

    if wordset in current_user.starred_word_sets.all():
        current_user.starred_word_sets.remove(wordset)
        messages.info(request, 'You removed the star from the story!')
        return HttpResponseRedirect(reverse('home'))
    else:
        current_user.starred_word_sets.add(wordset)
        current_user.save()
        messages.info(request, 'You starred the wordset!')
        return HttpResponseRedirect(reverse('home'))

def see_leaderboard(request):
    return render(request, 'leaderboard.html')