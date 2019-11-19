from django import forms

class SentenceInputForm(forms.Form):
    sentence = forms.CharField(label='Write a sentence to continue the story', max_length=100)
