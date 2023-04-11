import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import playergamelog
import requests
import pandas as pd
import argparse


class Game:
    def __init__(self, team1_nickname, team2_nickname, n, date):
        print(team1_nickname)
        self.team1_attributes = self.get_team_attributes(team1_nickname)
        self.team1_last_n_date = self.get_last_n_date_and_print_record(n, self.team1_attributes)
        self.team1_roster = self.get_team_roster(self.team1_attributes)

        print(team2_nickname)
        self.team2_attributes = self.get_team_attributes(team2_nickname)
        self.team2_last_n_date = self.get_last_n_date_and_print_record(n, self.team2_attributes)
        self.team2_roster = self.get_team_roster(self.team2_attributes)

        self.matchup_last_n_dict = self.create_matchup_last_n_dict(self.team1_attributes, self.team1_last_n_date, self.team2_attributes, self.team2_last_n_date)
        self.combined_roster_list = self.team1_roster + self.team2_roster
        self.stats_combined_roster_dict = self.create_stats_combined_roster_dict(self.combined_roster_list, self.matchup_last_n_dict)
            

    def get_team_attributes(self, team_nickname):
        nba_teams = teams.get_teams()
        team_attributes = None
        for team in nba_teams:
            if team['nickname'] == team_nickname:
                team_attributes = team
        return team_attributes


    def get_last_n_date_and_print_record(self, n, team_attributes):
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


    def create_matchup_last_n_dict(self, team1_attributes, team1_date, team2_attributes, team2_date):
        output_dict = {team1_attributes['id'] : team1_date, team2_attributes['id'] : team2_date}
        return output_dict


    def get_team_roster(self, team_attributes):
        time.sleep(2)
        team_roster = commonteamroster.CommonTeamRoster(team_attributes['id'])
        team_roster_list_with_attributes = team_roster.get_dict()['resultSets'][0]['rowSet']
        team_roster_list = []
        for player in team_roster_list_with_attributes:
            team_roster_list.append(player)
        return team_roster_list


    def get_last_n_player_stats(self, player, n_game_date):
        time.sleep(2)
        return playergamelog.PlayerGameLog(player_id=player[-2], season='2022-23', date_from_nullable=n_game_date).get_dict()["resultSets"]


    def create_stats_combined_roster_dict(self, combined_roster_list, matchup_last_n_dict):
        stats_combined_roster_dict = {}
        for player in combined_roster_list:
            player_stats_dict = {'Made Threes' : [], 'Rebounds' : [], 'Assists' : [], 'Steals' : [], 'Blocks' : [], 'Turnovers' : [], 'Points' : [], 'Pts + Ast' : [], 'Pts + Reb + Ast' : [], 'Reb + Ast' : [], 'Pts + Reb' : [], 'Steals + Blocks' : []}
            player_last_n_date = matchup_last_n_dict[player[0]]
            player_stats_last_n = self.get_last_n_player_stats(player, player_last_n_date)
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


