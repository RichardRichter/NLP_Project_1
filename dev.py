import categories
from collections import Counter
from nltk import ngrams
from extraction import load_tweets, load_answers

tweets = load_tweets()
tweets = categories.make_alpha(tweets)
tweets = categories.remove_hashtags(tweets)
tweets = categories.match_any(tweets, categories.patterns_exact)
tweets = categories.shorten(tweets)
tweets = categories.filter_words([word[0] for word in categories.count_words(tweets).most_common(50)], tweets)
tweets = categories.remove_words(['in', 'at', 'as', 'a', 'for', 'is'], tweets)

def get_ngrams(tweets):

	# Initialization
	engrams = {}
	n = 2
	result = [None]

	# Continue building a dictionary of ngrams until we no longer get any results
	while result:
		result = []
		for tweet in tweets:
			for gram in ngrams(tweet.split(), n): result.append(gram)
		engrams[n] = Counter(result)
		n += 1

	print(n, engrams[n-2])
	return engrams


x = get_ngrams(tweets)
print(x[2].most_common(20))
print(x[3].most_common(20))