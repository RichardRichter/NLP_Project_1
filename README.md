# NLP_Project_1

Issues with requirements and en_core_web_sm:

We used spacy for their named entity recognition, which requires the use of a package called en_core_web_sm. We found pip to be unreliable for installing this package consistently; usually it doesn't work. While we did include it in the requirements.txt, if necessary one should run 'python3 -m spacy download en_core_web_sm' directly within the terminal or python environment, and it should install normally. 

How to run our project:

We interpreted the directions such that the API's pre_ceremony function would be run first, followed by the autograder, followed by the API's main function. We were hesitant to change any of the parameters in the function signature, so we did processing for both 2013 and 2015 within pre_ceremony rather than doing it on a per year basis (which would require the addition of a 'year' parameter in the function signature). As such, if an additional year is to be tested, 3 function calls must be added in pre_ceremony for that year. These are (in order):
    l. extraction.save_tweets(year, 'ggyear.json')
    l. categories.save_awards(year)
    l. tweet_miner.main(year)
These are required to allow the API to have access to answers for any given year. Our tweet_miner function automatically produces both a .json and human-readable .txt output. Consequently, our main function simply reads the text that is already outputted to the .txt file.

Our program was designed to run in the following order:
    l. ggapi.pre_ceremony (We dont call this manually. We assumed that the grader would call it as it says in the description that it would be run first)
    l. autograder (Should be run for all years)
    l. ggapi.main
