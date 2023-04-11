import argparse
from game import Game
from odds import Odds


def main():
    
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    # Adding optional argument
    parser.add_argument("-i", "--team1input", help = "Input team one")

    parser.add_argument("-j", "--team2input", help = "Input team two")

    parser.add_argument("-n", "--n", help = "n")

    parser.add_argument("-d", "--date", help = "Date")
    
    # Read arguments from command line
    args = parser.parse_args()

    game = Game(args.team1input, args.team2input, args.n, args.date)

    odds = Odds(args.team1input, args.team2input, args.date, game.stats_combined_roster_dict)

    for key in odds.hit_dict.keys():
        print(key + ":")
        print(odds.hit_dict[key])
        print('\n')


if __name__ == "__main__":
    main()