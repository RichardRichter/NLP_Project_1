import spacy
import re
import string
from collections import Counter
from extraction import load_tweets

# nlp engine
nlp = spacy.load('en_core_web_sm')

# Takes in a list of strings, returns a list of strings containing only alpha characters [a-z]
def make_alpha(tweets):
	return [re.sub(r'[^a-z ]+', '', text.lower()) for text in tweets]

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
	for tweet in data:
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



# Grabbing common phrases that could precede or succeed category names
# These are patterns that guarantee that award names will precede them
patterns_specific = [r'.*\bnominated for (best\b.*)', r'.*\bw[io]ns? (best\b.*)', r'.*\bawarded (best\b.*)', r'.*\baward for (best\b.*)', r'.*\bawarded the (best\b.*)', r'.*\bwinner of (best\b.*)', r'.*\b(best\b.*)goes to\b.*', r'.*\b(best\b.*)awarded to\b.*', r'.*\b(best\b.*)won by\b.*']

# This pattern is much more broad, will grab everything
patterns = [r'.*\b(best\b.*)']

# Loadint in the tweets from the json
data = load_tweets()

# Cleaning the tweets by making them alpha and lowercase
data = make_alpha(data)

# Gathering all tweets that match a certain set of regex patterns
data = match_any(data, patterns_specific)

# Shortening the tweets to 10 words, which should cover all of the award names
data = shorten(data)

# Gathering a count of all words in the processed tweets
common = count_words(data)

# Returning the 100 most common words as a list of strings
common = [word[0] for word in common.most_common(100)]

# Filtering tweets to contain only the most common words
data = filter_words(common, data)

# Results of all this processing
categories = Counter(data)
for category in categories.most_common(20):
	print(category)



"""

# Collecting tweets with matches
for tweet in data:
	for pattern in patterns:
		match = re.match(pattern, tweet.lower())
		if match:

			# We only want the text that corresponds to where the award would be in the tweet (use group 1)
			processed.append(match.group(1))
			break

# Cleaning strings (all alpha)
processed = [re.sub(r'[^a-z ]+', '', text) for text in processed]

# Further cleaning if necessary, reduces max word count to 7
categories = []
for text in processed:
	words = text.split(' ')
	new = ' '.join(words[0:8])
	categories.append(new)
processed = categories[:]

# Counting the words in the processed tweets
common = Counter()
for tweet in processed:
	words = tweet.split(' ')
	for word in words:
		common[word] += 1

# Grabbing the 50 most common words
common = [word[0] for word in common.most_common(100)]

# Filtering out uncommon/rare words from the processed category tweets
filtered = []
for tweet in processed:
	words = tweet.split(' ')
	result = []
	for word in words:
		if word in common:
			result.append(word)
	filtered.append(' '.join(result))

processed = filtered[:]
count_categories = Counter(processed)
#print(count_categories.most_common(20))
for item in count_categories.most_common(50):
	print(item)


print(len(processed))
#print(processed[0:-1])

"""