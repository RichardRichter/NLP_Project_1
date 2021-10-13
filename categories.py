import spacy
import re
from collections import Counter
from extraction import load_tweets

# nlp is the 'natural language processor'
nlp = spacy.load('en_core_web_sm')
data = load_tweets()
potential_categoroies = []

# Common phrases that could precede or succeed category names
patterns = [r'.*\bnominated for\b(.*)', r'.*\bwon\b(.*)', r'.*\bawarded\b(.*)', r'.*\baward for\b(.*)', r'.*\bawarded the\b(.*)', r'(.*)\bawarded\b(.*)', r'.*\bwinner of\b(.*)']

# Collecting tweets with matches
for tweet in data:
	for pattern in patterns:
		match = re.match(pattern, tweet.lower())
		if match:

			# We only want the text that corresponds to where the award would be in the tweet (use group 1)
			potential_categoroies.append(match.group(1))
			break

#
print(len(potential_categoroies))
print(potential_categoroies[0:10])