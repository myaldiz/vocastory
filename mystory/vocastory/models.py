from django.db import models, transaction
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

    @classmethod
    def create(cls, text):
        """
        Processes a word into its base form
        """
        text_processed = text.strip().strip(string.punctuation) \
            .lower().split()[0]
        text = nlp(text_processed)
        word = cls(text=text.lemma_)
        word.save()
        return word

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

    @classmethod
    def get_top_wordsets_ordered(cls):
        stories = cls.objects \
            .annotate(
            num_stars=models.Count('starred_users')
        ).order_by('-num_stars')
        return list(stories)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("browse_wordset_stories", kwargs={'wordset_id': self.id})

    def get_like_url(self):
        return reverse("swap_like_wordset", kwargs={'wordset_id': self.id})

    # def get_is_liked(self, user):
    #     if user is not None and CustomUser.objects.get(id=user.id) in self.starred_users:
    #         return True
    #     else:
    #         return False


class Story(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        null=True)
    starred_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='starred_stories')

    @classmethod
    def get_top_stories_ordered(cls):
        stories = cls.objects \
            .annotate(num_stars=models.Count('starred_users')) \
            .order_by('-num_stars')
        return list(stories)

    def get_sentence_set_with_vote(self):
        return self.sentence_set \
            .annotate(votes=models.Count('voted_users'))

    def get_selected_sentences(self):
        return self.sentence_set.filter(is_selected=True) \
            .order_by('order')

    @transaction.atomic
    def get_stylized_last_two(self):
        """
        :return:
        """
        sentences = list(self.get_selected_sentences())
        return " ".join([i.stylized_text for i in sentences[-2:]])

    def get_stylized_text(self):
        """
        Gets the text for selected sentences for visualization
        """
        sentences = self.get_selected_sentences()
        return " ".join([i.stylized_text for i in sentences])

    @transaction.atomic
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

    @transaction.atomic
    def get_last_selected_time(self):
        """
        :return: time at which the last selected sentence was created
        """
        non_selected = self.sentence_set.filter(is_selected=True).order_by('-creation_date')
        if non_selected.exists():
            return non_selected[0].creation_date
        else:
            return timezone.now()

    @transaction.atomic
    def get_candidate_sentences(self):
        """
        :return: Last written sentences for the continuation of the story
        """
        return self.sentence_set.filter(order=self.get_candidate_index())

    # def check_completed(self):

    def check_time_and_select(self):
        """
        :return: nothing
        If sufficient time has elapsed, this method selects the sentence with most votes
        The time elapsed is the time of newest candidate-time of last selected sentence
        """
        sentences = self.sentence_set.order_by('-creation_date')
        if not sentences.exists():
            return

        last_sentence_time = sentences[0].creation_date
        delta = last_sentence_time - self.get_last_selected_time()

        if delta.seconds >= 30:
            sentences_with_votes = self.get_sentence_set_with_vote()
            candidates = sentences_with_votes.filter(order=self.get_candidate_index())
            candidates = candidates.order_by('-votes')
            with transaction.atomic():
                s = candidates[0]
                s.is_selected = True
                s.save()

    def get_read_url(self):
        return reverse("read_story", kwargs={'story_id': self.id})

    def get_write_url(self):
        return reverse("write_story", kwargs={'story_id': self.id})

    def get_review_url(self):
        return reverse("review_story", kwargs={'story_id': self.id})

    def get_like_url(self):
        return reverse("swap_like_story", kwargs={'story_id': self.id})

    # def get_is_liked(self, user):
    #     if user is not None and CustomUser.objects.get(id=user.id) in self.starred_users:
    #         return True
    #     else:
    #         return False



class Sentence(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
    stylized_text = models.CharField(max_length=300, null=True)
    order = models.IntegerField(default=0)  # Order in the story
    used_words = models.ManyToManyField(Word)  # Used words from the WordSet
    is_selected = models.BooleanField(default=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)  # story reference for the sentence
    voted_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='voted_sentences')

    # User reference for the sentence
    creator = models.ForeignKey('accounts.CustomUser',
                                on_delete=models.CASCADE,
                                related_name='created_sentences')

    @classmethod
    def create(cls, text, story, creator):
        """ TODO: Fix this
        Matches wordset words of the text,
        adds punctuation if not exists
        """
        order = story.get_candidate_index()
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

        with transaction.atomic():
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
                print(text)
                sentence.stylized_text = text
                sentence.save()
                for word in used_words:
                    sentence.used_words.add(word)
                sentence.save()
        return sentence

    @transaction.atomic
    def vote_sentence(self, user):
        if user is None:
            return False

        # if self.voted_users.filter(pk=user.id).exists():
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
        with transaction.atomic():
            review, _ = cls.objects.get_or_create(creator=user, story=story)
            review.flag = flag
            review.coherence = coherence
            review.creativity = creativity
            review.fun = fun
            review.comment = comment
            review.save()
        return review
