from django.db import models
import string
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser

# NLP engine only loaded if needed
nlp_engine = None


def nlp(*args, **kwargs):
    """
    This method tokenizes the sentence
    """
    global nlp_engine
    if nlp_engine == None:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import spacy
            nlp_engine = spacy.load("en_core_web_sm")
    return nlp_engine(*args, **kwargs)


class Word(models.Model):
    text = models.CharField(max_length=30)

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("show_word_meaning", kwargs={'word_id': self.id})


class WordSet(models.Model):
    title = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    words = models.ManyToManyField(Word)
    creator = models.ForeignKey('accounts.CustomUser',
                                on_delete=models.CASCADE,
                                related_name='created_word_sets')
    starred_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='starred_word_sets')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("browse_wordset_stories", kwargs={'wordset_id': self.id})

    def get_like_url(self):
        return reverse("swap_like_wordset", kwargs={'wordset_id': self.id})


class Story(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        null=True)

    @classmethod
    def get_top_stories_ordered(cls):
        """
        TODO: Sort by rating!!
        :return:
        """
        stories = cls.objects.all()
        return list(stories)

    def get_sentence_set_with_vote(self):
        return self.sentence_set \
            .annotate(votes=models.Count('voted_users'))

    def get_selected_sentences(self, order):
        return self.sentence_set.filter(is_selected=True, order__lte=order) \
            .order_by('order')

    def get_stylized_last_two(self):
        """
        :return:
        """
        order = self.get_last_selected_index()
        if order == -1:
            return " "
        sentences = list(self.get_selected_sentences(order))
        return " ".join([i.stylized_text for i in sentences[-2:]])

    def get_stylized_text(self):
        """
        Gets the text for selected sentences for visualization
        """
        order = self.get_last_selected_index()
        if order == -1:
            return " "
        sentences = self.get_selected_sentences(order)
        return " ".join([i.stylized_text for i in sentences])

    def get_used_word_list(self, order):
        """
        TODO: Get used words until that order
        :param order:
        :return:
        """
        pass

    def get_last_selected_index(self):
        """
        :return: order of the last selected sentence, might be -1
        """
        selected = self.sentence_set.filter(is_selected=True).order_by('-order')
        if not selected.exists():
            return -1
        return selected[0].order

    def get_candidate_index(self):
        return self.get_last_selected_index() + 1

    def get_last_selected_time(self):
        """
        :return: time at which the last selected sentence was created
        """
        non_selected = self.sentence_set.filter(is_selected=True).order_by('-creation_date')
        if non_selected.exists():
            return non_selected[0].creation_date

        return timezone.now()

    def is_readable(self):
        if len(self.get_candidate_sentences(self.get_candidate_index())) != 0:
            return True
        return False

    def get_candidate_sentences(self, order):
        """
        :return: Last written sentences for the continuation of the story
        """
        if order < 0:
            return []
        return self.sentence_set.filter(order=order)

    def get_read_url(self):
        return reverse("read_story", kwargs={'story_id': self.id})

    def get_write_url(self):
        return reverse("write_story", kwargs={'story_id': self.id})

    def get_review_url(self):
        return reverse("review_story", kwargs={'story_id': self.id})


class Sentence(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
    stylized_text = models.CharField(max_length=300, null=True)
    order = models.IntegerField(default=0)  # Order in the story
    used_words = models.ManyToManyField(Word)  # Used words from the WordSet
    is_selected = models.BooleanField(default=False)
    # Story reference for the sentence
    story = models.ForeignKey(Story,
                              on_delete=models.CASCADE)
    voted_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='voted_sentences')

    # User reference for the sentence
    creator = models.ForeignKey('accounts.CustomUser',
                                on_delete=models.CASCADE,
                                related_name='created_sentences')

    @classmethod
    def create(cls, order, text, story, creator):
        """
        Matches wordset words of the text,
        adds punctuation if not exists
        """
        word_set = story.word_set
        text = str(text).strip()
        if len(text) < 3:
            return None
        text = text + '.' if text[-1] not in string.punctuation else text

        def get_dic_reference(id, t):
            text = "<a href='"\
                   +"/vocastory/show_meaning/"\
                   +str(id)\
                   +"/'>"
            text += t
            text += "</a>"
            return text

        sentence = cls(text=text, order=order, story=story, creator=creator)
        text_tokens = nlp(text)

        used_words = set()
        for t in text_tokens:
            t_l = t.lemma_.lower()
            found_words = word_set.words.filter(text=t_l)
            if found_words.exists():
                text = text.replace(
                    t.text,
                    get_dic_reference(found_words.first().id, t.text)
                )
            used_words.update(found_words)

        if len(used_words) == 0:
            sentence.delete()
            return None
        else:
            sentence.stylized_text = text
            sentence.save()
            for word in used_words:
                sentence.used_words.add(word)
            sentence.save()
        return sentence

    def vote_sentence(self, user):
        if user is None:
            return False

        if user not in self.voted_users.all():
            self.voted_users.add(user)
            return True
        return False

    def __str__(self):
        return self.text


class StoryReview(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('accounts.CustomUser',
                                on_delete=models.CASCADE,
                                related_name='review_set')
    story = models.ForeignKey(Story,
                              on_delete=models.CASCADE,
                              related_name='review_set')
    flag = models.BooleanField(default=False, null=True)
    coherence = models.IntegerField(default=0, null=True)
    creativity = models.IntegerField(default=0, null=True)
    fun = models.IntegerField(default=0, null=True)
    comment = models.CharField(null=True, max_length=250)

    class Meta:
        unique_together = ['creator', 'story']

    @classmethod
    def create_or_edit(cls, user, story, flag, coherence, creativity, fun, comment):

        review, _ = cls.objects.get_or_create(creator=user, story=story)
        review.flag = flag
        review.coherence = coherence
        review.creativity = creativity
        review.fun = fun
        review.comment = comment
        review.save()
        return review
