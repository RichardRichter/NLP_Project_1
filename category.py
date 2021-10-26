import re
import spacy
from spacy import displacy


# GLOBAL VARIABLES (SAME FOR EVERY CATEGORY)
person_words = ['actor', 'director', 'actress']
stop_words = ['-', 'in', 'a', 'by', 'an', 'or', 'made', 'for']
patterns_after = [
    r'.*\b(best\b.*) goes to [^a-z]*([a-z0-9 -]*)[!#.?\x28]', r'.*\b(best\b.*) awarded to [^a-z]*([a-z0-9 -]*)[!#.?]',
    r'.*\b(best\b.*) won by [^a-z]*([a-z0-9 -]*)[!#.?]', r'.*\b(best\b.*): [^a-z]*([a-z0-9 -]*)[!#.?]',
    r'.*\b(best\b.*) - ([a-z0-9 ]*) - #goldenglobes', r'.*\b(best\b.*) - [a-z ]* - ([a-z0-9 ]*)[!#.?\x28]']

patterns_before = patterns_specific = \
    [r'(.*\b) nominated for (best\b.*)', r'(.*\b) w[io]ns? (best\b.*)', r'(.*\b) awarded (best\b.*)',
     r'(.*\b) awarded the (best\b.*)', r'(.*\b) winner of (best\b.*)', r'to ([a-z0-9 -]*) for winning best\b.*']


