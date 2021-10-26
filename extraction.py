import json
import pickle


def save_tweets(filename='tweets2', raw_json='gg2015.json'):
    # Grabbing all of the necessary text data
    data = [tweet['text'] for tweet in json.load(open(raw_json))]

    # Outputting the data to a pickle
    with open(filename, 'wb') as test:
        pickle.dump(data, test)


def load_tweets(filename='tweets2', num_tweets=-1):
    try:
        with open(filename, 'rb') as tweets:

            # Loading the pickle
            data = pickle.load(tweets, encoding='utf-8')

            # Returning the number of tweets we want
            return data[0:(-1 if num_tweets > len(data) else num_tweets)]

    # If we can't find the file under filename, create it
    except FileNotFoundError:
        save_tweets(filename)
        return load_tweets(filename, num_tweets)


def load_answers(year=2013):
    if year not in [2013, 2015]:
        return
    else:
        filename = str(year) + 'answers'

    try:
        with open(filename, 'rb') as answers:

            categories = pickle.load(answers, encoding='utf-8')
            return categories

    except FileNotFoundError:
        answers = [category for category in json.load(open('2013answers.json'))['award_data']]
        with open(filename, 'wb') as x:
            pickle.dump(answers, x)
        return load_answers()