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
        if "host" in line.lower() and "next" not in line.lower():
            text1 = nlp(line)
            # this assigns a label to every word/set of words in the sentence if possible
            for word in text1.ents:
                # ignore all other words that have labels that aren't people
                if word.label_ == 'PERSON':
                    person = word.text
                    # ignore irregular names like firstlast or Golden Globes
                    if " " in person and "golden" not in person.lower():
                        # very simple data cleaning to remove 's from the end of some names
                        if person[-2:] == "'s":
                            person = person[:-2] 
                        # this person already exists in the dictionary, so just increment the count
                        if person in ppl:
                            ppl[person] = ppl[person] + 1
                        # add the person to the dictionary
                        else:
                            ppl[person] = 1

# convert the ppl dictionary to a list of (votes, name) sorted so most frequent names come up first
sorted_dict = sorted([(value,key) for (key,value) in ppl.items()])
sorted_dict.sort(reverse=True)

# the top result means this name showed up the most, so it's definitely a host
(votes, definite_host) = sorted_dict[0]
hosts = [definite_host]

# there might be multiple hosts, so search 
keep_searching = True
host_index = 1

while keep_searching:
    # get the next most frequent name
    (num_votes, potential_host) = sorted_dict[host_index]
    # check that the votes is at leaast 60% of the definite host, threshold subject to change
    if float(num_votes) / votes > 0.6:
        # make potential host a host
        hosts.append(potential_host)
    else:
        # because this person doesn't have enough votes, subsequent entries will have even fewer votes so stop searching altogether
        keep_searching = False
    host_index += 1

print(hosts)