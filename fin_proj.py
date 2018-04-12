import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import sys

class Team:
    def __init__(self, name, sport, win, loss, PCT, GB, Home, Away, DIV, CONF,
                 PPG, OPPG, DIFF, STRK, L10, url=None):
        self.name = name
        self.sport = sport
        self.win = win
        self.loss = loss
        self.percentage = PCT
        self.gb = GB
        self.home = Home
        self.away = Away
        self.div = DIV
        self.conf = CONF
        self.ppg = PPG
        self.oppg = OPPG
        self.diff = DIFF
        self.strk = STRK
        self.last_ten = L10
        self.url = url

    def __str__(self):
        return ("{} ({}) {} - {}").format(self.name, self.sport, self.win, self.loss)

class Division:
    def __init__(self, name, sport, url=None):
        self.name = name
        self.sport = sport
        self.url = url

    def __str__(self):
        return ("{} ({})").format(self.name, self.sport)

class Player:
    def __init__(self, name, team, GP, GS, MINS, PPG, url=None):
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
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
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

def get_teams(sport): #Gets team names and stats
    if sport == 'nba':
        teams_list = []
        short_names_list = []
        stats_list = []
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
        #print(len(short_names_list))

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

        #print(len(short_names_list), len(stats_list))
        tup_teams_stats = zip(short_names_list, stats_list)
        return tup_teams_stats

        # for team in teams_list:
        #     for ind_stat in stats_list:
        #         team_class = Team(team, sport, ind_stat[0], ind_stat[1],
        #         ind_stat[2], ind_stat[3],ind_stat[4],ind_stat[5],ind_stat[6],
        #         ind_stat[7],ind_stat[8],ind_stat[9],ind_stat[10],ind_stat[11],
        #         ind_stat[12])
        #         print(team_class)
#get_teams('nba')
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

# def get_news(team_abbr):
#     division_url = "http://www.espn.com/nba/standings/_/group/division"
#     espn_url = "http://www.espn.com/"
#     page_text = make_request_using_cache(division_url)
#     page_soup = BeautifulSoup(page_text, 'html.parser')
#     two_conference_table = page_soup.find_all(class_ = 'Table2__responsiveTable Table2__table-outer-wrap standings-subgroups')
#     for table in two_conference_table:
#         table_body = table.find(class_ = 'Table2__tbody')
#         team_names = table_body.find_all(class_ = 'Table2__tr Table2__tr--sm Table2__even')
#         for team in team_names:
#             href_link = team.find('a')
#             team_link = href_link['href']
#             if team_abbr in team_link:
#                 full_url = espn_url + team_link
#                 team_page = make_request_using_cache(full_url)
#                 team_soup = BeautifulSoup(team_page, 'html.parser')
#
#                 team_soup.find_all()


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
            'PCT' TEXT NOT NULL,
            'GB' TEXT NOT NULL,
            'Home' TEXT NOT NULL,
            'Away' TEXT NOT NULL,
            'Div' TEXT NOT NULL,
            'CONF' TEXT NOT NULL,
            'PPG' TEXT NOT NULL,
            'OPPG' TEXT NOT NULL,
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
            'RPG' TEXT NOT NULL,
            'APG' TEXT NOT NULL,
            'BLKPG' TEXT NOT NULL,
            'STLPG' TEXT NOT NULL,
            'PFPG' TEXT NOT NULL,
            'TOPG' TEXT NOT NULL,
            'PPG' TEXT NOT NULL,
            'FG Percentage' TEXT NOT NULL,
            'Three Percentage' TEXT NOT NULL
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

    for tup in get_teams('nba'):
        insertion = (None, tup[0], tup[1][0].text, tup[1][1].text,tup[1][2].text
        ,tup[1][3].text, tup[1][4].text,tup[1][5].text,tup[1][6].text,
        tup[1][7].text,tup[1][8].text,tup[1][9].text,tup[1][10].text,
        tup[1][11].text,tup[1][12].text)
        statement = 'INSERT INTO "NBA_Teams" '
        statement += "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.execute(statement, insertion)

    for team_tup in get_teams('nba'): #this is to update players
        get_teams_tup = player_stats(team_tup[0]) #list of tuples containg (name, stats) ex: [(Derozan, [stats])]
        for player_tup in get_teams_tup:
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
#insert_stuff()
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


def interactive_prompt():
    if len(sys.argv) > 1 and sys.argv[1] == '--init':
        print('Deleting db and starting over from scratch.')
        init_db()
        insert_stuff()
        update_foreign_keys()
    else:
        print('Leaving the DB alone.')

if __name__=="__main__":
    interactive_prompt()
