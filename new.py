import sys
import copy
import numpy as np

class LaskerMorris:
    def __init__(self):
        # Board positions as nodes with valid moves (graph adjacency list)
        self.board_map = {
            "a7": ["a4", "d7"], "d7": ["a7", "g7", "d6"], "g7": ["d7", "g4"],
            "b6": ["b4", "d6"], "d6": ["d7", "b6", "f6", "d5"], "f6": ["d6", "f4"],
            "c5": ["d5", "c4"], "d5": ["d6", "c5", "e5"], "e5": ["d5", "e4"],
            "a4": ["a7", "b4", "a1"], "b4": ["b6", "a4", "c4", "b2"], "c4": ["c5", "b4", "c3"],
            "e4": ["e5", "f4", "e3"], "f4": ["f6", "e4", "g4", "f2"], "g4": ["g7", "f4", "g1"],
            "c3": ["c4", "d3"], "d3": ["c3", "e3", "d2"], "e3": ["e4", "d3"],
            "b2": ["b4", "d2"], "d2": ["d3", "b2", "f2", "d1"], "f2": ["f4", "d2"],
            "a1": ["a4", "d1"], "d1": ["d2", "a1", "g1"], "g1": ["g4", "d1"]
        }

        # List of all mills
        self.mills = [
            ["a7", "d7", "g7"], ["b6", "d6", "f6"], ["c5", "d5", "e5"], # Top row mills
            ["a4", "b4", "c4"], ["e4", "f4", "g4"], # Middle row mills
            ["c3", "d3", "e3"], ["b2", "d2", "f2"], ["a1", "d1", "g1"], # Bottom row mills

            ["a7", "a4", "a1"], ["b6", "b4", "b2"], ["c5", "c4", "c3"], # Left column mills
            ["d7", "d6", "d5"], ["d3", "d2", "d1"], # Middle column mills
            ["e5", "e4", "e3"], ["f6", "f4", "f2"], ["g7", "g4", "g1"] # Right column mills
        ]

        # Track pieces on the board (None = empty)
        # a part for self.positions that sets each position in the mill back to None
        self.positions = {key: None for key in self.board_map.keys()}
        '''
        self.positions = {
            "a7": [None], "d7": [None], "g7": [None],
            "b6": [None], "d6": [None], "f6": [None],
            "c5": [None], "d5": [None], "e5": [None],
            "a4": [None], "b4": [None], "c4": [None],
            "e4": [None], "f4": [None], "g4": [None],
            "c3": [None], "d3": [None], "e3": [None],
            "b2": [None], "d2": [None], "f2": [None],
            "a1": [None], "d1": [None], "g1": [None]
        }
        '''
        self.bluepieces = 10
        self.orangepieces = 10

    def place_piece(self, position, player):
        # Places a piece for a player ('X' or 'O') if the position is empty.
        if player == 'X' and self.bluepieces > 0:
            if self.positions[position] is None:
                self.bluepieces -= 1
                self.positions[position] = player
                return True
        elif player == 'O' and self.orangepieces > 0:
            if self.positions[position] is None:
                self.orangepieces -= 1
                self.positions[position] = player
                return True
        return False

    def move(self, start, end, player):
        # Moves a piece if the move is valid.
        if self.positions[start] == player and self.positions[end] is None and end in self.board[start]:
            self.positions[start] = None
            self.positions[end] = player
            return True
        return False
    
    def display(self):
        board_layout = [
            f"{self.get_symbol(0)}--------{self.get_symbol(1)}--------{self.get_symbol(2)}",
            f"|        |        |",
            f"|  {self.get_symbol(3)}-----{self.get_symbol(4)}-----{self.get_symbol(5)}  |",
            f"|  |     |     |  |",
            f"|  |  {self.get_symbol(6)}--{self.get_symbol(7)}--{self.get_symbol(8)}  |  |",
            f"|  |  |     |  |  |",
            f"{self.get_symbol(9)}--{self.get_symbol(10)}--{self.get_symbol(11)}     {self.get_symbol(12)}--{self.get_symbol(13)}--{self.get_symbol(14)}",
            f"|  |  |     |  |  |",
            f"|  |  {self.get_symbol(15)}--{self.get_symbol(16)}--{self.get_symbol(17)}  |  |",
            f"|  |     |     |  |",
            f"|  {self.get_symbol(18)}-----{self.get_symbol(19)}-----{self.get_symbol(20)}  |",
            f"|        |        |",
            f"{self.get_symbol(21)}--------{self.get_symbol(22)}--------{self.get_symbol(23)}",
        ]

        for line in board_layout:
            print(line)
        print()

    def get_symbol(self, pos):
        # Returns the symbol of a position or a placeholder if empty.
        return self.positions[pos] if self.positions[pos] else "+"