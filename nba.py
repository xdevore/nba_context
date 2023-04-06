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


def create_matchup_last_n_dict(team1_attributes, team1_date, team2_attributes, team2_date):
    output_dict = {team1_attributes['id'] : team1_date, team2_attributes['id'] : team2_date}
    return output_dict


def get_team_roster(team_attributes):
    time.sleep(2)
    team_roster = commonteamroster.CommonTeamRoster(team_attributes['id'])
    team_roster_list_with_attributes = team_roster.get_dict()['resultSets'][0]['rowSet']
    team_roster_list = []
    for player in team_roster_list_with_attributes:
        team_roster_list.append(player)
    return team_roster_list


def get_last_n_player_stats(player, n_game_date):
    time.sleep(2)
    return playergamelog.PlayerGameLog(player_id=player[-2], season='2022-23', date_from_nullable=n_game_date).get_dict()["resultSets"]


def create_stats_combined_roster_dict(combined_roster_list, matchup_last_n_dict):
    stats_combined_roster_dict = {}
    for player in combined_roster_list:
        player_stats_dict = {'FG3M' : [], 'REB' : [], 'AST' : [], 'STL' : [], 'BLK' : [], 'TOV' : [], 'PTS' : []}
        player_last_n_date = matchup_last_n_dict[player[0]]
        player_stats_last_n = get_last_n_player_stats(player, player_last_n_date)
        player_stats_last_n_list = player_stats_last_n[0]['rowSet']
        for game in player_stats_last_n_list:
            player_stats_dict['FG3M'].append(game[10])
            player_stats_dict['REB'].append(game[18])
            player_stats_dict['AST'].append(game[19])
            player_stats_dict['STL'].append(game[20])
            player_stats_dict['BLK'].append(game[21])
            player_stats_dict['TOV'].append(game[22])
            player_stats_dict['PTS'].append(game[24])
        stats_combined_roster_dict[player[3]] = player_stats_dict
    return stats_combined_roster_dict


def compare_odds(game_id, markets_list, date, stats_combined_roster_dict):
    for market in markets_list:
        odds_response = requests.get("https://api.prop-odds.com/beta/odds/" + game_id + "/" + market + "?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
        odds_response_list = odds_response['sportsbooks'][0]['market']['outcomes']
        for outcome in odds_response_list:
            description_split_list = outcome['description'].split('-')
            odds_player_name = description_split_list[0][:-1]
            odds_prop = description_split_list[1][1:]



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

    n = 10

    # print("\n" + args.team1input + ":")
    # team1_attributes = get_team_attributes(args.team1input)
    # team1_last_n_date = get_last_n_date_and_print_record(n, team1_attributes)
    # team1_roster = get_team_roster(team1_attributes)

    # # print(team1_attributes)
    # # print(team1_last_n_date)
    # # print(team1_roster)

    # print("\n" + args.team2input + ":")
    # team2_attributes = get_team_attributes(args.team2input)
    # team2_last_n_date = get_last_n_date_and_print_record(n, team2_attributes)
    # team2_roster = get_team_roster(team2_attributes)

    # # print(team2_attributes)
    # # print(team2_last_n_date)
    # # print(team2_roster)

    # matchup_last_n_dict = create_matchup_last_n_dict(team1_attributes, team1_last_n_date, team2_attributes, team2_last_n_date)

    # combined_roster_list = team1_roster + team2_roster
    # # print("\n" + "Combined Roster:")
    # # print(combined_roster_list)

    # stats_combined_roster_dict = create_stats_combined_roster_dict(combined_roster_list, matchup_last_n_dict)
    # print(stats_combined_roster_dict)

    test_stats_roster_dict = {'Caris LeVert': {'FG3M': [5, 2, 4, 1, 2, 2, 3, 1, 5, 4], 'REB': [3, 3, 4, 4, 1, 3, 2, 4, 3, 4], 'AST': [0, 4, 7, 3, 1, 2, 4, 3, 6, 7], 'STL': [1, 0, 1, 1, 1, 2, 2, 4, 1, 4], 'BLK': [0, 3, 1, 0, 0, 0, 0, 1, 0, 1], 'TOV': [1, 0, 2, 0, 2, 3, 1, 1, 2, 0], 'PTS': [19, 15, 15, 9, 10, 12, 18, 15, 24, 22]}, 'Evan Mobley': {'FG3M': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0], 'REB': [7, 16, 7, 15, 7, 16, 4, 8, 12, 6], 'AST': [4, 4, 5, 6, 5, 3, 3, 3, 5, 2], 'STL': [1, 0, 0, 1, 1, 1, 1, 0, 1, 1], 'BLK': [1, 4, 3, 4, 3, 4, 0, 4, 2, 1], 'TOV': [0, 0, 0, 0, 3, 0, 3, 2, 1, 0], 'PTS': [14, 14, 14, 20, 19, 26, 17, 20, 13, 26]}}

    compare_odds(game_id, markets_list, args.date, test_stats_roster_dict)


if __name__ == "__main__":
    main()