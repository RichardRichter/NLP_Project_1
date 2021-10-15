import json 
#import pickle

f = open('gg2013.json') 
#deserializes the json file to a python object
data = json.load(f) 

# creates a list of the text in each tweet of the data  
my_data = [tweet['text'] for tweet in data]
#print(my_data[0])

#outfile = open('tweets', 'wb')
#pickle.dumps(my_data, outfile)


with open('tweets.txt', 'w', encoding="utf-8") as f:
  for data in my_data:
    f.write(data)
    f.write("\n")