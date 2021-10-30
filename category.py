import re
import spacy
from spacy import displacy
import rapidfuzz
import nltk


# GLOBAL VARIABLES (SAME FOR EVERY CATEGORY)
person_words = ['actor', 'director', 'actress']
stop_words = ['-', 'in', 'a', 'by', 'an', 'or', 'made', 'for', 'performance', 'role', 'series']
patterns_after = [r'.*\b(best\b.*) goes to [^a-z]*([a-z0-9 -]*)[!#.?\x28]*',
                  r'.*\b(best\b.*) awarded to [^a-z]*([a-z0-9 -]*)[!.?]*',
                  r'.*\b(best\b.*) won by [^a-z]*([a-z0-9 -]*)[!.?]*',
                  r'.*\b(best\b.*): [^a-z]*([a-z0-9 -]*)[!.?]*', r'.*\b(best\b.*) is [^a-z]*([a-z0-9 -]*)[!.?]*',
                  r'.*\b(best.*) - (.* - .*) - goldenglobes', r'.*\b(best\b.*) - ([a-z0-9 ]*) - goldenglobes']

patterns_before = \
    [r'(.*\b) nominated for (best\b.*)', r'(.*\b) w[io]ns? (best\b.*)', r'(.*\b) awarded (best\b.*)',
     r'(.*\b) awarded the (best\b.*)', r'(.*\b) winner of (best\b.*)', r'to ([a-z0-9 -]*) for winning best\b.*',
     r'(.*) receives .* award']

buzz_words = ['nom', 'won', 'win', 'goes to', 'awarded', 'best']
# define nlp here so we don't have to load it several times per function
nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])