class Category:
    def __init__(self, name):
        self.name = name
        self.presenters = {}
        self.nominees = []
        self.winner = ''
        corrected_name = ' '.join(name.replace('-', ' ').split())
        words = corrected_name.lower().split(' ')
        self.keywords = [w for w in words if w not in stop_words]
        self.relevant_tweets = []
        self.other_tweets = []
        self.person = False
        for p in person_words:
            if p in self.keywords:
                self.person = True

    # helper function so we can sort categories by number of keywords
    def category_words(self):
        return len(self.keywords)

    # calculates % of keywords that exist in the tweet, assumes everything is lowercase already
    def match_score(self, tweet: str):
        matched_words = 0
        for word in self.keywords:
            if word in tweet:
                matched_words += 1.0

        return matched_words / len(self.keywords)

    # calculates % of words in word that exist in this category's keywords
    def rev_score(self, word: str):
        keywords = self.keywords
        words = word.split(" ")
        total_length = len(words)
        counter = 0.0
        for i in words:
            if i.lower() in keywords:
                counter += 1.0
        return counter / total_length

    # looks through tweets and updates self.presenters to be the list of presenters
    def find_presenter(self):
        if len(self.relevant_tweets) == 0:
            self.relevant_tweets = self.other_tweets

        nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
        ppl = {}
        pattern_better = re.compile(r'\bpresent\b')
        pattern_worse = re.compile(r'\bannounced\b|\bintroduced\b')
        for tweet in self.relevant_tweets:
            # YOUR PROBLEM IS THIS STUPID TRUE FALSE STATEMENT
            if pattern_better.search(tweet) is not None:
                text = nlp(tweet)
                for word in text.ents:
                    if word.label_ == 'PERSON':
                        person = word.text
                        if person in ppl:
                            ppl[person] = ppl[person] + 1
                        else:
                            ppl[person] = 1
                            # second_match = re.finditer(pattern_worse, tweet)
            # if second_match:
            #   text = nlp(tweet)
            #  for word in text.ents:
            #     if word.label_ == 'PERSON':
            #        person = word.text
            #       if person in ppl:
            #          ppl[person] = ppl[person]+1
            #     else:
            #        ppl[person] = 1

        if len(ppl) != 0:
            sorted_dict = sorted([(value, key) for (key, value) in ppl.items()])
            sorted_dict.sort(reverse=True)
            (votes, definitive_presenter) = sorted_dict[0]
            presenters = [definitive_presenter]
            keep_searching = True
            presenter_index = 1
            while keep_searching and len(sorted_dict) > 1:
                (num_votes, potential_host) = sorted_dict[presenter_index]
                if float(num_votes) / votes > 0.8:
                    presenters.append(potential_host)
                    keep_searching = False
                else:
                    keep_searching = False
                presenter_index += 1

            self.presenters = presenters

        # else:
            # print("NA")
        # print(count)
        # if len(sorted_dict) !=0:
        #    print(sorted_dict[0])
        # else:
        #    print("NA")

    def extract_nominees(self):
        if self.person:
            self.extract_people_nominees()
        else:
            self.extract_nonpeople_nominees()

    def extract_people_nominees(self):
        self.nominees = []

    # function if Category is not a person category (nlp package won't be as helpful)
    def extract_nonpeople_nominees(self):
        good_tweets = self.relevant_tweets
        temporary_nominees = {}
        weaker_nominees = {}

        for tweet in good_tweets:
            cleaned_tweet = re.sub(r'[^a-z0-9 #:….!?,\n-]+', '', tweet.lower())
            if 'nom' in cleaned_tweet:
                if cleaned_tweet.count('\n') > 3:
                    noms = cleaned_tweet.split('\n')
                    for nom in noms:
                        new_nom = nom
                        if nom.endswith(' #goldenglobes'):
                            new_nom = nom[:-14]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            if new_nom in temporary_nominees:
                                temporary_nominees[new_nom] = temporary_nominees[new_nom] + 1
                            else:
                                temporary_nominees[new_nom] = 1
                elif cleaned_tweet.count(',') > 3:
                    noms = cleaned_tweet.split(', ')
                    for nom in noms:
                        new_nom = nom
                        if nom.endswith(' #goldenglobes'):
                            new_nom = nom[:-14]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            if new_nom in temporary_nominees:
                                temporary_nominees[new_nom] = temporary_nominees[new_nom] + 1
                            else:
                                temporary_nominees[new_nom] = 1

        for tweet in self.other_tweets:
            cleaned_tweet = re.sub(r'[^a-z0-9 #:….!?,\n-]+', '', tweet.lower())
            if 'nom' in cleaned_tweet:
                if cleaned_tweet.count('\n') > 3:
                    noms = cleaned_tweet.split('\n')
                    for nom in noms:
                        new_nom = nom
                        if nom.endswith(' #goldenglobes'):
                            new_nom = nom[:-14]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            if new_nom in weaker_nominees:
                                weaker_nominees[new_nom] = weaker_nominees[new_nom] + 1
                            else:
                                weaker_nominees[new_nom] = 1

                elif cleaned_tweet.count(',') > 3:
                    noms = cleaned_tweet.split(', ')
                    for nom in noms:
                        new_nom = nom
                        if nom.endswith(' #goldenglobes'):
                            new_nom = nom[:-14]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            if new_nom in weaker_nominees:
                                weaker_nominees[new_nom] = weaker_nominees[new_nom] + 1
                            else:
                                weaker_nominees[new_nom] = 1

        # Count frequency of each nominee in most relevant tweets
        rule1 = {key: 0 for key, val in temporary_nominees.items()}
        if rule1:
            for tweet in good_tweets:
                for key in rule1:
                    if key in tweet.lower():
                        rule1[key] = rule1[key] + 1
            # Ignore keys that don't appear at all and keys that are too similar to category keywords
            filtered = {key: val for key, val in rule1.items() if self.rev_score(key) < 0.5 and val > 0}

            sorted_dict = sorted([(value, key) for (key, value) in filtered.items()])
            sorted_dict.sort(reverse=True)
            # attempt to remove nominees that are substrings of other nominees (favor the more specific one)
            for (votes1, nominee1) in sorted_dict:
                for (votes2, nominee2) in sorted_dict:
                    if nominee1 in nominee2 and nominee1 != nominee2:
                        sorted_dict.remove((votes1, nominee1))

            self.nominees = sorted_dict

        else:
            rule2 = {key: 0 for key, val in weaker_nominees.items()}
            for tweet in good_tweets:
                for key in rule2:
                    if key in tweet.lower():
                        rule2[key] = rule2[key] + 1

            filtered = {key: val for key, val in rule2.items() if self.rev_score(key) < 0.5 and val > 0}
            sorted_dict = sorted([(value, key) for (key, value) in filtered.items()])
            sorted_dict.sort(reverse=True)
            for (votes1, nominee1) in sorted_dict:
                for (votes2, nominee2) in sorted_dict:
                    if nominee1 in nominee2 and nominee1 != nominee2:
                        sorted_dict.remove((votes1, nominee1))

            self.nominees = sorted_dict

    # identifies winner by checking matching regular expressions
    def find_winner(self):
        nominees = {}

        for tweet in self.relevant_tweets:
            cleaned_tweet = re.sub(r'[^a-z0-9 #:.!?\x28\x29-]+', '', tweet.lower())
            cleaned_tweet = ' '.join(cleaned_tweet.split())
            matched_after = False
            for pattern in patterns_after:
                match = re.match(pattern, cleaned_tweet)
                if match:
                    matched_after = True
                    candidate = match.group(2)
                    if len(candidate) == 0:
                        break
                    if 'for' in candidate:
                        candidate = candidate[candidate.index('for') + 3:]
                    if 'from' in candidate:
                        candidate = candidate[candidate.index('from') + 4:]
                    candidate = candidate.strip()
                    # candidate is 2 or less characters or ignore it as it's probably not useful
                    if len(candidate) <= 2:
                        break
                    if candidate in nominees:
                        nominees[candidate] = nominees[candidate] + 1
                    else:
                        nominees[candidate] = 1
                    break
            # No match if first set of patterns so try to check the second set of patterns
            if not matched_after:
                for pattern2 in patterns_before:
                    match = re.match(pattern2, cleaned_tweet)
                    if match:
                        candidate = match.group(1)
                        if len(candidate) == 1:
                            break
                        if 'for' in candidate:
                            candidate = candidate[candidate.index('for') + 3:]
                        if 'from' in candidate:
                            candidate = candidate[candidate.index('from') + 4:]
                        candidate = candidate.strip()
                        if len(candidate) <= 2:
                            break
                        if candidate in nominees:
                            nominees[candidate] = nominees[candidate] + 1
                        else:
                            nominees[candidate] = 1
                        break

        candidate_frequencies = {}
        candidates = list(nominees.keys())
        # Find most common substring or intersection between collection of candidates
        for i in range(0, len(candidates)):
            for j in range(i + 1, len(candidates)):
                if i == j:
                    continue
                else:
                    name1 = candidates[i]
                    name2 = candidates[j]
                    len1 = len(name1)
                    len2 = len(name2)
                    # We only care if two different 'names' are different lengths.
                    # Because they are different keys, same length strings cannot be the same
                    if len1 > len2:
                        if name2 in name1:
                            if name2 not in candidate_frequencies:
                                # give double weight to original vote count of name2
                                candidate_frequencies[name2] = 2 * nominees[name2]
                            candidate_frequencies[name2] = candidate_frequencies[name2] + nominees[name1]

                    elif len2 > len1:
                        if name1 in name2:
                            if name1 not in candidate_frequencies:
                                # same logic but for name1
                                candidate_frequencies[name1] = 2 * nominees[name1]
                            candidate_frequencies[name1] = candidate_frequencies[name1] + nominees[name2]

        if candidate_frequencies:
            sorted_dict = sorted([(value, key) for (key, value) in candidate_frequencies.items()])
            sorted_dict.sort(reverse=True)
            winner = sorted_dict[0][1]
            if self.nominees:
                # the top nominee is confirmed the winner so remove it
                if winner == self.nominees[0][1]:
                    del self.nominees[0]

            self.winner = winner

        elif nominees:
            sorted_dict = sorted([(value, key) for (key, value) in nominees.items()])
            sorted_dict.sort(reverse=True)
            winner = sorted_dict[0][1]
            if self.nominees:
                # the top nominee is confirmed the winner so remove it
                if winner == self.nominees[0][1]:
                    del self.nominees[0]

            self.winner = winner

    def output_self(self):
        award_info = {}
        # presenters
        award_info['presenters'] = self.presenters
        # nominees
        if self.nominees:
            nominee_list = []
            found_nominees = 0
            for (votes, nominee) in self.nominees:
                if found_nominees < 4:
                    nominee_list.append(nominee)
                    found_nominees += 1
                else:
                    break
            award_info['nominees'] = nominee_list
        # bad case but it's bound to happen :(
        else:
            award_info['nominees'] = []
        # winner
        award_info['winner'] = self.winner
        return award_info
