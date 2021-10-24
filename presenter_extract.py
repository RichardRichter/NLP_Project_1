import spacy
import re
import spacy import displacy
from extraction import load_tweets


nlp = spacy.load("en_core_web_sm", disable=['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])

pattern = re.compile(r'present(t|ted|ts|ing)') 

lines = load_tweets()

for line in lines:
   

