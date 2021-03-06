import chess
from search import min_max, score_min_max
from evaluate import evaluate
import time
import os
from multiprocessing import Pool
import sys
import copy


def calculate_competence(competence, diff):
    """
    subtracts weights from competence based off of difference between the
    players moves score and the optimal moves score
    """
    if diff < 25:
        competence += .02
    if 25 <= diff < 50:
        competence += .01
    elif 50 <= diff < 100:
        competence -= competence * .01
    elif 100 <= diff < 200:
        competence -= competence * .02
    elif 200 <= diff:
        competence -= competence * .03
    # don't let competence fall below .7 or 1
    return min(max(competence, .7), 1)


def get_move(board):
    move = None
    start_time = time.time()
    while move not in board.legal_moves:
        try:
            move = chess.Move.from_uci(raw_input("enter uci move: "))
        except:
            move=None
    return move, time.time() - start_time


# passes stdin to supproccess
def initialize(fd):
    sys.stdin = os.fdopen(fd)


def game():
    players_competence = 1.0
    brd = chess.Board()
    move = None
    print("Regular Chess AI \n\n PLEASE MAKE A MOVE WITHIN 5 MINUTES OR PROGRAM WILL" +
            " TERMINATE \n")

    while not brd.is_game_over():
        if brd.turn == chess.WHITE:
            print(brd)
            print
            # gets user move and find best move at the same time then
            # calculates user moves score and best moves score simultaneusly
            if __name__ == '__main__':
                init_args = [sys.stdin.fileno()]
                p = Pool(
                    initializer=initialize,
                    initargs=init_args, processes=2)
                best_move_result = p.apply_async(min_max, (brd,))
                move_result = p.apply_async(get_move, (brd,))
                move, time_to_move = move_result.get(timeout=300)
                print
                best_move = best_move_result.get(timeout=300)
                best_brd = copy.deepcopy(brd)
                brd.push(move)
                best_brd.push(best_move)
                best_move_score_result = p.apply_async(
                    score_min_max, (best_brd,))
                move_score_result = p.apply_async(score_min_max, (brd,))
                print("Calculating Player Competence... \n")
                best_move_score = (
                    best_move_score_result.get(timeout=300))
                move_score = (move_score_result.get(timeout=300))
                diff = abs(best_move_score - move_score)
                players_competence = calculate_competence(
                    players_competence, round(diff, -1))
                print("difference between best play and player move: " +
                      str(diff))
                print("Player's estimated competence: " +
                      str(players_competence))
                print("Whites best_move: " + best_move.uci())
                print("Whites move: " + move.uci())
                print("Whites time to move: " + str(time_to_move) + "s")
                print
        else:
            print(brd)
            print
            start_time = time.time()
            move = min_max(brd)
            brd.push(move)
            print
            print("Black's move: " + move.uci())
            print(
                "Blacks time to move: " + str(time.time() - start_time) + "s")
            print
    print('Game Over')

game()





