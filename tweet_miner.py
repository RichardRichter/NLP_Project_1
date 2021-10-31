import sys
import spacy
from spacy import displacy
import extraction
import category
from category import Category
import host_extract
import json

# Super Important Values To Parameterize
YEAR = 2015
NUM_AWARDS = 25


def main():
    YEAR = sys.argv[1]
    # extract tweets
    extraction.save_tweets(raw_json='gg'+str(YEAR)+'.json')
    # run nathan's code to extract categories
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

    tweets = extraction.load_tweets()
    for tweet in tweets:
        for i in range(len(categories)):
            cat = categories[i]
            match_score = cat.match_score(tweet.lower())
            if match_score >= 0.9:
                is_relevant = True
                if not cat.person:
                    for word in category.person_words:
                        if word in tweet.lower():
                            is_relevant = False
                if is_relevant:
                    cat.relevant_tweets.append(tweet)
                    break
            elif match_score >= 0.5:
                cat.other_tweets.append(tweet)

    # counter = 1
    # for cat in categories:
    #     file_name = 'category' + str(counter) + '.txt'
    #     with open(file_name, mode='w', encoding='utf-8') as f:
    #         f.write(cat.name + ' Tweets' + ':\n')
    #         for tweet in cat.relevant_tweets:
    #             f.write(tweet + '\nNEW TWEET\n')
    #
    #     counter += 1

    overall_dict = dict()
    # find the hosts first
    overall_dict['hosts'] = host_extract.find_host(tweets)
    overall_dict['award_data'] = {}
    # make each category find its presenters, nominees, and winners
    for cat in categories:
        cat.extract_nominees()
        cat.find_winner()
        cat.find_presenters()
        overall_dict['award_data'][cat.name.lower()] = cat.output_self()

    output_file = open(str(YEAR)+'results.json', 'w', encoding='utf-8')
    json.dump(overall_dict, output_file)
    
    
    #This is where we need to start making the Text File
    #Hosts
    with open('award.txt', 'w') as f:
        for cat in categories:
            f.write('Award: ', cat.name)
            f.write('Winner: ', cat.winner) 
            f.write('Presenters: '.join(cat.presenters))
            f.write('Nominees" '.join(cat.nominees))
            f.write('\n')
            polarity_score =  cat.find_polarity_score(tweets)
            polarity_dict[cat.winner] = polarity_score
            f.write(f'{find_polarity_score(tweets)'}
        sorted(polarity_dict, key=polarity_dict.get)
        f.write(f'The least liked winner was {polarity_dict[0][1] with a polarity score of {polarity_dict[0][0]}\n')
        sorted(polarity_dict, key=polarity_dict.get, reverse = True)
        f.write(f'The most liked winner was {polarity_dict[0][1] with a polarity score of {polarity_dict[0][0]}\n')

 

if __name__ == "__main__":
    main()



