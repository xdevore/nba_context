import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playergamelog
import requests
import pandas as pd
import argparse


def call_last_ten(team_nickname):
    print(team_nickname)
    nba_teams = teams.get_teams()
    given_team = None
    for team in nba_teams:
        if team['nickname'] == team_nickname:
            given_team = team
    last_ten = teamgamelogs.TeamGameLogs(last_n_games_nullable=10, season_nullable='2022-23', team_id_nullable=given_team['id']).get_dict()
    last_ten_stats_list = last_ten['resultSets'][0]['rowSet']
    date_cutoff = last_ten_stats_list[-1][5].index("T")
    ten_game_date = last_ten_stats_list[-1][5][:date_cutoff]
    ten_game_date = ten_game_date[5:7] + "/"  + ten_game_date[8:10] + "/" + ten_game_date[:4]
    print(ten_game_date)
    record = {"W":0, "L":0}
    for game in last_ten_stats_list:
        if game[7] == "W":
            record["W"] += 1
        else:
            record["L"] += 1
    print(str(record["W"]) + "-" + str(record["L"]))
    time.sleep(2)
    team_roster = commonteamroster.CommonTeamRoster(given_team['id'])
    team_roster_list = team_roster.get_dict()['resultSets'][0]['rowSet']
    for player in team_roster_list:
        time.sleep(2)
        print(player[3])
        print(playergamelog.PlayerGameLog(player_id=player[-2], season='2022-23', date_from_nullable=ten_game_date).get_dict()["resultSets"])


def get_odds(game_id, markets_list, date):
    for market in markets_list:
        odds_response = requests.get("https://api.prop-odds.com/beta/odds/" + game_id + "/" + market + "?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
        odds_response_list = odds_response['sportsbooks'][0]['market']['outcomes']
        for value in odds_response_list:
            print(value['name'])

        

def get_game_id(team1, team2, date):
    games_response = requests.get("https://api.prop-odds.com/beta/games/nba?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
    games_list = games_response["games"]
    for game in games_list:
        if team1 in game['away_team'] or team2 in game['away_team']:
            game_id = game['game_id']
            game
            return game_id


def get_player_markets(game_id, date):
    markets_response = requests.get("https://api.prop-odds.com/beta/markets/" + game_id + "?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
    markets_list = []
    for market_dict in markets_response['markets']:
        market = market_dict['name']
        if 'player' in market:
            markets_list.append(market)
    return markets_list



def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    # Adding optional argument
    parser.add_argument("-i", "--team1input", help = "Input team one")

    parser.add_argument("-j", "--team2input", help = "Input team two")

    parser.add_argument("-d", "--date", help = "Date")
    
    # Read arguments from command line
    args = parser.parse_args()

    game_id = get_game_id(args.team1input, args.team2input, args.date)

    markets_list = get_player_markets(game_id, args.date)

    get_odds(game_id, markets_list, args.date)

    # call_last_ten(args.team1input)

    # call_last_ten(args.team2input)


    

if __name__ == "__main__":
    main()
