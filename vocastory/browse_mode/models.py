from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=25)
    # We may use some float descriptor in the future
    # descriptor = models.CharField(max_length=25)
    # TODO: Override init function to lower-case and remove spaces
    def __str__(self):
        return self.text

class WordSet(models.Model):
    title = models.CharField(max_length=50)
    creation_date = models.DateTimeField('date created')
    words = models.ManyToManyField(Word)

    def __str__(self):
        return self.title


class Sentence(models.Model):
    text = models.CharField(max_length=200)
    # Order in the story
    order = models.IntegerField(default=0)
    # Number of votes in the selection process
    votes = models.IntegerField(default=0)
    # Used words from the WordSet
    used_words = models.ManyToManyField(Word)
    # Is this sentence selected as part of the story
    is_selected = models.BooleanField(default=False)


    def process_used_words(self):
        """
        This method checks the used words in the sentence
        :return:
        """
        pass

    def __str__(self):
        return self.text


class Story(models.Model):
    completed = models.BooleanField(default=False)
    start_date = models.DateTimeField('date started')
    creation_date = models.DateTimeField('date created')
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)
    sentences = models.ManyToManyField(Sentence)

    def process_story_text(self):
        """
        :return: string of the story written so far
        """
        pass