# Takes an ordered sorted dict, list of (votes, nominee) R
# Removes less common entries that are too similar to more common entries
# Returns another sorted_dict form, with the similar names removed
# ASSUMES THE MOST CORRECT NAME IS THE MOST COMMON AS WELL (SUPER IMPORTANT)
def remove_similar_entries(sorted_dict: dict):
    if len(sorted_dict) > 0:
        # new dict to place names back in
        filtered_dict = {}
        # when we reach this index in sorted_dict, we know its not an unique name so we can ignore it
        ignore_list = []
        # sorted_dict is sorted so highest votes and therefore most accurate names appear first
        # THIS FACT IS SUPER IMPORTANT AND THE REASON WHY THIS WORKS
        for i in range(len(sorted_dict)):
            if i not in ignore_list:
                (count1, person1) = sorted_dict[i]
                # first time the unique person appears in new ppl dict so we add it in
                if person1 not in filtered_dict:
                    filtered_dict[person1] = count1
                for j in range(i + 1, len(sorted_dict)):
                    (count2, person2) = sorted_dict[j]
                    # this checks if person1 and person2 share more than 80% similarity ignoring random add-ons
                    # AKA Argo and Argo GoldenGlobes2013 will have 100% similarity
                    if rapidfuzz.fuzz.partial_ratio(person1, person2) > 80:
                        # person1 is most likely the correct version of the name
                        # ignore person2 when it becomes i in the loop
                        ignore_list.append(j)
                        if person1 in filtered_dict:
                            # add person2's votes to person1 because they refer to the same unique person
                            filtered_dict[person1] = filtered_dict[person1] + count2

        # sorted_dict should now have filtered out the same people but with typos in their name
        new_sorted_dict = sorted([(value, key) for (key, value) in filtered_dict.items()])
        new_sorted_dict.sort(reverse=True)
        return new_sorted_dict
    else:
        return sorted_dict


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
    def find_presenters(self):
        ppl = {}
        pattern_better = re.compile(
            r'(\spresent\s|\spresents\s|\spresenting\s|\spresenter\s|\spresenters\s|\spresented\s|\spresentation\s|\spresenta\s)')
        pattern_avoid = re.compile(r'(should|wish|want|need|desire|\bnot\b)')
        pattern_exclude = re.compile(r'(Wins|RT @|RT|Congrats|Congradulations|Best)')
        two_quick_pattern = re.compile(
            r'[^\s]+ [^\s]+ and [^\s]+ [^\s]+ (\spresent\s|\spresents\s|\spresenting\s|\spresenter\s|\spresenters\s|\spresented\s|\spresentation\s|\spresenta\s)')
        one_quick_pattern = re.compile(
            r'[^\s]+ [^\s]+ (\spresent\s|\spresents\s|\spresenting\s|\spresenter\s|\spresenters\s|\spresented\s|\spresentation\s|\spresenta\s)')
        for tweet in self.relevant_tweets:
            if two_quick_pattern.search(tweet) or one_quick_pattern.search(tweet):
                cap = (tweet.index(pattern_better.search(tweet).group(0)))
                sub_section_tweet = tweet[:cap]
                tweet_list = list(sub_section_tweet.split(" "))
                tags = nltk.pos_tag(tweet_list)
                targets = ["NNPS"]
                only_nnps = list(filter(lambda x: x[1] in targets, tags))
                for x in range(0, len(only_nnps)):
                    person = only_nnps[x][0]
                    person = person.replace('#', '')
                    person = person.replace('@', '')
                    if " " in person and not pattern_exclude.search(person):
                        if person[-2:] == "'s":
                            person = person[:-2]
                        if person in ppl:
                            ppl[person] = ppl[person] + 100
                        else:
                            ppl[person] = 100

        for tweet in self.relevant_tweets:
            if pattern_better.search(tweet):
                if not pattern_avoid.search(tweet):
                    cap = (tweet.index(pattern_better.search(tweet).group(0)))
                    sub_section_tweet = tweet[:cap]
                    tweet_list = list(sub_section_tweet.split(" "))
                    tags = nltk.pos_tag(tweet_list)
                    targets = ["NNPS"]
                    only_nnps = list(filter(lambda x: x[1] in targets, tags))
                    for x in range(0, len(only_nnps)):
                        person = only_nnps[x][0]
                        person = person.replace('#', '')
                        person = person.replace('@', '')
                        if " " in person and not pattern_exclude.search(person):
                            if person[-2:] == "'s":
                                person = person[:-2]
                            if person in ppl:
                                ppl[person] = ppl[person] + 10
                            else:
                                ppl[person] = 10

                    text = nlp(sub_section_tweet)
                    for word in text.ents:
                        if word.label_ == 'PERSON':
                            person = word.text
                            person = person.replace('#', '')
                            person = person.replace('@', '')
                            if " " in person and not pattern_exclude.search(person):
                                if person[-2:] == "'s":
                                    person = person[:-2]
                                if person in ppl:
                                    ppl[person] = ppl[person] + 10
                                else:
                                    ppl[person] = 10

        if len(ppl) == 0:
            for tweet in self.other_tweets:
                if pattern_better.search(tweet):
                    if not pattern_avoid.search(tweet):
                        cap = (tweet.index(pattern_better.search(tweet).group(0)))
                        sub_section_tweet = tweet[:cap]
                        tweet_list = list(sub_section_tweet.split(" "))
                        tags = nltk.pos_tag(tweet_list)
                        targets = ["NNPS"]
                        only_nnps = list(filter(lambda x: x[1] in targets, tags))

                        for x in range(0, len(only_nnps)):
                            person = only_nnps[x][0]
                            person = person.replace('#', '')
                            person = person.replace('@', '')
                            if " " in person and not pattern_exclude.search(person):
                                if person[-2:] == "'s":
                                    person = person[:-2]
                                if person in ppl:
                                    ppl[person] = ppl[person] + 1
                                else:
                                    ppl[person] = 1

                        text = nlp(sub_section_tweet)
                        for word in text.ents:
                            if word.label_ == 'PERSON':
                                person = word.text
                                person = person.replace('#', '')
                                person = person.replace('@', '')
                                if " " in person and not pattern_exclude.search(person):
                                    if person[-2:] == "'s":
                                        person = person[:-2]
                                    if person in ppl:
                                        ppl[person] = ppl[person] + 1
                                    else:
                                        ppl[person] = 1

        if len(ppl) != 0:
            if self.winner in ppl.keys():
                del ppl[self.winner]
            for nominee in self.nominees:
                if nominee in ppl.keys():
                    print(nominee, " is not a host for ", self.name)
                    del ppl[nominee]

            sorted_dict = sorted([(value, key) for (key, value) in ppl.items()])
            sorted_dict.sort(reverse=True)
            (votes, definitive_presenter) = sorted_dict[0]
            presenters = [definitive_presenter]
            keep_searching = True
            presenter_index = 1

            while keep_searching and len(sorted_dict) > 1:
                if len(presenters) < 2:
                    (num_votes, potential_host) = sorted_dict[presenter_index]
                    if float(num_votes) / votes > 0.6:
                        presenters.append(potential_host)
                        keep_searching = False
                    else:
                        keep_searching = False
                    presenter_index += 1

            self.presenters = presenters
        else:
            empty_list = ["NA"]
            self.presenters = empty_list

    def extract_nominees(self):
        if self.person:
            self.extract_people_nominees()
            self.extract_list_nominees()
        else:
            self.extract_list_nominees()

    # relies heavily on spacy
    def extract_people_nominees(self):
        ppl = {}
        for tweet in self.relevant_tweets:
            if any(word in tweet.lower() for word in buzz_words):
                new_nominees = True
                # to avoid running spacy, if tweets contain nominees we already know, we increment votes
                for key in ppl:
                    if key in tweet.lower():
                        ppl[key] += 1
                        new_nominees = False
                # run spacy if we didn't recognize any nominees from ppl dict
                if new_nominees:
                    text1 = nlp(tweet)
                    # this assigns a label to every word/set of words in the sentence if possible
                    for word in text1.ents:
                        # ignore all other words that have labels that aren't people
                        if word.label_ == 'PERSON':
                            person = word.text
                            # sometimes, spacy identifies person - show as a full name
                            if ' - ' in person:
                                person = person[:person.index(' - ')]
                            # get rid of trailing and leading white spaces, then lower case the name
                            person = person.strip().lower()
                            # person only valid if 25% or less of its words are part of category's keywords
                            if self.rev_score(person) <= 0.25:
                                # ignore irregular names like firstlast or golden globes and the in middle of person
                                if " " in person and "golden" not in person.lower() and " the " not in person.lower():
                                        if person[-2:] == "'s":
                                            person = person[:-2]
                                        # this person already exists in the dictionary, so just increment the count
                                        if person in ppl:
                                            ppl[person] = ppl[person] + 1
                                        # add the person to the dictionary
                                        else:
                                            ppl[person] = 1

        sorted_dict = sorted([(value, key) for (key, value) in ppl.items()])
        sorted_dict.sort(reverse=True)
        # use rapidfuzz to remove names that are too identical
        sorted_dict = remove_similar_entries(sorted_dict)
        if len(sorted_dict) > 0:
            self.nominees = sorted_dict

    # function if Category is not a person category (nlp package won't be as helpful)
    def extract_list_nominees(self):
        # extracted from relevant_tweets
        confident_nominees = {}
        # extracted from other_tweets
        weaker_nominees = {}

        for tweet in self.relevant_tweets:
            cleaned_tweet = re.sub(r'[^a-z0-9 :.!?,\n-]+', '', tweet.lower())
            if 'nom' in cleaned_tweet:
                if cleaned_tweet.count('\n') > 3:
                    noms = cleaned_tweet.split('\n')
                    for nom in noms:
                        new_nom = nom
                        # goldenglobes tends to be attached at the end of one element, so remove it in that case
                        # the first nominee tends to be caught in the statement list of nominees: first nominee
                        if nom.endswith(' goldenglobes'):
                            new_nom = nom[:-13]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            # if category is a person, we want white space for first last
                            if not self.person or ' ' in new_nom:
                                if new_nom in confident_nominees:
                                    confident_nominees[new_nom] = confident_nominees[new_nom] + 1
                                else:
                                    confident_nominees[new_nom] = 1
                elif cleaned_tweet.count(',') > 3:
                    noms = cleaned_tweet.split(', ')
                    for nom in noms:
                        new_nom = nom
                        if nom.endswith(' goldenglobes'):
                            new_nom = nom[:-13]
                        if ':' in new_nom:
                            new_nom = new_nom[nom.index(':') + 1:]
                        if len(new_nom) > 2:
                            new_nom = new_nom.strip()
                            if new_nom in confident_nominees:
                                confident_nominees[new_nom] = confident_nominees[new_nom] + 1
                            else:
                                confident_nominees[new_nom] = 1
        # only check other_tweets if we didn't find list formats from relevant_tweets
        if not confident_nominees:
            for tweet in self.other_tweets:
                cleaned_tweet = re.sub(r'[^a-z0-9 :.!?,\n-]+', '', tweet.lower())
                if 'nom' in cleaned_tweet:
                    if cleaned_tweet.count('\n') > 3:
                        noms = cleaned_tweet.split('\n')
                        for nom in noms:
                            new_nom = nom
                            if nom.endswith(' goldenglobes'):
                                new_nom = nom[:-13]
                            if ':' in new_nom:
                                new_nom = new_nom[nom.index(':') + 1:]
                            if len(new_nom) > 2:
                                new_nom = new_nom.strip()
                                if not self.person or ' ' in new_nom:
                                    if new_nom in weaker_nominees:
                                        weaker_nominees[new_nom] = weaker_nominees[new_nom] + 1
                                    else:
                                        weaker_nominees[new_nom] = 1

                    elif cleaned_tweet.count(',') > 3:
                        noms = cleaned_tweet.split(', ')
                        for nom in noms:
                            new_nom = nom
                            if nom.endswith(' goldenglobes'):
                                new_nom = nom[:-13]
                            if ':' in new_nom:
                                new_nom = new_nom[nom.index(':') + 1:]
                            if len(new_nom) > 2:
                                new_nom = new_nom.strip()
                                if not self.person or ' ' in new_nom:
                                    if new_nom in weaker_nominees:
                                        weaker_nominees[new_nom] = weaker_nominees[new_nom] + 1
                                    else:
                                        weaker_nominees[new_nom] = 1

        if confident_nominees:
            # Count frequency of each nominee in most relevant tweets
            rule1 = {key: 0 for key, val in confident_nominees.items()}
            for tweet in self.relevant_tweets:
                for key in rule1:
                    if key in tweet.lower():
                        rule1[key] = rule1[key] + 1
            # Ignore keys that don't appear at all and keys that are too similar to category keywords
            filtered = {key: val for key, val in rule1.items() if self.rev_score(key) < 0.5 and val > 0}

            sorted_dict = sorted([(value, key) for (key, value) in filtered.items()])
            sorted_dict.sort(reverse=True)
            # attempt to remove nominees that are substrings of other nominees (favor the more specific one)
            sorted_dict = remove_similar_entries(sorted_dict)
            if not self.person:
                self.nominees = sorted_dict
            else:
                # we assume the list is reliable if there are more than 3 nominees
                if len(sorted_dict) > 3:
                    # if list perfectly has 5 elements, we assume it has winner+4 nominees in correct order
                    if len(sorted_dict) == 5:
                        self.nominees = sorted_dict
                    else:
                        # convert self.nominees into a dictionary to make things easier
                        dict_nominees = {nominee: votes for (votes, nominee) in self.nominees}
                        # add the votes to self.nominees (this double counts but helps reassure winner and nominees)
                        for (votes, nominee) in sorted_dict:
                            if nominee in dict_nominees:
                                dict_nominees[nominee] = dict_nominees[nominee] + votes
                            else:
                                dict_nominees[nominee] = votes
                        # convert dict_nominees back into a list to store in self.nominees
                        new_nominees = sorted([(value, key) for (key, value) in dict_nominees.items()])
                        new_nominees.sort(reverse=True)
                        self.nominees = new_nominees

        else:
            rule2 = {key: 0 for key, val in weaker_nominees.items()}
            for tweet in self.relevant_tweets:
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

            if not self.person:
                self.nominees = sorted_dict
            else:
                # we assume the list is reliable if there are more than 3 nominees
                if len(sorted_dict) > 3:
                    # if list perfectly has 5 elements, we assume it has winner+4 nominees in correct order
                    if len(sorted_dict) == 5:
                        self.nominees = sorted_dict
                    else:
                        # convert self.nominees into a dictionary to make things easier
                        dict_nominees = {nominee:votes for (votes, nominee) in self.nominees}
                        # add the votes to self.nominees (this double counts but helps reassure winner and nominees)
                        for (votes, nominee) in sorted_dict:
                            if nominee in dict_nominees:
                                dict_nominees[nominee] = dict_nominees[nominee] + votes
                            else:
                                dict_nominees[nominee] = votes
                        # convert dict_nominees back into a list to store in self.nominees
                        new_nominees = sorted([(value, key) for (key, value) in dict_nominees.items()])
                        new_nominees.sort(reverse=True)
                        self.nominees = new_nominees

    # identifies winner by checking matching regular expressions
    def find_winner(self):
        nominees = {}

        for tweet in self.relevant_tweets:
            cleaned_tweet = re.sub(r'[^a-z0-9 :.!?\x28\x29-]+', '', tweet.lower())
            cleaned_tweet = ' '.join(cleaned_tweet.split())
            matched_after = False
            for pattern in patterns_after:
                match = re.match(pattern, cleaned_tweet)
                if match:
                    matched_after = True
                    candidate = match.group(2)
                    if len(candidate) == 0:
                        break
                    # check - , for, from because regex may retrieve both show and person and need to separate them
                    if ' - ' in candidate:
                        if self.person:
                            candidate = candidate[:candidate.index(' - ')]
                    if 'for' in candidate:
                        if not self.person:
                            candidate = candidate[candidate.index('for') + 3:]
                        else:
                            candidate = candidate[:candidate.index('for')]
                    if 'from' in candidate:
                        if not self.person:
                            candidate = candidate[candidate.index('from') + 4:]
                        else:
                            candidate = candidate[:candidate.index('from')]
                    if candidate.endswith(' goldenglobes'):
                        candidate = candidate[:-13]
                    candidate = candidate.strip()
                    # candidate is 2 or less characters or ignore it as it's probably not useful
                    if len(candidate) <= 2:
                        break
                    # person expects first last, no whitespace=> not a person name
                    if self.person and ' ' not in candidate:
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
                        if len(candidate) == 0:
                            break
                        if ' - ' in candidate:
                            if self.person:
                                candidate = candidate[:candidate.index(' - ')]
                        if 'for' in candidate:
                            if not self.person:
                                candidate = candidate[candidate.index('for') + 3:]
                            else:
                                candidate = candidate[:candidate.index('for')]
                        if 'from' in candidate:
                            if not self.person:
                                candidate = candidate[candidate.index('from') + 4:]
                            else:
                                candidate = candidate[:candidate.index('from')]
                        if candidate.endswith(' goldenglobes'):
                            candidate = candidate[:-13]
                        candidate = candidate.strip()
                        if len(candidate) <= 2:
                            break
                        if self.person and ' ' not in candidate:
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

            if self.nominees:
                matched_winner_to_nominee = False
                winner_index = 0
                top_nominee = self.nominees[0][1]
                while not matched_winner_to_nominee:
                    winner = sorted_dict[winner_index][1]
                    # the top nominee is confirmed the winner so remove it
                    if rapidfuzz.fuzz.partial_ratio(winner, top_nominee) == 100:
                        del self.nominees[0]
                        matched_winner_to_nominee = True
                    winner_index += 1

                self.winner = top_nominee

            else:
                self.winner = sorted_dict[0][1]

        elif nominees:
            sorted_dict = sorted([(value, key) for (key, value) in nominees.items()])
            sorted_dict.sort(reverse=True)

            if self.nominees:
                matched_winner_to_nominee = False
                winner_index = 0
                top_nominee = self.nominees[0][1]
                while not matched_winner_to_nominee:
                    winner = sorted_dict[winner_index][1]
                    # the top nominee is confirmed the winner so remove it
                    if rapidfuzz.fuzz.partial_ratio(winner, top_nominee) == 100:
                        del self.nominees[0]
                        matched_winner_to_nominee = True
                    winner_index += 1

                self.winner = top_nominee

            else:
                self.winner = sorted_dict[0][1]

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
