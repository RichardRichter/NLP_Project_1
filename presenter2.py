import json
import pickle
import spacy
import re
import nltk
#from googletrans import Translator, constants
#from pprint import pprint
#from textblob import TextBlob
def save_tweets(filename = 'tweets', raw_json='gg2013.json'):
    data = [tweet['text'] for tweet in json.load(open(raw_json))]
    with open(filename, 'wb') as test:
        pickle.dump(data,test)
def load_tweets(num_tweets=-1, filename='tweets'):
     with open(filename, 'rb') as tweets:
         data = pickle.load(tweets, encoding = 'utf-8')
         return data[0:(-1 if num_tweets > len(data) else num_tweets)]
def clean_the_tweets():
    dirty_tweets = load_tweets()
    #this removes hashtags
    clean_tweets = []
    cleansing_tweet = ""
    for tweet in dirty_tweets:
        #translator = Translator()
        cleansing_tweet = re.sub(r'\S*https\S*', "", tweet)
        #cleansing_tweet = re.sub(r'#\w*', "", cleansing_tweet)
        #cleansing_tweet = re.sub(r'@[^ ]*\b', "", cleansing_tweet)
        #translate = TextBlob(cleansing_tweet)
        #print(translate.detect_language())
        #language_used = translate.detect_language()
        #if language_used != 'en':
            #translation = translator.translate(cleansing_tweet)
            #print(translation.text)
        if cleansing_tweet[:4] == 'RT :':
            cleansing_tweet = cleansing_tweet[4:]
        clean_tweets.append(cleansing_tweet)     
    return clean_tweets
