class LaskerMorris:
    def __init__(self):
        # Board positions as nodes with valid moves (graph adjacency list)
        self.board = {
            0: [1, 9],  1: [0, 2, 4],  2: [1, 14],
            3: [4, 10],  4: [1, 3, 5, 7],  5: [4, 13],
            6: [7, 11],  7: [4, 6, 8],  8: [7, 12],
            9: [0, 10, 21],  10: [3, 9, 11, 18],  11: [6, 10, 15],
            12: [8, 13, 17],  13: [5, 12, 14, 20],  14: [2, 13, 23],
            15: [11, 16],  16: [15, 17, 19],  17: [12, 16],
            18: [10, 19],  19: [16, 18, 20, 22],  20: [13, 19],
            21: [9, 22],  22: [19, 21, 23],  23: [14, 22]
        }
        # Track pieces on the board (None = empty)
        self.positions = {i: None for i in range(24)}
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

    def move_piece(self, start, end, player):
        # Moves a piece if the move is valid.
        if self.positions[start] == player and self.positions[end] is None and end in self.board[start]:
            self.positions[start] = None
            self.positions[end] = player
            return True
        return False

    def display_board(self):
        # Displays the board state (simple textual representation).
        for i in range(24):
            print(self.positions[i] if self.positions[i] else ".", end=" ")
            if i % 3 == 2: 
                print()
        print()
    def evaluate_board(self, player):
        # Evaluates the current state of the board
        score = 0
        score += self.piece_count(player)
        score += self.mobility(player)
        return score

    def piece_count(self, player):
        # Returns total piece count
        on_board = sum(1 for piece in self.board if piece == player)
        if player == 'X':
            in_hand = self.bluepieces
        else: 
            in_hand = self.orangepieces
        
        return on_board + in_hand
    
    def mobility(self, player):
        # Returns number of available moves 
        place_moves = sum(1 for pos in self.positions if self.positions[pos] is None)  # Empty spots
        move_moves = sum(1 for pos, piece in self.positions.items() if piece == player 
                        for neighbor in self.board[pos] if self.positions[neighbor] is None) # Legal Adjacent Moves

        return place_moves + move_moves
    
    def form_mill(self, player):
        print("Hello World")
                        



    
game = LaskerMorris()
game.place_piece(0, 'X')
game.place_piece(1, 'X')
game.place_piece(21, 'X')
game.display_board()
game.form_mill('X')


