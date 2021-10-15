import spacy
from spacy import displacy

# for the sake of speed, disable every part of spacy except for named entity recognition
nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

#dictionary of how many times a Name comes up in all the tweets
ppl = {}

with open('tweets.txt', encoding='utf-8') as f:
    lines = f.readlines()
    # line here corresponds to a singular tweet's text
    for line in lines:
        text1 = nlp(line)
        # this assigns a label to every word/set of words in the sentence if possible
        for word in text1.ents:
            # ignore all other words that have labels that aren't people
            if word.label_ == 'PERSON':
                person = word.text
                # very simple data cleaning to remove 's from the end of some names
                if person[-2:] == "'s":
                    person = person[:-2] 
                # this person already exists in the dictionary, so just increment the count
                if person in ppl:
                    ppl[person] = ppl[person] + 1
                # add the person to the dictionary
                else:
                    ppl[person] = 1

    print("done")

sorted_dict = sorted([(value,key) for (key,value) in ppl.items()])
sorted_dict.sort(reverse=True)
print(sorted_dict)