# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 11:34:03 2023

@author: mmcga
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import date
import streamlit as st

def get_season_data(year, table='regular'):
    """
    

    Parameters
    ----------
    year : Int
        Calendar year to get season data for. 2022/23 is 2023.
        
    table : str
        'regular' or 'advanced'

    Returns
    -------
    Pandas Dataframe.

    """
    url_prefix = "https://www.basketball-reference.com/leagues/NBA_"
    
    if table=='regular':
        url_suffix = "_per_game.html"
    elif table == 'advanced':
        url_suffix = '_advanced.html'
        
    url = url_prefix + str(year) + url_suffix
    
    html = urlopen(url)
    
    soup = bs(html, features='lxml')
    
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')][1:]
    
    rows = soup.findAll('tr')[1:]
    rows_data = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    
    df = pd.DataFrame(rows_data,columns=headers).dropna()
    
    if table=='regular':
        int_cols = ['Age', 'G', 'GS']
        float_cols = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 
                      'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
        
        df.replace('',0,inplace=True)
        df.fillna(0,inplace=True)
        
        for col in int_cols:
            df[col] = df[col].astype(int)
            
        for col in float_cols:
            df[col] = df[col].astype(float)
            
        df['GS_PCT'] = round(df['GS'] / df['G'] *100,2)
        
    elif table=='advanced':
        int_cols = ['Age', 'G']
        float_cols = ['MP', 'PER', 'TS%', '3PAr', 'FTr',
               'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%',
               'OWS', 'DWS', 'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']
        
        df.replace('',0,inplace=True)
        
        for col in int_cols:
            df[col] = df[col].astype(int)
            
        for col in float_cols:
            df[col] = df[col].astype(float)
    
    return df

def drop_duplicate_players(df):
    """
    

    Parameters
    ----------
    df : Pandas DataFrame
        DF of NBA Season Data.

    Returns
    -------
    Dataframe with duplicate players removed and consolidated.

    """
    
    players_with_mult_teams = df[df['Tm']=='TOT']['Player']
    
    players_with_mult_teams_totals = df[(df['Player'].isin(players_with_mult_teams)) & (df['Tm']=='TOT')]
    
    players_with_single_team_totals = df[~df['Player'].isin(players_with_mult_teams)]
    
    new_df = pd.concat([players_with_mult_teams_totals, 
                        players_with_single_team_totals]).sort_values(by='Player').reset_index(drop=True)
    
    return new_df
    
#Create a dictionary of teams and their primary and secondary colours
team_colours = {
                'ATL':{'primary': '#E03A3E',
                      'secondary': '#26282A'},
                'BOS':{'primary': '#007A33',
                      'secondary': '#BA9653'},
                'BRK':{'primary': '#000000',
                      'secondary': '#FFFFFF'},
                'CHO':{'primary': '#00788C',
                      'secondary': '#1D1160'},
                'CHI':{'primary': '#CE1141',
                      'secondary': '#000000'},
                'CLE':{'primary': '#860038',
                      'secondary': '#041E42'},
                'DAL':{'primary': '#00538C',
                      'secondary': '#B8C4CA'},
                'DEN':{'primary': '#0E2240',
                      'secondary': '#FEC524'},
                'DET':{'primary': '#C8102E',
                      'secondary': '#1D42BA'},
                'GSW':{'primary': '#1D428A',
                      'secondary': '#FFC72C'},
                'HOU':{'primary': '#CE1141',
                      'secondary': '#C4CED4'},
                'IND':{'primary': '#002D62',
                      'secondary': '#FDBB30'},
                'LAC':{'primary': '#C8102E',
                      'secondary': '#1D428A'},
                'LAL':{'primary': '#552583',
                      'secondary': '#FDB927'},
                'MEM':{'primary': '#5D76A9',
                      'secondary': '#12173F'},
                'MIA':{'primary': '#98002E',
                      'secondary': '#F9A01B'},
                'MIL':{'primary': '#00471B',
                      'secondary': '#EEE1C6'},
                'MIN':{'primary': '#0C2340',
                      'secondary': '#78BE20'},
                'NOP':{'primary': '#0C2340',
                      'secondary': '#85714D'},
                'NYK':{'primary': '#006BB6',
                      'secondary': '#F58426'},
                'OKC':{'primary': '#007AC1',
                      'secondary': '#EF3B24'},
                'ORL':{'primary': '#0077C0',
                      'secondary': '#C4CED4'},
                'PHI':{'primary': '#006BB6',
                      'secondary': '#ED174C'},
                'PHO':{'primary': '#1D1160',
                      'secondary': '#E56020'},
                'POR':{'primary': '#E03A3E',
                      'secondary': '#000000'},
                'SAC':{'primary': '#5A2D81',
                      'secondary': '#63727A'},
                'SAS':{'primary': '#C4CED4',
                      'secondary': '#000000'},
                'TOR':{'primary': '#CE1141',
                      'secondary': '#000000'},
                'UTA':{'primary': '#002B5C',
                      'secondary': '#00471B'},
                'WAS':{'primary': '#002B5C',
                      'secondary': '#E31837'},
                'TOT':{'primary': '#000000',
                       'secondary': '#ffffff'}
                }

header = st.container()
graphs = st.container()


with header:
    st.title("NBA 6th Man of the Year Tracker")
    year = st.selectbox("Which year would you like to see?",
                        [y for y in range(2023,2013,-1)],
                        index=0)
    
    if year is not None:
        df = drop_duplicate_players(get_season_data(year,'regular'))
        adv_df = drop_duplicate_players(get_season_data(year,'advanced'))
        
        total_df = pd.merge(df,adv_df[['Player','PER','WS', 'WS/48', 
                               'OBPM', 'DBPM', 'BPM', 'VORP']], on='Player', how='left')
    
    #Ask User for inputted Games Started %
    gc_pct = st.slider("Please set the percentage of games started threshold:",
                       0,100,50)
    max_games_played = total_df['MP'].max()
    
    elig_df = total_df.loc[(total_df['GS_PCT']<=gc_pct) &
                           (total_df['G'] > max_games_played * 0.33) &
                           (total_df['PTS'] >= 8) &
                           (total_df['MP'] > 6)]
    
with graphs:
    plt.figure(figsize=(10,10))
    
    fig, ax = plt.subplots()
    ax.scatter(elig_df['PTS'],elig_df['PER'], color='grey', linewidths=2, edgecolors='black')
    
    plt.title('Sixth Man of the Year Race')
    plt.xlabel('Points per Game')
    plt.ylabel('PER')
    
    playerlist = list(elig_df.sort_values(by='PTS',ascending=False)['Player'][:10])
    
    for i, player in enumerate(playerlist):
        
        player_data = elig_df[elig_df['Player']==player]
        
        team = player_data['Tm'].item().strip()
        color1 = team_colours[team]['primary']
        color2 = team_colours[team]['secondary']
        
        ax.scatter(player_data['PTS'],player_data['PER'],s=125, color=color1, edgecolors=color2, linewidths=2)
        
        #Label the player on the plot
        if i % 2 == 0:
            x = 0.2
        elif i % 5 == 0:
            x = -0.3
        else:
            x = -0.4
        plt.text(np.array(player_data['PTS'])[0]*(1+0.001),
                 np.array(player_data['PER'])[0]+x,
                 np.array(player_data['Player'])[0].split()[1],
                fontdict={'size':8})
    
    st.pyplot(fig)