save_tweets()
class Category:
    def __init__(self, name):
        self.name = name
        self.nlp_name = ""
        self.presenters = {}
        self.nominees = {}
        stop_words = ['best', '-', 'in', 'a', 'by', 'an', 'or', 'made', "original"]
        words = name.lower().split(' ')
        self.keywords = [w for w in words if w not in stop_words]
        self.relevant_tweets = []
        self.less_relevant_tweets = []
        self.is_person = False
        self.person_identifier = ""
        self.contains_person()
        self.relevant_and_less_relevant_tweets()
        
        
    def contains_person(self):
        if 'actor' in self.keywords:
            if 'supporting' in self.keywords:
                self.person_identifier = "supporting actor"
            else: 
                self.person_identifier = "actor"
            self.is_person = True
            return
        if 'actress' in self.keywords:
            if 'supporting' in self.keywords:
               self.person_identifier = "supporting actress"
            else:
                self.person_identifier = "actress"
            self.is_person = True
            return
        if 'director' in self.keywords:
            self.person_identifier = "director"
            self.is_person = True
            return
        self.is_person = False
        return
    
    def match_score(self, tweet: str):
        matched_words = 0
        for word in self.keywords:
            if word in tweet.lower():
                matched_words += 1.0
        return matched_words / len(self.keywords)
    
    def relevant_and_less_relevant_tweets(self):
        tweets = clean_the_tweets()
        #print(tweets[0])
        if self.is_person == True:
            for tweet in tweets:
                if self.person_identifier in tweet:
                    match_score = self.match_score(tweet)
                    if match_score >= 0.70:
                        self.relevant_tweets.append(tweet) 
                    elif match_score >= 0.32:
                        self.less_relevant_tweets.append(tweet)
        else:
            for tweet in tweets:
                if 'actor' not in tweet and 'actress' not in tweet and 'director' not in tweet:
                    match_score = self.match_score(tweet)
                    if match_score >= 0.70:
                        self.relevant_tweets.append(tweet) 
                    elif match_score >= 0.32:
                        self.less_relevant_tweets.append(tweet)
    def find_presenter(self):
        #PRINT
        print(self.name)
        print(self.keywords)
        nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        ppl = {}
        pattern_better = re.compile(r'(present|presents|presenting|presenter|presenters|presented|presentation|presenta)')
        pattern_avoid = re.compile(r'(should|wish|want|need|desire)')
        print('you are in relevant tweets')
        for tweet in self.relevant_tweets:
            #print(tweet)
            #print(pattern_better.search(tweet))
            if pattern_better.search(tweet):
                if not pattern_avoid.search(tweet):
                    #print(tweet)
                    cap = (tweet.index(pattern_better.search(tweet).group(0)))
                    sub_section_tweet = tweet[:cap]
                    #print(sub_section_tweet)
                
                    tweet_list = list(sub_section_tweet.split(" "))
                    tags = nltk.pos_tag(tweet_list)
                    targets = ["NNP"]
                    only_nnps = list(filter(lambda x:x[1] in targets, tags))
                    #print("this is for nltk")
                    for x in range(0,len(only_nnps)):
                        #print(only_nnps[x][0])
                        person = only_nnps[x][0]
                        #print(person)
                        if " " in person:
                            if person[-2:] == "'s":
                                person = person[:-2]
                            if person in ppl:
                                ppl[person] = ppl[person]+1
                            else:
                                ppl[person] = 1
                    text = nlp(sub_section_tweet)
                    #print("this is for spacy")
                    for word in text.ents:
                        if word.label_ == 'PERSON':
                            person = word.text
                            if " " in person:
                                if person[-2:] == "'s":
                                    person = person[:-2]
                            #print(person)
                                if person in ppl:
                                    ppl[person] = ppl[person]+1
                                else:
                                    ppl[person] = 1 
            #if len(ppl) != 0:
             #   if pattern_worse.search(tweet):
             #       cap = (tweet.index(pattern_worse.search(tweet).group(0)))
             #       sub_section_tweet = tweet[:cap]
             #       tweet_list = list(sub_section_tweet.split(" "))
             #       tags = nltk.pos_tag(tweet_list)
             #       targets = ["NNP"]
             #       only_nnps = list(filter(lambda x:x[1] in targets, tags))
             #       for x in range(0,len(only_nnps)):
             #       #print(only_nnps[x][0])
             #           person = only_nnps[x][0]
             #           if person [-2:] == "'s":
             #               person = person[:-2]
             #           if person in ppl:
             #               ppl[person] = ppl[person]+1
             #           else:
             #               ppl[person] = 1
             #       text = nlp(sub_section_tweet)
             #       for word in text.ents:
             #           if word.label_ == 'PERSON':
             #               person = word.text
             #               if person in ppl:
             #                       ppl[person] = ppl[person]+1
             #               else:
             #                       ppl[person] = 1 
        if len(ppl) == 0:
            print("you are in less relevant tweets")
            for tweet in self.less_relevant_tweets:
                if pattern_better.search(tweet):
                #print(tweet)
                    cap = (tweet.index(pattern_better.search(tweet).group(0)))
                    sub_section_tweet = tweet[:cap]
                    #print(sub_section_tweet)
                    tweet_list = list(sub_section_tweet.split(" "))
                    tags = nltk.pos_tag(tweet_list)
                    targets = ["NNP"]
                    only_nnps = list(filter(lambda x:x[1] in targets, tags))
                    #print("this is for nltk")
                    for x in range(0,len(only_nnps)):
                        #print(only_nnps[x][0])
                        person = only_nnps[x][0]
                        #print(person)
                        if " " in person:
                            if person[-2:] == "'s":
                                person = person[:-2]
                            if person in ppl:
                                ppl[person] = ppl[person]+1
                            else:
                                ppl[person] = 1
                    text = nlp(sub_section_tweet)
                   # print("this is for spacy")
                    for word in text.ents:
                        if word.label_ == 'PERSON':
                            person = word.text
                            if " " in person:
                                if person[-2:] == "'s":
                                    person = person[:-2]
                            #print(person)
                                if person in ppl:
                                    ppl[person] = ppl[person]+1
                                else:
                                    ppl[person] = 1 
        #print("ppl: ", ppl)        
        if len(ppl) !=0:
            if "RT" in ppl.keys():
                del ppl["RT"]
            #print("ppl:", ppl)
            sorted_dict = sorted([(value, key) for (key, value) in ppl.items()])
            sorted_dict.sort(reverse=True)
            (votes, definitive_presenter) = sorted_dict[0]
            presenters = [definitive_presenter]
            keep_searching = True
            presenter_index = 1
            while keep_searching and len(sorted_dict)>1:
                if len(presenters) < 2:
                    (num_votes, potential_host) = sorted_dict[presenter_index]
                    if float(num_votes) / votes > 0.6:
                        presenters.append(potential_host)
                        keep_searching = False
                    else:
                        keep_searching = False
                    presenter_index += 1
            print(sorted_dict)
            print(presenters)
        else:
            print("NA")
        
                    

