import spacy
import re
import string
from collections import Counter
from extraction import load_tweets, load_answers

# Class representing a category
class Category():

	def __init__(self, title, medium, genre):
		self.title = title
		self.medium = medium
		self.genre = genre
		self.score = 0


# Actual category names
real_categories = (
                   [
                   'motion picture drama',
                   'motion picture animated',
                   'motion picture musical or comedy',
                   'motion picture foreign language',
                   'director motion picture',
                   'actor motion picture drama',
                   'actor motion picture musical or comedy',
                   'actress motion picture drama',
                   'actress motion picture musical or comedy'
                   'supporting actor motion picture',
                   'supporting actress motion picture'
                   'screenplay motion picture',
                   'original score motion picture',
                   'original song motion picture',
                   'television series drama',
                   'television series music or drama',
                   'miniseries or motion picture television',
                   'actor television series drama',
                   'actor television series musical or comedy'
                   'actor miniseries or motion picture television'
                   'actress television series drama',
                   'actress television series musical or comedy',
                   'actress miniseries or motion picture television',
                   'supporting actor television',
                   'supporting actress television',
                   'burnett lifetime achievement',
                   'demill lifetime achievement'
                   ]
                   )

# The most specific patterns, grab only text where the award precedes the string being identified. Allows us to know where to stop
patterns_exact = [r'.*\b(best\b.*) goes to\b.*', r'.*\b(best\b.*) awarded to\b.*', r'.*\b(best\b.*) won by\b.*']

# General Patterns
patterns_specific = [r'.*\bnominated for (best\b.*)', r'.*\bw[io]ns? (best\b.*)', r'.*\bawarded (best\b.*)', r'.*\baward for (best\b.*)', r'.*\bawarded the (best\b.*)', r'.*\bwinner of (best\b.*)', r'.*\b(best\b.*)goes to\b.*', r'.*\b(best\b.*)awarded to\b.*', r'.*\b(best\b.*)won by\b.*']

# The least specific patterns, will grab everything
patterns_ambiguous = [r'.*\b(best\b.*)']


# Takes in a list of strings, returns a list of strings containing only alpha characters [a-z]
def make_alpha(tweets):
	return [re.sub(r'[^a-z -#]+', '', text.lower()) for text in tweets]

# Reduce the number of words in each tweet (the beginning words should contain the award name)
def shorten(tweets, limit=10):
	result = []
	for tweet in tweets:
		words = tweet.split(' ')
		short = ' '.join(words[0:limit])
		result.append(short)

	return result

# Returns a list of tweets that matches any of the given patterns
def match_any(tweets, patterns):
	result = []
	for tweet in tweets:
		for pattern in patterns:
			match = re.match(pattern, tweet)
			if match:

				# We only want the text that corresponds to where the award would be in the tweet (use group 1)
				result.append(match.group(1))
				break

	return result

# Given a list of tweets, returns a Counter of all the words
def count_words(tweets):
	word_count = Counter()
	for tweet in tweets:
		word_count += Counter(tweet.split(' '))

	return word_count

# Given a list of words, filters a set of tweets to only include those words
def filter_words(filter_words, tweets):
	result = []
	for tweet in tweets:
		words = tweet.split(' ')
		filtered = ' '.join([word for word in words if word in filter_words])
		result.append(filtered)

	return result

# Given a list of words, filters a set of tweets to remove those words
def remove_words(to_remove, tweets):
	result = []
	for tweet in tweets:
		words = tweet.split(' ')
		filtered = ' '.join([word for word in words if word not in to_remove])
		result.append(filtered)

	return result

def remove_hashtags(tweets):
	result = []
	for tweet in tweets:
		words = tweet.split(' ')
		filtered = ' '.join([word for word in words if '#' not in word])
		result.append(filtered)

	return result



# Initial filtering process design, rudimentary
def find_categories_v1(tweets=None):

	# Initialization
	data =  tweets if tweets else load_tweets()

	# Cleaning the tweets by making them alpha and lowercase
	data = make_alpha(data)

	# Creating a copy of the data that will be parsed with lower quality
	data_lq = data[:]

	# Gathering all tweets that match a certain set of regex patterns
	data_hq = match_any(data, patterns_exact)
	data_lq = match_any(data, patterns_ambiguous)

	# Shortening the tweets to 10 words, which should cover all of the award names
	data_hq = shorten(data_hq)
	data_lq = shorten(data_lq)

	# Gathering a count of all words in the processed tweets
	common = count_words(data_hq)

	# Returning the 100 most common words as a list of strings
	common = [word[0] for word in common.most_common(50)]

	# Filtering tweets to contain only the most common words
	data_hq = filter_words(common, data_hq)
	data_lq = filter_words(common, data_lq)

	# Recombining the sets
	data = data_lq + data_hq

	# Removing some words
	data = remove_words(['in', 'at', 'as', 'a', 'for'], data)
	data = remove_hashtags(data)

	# Sorting the processed tweets, returning
	return Counter(data), len(data)

# Calculates the accuracy based on the real categories (hard-coded)
def get_accuracy(preds, real=real_categories):
	correct = []
	missed = []
	for category in real:
		if category in preds:
			correct.append(category)
		else:
			missed.append(category)

	accuracy = len(correct) / (len(correct) + len(missed))

	return accuracy, correct, missed


def find_categories_v2(tweets=None):

	data = tweets if tweets else load_tweets()
	data = make_alpha(data)
	data = remove_hashtags(data)
	data = match_any(data, patterns_exact)
	data = shorten(data)
	data = filter_words([word[0] for word in count_words(data).most_common(50)], data)
	data = remove_words(['in', 'at', 'as', 'a', 'for'], data)
	return Counter(data)

# Dev/Testing
#categories, num_found = find_categories_v1()
#print(get_accuracy(categories))

#print(get_accuracy(find_categories_v2()))