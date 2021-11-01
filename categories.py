import re
import pickle
from nltk import ngrams
from collections import Counter
from extraction import load_tweets, load_answers

def prog_print(s):
	print('                                               ', end='\r', flush=True)
	print(s, end='\r', flush=True)

# Class that extracts potential categories from a set of tweets
class CategoryExtractor():

	# A class representing a potential component of an award category
	class Component():

		def __init__(self, engram):

			# Text components of the ngram
			self.words = [word for word in engram[0]]
			self.phrase = ' '.join(self.words)
			self.type = None

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

		def __eq__(self, other):

			# Cant handle non component comparison
			if not isinstance(other, CategoryExtractor.Component):
				return NotImplemented

			# Comparing string contents
			return self.phrase == other.phrase

		def __hash__(self):
			return self.phrase.__hash__()

		# Sometimes there are issues with floating point numbers. Ensures that all scores are rounded to 3 decimals
		def clean_scores(self):
			self.r = round(self.r, 3)
			self.m = round(self.m, 3)
			self.g = round(self.g, 3)

		# Resets scores
		def reset_score(self):
			self.r = 0
			self.m = 0
			self.g = 0



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
		self.before_role = []
		self.before_medium = []

	# Returns extractor to initialized state
	def reset(self):
		self.components = []
		self.categories = []
		self.roles = []
		self.mediums = []
		self.genred = []

	# Processes a set of tweets and returns n of the most likely award categories. This is the single command that should be run to extract categories.
	def extract(self, n=27, return_type='category'):

		# Scoring potential components based on two set of filtered tweets
		prog_print('filtering tweets')
		counts, raw = self.tweet_filter_precise()

		# Getting components that contain best, scoring them
		prog_print('finding components (best included)')
		with_best = self.find_components(counts)

		prog_print('scoring components (best included)')
		with_best = self.score_components(with_best, counts)
		with_best = self.score_components(with_best, raw)

		# Getting components with best removed before being scores, scoring them
		prog_print('finding components (best excluded)')
		without_best = self.find_components(counts, remove_best=True)

		prog_print('scoring components (best excluded)')
		without_best = self.score_components(without_best, counts, remove_best=True)
		without_best = self.score_components(without_best, raw, remove_best=True)

		self.components = with_best + without_best

		# Cleaning up components after they've been scores, aggregating and deleting some
		prog_print('aggregating components')
		replaced = self.aggregate_components()

		# Categorizing the components based on their respective scores for r, m, and g.
		prog_print('categorizing components')
		self.categorize_components()

		# Rescoring
		prog_print('rescoring')
		for c in self.components: c.reset_score()
		self.components = self.score_components(self.components, counts, remove_best=True)
		self.components = self.score_components(self.components, raw, remove_best=True)
		self.sort_components()


		# Limiting the number of viable components after sorting
		#self.roles = self.roles[:10]
		self.mediums = self.mediums[:10]
		self.genres = self.genres[:10]

		# Another round of aggregation
		prog_print('more aggregation happening')
		self.aggregate_components_v2()

		# Extrapolating potential categories based on component combinations
		prog_print('extrapolating components')
		self.extrapolate()

		# Scoring categories
		prog_print('scoring categories')
		self.score_categories(raw)

		# Cleaning up the categories after scoring
		prog_print('aggregating categories')
		self.aggregate_categories()

		# Finding relevant tweets for each category to determine real names
		prog_print('finding filler words')
		self.find_filler()

		# Determining what to return
		prog_print('gathering answers')
		if return_type == 'category':
			return self.answers(n), replaced

		elif return_type in ['string', 'str']:
			return self.str_answers(n)

		else:
			print('This return type is not supported')
			return NotImplemented

	# Finding words that go inbetween the components
	def find_filler(self):

		tweets = self.tweet_filter_precise(remove_filler=False)[1]
		tweets = [' '.join(tweet.split()[1:]) for tweet in tweets]
		all_before = []
		all_after = []
		for t in tweets:
			for c in self.categories:
				if c.role is not None and c.role.phrase in t:
					before, role, after = t.partition(c.role.phrase)
					all_before.append(before)
					if c.medium.phrase in after:
						before, medium, after = t.partition(c.medium.phrase)
						all_after.append(before)

		all_keywords = [x for x in set([word for c in (self.roles[:5] + self.mediums + self.genres) for word in c.words])]

		all_before = self.remove_words(all_keywords, all_before)
		all_before = [x for x in all_before if len(x) > 0]
		all_after = self.remove_words(all_keywords, all_after)
		all_after = [x for x in all_after if len(x) > 0]

		self.before_role = Counter(all_before).most_common()[0][0]
		self.before_medium = Counter(all_after).most_common()[0][0]

		for c in self.categories:
			c.before_role = self.before_role
			c.before_medium = self.before_medium


	# Cleaning all component scores (rounding to nearest 3 digits)
	def clean_components(self):
		for c in self.roles + self.mediums + self.genres:
			c.clean_scores()


	# Sort the components into their proper category location
	def categorize_components(self):

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
				c.type = self.roles
			elif i == 1:
				self.mediums.append(c)
				c.type = self.mediums
			else:
				self.genres.append(c)
				c.type = self.genres

		# Sorting
		self.sort_components()

		# Fixing some floating point weirdness
		self.clean_components()

	# Sorts the categories in order of their scores
	def sort_components(self):
		self.roles.sort(reverse=True, key=lambda r: r.r)
		self.mediums.sort(reverse=True, key=lambda m: m.m)
		self.genres.sort(reverse=True, key=lambda g: g.g)


	# Finds a set of components for a set of tweets
	def find_components(self, tweets, limit=3, remove_best=False):

		# Getting the ngrams
		engrams = self.get_ngrams(tweets, limit)

		# Collecting potential components
		components = []
		for n in range(2, limit + 1):

			# Taking ngrams with 2, 3, or 4 words, and finding those that dont begin with best. There are more likely to be genres because they are at the end.
			components += [self.Component(engram) for engram in engrams[n].most_common() if 'or' not in [engram[0][0], engram[0][-1]]]

		# Removing 'best' keyword
		if remove_best:
			for component in components:
				if component.words[0] == 'best':
					component.words = component.words[1:]
					component.phrase = ' '.join(component.words)

		# Removing Duplicates
		components = [c for c in set(components)]

		return components

	# Aggregates components by resolving conflicts between duplicates
	def aggregate_components(self):

		# Components must be categorized before they can be aggregated, they will be categorized again after aggregation
		self.categorize_components()

		# Removing 'best' keyword
		for component in self.components:
			if component.words[0] == 'best':
				component.words = component.words[1:]
				component.phrase = ' '.join(component.words)


		# Gathering all words in components
		all_words = set([word for component in self.components for word in component.words])
		all_words = [(word, [0,0,0]) for word in all_words]


		# Scoring the words based on how often they show up in each component type
		def scored_word_count(comps, weight=1):
			counts = Counter()
			for i, c in enumerate(comps):
				for word in c.words:
					counts[word] += 10 / (i+1) ** weight

			for c in counts:
				counts[c] = round(counts[c], 2)

			return counts

		role_words = scored_word_count(self.roles, 1.)
		medium_words = scored_word_count(self.mediums, 1.)
		genre_words = scored_word_count(self.genres, 1.)

		for word in all_words:
			if word[0] in role_words:
				word[1][0] = role_words[word[0]]
			if word[0] in medium_words:
				word[1][1] = medium_words[word[0]]
			if word[0] in genre_words:
				word[1][2] = genre_words[word[0]]

		# Sorting the words after scoring
		role_words, medium_words, genre_words = [], [], []
		for word in all_words:
			best = word[1].index(max(word[1]))
			if best == 0:
				role_words.append(word[0])
			elif best == 1:
				medium_words.append(word[0])
			elif best == 2:
				genre_words.append(word[0])

		# Removing words that don't belong in components of a certain type (roles contain only role words)
		for c in self.components:
			if c.type is self.roles:
				c.words = [word for word in c.words if word in role_words]
			elif c.type is self.mediums:
				c.words = [word for word in c.words if word in medium_words]
			elif c.type is self.genres:
				c.words = [word for word in c.words if word in genre_words]
			c.phrase = ' '.join(c.words)

		self.components = [c for c in self.components if len(c.words) > 0]


		new = []
		replaced = []
		# Removing duplicates
		for c in self.components:
			
			# A copy of this component already exists. Find which is better
			try:
				copy = new.pop(new.index(c))
				if copy.type.index(copy) > c.type.index(c):
					new.append(c)
					replaced.append(copy)
				else:
					new.append(copy)
					replaced.append(c)

			# The component does not have a copy in the new list of components
			except ValueError:
				new.append(c)

		self.components = new
		return replaced


	# Second round of aggregation that occurs after rescoring
	def aggregate_components_v2(self):

		def logical_and(l):
			initial = True
			for item in l:
				initial = initial and item

			return initial

		def remove_copies(l):
			new = []
			new_words = []
			for c in l:
				c_words = [word for word in c.words]
				c_words.sort()
				if c_words not in new_words:
					new.append(c)
					new_words.append(c_words)
			return new

		self.roles = remove_copies(self.roles)
		self.mediums = remove_copies(self.mediums)
		self.genres = remove_copies(self.genres)


		for comp_type_master in [self.roles, self.mediums, self.genres]:
			threshold = 0
			if comp_type_master is self.roles:
				threshold = 0.8
			elif comp_type_master is self.mediums:
				threshold = 0.3
			elif comp_type_master is self.genres:
				threshold = 0.4
			comp_type = comp_type_master[:]
			for i, c in enumerate(comp_type):
				other_c = comp_type[:i] + comp_type[i+1:]
				contained_in = []
				for other in other_c:
					if logical_and([word in other.words for word in c.words]):
						contained_in.append(other)
				total_freq = sum(other.freq for other in contained_in)
				if total_freq > (c.freq * threshold):
					comp_type_master.remove(c)


	# Scores a set of components based on a set of tweets
	def score_components(self, components, tweets, remove_best=False):

		# Gathering components
		components = components if components else (self.components if self.components else self.find_components(tweets))

		# Removing 'best' from front of tweets
		if remove_best:
			tweets = [' '.join(tweet.split()[1:]) if tweet.split()[0] == 'best' else tweet for tweet in tweets]

		# Checking whether a component terminates at the end of the tweet
		for component in components:
			component.freq = 0
			component.scores = [0, 0, 0]
			for tweet in tweets:
				if tweet.startswith(component.phrase):
					component.freq += 1
					component.scores[0] += 2
					component.scores[1] += 1
					component.scores[2] -= 2
				elif tweet.endswith(component.phrase):
					component.freq += 1
					component.scores[0] -= 2
					component.scores[1] += 1
					component.scores[2] += 2
				elif component.phrase in tweet:
					component.freq += 1
					component.scores[0] -= 1
					component.scores[1] += 2
					component.scores[2] -= 1

		# Grabbing max value for each component type
		components.sort(reverse=True, key=lambda x: x.scores[0])
		r_max = components[0].scores[0]

		components.sort(reverse=True, key=lambda x: x.scores[1])
		m_max = components[0].scores[1]

		components.sort(reverse=True, key=lambda x: x.scores[2])
		g_max = components[0].scores[2]


		# Scoring each component's categories by their proportion of the maximum value
		for c in components:
			c.r += round(c.scores[0] / r_max, 3)
			c.m += round(c.scores[1] / m_max, 3)
			c.g += round(c.scores[2] / g_max, 3)

		return components


	# Scores the current set of categories based on a set of tweets
	def score_categories(self, tweets):

		# Sorting tweets to start with those that are most relevant
		self.categories.sort(reverse=True, key=lambda c: c.component_score)

		# Incrementing score for each match
		for category in self.categories:
			for tweet in tweets:
				if category.match_tweet(tweet):
					category.tweet_score += len(category.keywords) ** 3

	# Cleaning up categories by removing those that share exactly the same keywords
	def aggregate_categories(self):
		cats = self.categories
		for i, category in enumerate(cats):
			others = cats[:i] + cats[i+1:]
			for other in others:
				if category.keywords == other.keywords:
					if category.component_score > other.component_score:
						self.categories.remove(other)
					else:
						self.categories.remove(category)


	# Returns a list of n categories, ordered by highest probability
	def answers(self, n=27):

		# Sorting by tweet score
		self.categories.sort(reverse=True, key=lambda c: c.tweet_score)

		# List comp in case categories is not a list at this point
		return [c for c in self.categories][:n]


	# Returns a list of n categories as strings, ordered by highest probability
	def str_answers(self, n=27):
		return [str(category) for category in self.answers(n)]


	# Using the existing roles, mediums, and genres, extrapolates novel possible categories
	def extrapolate(self, limit=10):
		initial = len(self.categories)
		new = []
		for medium in self.mediums[:limit]:
			for role in self.roles[:limit]:
				cat = Category(medium, role)
				if cat not in self.categories:
					new.append(cat)
					self.categories.append(cat)
				for genre in self.genres[:limit]:
					cat = Category(medium, role, genre)
					if cat not in self.categories:
						new.append(cat)
						self.categories.append(cat)
			for genre in self.genres[:limit]:
				cat = Category(medium, genre=genre)
				if cat not in self.categories:
					new.append(cat)
					self.categories.append(cat)
		
		return new, len(self.categories) - initial


	# Finding the actual category names that pertain to each category after scoring
	def find_names(self, n=27):

		# Sorting by tweet score
		self.categories.sort(reverse=True, key=lambda c: c.tweet_score)

		# Finding tweets
		for i, category in enumerate(self.categories[:n]):
			print(f'finding names for category {i} / {n}', end="\r", flush=True)
			scores = Counter()
			for tweet in self.tweet_filter_precise(remove_filler=False)[1]:
				if category.match_tweet(tweet):
					scores[tweet] += len(category.keywords)
			category.names = scores.most_common()


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
		return [re.sub(r'[^a-z #]+', '', text.lower()) for text in tweets]

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

	# Returns a smaller list of more precisely filtered tweets
	def tweet_filter_precise(self, remove_filler=True):

		# Initialization, better name
		data = self.tweets

		# Matching to precise patterns
		data = self.match_any(data, self.patterns['exact'])

		# Shortening
		data = self.shorten(data)

		# Replacing TV with Television (explicitly allowed by TA)
		data =  [' '.join(['television' if word == 'tv' else word for word in tweet.split()]) for tweet in data]

		# Keeping only the 50 most common words
		data = self.filter_words([word[0] for word in self.count_words(data).most_common(50)], data)	

		# Removing words that do not contribute semantic value
		if remove_filler:
			data = self.remove_words(['in', 'is', 'at', 'as', 'a', 'of', 'by', 'an', 'for', 'the', 'on', 'to', 'and'], data)

		# Avoid tweets with only a single word remaining. Not possible
		data = [t for t in data if len(t) > 1]

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
		self.keywords = self.keywords()
		self.names = []

		# Fillers
		self.before_role = ''
		self.before_medium = ''

		# Score representing the probability of this category
		self.component_score = self.score_components()
		self.tweet_score = 0

		# Bool representing whether or not components overlap
		self.unique, self.overlaps = self.verify_integrity()

	def __repr__(self):
		r = self.role.phrase if self.role else 'NA'
		m = self.medium.phrase if self.medium else 'NA'
		g = self.genre.phrase if self.genre else 'NA'
		return f'(| {r} | {m} | {g} | Scores: c - {self.component_score}, t - {self.tweet_score})'


	# Output to a string that is serviceable for providing answers
	def __str__(self):

		# Ensuring that we dont say best twice
		if self.role and self.role.words[0] == 'best':
			words = self.role.words[1:]
			self.role.words = words
			self.role.phrase = ' '.join(words)

		# Outputting category to a string
		if self.medium and self.role and self.genre:
			return f'best {self.before_role} {self.role.phrase} {self.before_medium} {self.medium.phrase} - {self.genre.phrase}'

		elif not self.role:
			return f'best {self.medium.phrase} - {self.genre.phrase}'

		else:
			return f'best {self.role.phrase} - {self.medium.phrase}'

	def __eq__(self, other):

		# Check class of comparison
		if not isinstance(other, Category):
			return NotImplemented

		# All elements of the category must be equal
		return self.role == other.role and self.medium == other.medium and self.genre == other.genre


	# Ensures that category components are non-overlapping
	def verify_integrity(self):

		#Initialization
		unique = True
		overlaps = False
		components = [c for c in [self.role, self.medium, self.genre] if c is not None]

		# Determine whether or not all components are unique
		phrases = [c.phrase for c in components]
		for i, phrase in enumerate(phrases):
			others = phrases[:]
			others.pop(i)
			for other in others:
				if phrase in other:
					unique = False
					break

		# Deterimine whether any word overlap exists between components
		words = []
		for c in components:
			for w in c.words:
				words.append(w)
		counts = Counter(words)
		overlaps = counts.most_common(1)[0][1] > 1

		return unique, overlaps

	# Provides a score to a category based on the combined score of each component
	def score_components(self):

		# Gathering component scores
		r = self.role.r if self.role else 0
		m = self.medium.m if self.medium else 0
		g = self.genre.g if self.genre else 0
		total = [x for x in [r, m, g] if x > 0]

		# Returning average score per component present
		return round(sum(total) / len(total), 3)

	# Returns a boolean value corresponding to whether the given tweet matches this category
	def match_tweet(self, tweet):

		if tweet.split()[0] == 'best':
			tweet = ' '.join(tweet.split()[1:])

		# Cant match against nonstrings
		if not isinstance(tweet, str):
			return False

		# Determing what components we have to work with.
		if self.role:
			if tweet == self.role.phrase:
				return False
			elif tweet.startswith(self.role.phrase):
				tweet = tweet.replace(self.role.phrase + ' ', '')
			else:
				return False

		if self.genre:
			if tweet == self.genre.phrase:
				return False
			elif tweet.endswith(self.genre.phrase):
				x = tweet
				tweet = tweet.replace(' ' + self.genre.phrase, '')
			else:
				return False

		if self.medium.phrase in tweet:
			return True
		return False

	def keywords(self):
		keys = [w for w in self.medium.words]
		keys += self.role.words if self.role else []
		keys += self.genre.words if self.genre else []
		keys.sort()
		return keys


