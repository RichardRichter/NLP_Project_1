import json
f = open('gg2013.json')
data = json.load(f)
len(data)
my_data = []
for i in data:
  my_data.append(i['text'])
