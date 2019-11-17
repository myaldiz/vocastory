from django.shortcuts import render
from django.http import HttpResponse, Http404
from browse_mode.models import Story
from .forms import SentenceInputForm


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


def browse_word_sets(request):
    """
    When clicked select random story to continue..
    :param request:
    :return:
    """
    return HttpResponse('Browse the word sets!')
