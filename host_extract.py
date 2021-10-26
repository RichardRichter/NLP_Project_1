import spacy
from spacy import displacy
from extraction import load_tweets

# for the sake of speed, disable every part of spacy except for named entity recognition
nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])


# helper function that runs spacy on the tweet and extracts PERSON tags to put in ppl
def use_nlp(tweet: str, ppl):
    text1 = nlp(tweet)
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


# lines should be the iterable list of tweets obtained from load_tweets
def find_host(lines):
    # dictionary of how many times a Name comes up in all the tweets
    ppl = {}
    # only retrieve the first 1/10th of all the tweets to definitely use Spacy's name entity recognition
    sample_length = len(lines) // 10
    sample_of_lines = lines[:sample_length]
    # this is the remaining 9/10th of the tweets that we probably will not use Spacy on
    rest_of_lines = lines[sample_length:]
    # line here corresponds to a singular tweet's text
    for line in sample_of_lines:
        # we want to get tweets that mention "host"
        # but ignore tweets that contain "next" as those are predictions/desires for future hosts
        if "host" in line.lower() and "next" not in line.lower():
            # run the nlp helper function
            use_nlp(line, ppl)

    # clear obsolete names (names that appear 10 times or fewer are usually typos or the wrong person)
    ppl = {key:val for key, val in ppl.items() if val > 10}

    # iterate through the remaining 1/10ths of the tweets except for the last 1/10th
    for i in range(1, 9):
        n = i + 1
        # retrieve the next 1/10th of the list
        new_lines = lines[i*sample_length:n*sample_length]
        for line in new_lines:
            if "host" in line.lower() and "next" not in line.lower():
                # We might have to find new hosts if any of the old hosts can't be found in this tweet
                new_hosts = True
                for key in ppl:
                    # Found old host, so don't bother looking for new hosts
                    if key.lower() in line.lower():
                        ppl[key] += 1
                        new_hosts = False
                # If we didn't find any new hosts, we'll have to use Spacy and try to find new hosts
                if new_hosts:
                    use_nlp(line, ppl)

        # repeatedly clear obsolete names before going to the next 1/10th tweet
        ppl = {key:val for key, val in ppl.items() if val > 10}

    # retrieve the final 10th of the tweets to analyze
    # this is separate for the other for loop to cover weird integer division
    final_lines = lines[9*sample_length:]
    for line in final_lines:
        if "host" in line.lower() and "next" not in line.lower():
            new_hosts = True
            for key in ppl:
                if key.lower() in line.lower():
                    ppl[key] += 1
                    new_hosts = False

            if new_hosts:
                use_nlp(line, ppl)

    ppl = {key:val for key, val in ppl.items() if val > 10}

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
            # because this person doesn't have enough votes,
            # subsequent entries will have even fewer votes so stop searching altogether
            keep_searching = False
        host_index += 1

    return hosts
