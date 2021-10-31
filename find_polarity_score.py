import nltk
from textblob import TextBlob
def find_polarity_score(self):
    winner = self.winner
    neutral_count = 0
    neutral_list = []
    neutral_average = 0

    negative_count = 0
    negative_list = []
    negative_average = 0

    positive_count = 0
    positive_list = []
    positive_average = 0

    for tweet in tweets:
        if winner in tweet:
            blob1 = TextBlob(tweet)
            #print(blob1.sentiment)
            (polarity, subjectivity) = blob1.sentiment
            if polarity == 0:
                neutral_count += 1
                neutral_list.append(tweet)
                neutral_average += polarity
            elif polarity > 0:
                positive_count += 1
                positive_list.append(tweet)
                positive_average += polarity
            elif polarity < 1:
                negative_count += 1
                negative_list.append(tweet)
                negative_average += polarity
            #print(tweet)
            #print(polarity)
            #print(subjectivity)
    positive_average = positive_average / positive_count
    neutral_average = neutral_average / neutral_count
    negative_average = negative_average / negative_count

    #print(neutral_count)
    #print(negative_count)
    #print(positive_count)

    if positive_count > neutral_count and positive_count > negative_count:
        if positive_average >= .8:
            print("On average tweets mentioning ", winner, " were really positive")
            #print an example tweet
            print()
        elif positive_average <.8 and positive_average >= .3:
            print("On average tweets mentioning ", winner, " were relatively positive")
            #print an example tweet
            print(positive_average)
        else:
            print("On average tweets mentioning ", winner, " were only somewhat positive")
            #print an example tweet
            print()
        self.winner_polarity = positive_average
        return positive_average
    if neutral_count > positive_count and neutral_count > negative_count:
        print("WOW on average the tweets mentioning ", " ", " were neutral?? On Twitter?? #Shocking")
        #print an example tweet
        print()
        self.winner_polarity = neutral_average
        return neutral_average
    if negative_count > positive_count and negative_count > neutral_count:
        if negative_average >= .8:
            print("On average tweets mentioning ", winner, " were really negative")
            #print an example tweet
            print()
        elif negative_average <.8 and negative_average >= .3:
            print("On average tweets mentioning ", winner, " were relatively negative")
            #print an example tweet
            print()
        else:
            print("On average tweets mentioning ", winner, " were only somewhat negative")
            #print an example tweet
            print()
        self.winner_polarity = negative_average
        return negative_average
    #print(polarity_dictionary)
#Most Liked Winner
polarity_dict = {}
for cat in categories:
    polarity_score = find_polarity_score(cat)
    polarity_dict[cat.winner] = polarity_score

sorted(polarity_dict, key=polarity_dict.get)
print("The least liked winner was: ", polarity_dict[0][1], " with a polarity score of ", polarity_dict[1][0])
sorted(polarity_dict, key=polarity_dict.get, reverse = True)
print("The most liked winner was: ", polarity_dict[0][1], " with a polarity score of ", polarity_dict[1][0])
