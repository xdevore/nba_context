import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playergamelog
import requests
import pandas as pd
import argparse


def get_team_attributes(team_nickname):
    nba_teams = teams.get_teams()
    team_attributes = None
    for team in nba_teams:
        if team['nickname'] == team_nickname:
            team_attributes = team
    return team_attributes


def get_last_n_date_and_print_record(n, team_attributes):
    last_n = teamgamelogs.TeamGameLogs(last_n_games_nullable=n, season_nullable='2022-23', team_id_nullable=team_attributes['id']).get_dict()
    last_n_stats_list = last_n['resultSets'][0]['rowSet']
    date_cutoff = last_n_stats_list[-1][5].index("T")
    n_game_date = last_n_stats_list[-1][5][:date_cutoff]
    n_game_date = n_game_date[5:7] + "/"  + n_game_date[8:10] + "/" + n_game_date[:4]
    record = {"W":0, "L":0}
    for game in last_n_stats_list:
        if game[7] == "W":
            record["W"] += 1
        else:
            record["L"] += 1
    print("Last " + str(n) + " Record: " + str(record["W"]) + "-" + str(record["L"]))
    return n_game_date


def get_team_roster(team_attributes):
    time.sleep(2)
    team_roster = commonteamroster.CommonTeamRoster(team_attributes['id'])
    team_roster_list_with_attributes = team_roster.get_dict()['resultSets'][0]['rowSet']
    team_roster_list_names = []
    for player in team_roster_list_with_attributes:
        team_roster_list_names.append(player[3])
    return team_roster_list_names


def get_last_ten_player_stats(player, ten_game_date):
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

    # game_id = get_game_id(args.team1input, args.team2input, args.date)

    # markets_list = get_player_markets(game_id, args.date)

    # get_odds(game_id, markets_list, args.date)
    
    n = 10

    print("\n" + args.team1input + ":")
    team1_attributes = get_team_attributes(args.team1input)
    team1_last_n_date = get_last_n_date_and_print_record(n, team1_attributes)
    team1_roster = get_team_roster(team1_attributes)

    print(team1_attributes)
    print(team1_last_n_date)
    print(team1_roster)

    print("\n" + args.team2input + ":")
    team2_attributes = get_team_attributes(args.team2input)
    team2_last_n_date = get_last_n_date_and_print_record(n, team2_attributes)
    team2_roster = get_team_roster(team2_attributes)

    print(team2_attributes)
    print(team2_last_n_date)
    print(team2_roster)


if __name__ == "__main__":
    main()