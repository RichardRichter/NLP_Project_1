import spacy
import re
import string
from collections import Counter
from extraction import load_tweets

# nlp is the 'natural language processor'
nlp = spacy.load('en_core_web_sm')
data = load_tweets()
potential_categories = []

# Common phrases that could precede or succeed category names
patterns = [r'.*\bnominated for (best\b.*)', r'.*\bwon (best\b.*)', r'.*\bawarded (best\b.*)', r'.*\baward for (best\b.*)', r'.*\bawarded the (best\b.*)', r'(.*)\bawarded (best\b.*)', r'.*\bwinner of (best\b.*)']

# Collecting tweets with matches
for tweet in data:
	for pattern in patterns:
		match = re.match(pattern, tweet.lower())
		if match:

			# We only want the text that corresponds to where the award would be in the tweet (use group 1)
			potential_categories.append(match.group(1))
			break

# Cleaning strings (all alpha)
potential_categories = [re.sub(r'[^a-z ]+', '', text) for text in potential_categories]


print(len(potential_categories))
print(potential_categories[0:-1])