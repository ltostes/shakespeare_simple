from datetime import datetime
import time
import random
import math
import string
import os
import copy

PLAYER_STANDARD_COLORS    = {
                                'Pink'   : {'background_color' : '#ff4d4d', 'text_color' : '#ffffff'},
                                'Blue'   : {'background_color' : '#1732ff', 'text_color' : '#ffffff'},
                                'Green'  : {'background_color' : '#098a00', 'text_color' : '#ffffff'},
                                'Yellow' : {'background_color' : '#ffa600', 'text_color' : '#ffffff'},
                                'Orange' : {'background_color' : '#ff4400', 'text_color' : '#ffffff'},
                                'Brown'  : {'background_color' : '#452302', 'text_color' : '#ffffff'},
                                'Black'  : {'background_color' : '#000000', 'text_color' : '#ffffff'},
                                'White'  : {'background_color' : '#ffffff', 'text_color' : '#000000'},
                                'Red'    : {'background_color' : '#eb1f10', 'text_color' : '#ffffff'},
                                'Purple' : {'background_color' : '#8749b3', 'text_color' : '#ffffff'},
                                'Gray'   : {'background_color' : '#adadad', 'text_color' : '#ffffff'},
}

PLAYER_COLORS = ['Purple', 'Pink', 'Yellow', 'Blue', 'Orange', 'Red', 'Brown', 'Green', 'Gray', 'Black', 'White']

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DICTIONARIES_ROOT = os.path.join(APP_ROOT, '..', 'dictionaries')

DICTIONARIES = {
    "Original" :    DICTIONARIES_ROOT + "/palavras.csv",
    "CAH" :         DICTIONARIES_ROOT + "/cah_code_names.txt",
    "Pop Culture" : DICTIONARIES_ROOT + "/code_names_pop.txt",
    "Standard" :    DICTIONARIES_ROOT + "/code_names_dict.txt",
    "Simple" :      DICTIONARIES_ROOT + "/code_names_simple.txt",
    "French" :      DICTIONARIES_ROOT + "/code_names_french.txt",
    "Portuguese" :  DICTIONARIES_ROOT + "/code_names_portuguese.txt",
    "German" :      DICTIONARIES_ROOT + "/code_names_german.txt"
}

def get_stats():
    return 0, 'stats',1

class GameInfo(object):

    """Object for tracking game stats"""
    def __init__(self,dictionary='Original', players = [], max_singles = 1, default_game_id=False):
        self.dictionary = dictionary
        if default_game_id:
            self.game_id = 'DEFAULT' # self.generate_game_id()
        else:
            self.game_id = self.generate_game_id()
        self.players = players
        self.available_colors = copy.deepcopy(PLAYER_COLORS)
        self.date_created = datetime.now()
        self.date_modified = self.date_created
        self.max_singles = max_singles
        self.rounds = []

    def to_json(self):
        """Serialize object to JSON"""
        return {
            "game_id": self.game_id,
            "players": self.players,
            "available_colors": self.available_colors,
            "date_created": self.date_created.strftime(format="%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime(format="%Y-%m-%d %H:%M:%S"),
            "playtime": self.__playtime(),
            "options": {
                "dictionary": self.dictionary
            },
            "rounds" : self.rounds,
            "max_singles" : self.max_singles,
            "round_number" : len(self.rounds),
            "round_info"   : self.rounds[-1] if self.rounds else None
        }

    def start_round(self):
        """Startup new round"""

        # Round start time
        self.date_modified = datetime.now()
        round_start_time = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")

        # Getting current players set up and max singles
        current_players = self.players
        number_of_players = len(current_players)
        max_singles = self.max_singles

        # Load dictionary of words and shuffle
        words = self.__load_words(self.dictionary)
        random.shuffle(words)
        player_words = []

        # Defaulting max_singles if invalid
        if (max_singles > number_of_players) or (max_singles < 0): max_singles = 1

        # Sort out words equivalent to the number of players
        for player_number in range(0,number_of_players + (max_singles - 1)):
            player_words.append(words[int((player_number)/2)])

        # Scramble word orders
        random.shuffle(player_words)

        # Assign words to each player
        round_players = []
        for i in range(0, number_of_players):
            player_round = copy.deepcopy(current_players[i])
            player_round['round_word'] = player_words[i]

            round_players.append(player_round)

        # Form round object and save it
        new_round = {}
        new_round['start_time']     = round_start_time
        new_round['player_info']    = round_players

        self.rounds.append(new_round)

    def standard_player_setup(self,number_of_players):
        """Setup players with standard setup (colors in order)"""
        players = []

        # Looping through standard order
        for player_color in PLAYER_COLORS[:number_of_players]:
            player = {}
            # Assign standard colors in order
            player['Color'] = player_color
            player['Color_config'] = PLAYER_STANDARD_COLORS[player_color]

            players.append(player)

        self.players = players

    def add_player(self,player_color, player_name=''):
        player = {}

        player['Color'] = player_color

        if player_name: player['Name'] = player_name

        if player_color in self.available_colors:
            self.available_colors.remove(player_color)
            self.players.append(player)
            return "Player {} successfully added with color {}.".format(len(self.players),player_color)
        else:
            return "I'm sorry, this color is not available."

    def remove_player_by_index(self,index):
        self.players.pop(index)

    def remove_player_by_info(self,player_color, player_name=''):
        player = {}

        player['Color'] = player_color

        if player_name: player['Name'] = player_name

        if player in self.players:
            player_index = self.players.index(player)
            self.available_colors +=  player_color
            self.players.remove(player)
            return "Player {} with color {} successfully removed.".format(player_index,player_color)
        else:
            return "This player doesn't exist"


    def __playtime(self):
        # 2018-08-12 10:12:25.700528
        fmt = '%Y-%m-%d %H:%M:%S'
        d1 = self.date_created
        d2 = self.date_modified
        # Convert to Unix timestamp
        d1_ts = time.mktime(d1.timetuple())
        d2_ts = time.mktime(d2.timetuple())

        return round(float(d2_ts-d1_ts) / 60, 2)

    def __load_words(self, dict):
        words_file = open(DICTIONARIES[dict], 'r')
        return [elem for elem in words_file.read().split('\n') if len(elem.strip()) > 0]

    @classmethod
    def generate_game_id(cls):
        """Generate a random room ID"""
        id_length = 5
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase) for _ in range(id_length))
