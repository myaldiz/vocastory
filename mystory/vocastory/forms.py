from django import forms
#from multiselectfield import MultiSelectField

REPORT_OPTIONS = (
    ('key1', 'Spam'),
    ('key2', 'Inappropriate'),
    ('key3', 'Offensive'),
)

class SentenceInputForm(forms.Form):
    sentence = forms.CharField(label='Write a sentence to continue the story', max_length=100)

class SentenceSelectForm(forms.Form):
    int_option = forms.IntegerField(label='Write the number of the sentence you want to select', min_value=1)

class StoryRatingForm(forms.Form):
    rating = forms.IntegerField(label='Enter a rating between 1 and 10 for the story', min_value=1, max_value=10)
    report = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=REPORT_OPTIONS)
#class ReportForm(forms.Form):
    #report = forms.MultiSelectField(widget=forms.CheckboxSelectMultiple, choices=REPORT_OPTIONS)