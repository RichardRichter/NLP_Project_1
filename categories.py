import spacy
import re
import string
from collections import Counter
from extraction import load_tweets

# nlp is the 'natural language processor'
nlp = spacy.load('en_core_web_sm')
data = load_tweets()
processed = []

# Common phrases that could precede or succeed category names
patterns = [r'.*\bnominated for (best\b.*)', r'.*\bw[io]ns? (best\b.*)', r'.*\bawarded (best\b.*)', r'.*\baward for (best\b.*)', r'.*\bawarded the (best\b.*)', r'.*\bwinner of (best\b.*)', r'.*\b(best\b.*)goes to\b.*', r'.*\b(best\b.*)awarded to\b.*', r'.*\b(best\b.*)won by\b.*']

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
common = [word[0] for word in common.most_common(50)]

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
print(count_categories.most_common(10))


print(len(processed))
#print(processed[0:-1])