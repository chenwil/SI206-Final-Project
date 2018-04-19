from fin_proj import *
import unittest

class TestGetTeams(unittest.TestCase):

    def test_team_names_stats(self):
        team_names = []
        team_stats = []
        for tup in get_teams():
            team_name = tup[0]
            team_names.append(team_name)
            team_stat = tup[1]
            team_stats.append(team_stat)

        self.assertTrue(team_names[0], 'TOR')
        self.assertTrue(team_names[29], 'MEM')
        self.assertTrue(team_stats[0][0], 59)
        self.assertTrue(len(team_names), 30)
        self.assertTrue(len(team_stats), 30)
        self.assertTrue(len(team_stats[0]), 13)

class TestPlayerStats(unittest.TestCase):

    def test_players_stats(self):
        test_player_list = []
        test_athlete_stats = []
        for team_tup in get_teams(): #this is to update players
            get_players_tup = player_stats(team_tup[0]) #list of tuples containg (name, stats) ex: [(Derozan, [stats])]
            for player_tup in get_players_tup:
                player_name = player_tup[0]
                player_stat = player_tup[1]
                test_player_list.append(player_name)
                test_athlete_stats.append(player_stat)

        self.assertTrue(len(test_player_list), len(test_athlete_stats))
        self.assertTrue(test_player_list[0], 'OG Anunoby')
        self.assertTrue(test_player_list[591], 'Briante Weber')
        self.assertTrue(test_athlete_stats[0][1], 74)
        self.assertTrue(test_athlete_stats[591][8], .364 )

class TestDatabase(unittest.TestCase):

    def test_teams_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM NBA_Teams'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('OKC',), result_list)
        self.assertEqual(len(result_list), 30)

        sql = '''
            SELECT Name, Wins, Loss, L10
            FROM NBA_Teams
            WHERE Name="UTAH"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list[0]), 4)
        self.assertEqual(result_list[0][3], '8-2')
        self.assertEqual(result_list[0][2], '33')

        conn.close()

    def test_players_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM NBA_Players'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Julyan Stone',), result_list)
        self.assertEqual(len(result_list), 592)

        sql = '''
            SELECT Name, GP, PPG
            FROM NBA_Players
            WHERE Team="UTAH"
            ORDER BY PPG DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 17)
        self.assertEqual(result_list[0][0], 'Donovan Mitchell')

        conn.close()


if __name__ == '__main__':
    unittest.main()
