'''Version 0.35'''
import json
import tweet_miner
import extraction
import categories

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
OUR_AWARDS = ['best performance by an actor in a motion picture - drama', 'best motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an supporting actor in a series mini - movie', 'best actor - motion picture', 'best performance by an actor in a television series - drama', 'best original song - motion picture', 'best performance by an actress in a motion picture - comedy or musical', 'best television series - drama', 'best actress - motion picture', 'best supporting actor - series mini', 'best performance by an supporting actor in a mini - movie', 'best performance by an supporting actor in a miniseries - movie', 'best performance by an actress in a motion picture - drama', 'best television series - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best actor - television series', 'best supporting actress - motion picture', 'best performance by an actor in a television series - comedy or musical', 'best performance by an supporting actress in a series mini - movie', 'best supporting actor - motion picture', 'best supporting actor - mini', 'best actress - television series', 'best supporting actor - miniseries', 'best series mini - movie', 'best performance by an actress in a television series - drama', 'best performance by an actor in a mini - movie']
OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']


def get_answers(year):
    with open('%sresults.json' % year, 'r') as f:
        fres = json.load(f)
    return fres

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    fres = get_answers(year)
    hosts = fres['hosts']
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    awards = categories.load_awards(year)
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    fres = get_answers(year)
    nominees = {award: fres['award_data'][award]['nominees'] for award in OFFICIAL_AWARDS}
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    fres = get_answers(year)
    winners = {award: fres['award_data'][award]['winner'] for award in OFFICIAL_AWARDS}
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    fres = get_answers(year)
    presenters = {award: fres['award_data'][award]['presenters'] for award in OFFICIAL_AWARDS}
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Saving tweets as python objects
    extraction.save_tweets(2013, 'gg2013.json')
    extraction.save_tweets(2015, 'gg2015.json')
    
    # Award Category Extraction
    categories.save_awards(2013)
    categories.save_awards(2015)
    
    # Presenters, Winners, and Nominees
    tweet_miner.main(2013)
    tweet_miner.main(2015)
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    # pre_ceremony()
    print("Printing human readable output for 2013 and 2015 into console\n")
    print("These files also exist in .txt files in the form of award2013.txt and award2015.txt\n")
    print("Here is 2013's readable format\n")
    with open("award2013.txt", 'r', encoding="utf-8") as f:
        lines = f.read()
        print(lines)
    print("Here is 2015's readable format\n")
    with open("award2015.txt", 'r', encoding="utf-8") as f:
        lines = f.read()
        print(lines)
    
    return

if __name__ == '__main__':
    main()