import sys
import spacy
from spacy import displacy
import extraction
import category
from category import Category
import host_extract
import json
import rapidfuzz
import re

# Super Important Values To Parameterize
YEAR = 2015


def main(year_num):
    YEAR = year_num

    picture_drama = Category("Best Motion Picture - Drama")
    picture_musical_or_comedy = Category("Best Motion Picture - Comedy or Musical")
    picture_director = Category("Best Director - Motion Picture")
    picture_actor_drama = Category("Best Performance by an Actor in a Motion Picture - Drama")
    picture_actor_comedy = Category("Best Performance by an Actor in a Motion Picture - Comedy Or Musical")
    picture_actress_drama = Category("Best Performance by an Actress in a Motion Picture - Drama")
    picture_actress_comedy = Category("Best Performance by an Actress in a Motion Picture - Comedy Or Musical")
    picture_actor_supporting = Category("Best Performance by an Actor In A Supporting Role in a Motion Picture")
    picture_actress_supporting = Category("Best Performance by an Actress In A Supporting Role in a Motion Picture")
    picture_screen_play = Category("Best Screenplay - Motion Picture")
    picture_score = Category("Best Original Score - Motion Picture")
    picture_song = Category("Best Original Song - Motion Picture")
    picture_foreign = Category("Best Foreign Language Film")
    picture_animated = Category("Best Animated Feature Film")
    picture_cecil = Category("Cecil B. DeMille Award")
    tv_drama = Category("Best Television Series - Drama")
    tv_comedy = Category("Best Television Series - Comedy Or Musical")
    tv_actor_drama = Category("Best Performance by an Actor In A Television Series - Drama")
    tv_actor_comedy = Category("Best Performance by an Actor In A Television Series - Comedy Or Musical")
    tv_actress_drama = Category("Best Performance by an Actress In A Television Series - Drama")
    tv_actress_comedy = Category("Best Performance by an Actress In A Television Series - Comedy Or Musical")
    tv_miniseries = Category("Best Mini-Series or Motion Picture made for Television")
    tv_miniseries_actor = Category(
        "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television")
    tv_miniseries_actress = Category(
        "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television")
    tv_miniseries_actor_supporting = Category(
        "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")
    tv_miniseries_actress_supporting = Category(
        "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")

    unsorted_categories = [picture_drama, picture_musical_or_comedy, picture_director, picture_actor_drama,
                  picture_actor_comedy, picture_actress_drama, picture_actress_comedy, picture_actor_supporting,
                  picture_actress_supporting, picture_screen_play, picture_score, picture_song, picture_foreign,
                  picture_animated, picture_cecil, tv_drama, tv_comedy, tv_actor_drama, tv_actor_comedy,
                  tv_actress_drama, tv_actress_comedy, tv_miniseries, tv_miniseries_actor, tv_miniseries_actress,
                  tv_miniseries_actor_supporting, tv_miniseries_actress_supporting]

    categories = sorted(unsorted_categories, key=Category.category_words, reverse=True)

    tweets = extraction.load_tweets(YEAR)
    for tweet in tweets:
        tweet = re.sub(r'RT[^:]+:', '', tweet)
        tweet = re.sub(r'@', '', tweet)
        tweet = re.sub(r'#', '', tweet)
        tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet, flags=re.MULTILINE)
        tweet = re.sub(r' tv', ' Television', tweet, flags=re.IGNORECASE)
        tweet = re.sub(r'\\W+tv', r'\\W+Television', tweet, flags=re.IGNORECASE)
        tweet = tweet.replace('&amp', 'and')

        best_cat = None
        best_fit_ratio = 0
        found_tweet_category = False

        for i in range(len(categories)):
            cat = categories[i]
            match_score = cat.match_score(tweet.lower())
            if match_score == 1.0:
                cat.relevant_tweets.append(tweet)
                found_tweet_category = True
                break
            if match_score == best_fit_ratio and best_fit_ratio != 0:
                if len(cat.keywords) > len(best_cat.keywords):
                    best_cat = cat
                    best_fit_ratio = match_score
            elif match_score > best_fit_ratio:
                best_cat = cat
                best_fit_ratio = match_score
        if not found_tweet_category and best_fit_ratio > 0.5:
            best_cat.other_tweets.append(tweet)

    # counter = 1
    # for cat in categories:
    #     file_name = 'category' + str(counter) + '.txt'
    #     with open(file_name, mode='w', encoding='utf-8') as f:
    #         f.write(cat.name + ' Tweets' + ':\n')
    #         for tweet in cat.relevant_tweets:
    #             f.write(tweet + '\nNEW TWEET\n')
    #
    #     counter += 1
    # we might have to use spacy
    nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    overall_dict = dict()
    polarity_dict = dict()

    # find the hosts first
    overall_dict['hosts'] = host_extract.find_host(tweets)
    overall_dict['award_data'] = {}
    # make each category find its presenters, nominees, and winners
    for cat in categories:
        cat.extract_nominees(nlp)
        cat.find_winner()
        cat.find_presenters(nlp)
        polarity_score = cat.find_polarity_score(tweets)
        polarity_dict[cat.winner] = polarity_score
        if len(cat.nominees) < 4:
            if cat.person:
                find_me_some_nominees = {}
                cat_winner = cat.winner
                for tweet in tweets:
                    two_conditions = 'same' in tweet.lower() or 'ould have won' in tweet.lower()
                    if cat_winner.lower() in tweet.lower() and two_conditions:
                        text1 = nlp(tweet)
                        for word in text1.ents:
                            if word.label_ == 'PERSON':
                                person = word.text.lower()
                                if person[-2:] == "'s":
                                    person = person[:-2]
                                if " " in person and "golden" not in person and "rt " not in person:
                                    if rapidfuzz.fuzz.partial_ratio(person, cat_winner) < 70:
                                        if person in find_me_some_nominees:
                                            find_me_some_nominees[person] = find_me_some_nominees[person] + 1
                                        else:
                                            find_me_some_nominees[person] = 1

                sorted_dict = sorted([(value, key) for (key, value) in find_me_some_nominees.items()])
                sorted_dict.sort(reverse=True)
                sorted_dict = category.remove_similar_entries(sorted_dict)
                for element in sorted_dict:
                    if len(cat.nominees) >= 4:
                        break
                    else:
                        cat.nominees.append(element)

            else:
                non_people_nominees = {}
                cat_winner = cat.winner
                for tweet in tweets:
                    if cat_winner.lower() in tweet.lower() and 'ould have won' in tweet.lower():
                        match = re.match(r'(.*) should have won', tweet.lower())
                        if match:
                            nominee = match.group(1)
                            while '?' in nominee:
                                nominee = nominee[nominee.index('?')+1:].strip()
                            while '!' in nominee:
                                nominee = nominee[nominee.index('!')+1:].strip()
                            while '.' in nominee:
                                nominee = nominee[nominee.index('.')+1:].strip()
                            while 'but' in nominee:
                                nominee = nominee[nominee.index('but')+3:].strip()
                            if nominee in non_people_nominees:
                                non_people_nominees[nominee] = non_people_nominees[nominee] + 1
                            else:
                                non_people_nominees[nominee] = 1

                sorted_dict = sorted([(value, key) for (key, value) in non_people_nominees.items()])
                sorted_dict.sort(reverse=True)
                sorted_dict = category.remove_similar_entries(sorted_dict)
                for element in sorted_dict:
                    if len(cat.nominees) >= 4:
                        break
                    else:
                        cat.nominees.append(element)

        overall_dict['award_data'][cat.name.lower()] = cat.output_self()

    output_file = open(str(YEAR)+'results.json', 'w', encoding='utf-8')
    json.dump(overall_dict, output_file)

    with open("award"+str(YEAR)+".txt", 'w', encoding='utf-8') as f:
        f.write('Host: ' + ', '.join(overall_dict['hosts']).title() + '\n\n')
        for cat in categories:
            f.write('Award: ' + cat.name + '\n')
            f.write('Winner: ' + cat.winner.title() + '\n')
            f.write('Presenters: ' + ', '.join(cat.presenters).title() + '\n')
            nominee_list = []
            found_nominees = 0
            for (votes, nominee) in cat.nominees:
                if found_nominees < 4:
                    nominee_list.append(nominee)
                    found_nominees += 1
                else:
                    break
            f.write('Nominees: ' + ', '.join(nominee_list).title() + '\n')
            f.write('\n')
            f.write('Extra: ' + '\n'.join(cat.polarity_print_out) + '\n\n')

        # sorted_dict = sorted([(value, key) for (key, value) in newppl.items()])
        pd2 = sorted([(value, key) for (key, value) in polarity_dict.items()])
        p1 = 'The least liked winner was ' + str(pd2[0][1]).title() + ' with a polarity score of ' + str(pd2[0][0]) + '\n'
        f.write(p1)
        p2 = 'The most liked winner was' + str(pd2[-1][1]).title() + 'with a polarity score of ' + str(pd2[-1][0]) + '\n'
        f.write(p2)


if __name__ == "__main__":
    main(sys.argv[1])



