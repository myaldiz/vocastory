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


class Story(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    start_date = models.DateTimeField('date started')
    creation_date = models.DateTimeField('date created')
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)

    def get_selected_sentences(self):
        """
        Returns the sentences voted and selected by user
        :return:
        """
        return self.sentence_set.filter(is_selected=True).order_by('order')


    def get_text(self):
        """
        Gets the text for selected sentences for visualization
        :return:
        """
        sentences = self.get_selected_sentences()
        text = " ".join([i.text for i in sentences])
        return text


    def get_last_two(self):
        sentences = self.get_selected_sentences()
        return " ".join([str(i) for i in list(sentences)[-2:]])


    def get_candidate_sentences(self):
        non_selected = self.sentence_set.filter(is_selected=False).order_by('-order')
        last_idx = non_selected[-1].order

        # No new sentence is written
        if self.sentence_set.filter(is_selected=True, order=last_idx).exists():
            return []

        return self.sentence_set.filter(is_selected=False, order=last_idx)






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
    # story reference for the sentence
    story = models.ForeignKey(Story, on_delete=models.CASCADE)


    def process_used_words(self):
        """
        This method checks the used words in the sentence
        :return:
        """
        # self.story.word_set.all()
        pass

    def __str__(self):
        return self.text
