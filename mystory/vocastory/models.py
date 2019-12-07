import string
from django.utils import timezone
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Length
from django.db.models import CharField
from django.urls import reverse

from accounts.models import CustomUser

# NLP engine only loaded if needed
nlp_engine = None
CharField.register_lookup(Length, 'len')


def nlp(*args, **kwargs):
    """
    This method tokenizes the sentence
    """
    global nlp_engine
    if nlp_engine is None:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import spacy
            nlp_engine = spacy.load("en_core_web_sm")
    return nlp_engine(*args, **kwargs)


class Word(models.Model):
    text = CharField(max_length=30)

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("show_word_meaning", kwargs={'word_id': self.id})


class WordSet(models.Model):
    title = CharField(max_length=50)
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
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        null=True)

    @classmethod
    def get_stories_scored(cls):
        stories = cls.objects.filter(completed=True).annotate(
            q_score=
            models.Avg('review_set__coherence')
            + models.Avg('review_set__creativity')
            + models.Avg('review_set__fun'),
            p_score=models.Count(
                'review_set',
                filter=Q(review_set__comment__len__gte=5),
                output_field=models.FloatField(),
                distinct=True),
            score=F('q_score') + F('p_score'),
        )
        return stories

    @classmethod
    def get_top_stories_ordered(cls):
        return cls.get_stories_scored().order_by('-score')


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

    def get_used_word_list(self):
        order = self.get_last_selected_index()
        sentences = self.get_selected_sentences(order)
        used_words = set()
        for sentence in sentences:
            used_words.update(set(sentence.used_words.all()))
        return list(used_words)

    def get_unused_word_list(self):
        used_words = set(self.get_used_word_list())
        all_words = set(self.word_set.words.all())
        return list(all_words.difference(used_words))

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

    def is_readable(self, user):
        if self.completed:
            return False
        candidates = self.get_candidate_sentences(self.get_candidate_index())
        candidates = candidates.exclude(creator=user)
        candidate_ids = candidates.values_list('pk', flat=True)
        if user.voted_sentences.filter(pk__in=candidate_ids).exists():
            return False
        if candidates.exists():
            return True
        return False

    def is_writable(self, user):
        if self.completed:
            return False
        candidates = self.get_candidate_sentences(self.get_candidate_index())
        if candidates.filter(creator=user).exists():
            return False
        return True

    def is_reviewable(self, user):
        if not self.completed:
            return False

        if self.review_set.filter(creator=user).exists():
            return False
        return True

    def get_candidate_sentences(self, order):
        """
        :return: Last written sentences for the continuation of the story
        """
        if order < 0:
            return []
        return self.sentence_set.filter(order=order)

    def close_sentence_poll(self):
        if self.completed:
            return
        order = self.get_candidate_index()
        candidate_sentences = self.get_candidate_sentences(order)
        if len(candidate_sentences) == 0:
            return
        candidate_sentences = candidate_sentences.order_by('-creation_date')
        delta = timezone.now() - candidate_sentences[0].creation_date
        candidate_sentences = candidate_sentences \
            .annotate(votes=models.Count('voted_users')).order_by('-votes')

        # if delta > timezone.timedelta(minutes=30) \
        #         or candidate_sentences[0].votes > 3 \ 
        #         or (delta > timezone.timedelta(minutes=15) and candidate_sentences[0].votes > 1):
        if delta > timezone.timedelta(minutes=2) \
                or candidate_sentences[0].votes > 3 \
                or (delta > timezone.timedelta(minutes=1) and candidate_sentences[0].votes > 1):
            sentence = Sentence.objects.get(id=candidate_sentences[0].id)
            sentence.is_selected = True
            sentence.save()

    def finish_story(self):
        if len(self.get_unused_word_list()) == 0:
            self.completed = True
            self.save()

    def get_read_url(self):
        return reverse("read_story", kwargs={'story_id': self.id})

    def get_write_url(self):
        return reverse("write_story", kwargs={'story_id': self.id})

    def get_review_url(self):
        return reverse("review_story", kwargs={'story_id': self.id})


class Sentence(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    text = CharField(max_length=200)
    stylized_text = CharField(max_length=300, null=True)
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
            text = "<a href='" \
                   + "/vocastory/show_meaning/" \
                   + str(id) \
                   + "/'>"
            text += t
            text += "</a>"
            return text

        sentence = cls(text=text, order=order, story=story, creator=creator)
        text_tokens = nlp(text)
        used_words = set()
        for t in text_tokens:
            t_l = t.lemma_.lower()
            found_words = word_set.words.filter(text=t_l)
            found_exact = word_set.words.filter(text=t.text.lower())
            if found_words.exists():
                text = text.replace(
                    t.text,
                    get_dic_reference(found_words.first().id, t.text)
                )
                used_words.update(found_words)
            elif found_exact.exists():
                text = text.replace(
                    t.text,
                    get_dic_reference(found_exact.first().id, t.text)
                )
                used_words.update(found_exact)

        if len(used_words) == 0:
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
    comment = CharField(null=True, max_length=250)

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
