import copy

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

    def evaluate(self, player, state):
        # Evaluates the current state of the board
        score = 0
        score += self.piece_count(player, state) * 5
        # print("Piece Count:", self.piece_count(player))
        score += self.mobility(player, state)
        # print(self.mobility(player))
        score += self.form_mill(player, state) * 100
        # print(self.form_mill(player))
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
    
    def form_mill(self, player, state):
        # Returns amount of mills a player can complete with a single move
        p_mills = [] # List of mills player can complete

        for mill in self.mills:
            a, b, c = mill
            pieces = [state[a], state[b], state[c]]
            if pieces.count(player) == 2 and pieces.count(None) == 1:
                p_mills.append(pieces)

        return len(p_mills)

    def minimax(self, depth, alpha, beta, isMax, player, state):
        if depth == 0 or self.terminal(state):
            return None, self.evaluate(player, state)
        
        b_move = None

        if isMax:
            b_score = -1000
            for move in self.legal_moves(player, state):
                mm_move = self.mm_move(move, player, state)
                _, score = self.minimax(depth - 1, alpha, beta, False, self.opponent(player), state)
                self.mm_undo(move, player, state, mm_move)

                if score > b_score:
                    b_score = score
                    b_move = move
                
                alpha = max(alpha, b_score)
                if beta <= alpha:
                    break
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
                
        
    def best_move(self, max_depth, player):
        b_move = None
        board_state = copy.copy(self.positions)
        for depth in range(1, max_depth + 1):
            move, _ = self.minimax(depth, -1000, 1000, True, player, board_state)
            if move is not None:
                b_move = move

        return b_move
        
    # Return boolean representing terminal state
    def terminal(self, state):
        return self.piece_count('X', state) < 3 or self.piece_count('O', state) < 3
    
    # Count pieces in players hand
    def count_hand(self, player):
        if player == 'X':
            in_hand = self.bluepieces
        else: 
            in_hand = self.orangepieces
        return in_hand
    
    def legal_moves(self, player, state):
        # Return list of moves player can legally make
        moves = []
        in_hand = self.count_hand(player)
        # Placement Phase
        if in_hand > 0:
            for pos in state:
                if state[pos] == None:
                    moves.append(("place", pos))
        # Movement Phase
        elif self.piece_count(player, state) > 3:
            for start in state:
                if state[start] == player:
                    for neighbor in self.board[start]:
                        if state[neighbor] == None:
                            moves.append(("move", start, neighbor))
        # Flying Phase
        else: 
            for start in state:
                if state[start] == player:
                    for end in state:
                        if state[end] is None:
                            moves.append(("move", start, end)) 
        return moves

    def mill_complete(self, player, state):
        for mill in self.mills:
            a, b, c = mill
            pieces = [state[a], state[b], state[c]]
            if pieces.count(player) == 3:
                return True
        return False
    
    def mm_move(self, move, player, state):
        capture = None
        if move[0] == "place":
            state[move[1]] = player
            if player == "X":
                self.bluepieces -= 1
            else:
                self.orangepieces -= 1
            if self.mill_complete(player, state):
                capture = self.best_capture(player, state)
                if capture is not None:
                    state[capture] = None
        elif move[0] == "move":
            state[move[1]] = None
            state[move[2]] = player
            if self.mill_complete(player, state):
                capture = self.best_capture(player, state)
                if capture is not None:
                    state[capture] = None
        return capture
    
    def mm_undo(self, move, player, state, capture=None):
        if move[0] == "place":
            state[move[1]] = None
            if player == "X":
                self.bluepieces += 1
            else:
                self.orangepieces += 1        
        elif move[0] == "move":
            state[move[1]] = player
            state[move[2]] = None
        if capture is not None and state[capture] is None:
            state[capture] = self.opponent(player)


    def best_capture(self, player, state):
        opponent = self.opponent(player)
        for pos in state:
            if state[pos] == opponent:
                return pos
        return None

        
        
game = LaskerMorris()

player = "X"
opponent = game.opponent(player)


def test_move(depth, player):
    p_move = game.best_move(depth, player)
    if p_move[0] == "place":
        print("PLACE", i + 1, p_move, player)
        game.place(p_move[1], player)
        print("X IN HAND:", game.bluepieces)
        print("O IN HAND:", game.orangepieces)
        if game.mill_complete(player, game.positions):
            capture = game.best_capture(player, game.positions)
            print("MILL FORMED, CAPTURING POSITION:", capture)
            game.capture(capture, player)
    elif p_move[0] == "move":
        print("MOVE", i + 1, p_move, player)
        game.move(p_move[1], p_move[2], player) 
        if game.mill_complete(player, game.positions):
            capture = game.best_capture(player, game.positions)
            print("MILL FORMED, CAPTURING POSITION:", capture)
            game.capture(capture, player)
    game.display()


for i in range(25):
    if i % 2 == 0:
        test_move(3, player)
    else:
        test_move(3, opponent)