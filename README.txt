Documentation
1. The names of the members of your group. A detailed description of what each teammate contributed to the project.
- Grace Robinson and Jesse Vu worked together to implement minimax with alpha beta pruning as well as working on the evaluation functions. We also designed the game representation and worked on the legal moves and heuristic stuff to improve it.
- Andrey S helped with some of the evaluation functions and debugging.
2. Instructions on compiling and running your program.
- To compile and run the program we used cs4341-referee laskermorris -p1 "python masterplayerg.py" -p2 "python masterplayerg.py" --visual --log
3. The utility function that your program uses.
- The utility function:
        if self.terminal(state):
            if self.piece_count(player, state) < 3:  # Loss condition
                return -1000
            if self.piece_count(self.opponent(player), state) < 3:  # Win condition
                return 1000
4. The evaluation function that your program uses.
- The evaluation function looks at piece count (+5), mobility, mills formed (+50, this one is prioritezed), and trapping an opponent (+20).
5. The heuristics and/or strategies that you employed to decide how to expand nodes of the minimax tree without exceeding your time limit.
- We used iterative deepening which ensured that the AI made a valid move that was also within the time constraint. We also prioritized forming a mill as well as having defensive play when down to 3 pieces all to improve the game.
6. Results:
    a. describe which tests you ran to try out your program. Did your program play against human players? Did your program play against itself? Did your program play against other programs? How did your program do during those games?
    - The test that we ran was that we played the program against itself. We also used the --log in order to look at how the game was actually playing to get a better idea of what needed to change and be improved.
    b. describe the strengths and the weaknesses of your program.
    - Some of the strengths is that the program does effectivly form mills and remove opponents pieces but one of the weaknesses is that it fails to get out of a stalemate early on.
7. A discussion of why the evaluation function and the heuristic(s) you picked are good choices.
- The evaluation function and the heuristic(s) we picked are good choices because they ensure that there is pressure on the opponent forcing the opponent to have fewer options. It also respects the time limit so it always makes a move in time.