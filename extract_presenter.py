class Category:
    def __init__(self, name):
        self.name = name
        self.nlp_name = ""
        self.presenters = {}
        self.nominees = {}
        stop_words = ['-', 'in', 'a', 'by', 'an', 'or', 'made', 'for']
        words = name.lower().split(' ')
        self.keywords = [w for w in words if w not in stop_words]
        self.relevant_tweets = []
        self.less_relevant_tweets = []
    def match_score(self, tweet: str):
        matched_words = 0
        for word in self.keywords:
            if word in tweet.lower():
                matched_words += 1.0
        return matched_words / len(self.keywords)
    def relevant_and_less_relevant_tweets(self):
        tweets = load_tweets()
        for tweet in tweets:
            match_score = self.match_score(tweet)
            if match_score >= 0.80:
                self.relevant_tweets.append(tweet) 
            if match_score >= 0.5:
                self.less_relevant_tweets.append(tweet) 
    def find_presenter(self):
        #PRINT
        print(self.name)
        tweets = load_tweets()
        self.relevant_and_less_relevant_tweets()
        if len(self.relevant_tweets) == 0:
            self.relevant_tweets = self.less_relevant_tweets      
        #PRINT
        # print(len(self.relevant_tweets))
        nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        ppl = {}
        pattern_better = re.compile(r'\b(presents|presenting|presenter|presenters|announce|announces|announced)\b')
        pattern_worse = re.compile(r'\bannounced\b|\bintroduced\b')
        for tweet in self.relevant_tweets:
            if pattern_better.search(tweet):
                #print(tweet)
                cap = (tweet.index(pattern_better.search(tweet).group(0)))
                #print(cap)
                #for x in range (cap, -1,-1):
                #    potential_names.append(tweet[x:cap])
                sub_section_tweet = tweet[:cap]
                #print(sub_section_tweet)
                text = nlp(sub_section_tweet)
                for word in text.ents:
                    if word.label_ == 'PERSON':
                        person = word.text
                        if person in ppl:
                            ppl[person] = ppl[person]+1
                        else:
                            ppl[person] = 1 
#            if pattern_worse.search(tweet):
#                print("match tweet")
#                print(tweet)
#                text = nlp(tweet)
#                for word in text.ents:
#                    if word.label_ == 'PERSON':
#                        person = word.text
#                        if person in ppl:
#                            ppl[person] = ppl[person]+1
#                        else:
#                            ppl[person] = 1
                
        if len(ppl) !=0:
            sorted_dict = sorted([(value, key) for (key, value) in ppl.items()])
            sorted_dict.sort(reverse=True)
            (votes, definitive_presenter) = sorted_dict[0]
            presenters = [definitive_presenter]
            keep_searching = True
            presenter_index = 1
            while keep_searching and len(sorted_dict)>1:
                (num_votes, potential_host) = sorted_dict[presenter_index]
                if float(num_votes) / votes > 0.8:
                    presenters.append(potential_host)
                    keep_searching = False
                else:
                    keep_searching = False
                presenter_index += 1
            print(presenters)
        else:
            print("NA")
        #print(count)
        #if len(sorted_dict) !=0:
        #    print(sorted_dict[0])
        #else:
        #    print("NA")
                    

picture_director = Category("Best Director - Motion Picture")

picture_drama = Category("Best Motion Picture - Drama")
picture_actor_drama = Category("Best Performance by an Actor in a Motion Picture - Drama")
picture_actress_drama = Category("Best Performance by an Actress in a Motion Picture - Drama")

picture_musical_or_comedy = Category("Best Motion Picture - Musical or Comedy")
picture_actor_comedy = Category("Best Performance by an Actor in a Motion Picture - Comedy Or Musical")
picture_actress_comedy = Category("Best Performance by an Actress in a Motion Picture - Comedy Or Musical")

picture_actor_supporting = Category("Best Performance by an Actor In A Supporting Role in a Motion Picture")
picture_actress_supporting = Category("Best Performance by an Actress In A Supporting Role in a Motion Picture")

picture_screen_play= Category("Best Screenplay - Motion Picture")
picture_score = Category("Best Original Score - Motion Picture")
picture_song = Category("Best Original Song - Motion Picture")
picture_foreign = Category("Best Foreign Language Film")
picture_animated = Category("Best Animated Feature Film")
picture_cecil = Category("Cecil B. DeMille Award for Lifetime Achievement in Motion Pictures")

tv_drama = Category("Best Television Series - Drama")
tv_actor_drama = Category("Best Performance by an Actor In A Television Series - Drama")
tv_actress_drama = Category("Best Performance by an Actress In A Television Series - Drama")

tv_comedy = Category("Best Television Series - Comedy Or Musical")
tv_actor_comedy = Category("Best Performance by an Actor In A Television Series - Comedy Or Musical")
tv_actress_comedy = Category("Best Performance by an Actress In A Television Series - Comedy Or Musical")

tv_miniseries = Category("Best Mini-Series or Motion Picture made for Television")
tv_miniseries_actor = Category("Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television")
tv_miniseries_actress = Category("Best Performance by an Actress In A Mini-series or Motion Picture Made for Television")
tv_miniseries_actor_supporting = Category("Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")
tv_miniseries_actress_supporting = Category("Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")

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
