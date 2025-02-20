import copy
import sys

class LaskerMorris:
    def __init__(self):
        # Board positions as nodes with valid moves (graph adjacency list)
        self.board = {
            "a7": ["a4", "d7"], "d7": ["a7", "g7", "d6"], "g7": ["d7", "g4"],
            "b6": ["b4", "d6"], "d6": ["d7", "b6", "f6", "d5"], "f6": ["d6", "f4"],
            "c5": ["d5", "c4"], "d5": ["d6", "c5", "e5"], "e5": ["d5", "e4"],
            "a4": ["a7", "b4", "a1"], "b4": ["b6", "a4", "c4", "b2"], "c4": ["c5", "b4", "c3"],
            "e4": ["e5", "f4", "e3"], "f4": ["f6", "e4", "g4", "f2"], "g4": ["g7", "f4", "g1"],
            "c3": ["c4", "d3"], "d3": ["c3", "e3", "d2"], "e3": ["e4", "d3"],
            "b2": ["b4", "d2"], "d2": ["d3", "b2", "f2", "d1"], "f2": ["f4", "d2"],
            "a1": ["a4", "d1"], "d1": ["d2", "a1", "g1"], "g1": ["g4", "d1"]
        }

        # Mills (winning sets)
        self.mills = [
            ["a7", "d7", "g7"], ["b6", "d6", "f6"], ["c5", "d5", "e5"],
            ["a4", "b4", "c4"], ["e4", "f4", "g4"],
            ["c3", "d3", "e3"], ["b2", "d2", "f2"], ["a1", "d1", "g1"],
            ["a7", "a4", "a1"], ["b6", "b4", "b2"], ["c5", "c4", "c3"],
            ["d7", "d6", "d5"], ["d3", "d2", "d1"],
            ["e5", "e4", "e3"], ["f6", "f4", "f2"], ["g7", "g4", "g1"]
        ]

        # Track board positions
        self.positions = {pos: None for pos in self.board.keys()}
        self.bluepieces = 10
        self.orangepieces = 10


    # Board Interactions #
    def place(self, position, player):
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
    # Board Interactions #


    # Evaluation Function and Evaluation Helpers # 
    def evaluate(self, player, state):
        # Evaluates the current state of the board
        score = 0
        score += self.piece_count(player, state) * 5
        score += self.mobility(player, state) * 2
        score += self.form_mill(player, state) * 50
        score += self.trap_opponent(player, state) * 20
        return score

    def piece_count(self, player, state):
        # Returns total piece count
        on_board = sum(1 for pos in state if state[pos] == player)
        in_hand = self.count_hand(player)
        return on_board + in_hand
    
    def mobility(self, player, state):
        # Returns number of available moves
        place_moves = 0 
        if self.count_hand(player) > 0:
            place_moves = sum(1 for pos in state if state[pos] is None)  # Empty spots
        move_moves = sum(1 for pos, piece in state.items() if piece == player 
                        for neighbor in self.board[pos] if state[neighbor] is None) # Legal Adjacent Moves

        return place_moves + move_moves
    
    def trap_opponent(self, player, state):
        # Identify if an opponent's piece has no legal moves
        # Returns number of opponent pieces that are completely immobile
        opponent = self.opponent(player)
        trapped_pieces = 0

        for pos, piece in state.items():
            if piece == opponent:
                if all(state[neighbor] is not None for neighbor in self.board[pos]):  # No available moves
                    trapped_pieces += 1

        return trapped_pieces
    
    def form_mill(self, player, state):
        # Returns amount of mills a player can complete with a single move
        p_mills = [] # List of mills player can complete

        for mill in self.mills:
            a, b, c = mill
            pieces = [state[a], state[b], state[c]]
            if pieces.count(player) == 2 and pieces.count(None) == 1:
                p_mills.append(pieces)

        return len(p_mills)
    # Evaluation Function and Evaluation Helpers # 


    # Calculate Best Move / Minimax / Minimax Helpers #
    def best_move(self, max_depth, player):
        # Return the best move as a string compatible with referee (xx, xx, xx)
        b_move = None
        board_state = copy.copy(self.positions)
        # Iterate depth for minimax until max_depth - Iterative Deepening
        for depth in range(1, max_depth + 1):
            move, _ = self.minimax(depth, -1000, 1000, True, player, board_state)
            if move is not None:
                b_move = move
        
        capture = self.check_capture(b_move, player)
        if capture != "r0":
            self.capture(capture, player)
        # Format string for referee
        if b_move[0] == "place":
            move_str = f"{'h1' if player == 'X' else 'h2'} {b_move[1]} {self.check_capture(b_move, player)}"
        elif b_move[0] == "move":
            move_str = f"{b_move[1]} {b_move[2]} {self.check_capture(b_move, player)}"

        return move_str
    
    def minimax(self, depth, alpha, beta, isMax, player, state):
        # Return the best move and the best score as a tuple: (best_move, best_score)

        if depth == 0 or self.terminal(state): # If at end of recursion (depth 0) or terminal state, return evaluation of board state
            return None, self.evaluate(player, state)
        
        b_move = None

        # Maximizer (player)
        if isMax:
            b_score = -1000
            # For every legal move, calculate score of board state
            for move in self.legal_moves(player, state): 
                mm_move = self.mm_move(move, player, state)
                # Recursively call minimax until depth 0 or terminal state. Propagate best score upwards
                _, score = self.minimax(depth - 1, alpha, beta, False, self.opponent(player), state)
                self.mm_undo(move, player, state, mm_move)

                if score > b_score:
                    b_score = score
                    b_move = move
                
                alpha = max(alpha, b_score)
                if beta <= alpha:
                    break
        # Minimizer (opponent)
        else:
            b_score = 1000
            for move in self.legal_moves(player, state):
                mm_move = self.mm_move(move, player, state)
                _, score = self.minimax(depth - 1, alpha, beta, False, self.opponent(player), state)
                self.mm_undo(move, player, state, mm_move)

                if score < b_score:
                    b_score = score
                    b_move = move
            
                beta = min(beta, b_score)
                if beta <= alpha:
                    break
        return b_move, b_score
    
    def mm_move(self, move, player, state):
        # Make move for minimax search: move = ('place/move', position, position2 - only for a move)
        capture = None
        if move[0] == "place": # Check for a place
            state[move[1]] = player # Place piece in given position
            # Take piece out of hand
            if player == "X":
                self.bluepieces -= 1
            else:
                self.orangepieces -= 1
            # Check if move completed a mill
            if self.mill_complete(player, state):
                # Set capture to the position of the best opponent piece to remove (currently just 1st available capture)
                capture = self.best_capture(player, state)
                state[capture] = None # Remove the captured piece from the board
        elif move[0] == "move": # Check for a move 
            # Set start position to None, set end position to player
            state[move[1]] = None
            state[move[2]] = player
            if self.mill_complete(player, state):
                # Same capture logic as above
                capture = self.best_capture(player, state)
                state[capture] = None
        return capture
    
    def mm_undo(self, move, player, state, capture):
        # Undo mm_move in minimax search: move = ('place/move', position, position2 - only for a move)
        if move[0] == "place": # Check for a place 
            state[move[1]] = None # Undo move
            # Restore used pieces
            if player == "X": 
                self.bluepieces += 1
            else:
                self.orangepieces += 1        
        elif move[0] == "move": # Check for a move 
            # Return start position to player, reset end position
            state[move[1]] = player 
            state[move[2]] = None
        # If piece was captured, restore piece
        if capture is not None and state[capture] is None:
            state[capture] = self.opponent(player)
    # Calculate Best Move / Minimax / Minimax Helpers #


    # Gameplay Loop #
    def play(self, depth):
        player_color = sys.stdin.readline().strip()
        player = "X" if player_color == "blue" else "O"
        opponent = self.opponent(player)

        # Make the first move for blue
        if player_color == "blue":
            p_move = self.best_move(depth, player).split()
            self.apply_move(' '.join(p_move), player)
            print(' '.join(p_move), flush=True)

        # Main play loop
        while True:
            try:
                line = sys.stdin.readline().strip()

                if line.startswith("END:"):
                    print(line, flush=True)
                    break

                if line:
                    if self.apply_move(line, opponent):
                        p_move = self.best_move(depth, player).split()
                        self.apply_move(' '.join(p_move), player)
                        print(' '.join(p_move), flush=True)
                    else:
                        print(f"Invalid move received: {line}", file=sys.stderr)
                        break

            except EOFError:
                break

    def apply_move(self, move, player):
        parts = move.split()
        if len(parts) == 3:
            if parts[0].startswith("h"):
                return self.place(parts[1], player)
            else:
                return self.move(parts[0], parts[1], player)
        return False
    # Gameplay Loop #

                    
    # Helper Functions
    def opponent(self, player):
        # Return opposite player (X -> O) (O -> X)
        return 'X' if player == 'O' else 'O'
        
    def terminal(self, state):
        # Game ends if a player has fewer than 3 pieces
        if self.piece_count('X', state) < 3 or self.piece_count('O', state) < 3:
            return True
        
        # Game ends if a player has no legal moves (immobilized)
        if not self.legal_moves('X', state) and not self.legal_moves('O', state):
            return True

        return False

    
    def count_hand(self, player):
        # Count pieces in players hand
        if player == 'X':
            in_hand = self.bluepieces
        else: 
            in_hand = self.orangepieces
        return in_hand
    
    def legal_moves(self, player, state):
        # Return list of moves player can legally make
        moves = []
        opponent = self.opponent(player)
        
        # Initial Phase
        if self.count_hand(player) > 0:
            for pos in state:
                if state[pos] is None:  # Empty spot
                    # Check if placing here creates a mill
                    temp_state = state.copy()
                    temp_state[pos] = player
                    capture = self.best_capture(player, temp_state) if self.mill_complete(player, temp_state) else "r0"
                    moves.append(("place", pos, capture))

        # Moving Phase and Flying Phase
        else:
            can_fly = self.piece_count(player, state) == 3  # Can "fly" if only 3 pieces left

            for start in state:
                if state[start] == player:  # Find player's pieces
                    possible_moves = state.keys() if can_fly else self.board[start]  # Fly anywhere or move adjacently
                    
                    for end in possible_moves:
                        if state[end] is None:  # Empty destination
                            temp_state = state.copy()
                            temp_state[start] = None
                            temp_state[end] = player
                            capture = self.best_capture(player, temp_state) if self.mill_complete(player, temp_state) else "r0"
                            moves.append(("move", start, end, capture))

        return moves

    
    def mill_complete(self, player, state):
        # Check array of possible mills for complete mill
        for mill in self.mills:
            a, b, c = mill
            pieces = [state[a], state[b], state[c]]
            if pieces.count(player) == 3:
                return True
        return False
    
    def check_capture(self, move, player):
        board_copy = copy.copy(self.positions)
        if move[0] == "place":
            board_copy[move[1]] = player
        elif move[0] == 'move':
            board_copy[move[1]] = None
            board_copy[move[2]] = player
        
        if self.mill_complete(player, board_copy):
            return self.best_capture(player, board_copy)
        else:
            return "r0"

    def best_capture(self, player, state):
        # Select the best opponent piece to capture when forming a mill.
        opponent = self.opponent(player)
        candidate_pieces = []  # Stores pieces that can be captured

        # Identify opponent pieces that are not in mills
        for pos in state:
            if state[pos] == opponent:
                if not self.part_of_mill(pos, state, opponent):  # Prefer non-mill pieces
                    candidate_pieces.append((pos, self.mobility(opponent, state)))

        # If there are non-mill pieces, prioritize those that limit the opponent's mobility
        if candidate_pieces:
            return min(candidate_pieces, key=lambda x: x[1])[0]  # Pick piece that most reduces opponent mobility

        # If all opponent pieces are in mills, remove the most disruptive piece
        candidate_pieces = [(pos, self.mobility(opponent, state)) for pos in state if state[pos] == opponent]
        return min(candidate_pieces, key=lambda x: x[1])[0] if candidate_pieces else None

    # Helper Functions #    
    def part_of_mill(self, pos, state, player):
        # Checks if the given position is part of an existing mill
        for mill in self.mills:
            if pos in mill:
                pieces = [state[p] for p in mill]
                if pieces.count(player) == 3:  # The entire mill is formed
                    return True
        return False


if __name__ == "__main__":
    game = LaskerMorris()
    game.play(3)