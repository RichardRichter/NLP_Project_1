import json
import pickle

def save_tweets(filename='tweets', raw_json='gg2015.json'):

  # Grabbing all of the necessary text data
  data = [tweet['text'] for tweet in json.load(open(raw_json))]

  # Outputting the data to a pickle
  with open(filename, 'wb') as test:
    pickle.dump(data, test)


def load_tweets(num_tweets=-1, filename='tweets'):
	with open(filename, 'rb') as tweets:

		# Loading the pickle
		data = pickle.load(tweets, encoding='utf-8')

		# Returning the number of tweets we want
		return data[0:(-1 if num_tweets > len(data) else num_tweets)]


save_tweets()
