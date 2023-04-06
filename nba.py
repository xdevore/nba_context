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
        player_stats_dict = {'Made Threes' : [], 'Rebounds' : [], 'Assists' : [], 'Steals' : [], 'Blocks' : [], 'Turnovers' : [], 'Points' : [], 'Pts + Ast' : [], 'Pts + Reb + Ast' : [], 'Reb + Ast' : [], 'Pts + Reb' : [], 'Steals + Blocks' : []}
        player_last_n_date = matchup_last_n_dict[player[0]]
        player_stats_last_n = get_last_n_player_stats(player, player_last_n_date)
        player_stats_last_n_list = player_stats_last_n[0]['rowSet']
        for game in player_stats_last_n_list:
            player_stats_dict['Made Threes'].append(game[10])
            player_stats_dict['Rebounds'].append(game[18])
            player_stats_dict['Assists'].append(game[19])
            player_stats_dict['Steals'].append(game[20])
            player_stats_dict['Blocks'].append(game[21])
            player_stats_dict['Turnovers'].append(game[22])
            player_stats_dict['Points'].append(game[24])
            player_stats_dict['Pts + Ast'].append(game[19] + game[24])
            player_stats_dict['Pts + Reb + Ast'].append(game[18] + game[19] + game[24])
            player_stats_dict['Reb + Ast'].append(game[18] + game[19])
            player_stats_dict['Pts + Reb'].append(game[18] + game[24])
            player_stats_dict['Steals + Blocks'].append(game[20] + game[21])
        stats_combined_roster_dict[player[3]] = player_stats_dict
    return stats_combined_roster_dict


def compare_odds(game_id, markets_list, date, stats_combined_roster_dict):
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
                        total_hit = make_comparison(odds_player_name, stats_combined_roster_dict[odds_player_name], odds_prop, outcome)
                        if total_hit['total_hit'] == "8/10" or total_hit['total_hit'] == "9/10" or total_hit['total_hit'] == "10/10":
                            hit_dict[outcome['description']] = total_hit
                else:
                    if '+' in outcome['description']:
                        description_split_list = outcome['description'].split(' ')
                        if 'To' in description_split_list:
                            odds_prop = description_split_list[3]
                            odds_handicap = description_split_list[2][:-1]
                            odds_info = {'handicap' : odds_handicap, 'name' : outcome['name']}
                            if outcome['name'] in stats_combined_roster_dict.keys():
                                total_hit = make_comparison(outcome['name'], stats_combined_roster_dict[outcome['name']], odds_prop, odds_info)
                                if total_hit['total_hit'] == "8/10" or total_hit['total_hit'] == "9/10" or total_hit['total_hit'] == "10/10":
                                    hit_dict[outcome['description']] = total_hit
    return hit_dict


def make_comparison(player_name, player_stats, odds_prop, odds_info):
    hit = 0
    total = 0
    if 'Under' not in odds_info['name'] and 'First' not in odds_info['name']:
        for value in player_stats[odds_prop]:
            if int(value) >= float(odds_info['handicap']):
                hit += 1
            total += 1
    total_hit = str(hit) + "/" + str(total)
    return {'player name' : player_name, 'total_hit' : total_hit, 'handicap' : odds_info['handicap'], 'last_n' : player_stats[odds_prop]}


def get_game_id(team1, team2, date):
    games_response = requests.get("https://api.prop-odds.com/beta/games/nba?date=" + date + "&api_key=iUPX6GieMOK4F0CM8Gl5eVY9X0zmXRqCksKvPVClQ").json()
    games_list = games_response["games"]
    for game in games_list:
        if team1 in game['away_team'] or team2 in game['away_team']:
            game_id = game['game_id']
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

    print("\n" + args.team1input + ":")
    team1_attributes = get_team_attributes(args.team1input)
    team1_last_n_date = get_last_n_date_and_print_record(n, team1_attributes)
    team1_roster = get_team_roster(team1_attributes)

    # print(team1_attributes)
    # print(team1_last_n_date)
    # print(team1_roster)

    print("\n" + args.team2input + ":")
    team2_attributes = get_team_attributes(args.team2input)
    team2_last_n_date = get_last_n_date_and_print_record(n, team2_attributes)
    team2_roster = get_team_roster(team2_attributes)

    # print(team2_attributes)
    # print(team2_last_n_date)
    # print(team2_roster)

    matchup_last_n_dict = create_matchup_last_n_dict(team1_attributes, team1_last_n_date, team2_attributes, team2_last_n_date)

    combined_roster_list = team1_roster + team2_roster
    # print("\n" + "Combined Roster:")
    # print(combined_roster_list)

    stats_combined_roster_dict = create_stats_combined_roster_dict(combined_roster_list, matchup_last_n_dict)

    hit_dict = compare_odds(game_id, markets_list, args.date, stats_combined_roster_dict)

    for key in hit_dict.keys():
        print(key + ":")
        print(hit_dict[key])
        print('\n')


if __name__ == "__main__":
    main()