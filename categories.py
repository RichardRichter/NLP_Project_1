import spacy
import re
import string
from nltk import ngrams
from collections import Counter
from extraction import load_tweets, load_answers

# Class that extracts potential categories from a set of tweets
class CategoryExtractor():

	# A class representing a potential component of an award category
	class Component():

		def __init__(self, engram):

			# Text components of the ngram
			self.words = [word for word in engram[0]]
			self.phrase = ' '.join(self.words)

			# Scores in reference to role, medium, or genre determination
			self.r = 0.0
			self.m = 0.0
			self.g = 0.0

			# Other scores, continually reset as metrics are tested
			self.scores = [engram[1]]
			self.freq = 0

		def __str__(self):
			return f"({self.phrase} | r:{self.r}, m:{self.m}, g:{self.g} | freq:{self.freq})"

		def __repr__(self):
			return str(self)



	def __init__(self, tweets):
		# Cleaning the tweets
		self.tweets = self.remove_hashtags(self.make_alpha(tweets))

		# Regex patterns for grabbing text, ordered by level of precision
		self.patterns = {
			"exact": [r'.*\b(best\b.*) goes to\b.*', r'.*\b(best\b.*) awarded to\b.*', r'.*\b(best\b.*) won by\b.*'],
			"specific": [r'.*\bnominated for (best\b.*)', r'.*\bw[io]ns? (best\b.*)', r'.*\bawarded (best\b.*)', r'.*\baward for (best\b.*)', r'.*\bawarded the (best\b.*)', r'.*\bwinner of (best\b.*)', r'.*\b(best\b.*)goes to\b.*', r'.*\b(best\b.*)awarded to\b.*', r'.*\b(best\b.*)won by\b.*'],
			"ambiguous": [r'.*\b(best\b.*)']
		}

		# Other Initialization
		self.components = []
		self.categories = []
		self.roles = []
		self.mediums = []
		self.genres = []


	def determine_components(self):

		# Resetting
		self.roles = []
		self.mediums = []
		self.genres = []

		# Component Determination
		for c in self.components:
			scores = [c.r, c.m, c.g]
			i = scores.index(max(scores))
			if i == 0:
				self.roles.append(c)
			elif i == 1:
				self.mediums.append(c)
			else:
				self.genres.append(c)

		# Sorting
		self.roles.sort(reverse=True, key=lambda r: r.r)
		self.mediums.sort(reverse=True, key=lambda m: m.m)
		self.genres.sort(reverse=True, key=lambda g: g.g)


	# Find components that correspond to genres
	def score_components(self, tweets=None, limit=4):

		#Getting the ngrams
		engrams = self.get_ngrams(tweets, limit)

		# Getting the potential components
		components = []
		if not self.components:

			# Taking ngrams with 2, 3, or 4 words, and finding those that dont begin with best. There are more likely to be genres because they are at the end.
			for n in range(2, limit + 1):
				components += [self.Component(engram) for engram in engrams[n].most_common(50) if engram[0][0] not in ['or'] and engram[0][-1] != 'or']

		else:
			components = self.components

		endings = Counter([tweet.split()[-1] for tweet in tweets]).most_common(20)

		# Checking whether a component terminates at the end of the tweet
		for component in components:
			cstart = component.words[0]
			cend = component.words[-1]
			component.scores = [0, 0, 0]
			for tweet in tweets:
				words = tweet.split()
				tstart = words[0]
				tend = words[-1]
				if component.phrase in tweet:
					component.freq += 1
					if cstart == tstart and cend != tend:
						component.scores[0] += 2
						component.scores[1] += 1
						component.scores[2] -= 2
					elif cstart != tstart and cend == tend:
						component.scores[0] -= 2
						component.scores[1] += 1
						component.scores[2] += 2
					else:
						component.scores[0] -= 1
						component.scores[1] += 2
						component.scores[2] -= 1

		components.sort(reverse=True, key=lambda x: x.freq)
		freq_max = components[0].freq

		components = [component for component in components if component.freq > (0.1 * freq_max)]

		components.sort(reverse=True, key=lambda x: x.scores[0])
		r_max = components[0].scores[0]

		components.sort(reverse=True, key=lambda x: x.scores[1])
		m_max = components[0].scores[1]

		components.sort(reverse=True, key=lambda x: x.scores[2])
		g_max = components[0].scores[2]

		for c in components:
			c.r += round(c.scores[0] / r_max, 3)
			c.m += round(c.scores[1] / m_max, 3)
			c.g += round(c.scores[2] / g_max, 3)

		self.components = components
		return components


	# Returns a list of n categories, ordered by highest probability
	def answers(self, n=27):
		return []

	# Returns a list of n categories as strings, ordered by highest probability
	def str_answers(self, n=27):
		return [str(category) for category in self.answers(n)]

	# Using the existing roles, mediums, and genres, extrapolates novel possible categories
	def extrapolate(self):
		pass

	# Returns some metrics about the accuracy of the model
	def get_acc(self):
		answers = load_answers()
		preds = self.str_answers()
		correct = []
		missed = []
		false = []
		for answer in answers:
			if answer in preds:
				correct.append(answer)
			else:
				missed.append(answer)

		for pred in preds:
			if pred not in answers:
				false.append(answer)

		accuracy = len(correct) / len(answers)

		return accuracy, correct, missed, false

	# Takes in a list of strings, returns a list of strings containing only alpha characters [a-z]
	@staticmethod
	def make_alpha(tweets):
		return [re.sub(r'[^a-z -#]+', '', text.lower()) for text in tweets]

	# Reduce the number of words in each tweet (the beginning words should contain the award name)
	@staticmethod
	def shorten(tweets, limit=10):
		result = []
		for tweet in tweets:
			words = tweet.split(' ')
			short = ' '.join(words[0:limit])
			result.append(short)
	
		return result

	# Returns a list of tweets that matches any of the given patterns
	@staticmethod
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
	@staticmethod
	def count_words(tweets):
		word_count = Counter()
		for tweet in tweets:
			word_count += Counter(tweet.split(' '))
	
		return word_count

	# Given a list of words, filters a set of tweets to only include those words
	@staticmethod
	def filter_words(filter_words, tweets):
		result = []
		for tweet in tweets:
			words = tweet.split(' ')
			filtered = ' '.join([word for word in words if word in filter_words])
			result.append(filtered)

		return result


	# Given a list of words, filters a set of tweets to remove those words (always includes empty words)
	@staticmethod
	def remove_words(to_remove, tweets):
		result = []
		for tweet in tweets:
			words = tweet.split(' ')
			filtered = ' '.join([word for word in words if word not in to_remove + ['']])
			result.append(filtered)

		return result

	# Removes words with hashtags and empty words
	@staticmethod
	def remove_hashtags(tweets):
		result = []
		for tweet in tweets:
			words = tweet.split(' ')
			filtered = ' '.join([word for word in words if '#' not in word and word != ''])
			result.append(filtered)

		return result

	# Returns a large list of broadly filtered tweets
	def tweet_filter_broad(self):
	
		# Initialization
		data = self.tweets

		# Creating a copy of the data that will be parsed with lower quality
		data_lq = data[:]

		# Gathering all tweets that match a certain set of regex patterns
		data_hq = self.match_any(data, self.patterns['exact'])
		data_lq = self.match_any(data, self.patterns['ambiguous'])

		# Shortening the tweets to 10 words, which should cover all of the 	award names
		data_hq = self.shorten(data_hq)
		data_lq = self.shorten(data_lq)

		# Gathering a count of all words in the processed tweets
		common = self.count_words(data_hq)

		# Returning the 100 most common words as a list of strings
		common = [word[0] for word in common.most_common(50)]

		# Filtering tweets to contain only the most common words
		data_hq = self.filter_words(common, data_hq)
		data_lq = self.filter_words(common, data_lq)

		# Recombining the sets
		data = data_lq + data_hq

		# Removing words that do not contribute semantic value
		data = self.remove_words(['in', 'at', 'as', 'a', 'for'], data)

		# Sorting the processed tweets
		return Counter(data), data

	# Returns a smaller list of more precisely filtered tweets
	def tweet_filter_precise(self):

		# Initialization, better name
		data = self.tweets

		# Matching to precise patterns
		data = self.match_any(data, self.patterns['exact'])

		# Shortening
		data = self.shorten(data)

		# Keeping only the 50 most common words
		data = self.filter_words([word[0] for word in self.count_words(data).most_common(50)], data)	

		# Removing words that do not contribute semantic value
		data = self.remove_words(['in', 'is', 'at', 'as', 'a', 'for'], data)

		# Sorting processed tweets
		return Counter(data), data

	# Given a set of tweets, returns a dicitonary containing all of the ngrams for each length n, where n is the set of dictionary keys
	@staticmethod
	def get_ngrams(tweets, limit=None):

		# Initialization
		engrams = {}
		n = 2
		result = [None]
	
		# Continue building a dictionary of ngrams until we no longer get any results
		while result and n <= limit:
			result = []
			for tweet in tweets:
				for gram in ngrams(tweet.split(), n): result.append(gram)
			engrams[n] = Counter(result)
			n += 1

		return engrams


# Class representing a potential award category
class Category():

	def __init__(self, medium, role=None, genre=None):

		# Initialization
		self.role = role
		self.medium = medium
		self.genre = genre

		# Score representing the probability of this category
		self.score = 0


	# Output to a string that is serviceable for providing answers
	def __str__(self):
		if self.medium and self.role and self.genre:
			return f'best performance by an {self.role} in a {self.medium} - {self.genre}'
		elif not self.role:
			return f'best {self.medium} - {self.genre}'
		else:
			return f'best {self.role} - {self.medium}'


real_categories = [
	Category('motion picture', 'screenplay'),
	Category('motion picture', 'director'),
	Category('television series', 'actress', 'comedy or musical'),
	Category('film', 'foreign language'),
	Category('motion picture', 'supporting actor')
]


x = CategoryExtractor(load_tweets('2013tweets'))
for t in [x.tweet_filter_precise()[1]]: x.score_components(t)
x.determine_components()
for z in x.roles: print(z)
print()
for z in x.mediums: print(z)
print()
for z in x.genres: print(z)
print('\n', x.components)


#for answer in load_answers(): print(answer)
#for category in real_categories: print(category)