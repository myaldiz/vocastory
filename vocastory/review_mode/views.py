from django.shortcuts import render
from django.http import HttpResponse
from browse_mode.models import Story

from django.http import Http404


def review_story(request, story_id):
    try:
        story = Story.objects.get(pk=story_id)

        context = {'story': story, 'story_text': story.get_text()}


    except Story.DoesNotExist:
        raise Http404("Story does not exists!!")

    return render(request, 'review_mode/review_story.html', context)
