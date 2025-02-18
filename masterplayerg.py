import sys
import copy
import numpy as np

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

        # List of all mills
        self.mills = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Top row mills
        (9, 10, 11), (12, 13, 14), (15, 16, 17),  # Middle row mills
        (18, 19, 20), (21, 22, 23),  # Bottom row mills
        (0, 9, 21), (3, 10, 18), (6, 11, 15),  # Left column mills
        (1, 4, 7), (16, 19, 22),  # Middle column mills
        (8, 12, 17), (5, 13, 20), (2, 14, 23)  # Right column mills
        ]

        # Track pieces on the board (None = empty)
        self.positions = {i: None for i in range(24)}
        self.bluepieces = 10
        self.orangepieces = 10

    def opponent(self, player):
        return 'X' if player == 'O' else 'O'
    
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
    
    def capture(self, pos, player):
        if self.positions[pos] == self.opponent(player):
            self.positions[pos] = None
            return True
        return False

    def display(self):
        # Displays the board state (simple textual representation).
        for i in range(24):
            print(self.positions[i] if self.positions[i] else ".", end=" ")
            if i % 3 == 2: 
                print()
        print()
    
    def get_symbol(self, pos):
        # Returns the symbol of a position or a placeholder if empty.
        return self.positions[pos] if self.positions[pos] else "+"

    def evaluate(self, player):
        # Evaluates the current state of the board
        score = 0
        score += self.piece_count(player) * 5
        score += self.mobility(player)
        score += self.form_mill(player) * 100
        score += self.block_opponent(player, 'O' if player == 'X' else 'X') * 10
        # score += self.best_move(player)
        return score

    def piece_count(self, player):
        # Returns total piece count
        on_board = sum(1 for pos in self.positions if self.positions[pos] == player)
        in_hand = self.count_hand(player)
        return on_board + in_hand
    
    def mobility(self, player):
        # Returns number of available moves 
        place_moves = sum(1 for pos in self.positions if self.positions[pos] is None)  # Empty spots
        move_moves = sum(1 for pos, piece in self.positions.items() if piece == player 
                        for neighbor in self.board[pos] if self.positions[neighbor] is None) # Legal Adjacent Moves

        return place_moves + move_moves
    
    def block_opponent(self, player, opponent):
        # this checks if the opponent is one move away from forming a mill and blocks it
        # the defensive play
        block_moves = 0
        for pos in self.positions:
            if self.positions[pos] is None:
                self.positions[pos] = player
                # fix this!
                if self.form_mill(player):
                    block_moves += 1
                self.positions[pos] = None
        return block_moves
    
    def form_mill(self, player):
        # Returns amount of mills a player can complete with a single move
        p_mills = [] # List of mills player can complete

        for mill in self.mills:
            a, b, c = mill
            pieces = [self.positions[a], self.positions[b], self.positions[c]]
            if pieces.count(player) == 2 and pieces.count(None) == 1:
                p_mills.append(pieces)

        return len(p_mills)

    def minimax(self, depth, alpha, beta, isMax, player):
        if depth == 0 or self.terminal():
            score = self.evaluate(player)
            # print(f"Depth {depth} | Evaluating Board for {player}: {score}")
            return score
        if isMax:
            best = -1000
            for move in self.legal_moves(player):
                mm_move = self.mm_move(move, player)
                score = self.minimax(depth - 1, alpha, beta, False, self.opponent(player))
                self.mm_undo(move, player, mm_move)
                # print(f"Depth {depth} | Maximizing {player} | Move: {move} | Score: {score}")

                best = max(best, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return best
        else:
            best = 1000
            for move in self.legal_moves(player):
                mm_move = self.mm_move(move, player)
                score = self.minimax(depth - 1, alpha, beta, True, player)
                self.mm_undo(move, player, mm_move)
                # print(f"Depth {depth} | Minimizing {player} | Move: {move} | Score: {score}")

                best = min(best, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best
        
    def best_move(self, max_depth, player):
        b_score = -1000
        b_move = None

        for depth in range(1, max_depth + 1):
            for move in self.legal_moves(player):
                mm_move = self.mm_move(move, player)
                score = self.minimax(depth, -1000, 1000, False, player)
                self.mm_undo(move, player, mm_move)
                # print(f"Depth {depth} | Testing Move: {move} | Score: {score}")

                if score > b_score:
                    b_score = score
                    b_move = move
                
                if b_score == 1000:
                    return b_move
        
        # print(f"Best Move Chosen: {b_move} with Score: {b_score}")        
        return b_move
        
    # Return boolean representing terminal state
    def terminal(self):
        return self.piece_count('X') < 3 or self.piece_count('O') < 3
    
    # Count pieces in players hand
    def count_hand(self, player):
        if player == 'X':
            in_hand = self.bluepieces
        else: 
            in_hand = self.orangepieces
        return in_hand
    
    def legal_moves(self, player):
        # Return list of moves player can legally make
        moves = []
        in_hand = self.count_hand(player)
        # Placement Phase
        if in_hand > 0:
            for pos in self.positions:
                if self.positions[pos] == None:
                    moves.append(("place", pos))
        # Movement Phase
        elif self.piece_count(player) > 3:
            for start in self.positions:
                if self.positions[start] == player:
                    for neighbor in self.board[start]:
                        if self.positions[neighbor] == None:
                            moves.append(("move", start, neighbor))
        # Flying Phase
        else: 
            for start in self.positions:
                if self.positions[start] == player:
                    for end in self.positions:
                        if self.positions[end] is None:
                            moves.append(("move", start, end)) 
        return moves

    def mill_complete(self, player):
        for mill in self.mills:
            a, b, c = mill
            pieces = [self.positions[a], self.positions[b], self.positions[c]]
            if pieces.count(player) == 3:
                return True
        return False
    
    def mm_move(self, move, player):
        if move[0] == "place":
            self.place(move[1], player)
            if self.mill_complete(player):
                capture = self.best_capture(player)
                if capture is not None:
                    self.capture(capture, player)
                    return capture
        elif move[0] == "move":
            self.move(move[1], move[2], player)
            if self.mill_complete(player):
                capture = self.best_capture(player)
                if capture is not None:
                    self.capture(capture, player)
                    return capture
        return None
    
    def mm_undo(self, move, player, capture=None):
        if move[0] == "place":
            self.positions[move[1]] = None
            if player == "X":
                self.bluepieces += 1
            else:
                self.orangepieces += 1        
            if capture:
                self.positions[capture] = self.opponent(player)
        elif move[0] == "move":
            self.positions[move[1]] = player
            self.positions[move[2]] = None
            if capture:
                self.positions[capture] = self.opponent(player)

    def best_capture(self, player):
        opponent = self.opponent(player)
        for pos in self.positions:
            if self.positions[pos] == opponent:
                return pos
        return None

    # this checks to see who the winner is by looking at the number of pieces left
    def check_winner(self):
        if self.piece_count('X') < 3:
            print("Orange (O) Wins!")
            return 'O'
        elif self.piece_count('O') < 3:
            print("Blue (X) Wins!")
            return 'X'

        if not self.valid_moves('X'):
            print("Orange (O) Wins! Blue (X) has no valid moves.")
            return 'O'
        elif not self.valid_moves('O'):
            print("Blue (X) Wins! Orange (O) has no valid moves.")
            return 'X'
        return None
    
    
    def play(self):
        player_color = None

        while True:
            try:
                game_input = sys.stdin.readline().strip()

                # this determines the player's color at the start
                if game_input in ['blue', 'orange']:
                    player_color = game_input
                    is_blue = (player_color == 'blue')

                    # this is for when blue plays first
                    if is_blue:
                        move = self.best_move('X')
                        if move is not None:
                            # this sends the move to the referee
                            print(move, flush=True)
                            self.place_piece(move, 'X')

                    continue

                # this processes the opponent's move
                opponent_move = int(game_input)

                if opponent_move in self.valid_moves('O' if player_color == 'blue' else 'X'):
                    self.place_piece(opponent_move, 'O' if player_color == 'blue' else 'X')

                # this checks if game has ended
                if self.check_winner():
                    break

                # ai move
                move = self.best_move('X' if player_color == 'blue' else 'O')
                if move is not None:
                    # this sends the move to the referee
                    print(move, flush=True)
                    self.place_piece(move, 'X' if player_color == 'blue' else 'O')

            except EOFError:
                break
    

    '''
    # this runs the game on a loop until there is a winner
    def play(self):
        while True:
            move = self.best_move('X')
            if move is not None:
                self.place_piece(move, 'X')
                print(f"X plays: {move}")
            
            if self.check_winner():  # Check if game is over
                break

            move = self.best_move('O')
            if move is not None:
                self.place_piece(move, 'O')
                print(f"O plays: {move}")

            if self.check_winner():  # Check again after opponent's move
                break
    '''
                        
if __name__ == "__main__":
    game = LaskerMorris()
    game.play()


