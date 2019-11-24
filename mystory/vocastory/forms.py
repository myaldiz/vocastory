from django import forms

class SentenceInputForm(forms.Form):
    sentence = forms.CharField(label='Write a sentence to continue the story', max_length=100)
class SentenceSelectForm(forms.Form):
    int_option = forms.IntegerField(label='Write the number of the sentence you want to select', min_value=1)
    #int_option = forms.CharField(label='Write the number of the sentence you want to select', max_length=2)