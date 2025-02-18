import copy

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
            f"{self.get_symbol("a7")}--------{self.get_symbol("d7")}--------{self.get_symbol("g7")}",
            f"|        |        |",
            f"|  {self.get_symbol("b6")}-----{self.get_symbol("d6")}-----{self.get_symbol("f6")}  |",
            f"|  |     |     |  |",
            f"|  |  {self.get_symbol("c5")}--{self.get_symbol("d5")}--{self.get_symbol("e5")}  |  |",
            f"|  |  |     |  |  |",
            f"{self.get_symbol("a4")}--{self.get_symbol("b4")}--{self.get_symbol("c4")}     {self.get_symbol("e4")}--{self.get_symbol("f4")}--{self.get_symbol("g4")}",
            f"|  |  |     |  |  |",
            f"|  |  {self.get_symbol("c3")}--{self.get_symbol("d3")}--{self.get_symbol("e3")}  |  |",
            f"|  |     |     |  |",
            f"|  {self.get_symbol("b2")}-----{self.get_symbol("d2")}-----{self.get_symbol("f2")}  |",
            f"|        |        |",
            f"{self.get_symbol("a1")}--------{self.get_symbol("d1")}--------{self.get_symbol("g1")}",
        ]

        for line in board_layout:
            print(line)
        print()

    def get_symbol(self, position):
        # Returns the symbol of a position or a placeholder if empty.
        return self.positions.get(position, "+")


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