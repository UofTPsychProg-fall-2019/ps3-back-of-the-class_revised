#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 19:25:06 2019

@author: tianasimovic
"""

#%% import packages 
import os
import numpy as np
import pandas as pd
# pip install xlrd

#%%
# Question 1: reading and cleaning

# read in the included IAT_2018.csv file
# please start from /pandorable folder. Note, to read excel, please 'pip install xlrd'
this_path = os.getcwd()
data_path = this_path+'/IAT_2018.csv'
IAT = pd.read_csv(data_path)

# rename and reorder the variables to the following (original name->new name):
# session_id->id
# genderidentity->gender
# raceomb_002->race
# edu->edu
# politicalid_7->politic
# STATE -> state
# att_7->attitude 
# tblacks_0to10-> tblack
# twhites_0to10-> twhite
# labels->labels
# D_biep.White_Good_all->D_white_bias
# Mn_RT_all_3467->rt

IAT = IAT.rename(columns={'session_id':'id','genderidentity':'gender','raceomb_002':'race',
                          'edu':'edu','politicalid_7':'politic','STATE':'state',
                          'att_7':'attitude','tblacks_0to10':'tblack','twhites_0to10':'twhite',
                          'labels':'labels','D_biep.White_Good_all':'D_white_bias',
                          'Mn_RT_all_3467':'rt'})

# remove all participants that have at least one missing value
IAT_clean = IAT.dropna(axis=0,how='any')
if sum(IAT_clean.isnull().mean())==0: #check to see if IAT_clean is truly clean.
    print('IAT_clean is truly clean')
elif sum(IAT_clean.isnull().mean())!=0:
    print('IAT_clean is not clean')

# check out the replace method: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
# use this to recode gender so that 1=men and 2=women (instead of '[1]' and '[2]')

IAT_clean = IAT_clean.replace(to_replace = {'gender':'[1]'}, value = 'men')
IAT_clean = IAT_clean.replace(to_replace = {'gender':'[2]'}, value = 'women')

# use this cleaned dataframe to answer the following questions

#%%
# Question 2: sorting and indexing

# use sorting and indexing to print out the following information:

# the ids of the 5 participants with the fastest reaction times
IAT_clean = IAT_clean.sort_values(by = 'rt', ascending = [True])
IAT_clean.id[0:5]

# the ids of the 5 men with the strongest white-good bias
IAT_men = IAT_clean[(IAT_clean.gender=='men')]
IAT_men = IAT_men.sort_values(by = 'D_white_bias', ascending = [False])
IAT_men.id[0:5]

# the ids of the 5 women in new york with the strongest white-good bias
IAT_women = IAT_clean[(IAT_clean.gender=='women') & (IAT_clean.state=='NY')]
IAT_women = IAT_women.sort_values(by = 'D_white_bias', ascending = [False])
IAT_women.id[0:5]

#%%
# Question 3: loops and pivots

# check out the unique method: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.unique.html
# use it to get a list of states
states = IAT_clean.state.unique()

# write a loop that iterates over states to calculate the median white-good
# bias per state
# store the results in a dataframe with 2 columns: state & bias
for state in states:
    print(state)
    if state==states[0]:
        bias_per_state = pd.DataFrame({'state':[state],
                                   'median_D_white_bias':np.median(IAT_clean.D_white_bias[(IAT_clean.state==state)])
                                   })
    else:
        bias_per_state_perloop = pd.DataFrame({'state':[state],
                                   'median_D_white_bias':np.median(IAT_clean.D_white_bias[(IAT_clean.state==state)])
                                   })
        bias_per_state = pd.concat([bias_per_state,bias_per_state_perloop],axis=0)

# now use the pivot_table function to calculate the same statistics
state_bias = pd.pivot_table(IAT_clean, values = 'D_white_bias', #get D_white_bias
                            index = ['state'], #organize by state
                            #columns=[],
                            aggfunc=np.median)

# make another pivot_table that calculates median bias per state, separately 
# for each race (organized by columns)
state_race_bias = pd.pivot_table(IAT_clean, values = 'D_white_bias', #get D_white_bias
                            index = ['state'], #organize by state
                            columns=['race'],
                            aggfunc=np.median)

#%%
# Question 4: merging and more merging

"""
1	American Indian/Alaska Native
2	East Asian
3	South Asian
4	Native Hawaiian or other Pacific Islander
5	Black or African American
6	White
7	More than one race - Black/White
8	More than one race - Other
9	Other or Unknown
"""

# add a new variable that codes for whether or not a participant identifies as 
# black/African American
IAT_clean['is_black'] = 1*(IAT.race==5)

# use your new variable along with the crosstab function to calculate the 
# proportion of each state's population that is black 
# *hint check out the normalization options
prop_black = pd.crosstab(IAT_clean.state, IAT_clean.is_black, normalize='index')

# state_pop.xlsx contains census data from 2000 taken from http://www.censusscope.org/us/rank_race_blackafricanamerican.html
# the last column contains the proportion of residents who identify as 
# black/African American 
# read in this file and merge its contents with your prop_black table
this_path = os.getcwd()
data_path = this_path+'/state_pop.xlsx'
census = pd.read_excel(data_path) #Note, to read excel, please 'pip install xlrd'

sorted_states = states
sorted_states.sort()
prop_black['State'] = sorted_states

merged = pd.merge(prop_black,census, on='State')

# use the corr method to correlate the census proportions to the sample proportions
corr_census_prop_black = merged.corr()[1]['per_black']

# now merge the census data with your state_race_bias pivot table
state_race_bias['State'] = sorted_states
merged_state_race_bias = pd.merge(state_race_bias,census, on='State')

# use the corr method again to determine whether white_good biases is correlated 
# with the proportion of the population which is black across states
# calculate and print this correlation for white and black participants

corr_bias_bw = pd.DataFrame({'corr_bias_across_states':['Pearson r'],
                                   'corr_black':merged_state_race_bias.corr('pearson')[5]['per_black'],
                                   'corr_white':merged_state_race_bias.corr('pearson')[6]['per_black']
                                   })

print('Amongst caucasian individuals, the correlation between white-positive '
      'biases and the percentage of African Americans in the population is '
      '{:.3f}. However, the same relationship amongst African-American '
      'individuals is {:.3f}.'.format(corr_bias_bw['corr_white'][0],corr_bias_bw['corr_black'][0]))