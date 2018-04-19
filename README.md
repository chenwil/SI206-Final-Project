# SI206-Final-Project

This program scrapes from the ESPN website, specifically the NBA section of the
website. I start from scraping the ESPN "Standings" section of the website,
and crawl my way through to individual player stats. The stats are then stored
into a cache.json file. (Update: ESPN Website has been updated since time I
originally created this project, web scraping will be inaccurate now.
Use the cache.json file I upload which contains stats I had
originally scraped. These were real time stats from the past, just if you
delete this cache.json file, it will not be able to scrape new data.) My program
then creates and populates a SQLite database with two tables NBA_Teams and
NBA_Players.(three including Division but that is not needed in this program so
disregard)


Instructions for running:
1. Run Program
2. Select an initial command
  - If you pick top 5 Teams, will print a graph of the top 5 teams with W/L.
  - If you pick top 5 scorers, will print a graph of top 5 scorers with PPG/APPG
  - If you pick 'Search a specific team', will print a list of all 30 teams.
3. If you picked search a specific team, you will have option to select a team
   out of the 30 teams listed.
4. After selecting a team, you get the option to print out team stats or roster.
   - If you select team, prints out stats for the team.
   - If you select roster, prints out a list of each player on the team.
5. If you picked roster, you get the option to choose an individual player on
   the team.
   -After selecting an individual player, it prints their stats and a graph of
    some of their significant stats.

Important functions:
  -player_stats('nba_team') scrapes the ESPN website for the stats of each
   individual player on the chosen team.
  -get_team_stats_list(), get_team_short_names_list() scrapes the ESPN website
   for team names and and team stats. get_teams() zips the return of
   get_team_stats_list() and get_team_short_names_list() together.
  -get_stats_sql(), player_stats_sql() deal with plotting graphs given a team
   name/player name.
  -init_db(), insert_stuff(), and update_foreign_keys() deal with setting up
   the database.
