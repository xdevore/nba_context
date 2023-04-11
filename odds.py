import requests


class Odds:

    game_id = None
    game_info = None
    player_markets = None
    hit_dict = None

    def __init__(self, team1, team2, date, input_game_info):
        self.game_id = self.get_game_id(team1, team2, date)
        self.game_info = input_game_info
        self.player_markets = self.get_player_markets(self.game_id, date)
        self.hit_dict = self.compare_odds(self.game_id, self.player_markets, date, input_game_info)


    def get_game_id(self, team1, team2, date):
        games_response = requests.get("https://api.prop-odds.com/beta/games/nba?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
        games_list = games_response["games"]
        for game in games_list:
            if team1 in game['away_team'] or team2 in game['away_team']:
                game_id = game['game_id']
                return game_id


    def get_player_markets(self, game_id, date):
        markets_response = requests.get("https://api.prop-odds.com/beta/markets/" + game_id + "?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
        markets_list = []
        for market_dict in markets_response['markets']:
            market = market_dict['name']
            if 'player' in market:
                markets_list.append(market)
        return markets_list

    def compare_odds(self, game_id, markets_list, date, stats_combined_roster_dict):
        hit_dict = {}
        for market in markets_list:
            odds_response = requests.get("https://api.prop-odds.com/beta/odds/" + game_id + "/" + market + "?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
            odds_response_list = odds_response['sportsbooks'][0]['market']['outcomes']
            for outcome in odds_response_list:
                if 'Under' in outcome['name'] or 'Alt' in outcome['description']:
                    continue
                else:
                    if '-' in outcome['description']:
                        description_split_list = outcome['description'].split('-')
                        odds_player_name = description_split_list[0][:-1]
                        odds_prop = description_split_list[1][1:]
                        if "Alt" in odds_prop:
                            odds_prop = odds_prop[4:]
                        if odds_player_name in stats_combined_roster_dict.keys():
                            total_hit = self.make_comparison(odds_player_name, stats_combined_roster_dict[odds_player_name], odds_prop, outcome)
                            if total_hit['total_hit'] >= 0.7:
                                hit_dict[outcome['description']] = total_hit
                    else:
                        if '+' in outcome['description']:
                            description_split_list = outcome['description'].split(' ')
                            if 'To' in description_split_list:
                                odds_prop = description_split_list[3]
                                odds_handicap = description_split_list[2][:-1]
                                odds_info = {'handicap' : odds_handicap, 'name' : outcome['name']}
                                if outcome['name'] in stats_combined_roster_dict.keys():
                                    total_hit = self.make_comparison(outcome['name'], stats_combined_roster_dict[outcome['name']], odds_prop, odds_info)
                                    if total_hit['total_hit'] >= 0.7:
                                        hit_dict[outcome['description']] = total_hit
        return hit_dict

    def make_comparison(self, player_name, player_stats, odds_prop, odds_info):
        hit = 0
        total = 0
        if 'Under' not in odds_info['name'] and 'First' not in odds_info['name']:
            for value in player_stats[odds_prop]:
                if int(value) >= float(odds_info['handicap']):
                    hit += 1
                total += 1
        total_hit = hit/total
        return {'player name' : player_name, 'total_hit' : total_hit, 'handicap' : odds_info['handicap'], 'last_n' : player_stats[odds_prop]}