picture_director = Category("Best Director - Motion Picture")
picture_drama = Category("Best Motion Picture - Drama")
picture_actor_drama = Category("Best Actor in a Motion Picture - Drama")
picture_actress_drama = Category("Best Actress in a Motion Picture - Drama")
picture_musical_or_comedy = Category("Best Motion Picture - Musical or Comedy")
picture_actor_comedy = Category("Best Actor in a Motion Picture - Comedy Or Musical")
picture_actress_comedy = Category("Best Actress in a Motion Picture - Comedy Or Musical")
picture_actor_supporting = Category("Best Supporting Actor - Motion Picture")
picture_actress_supporting = Category("Best Supporting Actress - Motion Picture")
picture_screen_play= Category("Best Screenplay")
picture_score = Category("Best Original Score")
picture_song = Category("Best Original Song")
picture_foreign = Category("Best Foreign Language Film")
picture_animated = Category("Best Animated Feature Film")
picture_cecil = Category("Cecil B. DeMille Award for Lifetime Achievement in Motion Pictures")
tv_drama = Category("Best Television Series - Drama")
tv_actor_drama = Category("Best Actor In A Television Series - Drama")
tv_actress_drama = Category("Best Actress In A Television Series - Drama")
tv_comedy = Category("Best Television Series - Comedy Or Musical")
tv_actor_comedy = Category("Best Actor In A Television Series - Comedy Or Musical")
tv_actress_comedy = Category("Best Actress In A Television Series - Comedy Or Musical")
tv_miniseries = Category("Best Mini-Series or Television Film")
tv_miniseries_actor = Category("Best Actor - Mini-Series Television Film")
tv_miniseries_actress = Category("Best Actress - Mini-series Television Film")
tv_miniseries_actor_supporting = Category("Best Supporting Actor - Series, Mini-Series or Television Film")
tv_miniseries_actress_supporting = Category("Best Supporting Actress - Series, Mini-Series or Television Film")

tv_miniseries_actor.find_presenter()
tv_actress_comedy.find_presenter()
tv_miniseries_actor_supporting.find_presenter()
picture_director.find_presenter()
tv_miniseries_actress.find_presenter()
tv_miniseries.find_presenter()
picture_actress_drama.find_presenter()
picture_actor_drama.find_presenter()
picture_animated.find_presenter()
picture_actor_supporting.find_presenter()
picture_cecil.find_presenter()
tv_comedy.find_presenter()
picture_actress_comedy.find_presenter()
tv_actress_drama.find_presenter()
picture_actress_supporting.find_presenter()
picture_actor_comedy.find_presenter()
tv_actor_drama.find_presenter()
tv_drama.find_presenter()
picture_musical_or_comedy.find_presenter()
tv_actor_comedy.find_presenter()
picture_score.find_presenter()
picture_song.find_presenter()
picture_screen_play.find_presenter()
tv_miniseries_actress_supporting.find_presenter()
picture_drama.find_presenter()
picture_foreign.find_presenter()
