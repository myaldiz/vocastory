from django.db import models, transaction
import string
from datetime import timedelta

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
        text_processed = text.strip().strip(string.punctuation)\
            .lower().split()[0]
        text = nlp(text_processed)
        return cls(text=text.lemma_)

    def __str__(self):
        return self.text


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
        stories = cls.objects\
            .annotate(
            num_stars=models.Count('starred_users')
        ).order_by('-num_stars')
        return list(stories)

    def __str__(self):
        return self.title


class Story(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    word_set = models.ForeignKey(
        WordSet,
        on_delete=models.CASCADE,
        null=True
    )
    starred_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='starred_stories')

    def get_sentence_set_with_vote(self):
        return self.sentence_set.\
            annotate(votes=models.Count('voted_users'))

    @classmethod
    def get_top_stories_ordered(cls):
        stories = cls.objects.\
            annotate(num_stars=models.Count('starred_users')).\
            order_by('-num_stars')
        return list(stories)

    def get_selected_sentences(self):
        """
        Returns the sentences voted and selected by users
        """
        return self.sentence_set.filter(is_selected=True).order_by('order')


    def get_text(self):
        """
        Gets the text for selected sentences for visualization
        """
        sentences = self.get_selected_sentences()
        text = " ".join([i.text for i in sentences])
        return text


    def get_last_two(self):
        """
        :return: text of the last two selected sentence
        """
        sentences = self.get_selected_sentences()
        return " ".join([str(i) for i in list(sentences)[-2:]])

    def get_last_idx(self):
        """
        :return: order of the last selected sentence
        """
        non_selected = self.sentence_set.filter(is_selected=True).order_by('-order')
        return non_selected[0].order

    def get_last_time(self):
        """
        :return: time at which the last selected sentence was created
        """
        non_selected = self.sentence_set.filter(is_selected=True).order_by('-creation_date')
        return non_selected[0].creation_date

    def get_candidate_sentences(self):
        """
        :return: Last written sentences for the continuation of the story
        """
        non_selected = self.sentence_set.filter(is_selected=False).order_by('-order')
        last_idx = non_selected[0].order

        # No new sentence is written
        if self.sentence_set.filter(is_selected=True, order=last_idx).exists():
            return []

        return self.sentence_set.filter(order=last_idx).order_by('creation_date')

    def check_time_and_select(self):
        """
        :return: nothing
        If sufficient time has elapsed, this method selects the sentence with most votes
        The time elapsed is the time of newest candidate-time of last selected sentence
        """
        sentences = self.sentence_set.order_by('-creation_date')
        max_time = sentences[0].creation_date
        delta=max_time-self.get_last_time()
        if delta.seconds>=120:    
            sentences_with_votes=self.get_sentence_set_with_vote()
            candidates = sentences_with_votes.filter(order=self.get_last_idx()+1)
            candidates=candidates.order_by('-votes')
            s=candidates[0]
            selected_sentence=Sentence(text=s.text, is_selected=True, order=self.get_last_idx()+1, story=self)
            selected_sentence.save()
            
            

class Sentence(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
    order = models.IntegerField(default=0)  # Order in the story
    used_words = models.ManyToManyField(Word)   # Used words from the WordSet
    is_selected = models.BooleanField(default=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)  # story reference for the sentence
    voted_users = models.ManyToManyField(
        'accounts.CustomUser',
        related_name='voted_sentences')

    # User reference for the sentence
    creator = models.ForeignKey('accounts.CustomUser',
                                on_delete=models.CASCADE,
                                related_name='created_sentences',
                                null=True)


    @classmethod
    def create(cls, text, order, story, creator, wordset):
        """
        Matches wordset words of the text,
        adds punctuation if not exists
        """
        text = str(text).strip()
        if len(text) < 3:
            return None
        text = text+'.' if text[-1] not in string.punctuation else text

        # Make sure it is atomic
        with transaction.atomic():
            sentence = cls(text=text, order=order, story=story, creator=creator)
            sentence.save()
            text_tokens = nlp(text)

            # if WordSet is provided, check for matches
            if isinstance(wordset, WordSet):
                used_words = set()
                for t in text_tokens:
                    t = t.lemma_.lower()
                    found_words = wordset.words.filter(text=t)
                    used_words.update(found_words)

                for word in used_words:
                    sentence.used_words.add(word)

        return sentence

    
    def vote_sentence(self, user):
        if user == None:
            return False
        
        #if self.voted_users.filter(pk=user.id).exists():
        if user not in self.voted_users.all():
            self.voted_users.add(user)
        


    def __str__(self):
        return self.text
