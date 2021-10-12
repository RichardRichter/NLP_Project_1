import json #needs to be imported to read json files
f = open('gg2013.json') 
data = json.load(f) #deserializes the json file to a python object
len(data)
my_data = [] # creates a list for our tweets
for i in data:
  my_data.append(i['text']) # for every tweet in the data, its going to extract the text section
