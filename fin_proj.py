import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import sys
from print_table import *
import plotly.plotly as py
import plotly.graph_objs as go

class Division:
    def __init__(self, name, sport, url=None):
        self.name = name
        self.sport = sport
        self.url = url

    def __str__(self):
        return ("{} ({})").format(self.name, self.sport)

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

# The main cache function: it will always return the result for this
# url+params combo. However, it will first look to see if we have already
# cached the result and, if so, return the result from cache.
# If we haven't cached the result, it will get a new one (and cache it)
def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def get_divisions(sport): #Returns a list of different divisions
    if sport == 'nba':
        division_list = []
        division_url = "http://www.espn.com/nba/standings/_/group/division"
        page_text = make_request_using_cache(division_url)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        two_conference_table = page_soup.find_all(class_ = 'Table2__responsiveTable Table2__table-outer-wrap standings-subgroups')
        #Two tables (Eastern / Western)
        for table in two_conference_table:
            table_body = table.find(class_ = 'Table2__tbody') #everything in each table
            division_names = table_body.find_all(class_ = 'subgroup-headers Table2__sub-header Table2__tr Table2__tr--sm Table2__even') #Each Division
            for division in division_names:
                div_name = division.text
                div_class = Division(div_name, sport)
                division_list.append(div_class)
        return division_list

