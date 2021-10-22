import sys
import spacy
from spacy import displacy
import extraction
from category import Category


# Super Important Values To Parameterize
YEAR = 2013
NUM_AWARDS = 25


def main():
    # extract tweets
    # extraction.save_tweets()
    categories = []
    # run nathan's code to extract categories
    picture_drama = Category("Best Motion Picture - Drama")
    picture_musical_or_comedy = Category("Best Motion Picture - Musical or Comedy")
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
    picture_cecil = Category("Cecil B. DeMille Award for Lifetime Achievement in Motion Pictures")
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

    categories = [picture_drama, picture_musical_or_comedy, picture_director, picture_actor_drama,
                  picture_actor_comedy, picture_actress_drama, picture_actress_comedy, picture_actor_supporting,
                  picture_actress_supporting, picture_screen_play, picture_score, picture_song, picture_foreign,
                  picture_animated, picture_cecil, tv_drama, tv_comedy, tv_actor_drama, tv_actor_comedy,
                  tv_actress_drama, tv_actress_comedy, tv_miniseries, tv_miniseries_actor, tv_miniseries_actress,
                  tv_miniseries_actor_supporting, tv_miniseries_actress_supporting]

    tweets = extraction.load_tweets()
    for tweet in tweets:
        for cat in categories:
            if cat.match_score(tweet) >= 0.8:
                cat.relevant_tweets.append(tweet)

    counter = 1
    for cat in categories:
        file_name = 'category' + str(counter) + '.txt'
        with open(file_name, mode='w', encoding='utf-8') as f:
            f.write(cat.name + 'Tweets' + ':')
            for tweet in cat.relevant_tweets:
                f.write(tweet + '\n')

        counter += 1

    print("done")

if __name__ == "__main__":
    main()

    

