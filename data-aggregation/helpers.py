"""
Helper objects/functions for data cleaning and aggregation
"""
import re
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dateutil import parser
from collections import defaultdict
import string

"""
Extractor object used to clean email data. Content stopwords are not included in
this repo for security reasons.
"""
class Extractor():
    def __init__(self, columns_of_interest, content_topics=None, parent_dir=False):
        self.club_names = get_list_names(parent_dir)
        self.sia = SentimentIntensityAnalyzer()
        self.columns = set(columns_of_interest)
        self.topic_mapping = {'arts': 0, 'athletics': 1, 'culture': 2,
                            'miscellaneous': 3, 'politics': 4, 'preprofessional': 5, 'service': 6}

        # if the content_topics argument is passed in, load in the according stopwords
        if content_topics is not None:
            self.stopwords = set(nltk.corpus.stopwords.words("english"))
            if 'semitism' in content_topics:
                self.semitism_stopwords = []
                f = open("./content-stopwords/semitism.txt", "r")
                for x in f:
                    self.semitism_stopwords.append(x.strip())
            if 'crypto' in content_topics:
                self.crypto_stopwords = []
                f = open("./content-stopwords/crypto.txt", "r")
                for x in f:
                    self.crypto_stopwords.append(x.strip())
            if 'felipes' in content_topics:
                self.felipes_stopwords = []
                f = open("./content-stopwords/felipes.txt", "r")
                for x in f:
                    self.felipes_stopwords.append(x.strip())
            if 'jefes' in content_topics:
                self.jefes_stopwords = []
                f = open("./content-stopwords/jefes.txt", "r")
                for x in f:
                    self.jefes_stopwords.append(x.strip())


    # parse meta data for an individual email
    def get_email_info(self, entry, topic_model=False):
        # base parsing
        id = entry['id']

        # if preprocessing for topic model, just return the combined subject and content
        if topic_model:
            content = reformat(entry['content'])
            subject = reformat(entry['subject'])
            d = {'id': id,
                'content': content,
                'subject': subject}
        else:
            content = reformat(entry['content'])
            subject = reformat(entry['subject'])
            to = self.extract_email_address(entry['to'])
            from_ = self.extract_email_address(entry['from'])
            parent = entry['parent-id']
            timestamp = None
            # sometimes the data is nan, ignore
            try:
                timestamp =  parser.parse(entry['date'])
            except:
                timestamp = None

            length = 0
            if isinstance(content, str):
                length = len(content)

            # initialize output dictionary
            d = {'id': id,
                'to': to,
                'from': from_,
                'parent': parent,
                'timestamp': timestamp,
                'content-length': length,
                'to-affiliation': self.extract_affiliation(to),
                'from-affiliation': self.extract_affiliation(from_)}


            # determine topic
            # create sets of topic words
            self.service_keywords = set([])
            f = open("./content-stopwords/topic-keywords/service.txt", "r")
            for x in f:
                self.service_keywords.add(x.lower().strip())
            f.close()
            self.arts_keywords = set([])
            f = open("./content-stopwords/topic-keywords/creative-and-performing-arts.txt", "r")
            for x in f:
                self.arts_keywords.add(x.lower().strip())
            f.close()
            self.culture_keywords = set([])
            f = open("./content-stopwords/topic-keywords/culture-and-identity.txt", "r")
            for x in f:
                self.culture_keywords.add(x.lower().strip())
            f.close()
            self.politics_keywords = set([])
            f = open("./content-stopwords/topic-keywords/government-and-politics.txt", "r")
            for x in f:
                self.politics_keywords.add(x.lower().strip())
            f.close()
            self.athletics_keywords = set([])
            f = open("./content-stopwords/topic-keywords/athletics.txt", "r")
            for x in f:
                self.athletics_keywords.add(x.lower().strip())
            f.close()
            self.preprofessional_keywords = set([])
            f = open("./content-stopwords/topic-keywords/preprofessional-opportunities.txt", "r")
            for x in f:
                self.preprofessional_keywords.add(x.lower().strip())
            f.close()
            d['topic'] = self.topic_mapping[self.categorize_topic(content)]

            # find affiliation
            affiliation = self.extract_club_affiliation(to, from_)
            d['affiliation'] = affiliation
            # calculate sentiments
            subject_sentiments = self.calculate_content_sentiment(subject)
            content_sentiments = self.calculate_content_sentiment(content)

            # expand so that each sentiment float has its own column
            if subject_sentiments is not None:
                d['sub-neg'] = subject_sentiments['neg']
                d['sub-neu'] = subject_sentiments['neu']
                d['sub-pos'] = subject_sentiments['pos']
                d['sub-com'] = subject_sentiments['compound']
            else:
                d['sub-neg'] = 0
                d['sub-neu'] = 0
                d['sub-pos'] = 0
                d['sub-com'] = 0
            if content_sentiments is not None:
                d['con-neg'] = content_sentiments['neg']
                d['con-neu'] = content_sentiments['neu']
                d['con-pos'] = content_sentiments['pos']
                d['con-com'] = content_sentiments['compound']
            else:
                d['con-neg'] = 0
                d['con-neu'] = 0
                d['con-pos'] = 0
                d['con-com'] = 0

            # find word frequency distributions
            con_word_freq = self.find_word_freq(content)
            sub_word_freq = self.find_word_freq(subject)

            # count relevant stopwords
            content_semitic_word_freq = self.count_semitic_stopwords(con_word_freq)
            content_crypto_word_freq = self.count_crypto_stopwords(con_word_freq)
            subject_semitic_word_freq = self.count_semitic_stopwords(sub_word_freq)
            subject_crypto_word_freq = self.count_crypto_stopwords(sub_word_freq)
            content_felipes_word_freq = self.count_felipes_stopwords(con_word_freq)
            content_jefes_word_freq = self.count_jefes_stopwords(con_word_freq)
            subject_felipes_word_freq = self.count_felipes_stopwords(sub_word_freq)
            subject_jefes_word_freq = self.count_jefes_stopwords(sub_word_freq)

            # expand to output dictionary
            d['con-semitic-wf'] = content_semitic_word_freq
            d['con-crypto-wf'] = content_crypto_word_freq
            d['sub-semitic-wf'] = subject_semitic_word_freq
            d['sub-crypto-wf'] = subject_crypto_word_freq

            d['con-felipes-wf'] = content_felipes_word_freq
            d['con-jefes-wf'] = content_jefes_word_freq
            d['sub-felipes-wf'] = subject_felipes_word_freq
            d['sub-jefes-wf'] = subject_jefes_word_freq

        return d


    # count keywords in an email's content, categorize the topic
    def categorize_topic(self, text):
        if isinstance(text, float):
            return 'miscellaneous'
        topic_wf_dict = defaultdict(lambda: 0)
        text = text.lower()
        words = text.split()
        num_words = len(words)
        for word in words:
            word = word.translate(str.maketrans('', '', string.punctuation))
            if word in self.service_keywords:
                topic_wf_dict['service'] += 1
            elif word in self.arts_keywords:
                topic_wf_dict['arts'] += 1
            elif word in self.culture_keywords:
                topic_wf_dict['culture'] += 1
            elif word in self.politics_keywords:
                topic_wf_dict['politics'] += 1
            elif word in self.athletics_keywords:
                topic_wf_dict['athletics'] += 1
            elif word in self.preprofessional_keywords:
                topic_wf_dict['preprofessional'] += 1
        topic = 'miscellaneous'
        # use the highest count value to categorize
        highest_value = 1
        for key in topic_wf_dict:
            if topic_wf_dict[key] > highest_value:
                highest_value = topic_wf_dict[key]
                topic = key
        return topic


    # find word frequency distribution of given text
    def find_word_freq(self, text):
        if not isinstance(text, str):
            return defaultdict(lambda: 0)
        # replace hyphens
        text = text.replace('-', '')
        # tokenize
        word_list = nltk.word_tokenize(text)
        # remove punctuation
        word_list = [w for w in word_list if w.isalpha()]
        # remove stopwords
        word_list = [w for w in word_list if w.lower() not in self.stopwords]
        # make everything lowercase
        word_list = [w.lower() for w in word_list]
        # calculate word frequency distribution
        return nltk.FreqDist(word_list)

    # count stopwords relating to Felipe's
    def count_felipes_stopwords(self, fd):
        counter = 0
        for stopword in self.felipes_stopwords:
            counter += fd[stopword]
        return counter

    # count stopwords relating to Jefe's
    def count_jefes_stopwords(self, fd):
        counter = 0
        for stopword in self.jefes_stopwords:
            counter += fd[stopword]
        return counter

    # count stopwords relating to anti-semitism
    def count_semitic_stopwords(self, fd):
        counter = 0
        for stopword in self.semitism_stopwords:
            counter += fd[stopword]
        return counter

    # count stopwords relating to crypto
    def count_crypto_stopwords(self, fd):
        counter = 0
        for stopword in self.crypto_stopwords:
            counter += fd[stopword]
        return counter


    # baseline email parsing
    def parse(self, entry):
        # base parsing
        id = entry['id']
        to = self.extract_email_address(entry['to'])
        from_ = self.extract_email_address(entry['from'])
        parent = entry['parent-id']
        subject = entry['subject']

        # output dictionary
        d = {'id': id, 'to': to, 'from': from_, 'parent': parent, 'subject': subject}

        # only calculate columns specified from csv_aggregation.py
        if 'affiliation' in self.columns:
            d['to-affiliation'] = self.extract_affiliation(to)
            d['from-affiliation'] = self.extract_affiliation(from_)
        if 'num_club_affiliations' in self.columns:
            d['club-affiliation'] = self.extract_club_affiliation(to, from_)
        if 'avg_sent_sentiment' in self.columns or 'avg_received_sentiment' in self.columns:
            # remove delimiters from text content that were added for the scp process
            entry['content'] = reformat(entry['content'])
            d['content-sentiment'] = self.calculate_content_sentiment(entry['content'])
        if 'timestamps' in self.columns:
            d['timestamp'] = self.extract_mail_timestamp(entry['date'])
        if 'avg_sent_content_length' in self.columns:
            entry['content'] = reformat(entry['content'])
            d['content-length'] = self.calculate_content_length(entry['content'])

        return d


    # use regex to extract the email address
    def extract_email_address(self, text):
        # if nan value
        if isinstance(text, float):
            return -1
        # search for email
        match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        # sometimes undisclosed recipients
        if match is None:
            return text
        return match.group(0)


    # calculate the length of an email's content
    def calculate_content_length(self, text):
        try:
            return len(text)
        except:
            return 0


    # use nltk polarity scoring to compute email content sentiment
    def calculate_content_sentiment(self, text):
        # use nltk's built-in sentiment model to calculate positive, neutral, negative, and compounds scores
        sentiment = None
        # if there is no content, skip over. The None value is handled by csv_aggregation.py
        try:
            sentiment = self.sia.polarity_scores(text)
        except:
            pass
        return sentiment



    def extract_mail_timestamp(self, text):
        return 0


    # extract the domain affiliation of an email
    def extract_affiliation(self, text):
        if isinstance(text, int):
            return ""
        try:
            # sometimes carrots or double quotes remain at the end, so replace with emtpy string. This will not throw an error.
            return text.split('@')[1].replace(">", "").replace('"', '')
        except:
            return ""


    # extract the club affiliation of a listserv email address
    def extract_club_affiliation(self, to, from_):
        to_email, from_email = "", ""
        try:
            to_email = to[:to.index('@')]
        except Exception:
            pass

        try:
            from_email = from_[:from_.index('@')]
        except Exception:
            pass

        if to_email in self.club_names:
            return to_email
        elif from_email in self.club_names:
            return from_email

        return ""