def get_team_short_names_list():
    short_names_list = []

    division_url = "http://www.espn.com/nba/standings/_/group/division"
    page_text = make_request_using_cache(division_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    two_conference_table = page_soup.find_all(class_ = 'Table2__responsiveTable Table2__table-outer-wrap standings-subgroups')
    for table in two_conference_table:
        table_body = table.find(class_ = 'Table2__tbody')
        team_names = table_body.find_all(class_ = 'Table2__tr Table2__tr--sm Table2__even')
        for team in team_names:
            short_name = team.find(class_ = 'dn show-mobile').text
            short_names_list.append(short_name) #Short Name Ex: BOS or TOR
        bottom_teams = table_body.find_all(class_ = 'no-border-bottom Table2__tr Table2__tr--sm Table2__even')
        for bottom_team in bottom_teams:
            bottom_short_name = bottom_team.find(class_ = 'dn show-mobile').text
            short_names_list.append(bottom_short_name)
    return short_names_list

def get_team_stats_list():
    stats_list = []

    division_url = "http://www.espn.com/nba/standings/_/group/division"
    page_text = make_request_using_cache(division_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    two_data_table = page_soup.find_all(class_ = 'Table2__shadow-wrapper')
    for table in two_data_table:
        data_body = table.find(class_ = 'Table2__tbody')
        team_stats = data_body.find_all(class_ = 'Table2__tr Table2__tr--sm Table2__even')
        for team_stat in team_stats:
            ind_stat = team_stat.find_all(class_ = 'Table2__td')
            stats_list.append(ind_stat) #list of ind stats for each team into a big list of stats
        bottom_stats = data_body.find_all(class_ = 'no-border-bottom Table2__tr Table2__tr--sm Table2__even') #!!!!!!!!!!!!!!!!!!!
        for bottom_stat in bottom_stats:
            bottom_no_border_stats = bottom_stat.find_all(class_ = 'Table2__td')
            stats_list.append(bottom_no_border_stats)

    return stats_list

def get_teams(): #zip team names and stats

    #print(len(short_names_list), len(stats_list))
    tup_teams_stats = zip(get_team_short_names_list(), get_team_stats_list())
    return tup_teams_stats

get_teams()

def get_stats_sql(team):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = 'SELECT Name, Wins, Loss, PCT, PPG, L10  FROM NBA_Teams WHERE Name = "{}"'.format(team)
    results = cur.execute(sql)
    print_table(results)
    conn.close()

def player_stats(team_abbr):
    player_list = []
    player_stats_list = []
    division_url = "http://www.espn.com/nba/standings/_/group/division"
    espn_url = "http://www.espn.com/"
    page_text = make_request_using_cache(division_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    two_conference_table = page_soup.find_all(class_ = 'Table2__responsiveTable Table2__table-outer-wrap standings-subgroups')
    for table in two_conference_table:
        table_body = table.find(class_ = 'Table2__tbody')
        team_names = table_body.find_all(class_ = 'Table2__tr Table2__tr--sm Table2__even')
        #print(len(team_names))
        for team in team_names:
            href_link = team.find('a')
            team_link = href_link['href']
            if team_abbr.lower() in team_link: #might need to remove later
                #print('hello')
                full_url = espn_url + team_link
                team_page = make_request_using_cache(full_url)
                team_soup = BeautifulSoup(team_page, 'html.parser')
                header_bar = team_soup.find(id = 'global-nav-secondary')
                headers = header_bar.find_all(class_ = 'sub')
                roster = headers[3]
                roster_href_link = roster.find('a')
                roster_link = roster_href_link['href']
                #print(roster_link)
                roster_page = make_request_using_cache(roster_link)
                roster_soup = BeautifulSoup(roster_page, 'html.parser')
                table_body = roster_soup.find(class_ = 'mod-content')
                player_profile = table_body.find_all('tr')
                for profile in player_profile[2:-1]:
                    player_href_link = profile.find('a')
                    name = player_href_link.text
                    player_list.append(name)
                    player_link = player_href_link['href']
                    #print(player_link)
                    player_page = make_request_using_cache(player_link)
                    player_soup = BeautifulSoup(player_page, 'html.parser')
                    stats_table = player_soup.find(class_ = 'mod-container mod-table mod-no-footer')
                    #if there are multiple oddrows do this one, else do that one

                    current_stats = stats_table.find(class_ = 'oddrow')
                    ind_stats = current_stats.find_all('td')
                    #print(len(ind_stats))
                    if len(ind_stats) == 6:
                        #print('hello')
                        msl = []
                        content = stats_table.find(class_ = 'mod-content')
                        current_stats = content.find_all(class_ = 'oddrow')
                        for oddrow in current_stats:
                            ind_stats = oddrow.find_all(style = 'text-align:right;')
                            #print(len(ind_stats))
                            for stat in ind_stats:
                                #print(stat.text)
                                msl.append(stat) #msl has all the stats
                        needed_stats = []

                        needed_stats.append(msl[0])
                        needed_stats.append(msl[9])
                        needed_stats.append(msl[10])
                        needed_stats.append(msl[11])
                        needed_stats.append(msl[12])
                        needed_stats.append(msl[13])
                        needed_stats.append(msl[14])
                        needed_stats.append(msl[2])
                        needed_stats.append(msl[4])
                        needed_stats.append(msl[6])

                        #print(needed_stats[0].text)
                        player_stats_list.append(needed_stats)
                    else:
                        #print(len(ind_stats))
                        del_first_ind = ind_stats[1:]
                        #print(len(del_first_ind))
                        needed_stats = []
                        needed_stats.append(del_first_ind[0])
                        needed_stats.append(del_first_ind[8])
                        needed_stats.append(del_first_ind[9])
                        needed_stats.append(del_first_ind[10])
                        needed_stats.append(del_first_ind[11])
                        needed_stats.append(del_first_ind[12])
                        needed_stats.append(del_first_ind[13])
                        needed_stats.append(del_first_ind[14])
                        needed_stats.append(del_first_ind[3])
                        needed_stats.append(del_first_ind[5])

                        player_stats_list.append(needed_stats)


    #need to get links for the bottom border ones too
    two_conf_table = page_soup.find_all(class_ = 'Table2__responsiveTable Table2__table-outer-wrap standings-subgroups')
    for table in two_conf_table:
        table_body = table.find(class_ = 'Table2__tbody')
        bottom_team_names = table_body.find_all(class_ = 'no-border-bottom Table2__tr Table2__tr--sm Table2__even')
        for team in bottom_team_names:
            href_link = team.find('a')
            team_link = href_link['href']
            #print(team_link)
            if team_abbr.lower() in team_link: #might need to remove later
                #print('hello')
                full_url = espn_url + team_link
                team_page = make_request_using_cache(full_url)
                team_soup = BeautifulSoup(team_page, 'html.parser') #go to team page
                header_bar = team_soup.find(id = 'global-nav-secondary')
                headers = header_bar.find_all(class_ = 'sub')
                roster = headers[3]
                roster_href_link = roster.find('a')
                roster_link = roster_href_link['href']
                #print(roster_link)
                roster_page = make_request_using_cache(roster_link) #go to roster page
                roster_soup = BeautifulSoup(roster_page, 'html.parser')
                table_body = roster_soup.find(class_ = 'mod-content')
                player_profile = table_body.find_all('tr')
                for profile in player_profile[2:-1]:
                    player_href_link = profile.find('a')
                    name = player_href_link.text
                    player_list.append(name)
                    player_link = player_href_link['href']
                    #print(player_link)
                    player_page = make_request_using_cache(player_link)
                    player_soup = BeautifulSoup(player_page, 'html.parser')
                    stats_table = player_soup.find(class_ = 'mod-container mod-table mod-no-footer')
                    #if there are multiple oddrows do this one, else do that one

                    current_stats = stats_table.find(class_ = 'oddrow')
                    ind_stats = current_stats.find_all('td')
                    #print(len(ind_stats))
                    if len(ind_stats) == 6:
                        #print('hello')
                        msl = []
                        content = stats_table.find(class_ = 'mod-content')
                        current_stats = content.find_all(class_ = 'oddrow')
                        for oddrow in current_stats:
                            ind_stats = oddrow.find_all(style = 'text-align:right;')
                            #print(len(ind_stats))
                            for stat in ind_stats:
                                #print(stat.text)
                                msl.append(stat) #msl has all the stats
                        needed_stats = []

                        needed_stats.append(msl[0])
                        needed_stats.append(msl[9])
                        needed_stats.append(msl[10])
                        needed_stats.append(msl[11])
                        needed_stats.append(msl[12])
                        needed_stats.append(msl[13])
                        needed_stats.append(msl[14])
                        needed_stats.append(msl[2])
                        needed_stats.append(msl[4])
                        needed_stats.append(msl[6])

                        #print(needed_stats[0].text)
                        player_stats_list.append(needed_stats)
                    else:
                        #print(len(ind_stats))
                        del_first_ind = ind_stats[1:]
                        #print(len(del_first_ind))
                        needed_stats = []
                        needed_stats.append(del_first_ind[0])
                        needed_stats.append(del_first_ind[8])
                        needed_stats.append(del_first_ind[9])
                        needed_stats.append(del_first_ind[10])
                        needed_stats.append(del_first_ind[11])
                        needed_stats.append(del_first_ind[12])
                        needed_stats.append(del_first_ind[13])
                        needed_stats.append(del_first_ind[14])
                        needed_stats.append(del_first_ind[3])
                        needed_stats.append(del_first_ind[5])

                        player_stats_list.append(needed_stats)

    #print(len(links_count))
    # print(len(player_list), len(player_stats_list))
    player_list_stats = zip(player_list, player_stats_list)
    return player_list_stats

#player_stats('IND')

def player_stats_sql(player_name):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''
        SELECT p.Name, p.Team, t.Wins, t.Loss, p.GP, p.RPG, p.APG, p.BLKPG,
        p.STLPG, p.PFPG, p.TOPG, p.PPG
        FROM NBA_Players AS p
        JOIN NBA_Teams AS t
            ON p.TeamID = t.Id
        WHERE p.Name = "{}"
        '''.format(player_name)

    results = cur.execute(sql)
    print_table(results)

    sql = '''
        SELECT p.Name, p.Team, t.Wins, t.Loss, p.GP, p.RPG, p.APG, p.BLKPG,
        p.STLPG, p.PFPG, p.TOPG, p.PPG
        FROM NBA_Players AS p
        JOIN NBA_Teams AS t
            ON p.TeamID = t.Id
        WHERE p.Name = "{}"
        '''.format(player_name)

    results = cur.execute(sql)
    result_list = cur.fetchall()
    stats_list = ['RPG', 'APG', 'BLKPG', 'STLPG', 'PFPG', 'TOPG', 'PPG']
    actual_stats = [result_list[0][5],result_list[0][6],
                    result_list[0][7],result_list[0][8],result_list[0][9],
                    result_list[0][10],result_list[0][11]]
    player_name = result_list[0][0]

    trace0 = go.Bar(
        x= stats_list,
        y=actual_stats,
        marker=dict(
            color='rgb(0,108,182)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
        opacity=0.6
    )

    data = [trace0]
    layout = go.Layout(
        title= '{} Stats'.format(player_name),
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='player_stat_graph')

    conn.close()

def make_team_graph():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''
        SELECT Name, Wins, Loss
        FROM NBA_Teams
        ORDER BY Wins DESC LIMIT 5
        '''

    names_list = [] #names
    win_list = []
    loss_list = []
    results = cur.execute(sql)
    result_list = results.fetchall()
    for tup in result_list:
        names_list.append(tup[0])
        win_list.append(tup[1])
        loss_list.append(tup[2])

    conn.close


    trace1 = go.Bar(
        x=names_list,
        y=win_list,
        text=win_list,
        textposition = 'auto',
        marker=dict(
            color='rgb(0,108,182)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5),
            ),
        opacity=0.6,
        name = 'Wins'
    )

    trace2 = go.Bar(
        x=names_list,
        y=loss_list,
        text=loss_list,
        textposition = 'auto',
        marker=dict(
            color='rgb(236,27,76)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5),
            ),
        opacity=0.6,
        name = 'Losses'
    )

    data = [trace1,trace2]
    layout = go.Layout(title='NBA Top 5 Teams',)
    fig = go.Figure(data=data, layout=layout )


    py.plot(fig, filename='NBA Top 5 Teams')

def make_players_graph():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''
        SELECT Name, PPG, APG
        FROM NBA_Players
        ORDER BY PPG DESC LIMIT 6
        '''

    names_list = [] #names
    ppg_list = []
    apg_list = []
    results = cur.execute(sql)
    result_list = results.fetchall()
    for tup in result_list:
        names_list.append(tup[0])
        ppg_list.append(tup[1])
        apg_list.append(tup[2])

    conn.close


    trace1 = go.Bar(
        x=names_list,
        y=ppg_list,
        text=apg_list,
        textposition = 'auto',
        marker=dict(
            color='rgb(0,108,182)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5),
            ),
        opacity=0.6,
        name = 'PPG'
    )

    trace2 = go.Bar(
        x=names_list,
        y=apg_list,
        text=apg_list,
        textposition = 'auto',
        marker=dict(
            color='rgb(236,27,76)',
            line=dict(
                color='rgb(8,48,107)',
                width=1.5),
            ),
        opacity=0.6,
        name = 'APG'
    )

    data = [trace1,trace2]
    layout = go.Layout(title='NBA Top 5 Scorers',)
    fig = go.Figure(data=data, layout=layout )


    py.plot(fig, filename='NBA Top 5 Scorers')


DBNAME = 'espn.db'
def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        DROP TABLE IF EXISTS "NBA_Divisions"
        '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS "NBA_Teams"
        '''

    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS "NBA_Players"
        '''

    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'NBA_Divisions' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Division' TEXT NOT NULL
         );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'NBA_Teams' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Wins' TEXT NOT NULL,
            'Loss' TEXT NOT NULL,
            'PCT' FLOAT NOT NULL,
            'GB' FLOAT NOT NULL,
            'Home' TEXT NOT NULL,
            'Away' TEXT NOT NULL,
            'Div' TEXT NOT NULL,
            'CONF' TEXT NOT NULL,
            'PPG' FLOAT NOT NULL,
            'OPPG' FLOAT NOT NULL,
            'DIFF' TEXT NOT NULL,
            'STRK' TEXT NOT NULL,
            'L10' TEXT NOT NULL
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'NBA_Players' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Team' TEXT NOT NULL,
            'TeamID' TEXT,
            'GP' TEXT NOT NULL,
            'RPG' FLOAT NOT NULL,
            'APG' FLOAT NOT NULL,
            'BLKPG' FLOAT NOT NULL,
            'STLPG' FLOAT NOT NULL,
            'PFPG' FLOAT NOT NULL,
            'TOPG' FLOAT NOT NULL,
            'PPG' FLOAT NOT NULL,
            'FG Percentage' FLOAT NOT NULL,
            'Three Percentage' FLOAT NOT NULL
        );
    '''
    cur.execute(statement)

    conn.commit()
    conn.close()

def insert_stuff():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for division in get_divisions('nba'):
        insertion = (None, division.name)
        statement = 'INSERT INTO "NBA_Divisions" '
        statement += "VALUES (?,?)"
        cur.execute(statement, insertion)

    for tup in get_teams():
        insertion = (None, tup[0], tup[1][0].text, tup[1][1].text,tup[1][2].text
        ,tup[1][3].text, tup[1][4].text,tup[1][5].text,tup[1][6].text,
        tup[1][7].text,tup[1][8].text,tup[1][9].text,tup[1][10].text,
        tup[1][11].text,tup[1][12].text)
        statement = 'INSERT INTO "NBA_Teams" '
        statement += "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.execute(statement, insertion)

    for team_tup in get_teams(): #this is to update players
        get_players_tup = player_stats(team_tup[0]) #list of tuples containg (name, stats) ex: [(Derozan, [stats])]
        for player_tup in get_players_tup:
            print(team_tup[0])
            insertion = (None, player_tup[0], team_tup[0], None, player_tup[1][0].text,
            player_tup[1][1].text,player_tup[1][2].text,player_tup[1][3].text,player_tup[1][4].text,
            player_tup[1][5].text,player_tup[1][6].text,player_tup[1][7].text,player_tup[1][8].text,
            player_tup[1][9].text)

            statement = 'INSERT INTO "NBA_Players" '
            statement+= 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

            cur.execute(statement, insertion)

    conn.commit()
    conn.close()

def update_foreign_keys():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'SELECT * FROM NBA_Teams'
    cur.execute(statement)
    team_name_id = {}

    for team in cur:
        team_name = team[1]
        team_id = team[0]
        team_name_id[team_name] = team_id

    for team_name in team_name_id:
        ind_team_id = team_name_id[team_name]
        insert = (ind_team_id, team_name)

        statement = '''
                    UPDATE NBA_Players
                    SET TeamID = ?
                    WHERE Team = ?
                    '''
        cur.execute(statement, insert)

    conn.commit()
    conn.close()

def run_program():
    counter = 1
    init_commands_list = "\nCommands:\n1.Top 5 Teams\n2.Top 5 Scorers\n3.Search a specific team\n"
    print(init_commands_list)
    first_command = input("Select a number to start (Ex: 1): ")
    if first_command == "1":
        make_team_graph()
        run_exit = input('\nRun again or exit?: ')
        return run_exit
    elif first_command == "2":
        make_players_graph()
        run_exit = input('\nRun again or exit?: ')
        return run_exit
    elif first_command == "3":
        for team in get_team_short_names_list():
            print("{}. {}".format(counter, team))
            counter += 1
        user_team_input = input("Select a team to find stats for (Ex: TOR): ")
        if user_team_input in get_team_short_names_list():
            statement = "Do you want team stats or roster stats? "
            statement += "('team' for team or 'roster' for roster): "
            team_stats_roster = input(statement)
            if team_stats_roster == "team":

                get_stats_sql(user_team_input)

                run_exit = input('\nRun again or exit?: ')
                return run_exit
            elif team_stats_roster == "roster":
                get_players_tup = player_stats(user_team_input)
                counter = 1
                player_list = []
                for player_tup in get_players_tup:
                    player_list.append(player_tup[0])
                    print("{}. {}".format(counter, player_tup[0]))
                    counter += 1
                player_choice = input("Select a player (Ex: 'Lebron James'): ")
                player_stats_sql(player_choice)
                run_exit = input('\nRun again or exit?: ')
                return run_exit
            else:
                print("Invalid Input")
                run_exit = input('\nRun again or exit?: ')
                return run_exit
        else:
            print("invalid input")
            run_exit = input('\nRun again or exit?: ')
            return run_exit
    else:
        print("invalid input")
        run_exit = input('\nRun again or exit?: ')
        return run_exit

def interactive_prompt():
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        print('Deleting db and starting over from scratch.')
        init_db()
        insert_stuff()
        update_foreign_keys()
    else:
        print('Using previous database')
        print('-' * 20)

    print("Hello, welcome to NBA Stats Program")
    next_choice = run_program()
    while next_choice != "Exit":
        if next_choice.upper() == 'RUN AGAIN':
            next_choice = run_program()
        elif next_choice.upper() == 'EXIT':
            break
        else:
            print("invalid input, restarting program")
            next_choice = run_program()


if __name__=="__main__":
    interactive_prompt()