def get_categories(tweets, n=27):
	extractor = CategoryExtractor(tweets)
	return extractor.extract(n, return_type='str')

def save_awards(year):

	filename = str(year) + 'awards'

	# Grabbing all of the necessary text data
	data = get_categories(load_tweets(year))

	# Outputting the data to a pickle
	with open(filename, 'wb') as award_file:
		pickle.dump(data, award_file)


def load_awards(year):
	
	filename = str(year) + 'awards'

	try:
		with open(filename, 'rb') as awards:

			# Loading the pickle
			data = pickle.load(awards, encoding='utf-8')
	
			# Returning the number of tweets we want
			return data

	# If we can't find the file under filename, create it
	except FileNotFoundError:
		save_awards(year)
		return load_awards(year)


# DEV AND TESTING
if __name__ == "__main__":
	'''
	x = CategoryExtractor(load_tweets('2015tweets'))
	answers, replaced = x.extract(n=40)
	print()
	for z in x.roles: print(z)
	print()
	for z in x.mediums: print(z)
	print()
	for z in x.genres: print(z)
	print()
	for a in answers: print(a.__repr__())
	print()
	for a in answers[:27]: print(a)
	print()
	for a in answers[27:]:print(a)
	print()
	for m in load_answers(): print(m)
	print()
	print(x.get_acc())
	print(x.before_role.__repr__())
	print(x.before_medium.__repr__())
	'''
	print(load_awards(2015))