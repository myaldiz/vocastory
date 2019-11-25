from django import forms
#from multiselectfield import MultiSelectField

# REPORT_OPTIONS = (
#     ('key1', 'Spam'),
#     ('key2', 'Inappropriate'),
#     ('key3', 'Offensive'),
# )

class SentenceInputForm(forms.Form):
    sentence = forms.CharField(label='Write a sentence to continue the story', max_length=100)


class SentenceSelectForm(forms.Form):
    int_option = forms.IntegerField(label='Write the number of the sentence you want to select', min_value=1)


class StoryRatingForm(forms.Form):
    flag = forms.BooleanField(label='Report this story', required=False)
    coherence = forms.IntegerField(label='Coherence', min_value=1, max_value=10, required=False)
    creativity = forms.IntegerField(label='Creativity', min_value=1, max_value=10, required=False)
    fun = forms.IntegerField(label='Fun', min_value=1, max_value=10, required=False)

    #forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=REPORT_OPTIONS)