# extract an email address from input text 
def extract_email_address(text):
    # if nan value
    if isinstance(text, float):
        return -1
    # search for email
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    # sometimes undisclosed recipients
    if match is None:
        return text
    return match.group(0)


# helper function to swap keys and values of a dictionary
def swap_keys_values(dictionary):
    swapped_dict = {value: key for key, value in dictionary.items()}
    return swapped_dict


# merge two nx graphs
def merge_graphs(graph1, graph2):
    graph1.nodes.update(graph2.nodes)
    for node in graph1.graph:
        if node in graph2.graph:
            graph1.graph[node] = graph1.graph[node] + graph2.graph[node]
    for node in graph2.graph:
        if node not in graph1.graph:
            graph1.graph[node] = graph2.graph[node]
    return graph1


# load club names from disk
def get_list_names(parent_dir=False):
    club_names = set([])
    listnames_path = None
    if parent_dir:
        listnames_path = '../metadata/HCS-listnames.txt'
    else:
        listnames_path = './metadata/HCS-listnames.txt'
    f = open(listnames_path, 'r')
    for x in f:
        # get rid of delimiter character at the end
        club_names.add(x[:-1])
    return club_names


# text reformatting after scp'ing from AWS
def reformat(text):
    # replace delimiter that was added for scp'ing
    # sometimes text is nan, in which case just return it. It will be handled by the Extractor
    try:
        return text.replace(":|:", " ")
    except:
        return text


# extract the affiliation domain from an email address
def extract_affiliation(text):
    if isinstance(text, int):
        return ""
    try:
        # sometimes carrots or double quotes remain at the end, so replace with emtpy string. This will not throw an error.
        return text.split('@')[1].replace(">", "").replace('"', '')
    except:
        return ""
