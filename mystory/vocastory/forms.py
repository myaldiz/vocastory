from django import forms


class SentenceInputForm(forms.Form):
    sentence = forms.CharField(label='Write a sentence to continue the story', widget=forms.Textarea, max_length=200)


# class WordSetInputForm(forms.Form):
#     sentence = forms.CharField(label='Write words to create word list', max_length=200)


class SentenceSelectForm(forms.Form):
    sentence_choice = forms.ChoiceField(label="Choices", widget=forms.RadioSelect)


class StoryRatingForm(forms.Form):
    flag = forms.BooleanField(label='Report this story', required=False)
    coherence = forms.IntegerField(label='Coherence', min_value=1, max_value=10)
    creativity = forms.IntegerField(label='Creativity', min_value=1, max_value=10)
    fun = forms.IntegerField(label='Fun', min_value=1, max_value=10)
    comment = forms.CharField(label='Comment', max_length=200, widget=forms.Textarea, required=False)
