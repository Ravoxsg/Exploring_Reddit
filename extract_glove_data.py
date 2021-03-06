# Creates the csv file which is a list of the number of users who authored at least 10 posts in pairs of subreddits

import numpy as np 
import os
import csv
import ast 
from tqdm import tqdm
import yaml
import time
import gc
import bz2
import json
import pickle


# PARAMETERS
data_path = 'E:/bz2_files/' # where are the bz2 files?
output_path = 'C:/Users/mathi/Documents/ETUDES/4-University of Toronto/WINTER/3-Topics in CSS/3_Project/Exploring_Reddit/community2vec embeddings/' # where do you want to save the threads data?
starting_year = 2016
starting_month = 1
ending_year = 2016
ending_month = 12
min_common_posts = 10
sub_thres = 200


# creates one dictionary containing the number of times each author (keys) posted in each subreddit 
def authors_per_sub(data_path, starting_year, starting_month, ending_year, ending_month):

    authors = {}
    times = []
    lines = 0
    failed_conversions = 0

    os.chdir(data_path)

    # go through the post submissions first
    for filename in os.listdir('.'):
        if filename.startswith('RS'): # was getting issues since it would pick up files that were not RS_, or RC_
            date = filename[3:-4].split('-')
            year = int(date[0])
            month = int(date[1])
            # taking files relevant to us
            if ((year >= starting_year) & (year <= ending_year)) & ((month >= starting_month) & (month <= ending_month)):
                if filename.startswith('RS_'):
                    bz_file = bz2.BZ2File(filename)
                    for line in tqdm(bz_file):
                        lines += 1
                        try:
                            time1 = time.time()
                            thread_dico = json.loads(line.decode("utf-8"))
                            time2 = time.time()
                            times.append(time2-time1)
                            if (thread_dico != None) & (thread_dico != {}):
                                if thread_dico["author"] in authors.keys():
                                    if thread_dico["subreddit"] in authors[thread_dico["author"]].keys():
                                        authors[thread_dico["author"]][thread_dico["subreddit"]] += 1
                                    else:
                                        authors[thread_dico["author"]][thread_dico["subreddit"]] = 1
                                else:
                                    authors[thread_dico["author"]] = {thread_dico["subreddit"]: 1}
                        except KeyError:
                            failed_conversions += 1
                            continue
    return authors, times, failed_conversions/lines

# returns a dictionary of subreddits (keys) which values are dictionaries of all other subreddits with the number of authors commenting in both at least a certain number of times
def authors_in_common(authors, min_common_posts):

    subreddits = {}
    i = 0
    times = []

    for author in tqdm(authors):
        if len(authors[author].keys()) <= sub_thres:
            t1 = time.time()
            for subreddit1 in authors[author]:
                for subreddit2 in authors[author]:
                    if subreddit1 != subreddit2:
                        if (authors[author][subreddit1] >= min_common_posts) and (authors[author][subreddit2] >= min_common_posts):
                            if subreddit1 in subreddits.keys():
                                if subreddit2 in subreddits[subreddit1].keys():
                                    subreddits[subreddit1][subreddit2] += 1
                                else:
                                    subreddits[subreddit1][subreddit2] = 1
                            else:
                                subreddits[subreddit1] = {subreddit2: 1}
            t2 = time.time()
            i += 1
            if (i % 10000) == 0:
                print(i)
                print(t2-t1)
            times.append(t2-t1)

    return subreddits, np.mean(np.array(times))


if __name__ == '__main__':

    authors, times, conv_ratio = authors_per_sub(data_path, starting_year, starting_month, ending_year, ending_month)

    subreddits, t = authors_in_common(authors, min_common_posts)
    print('average time per author: {}'.format(t))

    os.chdir(output_path)

    with open('common_authors_{}_{}_to_{}_{}.csv'.format(starting_year, starting_month, ending_year, ending_month), 'w') as file:
        file.write("t1_subreddit"+','+"t2_subreddit"+','+"NumOverlaps"+'\n')
        for sub1 in subreddits.keys():
            for sub2 in subreddits[sub1].keys():
                file.write(sub1+','+sub2+','+str(subreddits[sub1][sub2])+'\n')