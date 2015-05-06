import chess
from evaluate import evaluate
from collections import OrderedDict

TABLE_SIZE = 500000
DEPTH = 3
tp = OrderedDict()
exact_flag = 0
alpha_flag = 1
beta_flag = 2


class Entry():
    def __init__(self, score, depth, flag, move=None):
        self.score = score
        self.depth = depth
        self.flag = flag
        self.move = move


def search_hash(depth, alpha, beta, hsh):
    global tp
    record = tp.get(hsh)
    if record:
        if record.depth >= depth:
                if record.flag == 0:
                    return record.score
                elif record.flag == 1:
                    if record.score <= alpha:
                        return alpha
                else:
                    if record.score >= beta:
                        return beta
    return None


def input_hash(hsh, depth, score, flag, move=None):
    global tp
    exists = tp.get(hsh)
    if exists:
        if exists.depth > depth:
            return
    tp[hsh] = Entry(score, depth, flag, move)
    if len(tp) > TABLE_SIZE:
        tp.popitem(False)


def check_best_move(hsh, moves):
    record = tp.get(hsh)
    moves = list(moves)
    if record:
        if record.move:
            moves.remove(record.move)
            moves.insert(0, record.move)
    return moves


def min_max(board):
    hsh = board.zobrist_hash()
    best_move = None
    alpha, beta = -1000000, 1000000
    if board.turn == chess.WHITE:
        for move in check_best_move(hsh, board.generate_legal_moves()):
            board.push(move)  # make move
            score = _min_max(board, alpha, beta)
            board.pop()  # unmake move
            if score > alpha:
                alpha = score
                best_move = move
                if alpha >= beta:
                    break
        input_hash(hsh, DEPTH, alpha, alpha_flag, best_move)
        return best_move
    else:
        for move in check_best_move(hsh, board.generate_legal_moves()):
            board.push(move)  # make move
            score = _min_max(board, alpha, beta)
            board.pop()  # unmake move
            if score < beta:
                beta = score
                best_move = move
                if alpha >= beta:
                    break
        input_hash(hsh, DEPTH, beta, beta_flag, best_move)
        return best_move


def score_min_max(board):
    hsh = board.zobrist_hash()
    alpha, beta = -1000000, 1000000
    best_move = None
    if board.turn == chess.WHITE:
        for move in check_best_move(hsh, board.generate_legal_moves()):
            board.push(move)  # make move
            score = _min_max(board, alpha, beta)
            board.pop()  # unmake move
            if score > alpha:
                alpha = score
                best_move = move
                if alpha >= beta:
                    break
        input_hash(hsh, DEPTH, alpha, alpha_flag, best_move)
        return alpha
    else:
        for move in check_best_move(hsh, board.generate_legal_moves()):
            board.push(move)  # make move
            score = _min_max(board, alpha, beta)
            board.pop()  # unmake move
            if score < beta:
                beta = score
                best_move = move
                if alpha >= beta:
                    break
        input_hash(hsh, DEPTH, beta, beta_flag, best_move)
        return beta


def _min_max(board, alpha, beta, depth=DEPTH-1):
    hsh = board.zobrist_hash()
    score = search_hash(depth, alpha, beta, hsh)
    best_move = None
    if score:
        return score
    if board.is_game_over() or depth == 0:
        score = evaluate(board)
        input_hash(hsh, depth, score, exact_flag)
        return score
    else:
        if board.turn == chess.WHITE:
            for move in check_best_move(hsh, board.generate_legal_moves()):
                board.push(move)  # make move
                score = _min_max(board, alpha, beta, depth-1)
                board.pop()  # unmake move
                if score > alpha:
                    alpha = score
                    best_move = move
                    if alpha >= beta:
                        break
            input_hash(hsh, depth, alpha, alpha_flag, best_move)
            return alpha
        else:
            for move in check_best_move(hsh, board.generate_legal_moves()):
                board.push(move)  # make move
                score = _min_max(board, alpha, beta, depth-1)
                board.pop()  # unmake move
                if score < beta:
                    beta = score
                    best_move = move
                    if alpha >= beta:
                        break
            input_hash(hsh, depth, beta, beta_flag, best_move)
            return beta


def ai_min_max(board, competence):
    hsh = board.zobrist_hash()
    alpha, beta = -1000000, 1000000
    best_move = None
    for move in check_best_move(hsh, board.generate_legal_moves()):
        board.push(move)  # make move
        score = _ai_min_max(board, alpha, beta, competence)
        board.pop()  # unmake move
        if score < beta:
            beta = score
            best_move = move
    return best_move


def score_ai_min_max(board, competence):
    hsh = board.zobrist_hash()
    alpha, beta = -1000000, 1000000
    for move in check_best_move(hsh, board.generate_legal_moves()):
        board.push(move)  # make move
        score = _ai_min_max(board, alpha, beta, competence)
        board.pop()  # unmake move
        if score < beta:
            beta = score
    return beta


def _ai_min_max(board, alpha, beta, competence, depth=DEPTH-1):
    hsh = board.zobrist_hash()
    score = search_hash(depth, alpha, beta, hsh)
    if score:
        return score
    if board.is_game_over() or depth == 0:
        score = evaluate(board)
        input_hash(hsh, depth, score, exact_flag)
        return score
    else:
        if board.turn == chess.WHITE:
            best_moves_and_alphas = []
            for move in check_best_move(hsh, board.generate_legal_moves()):
                board.push(move)  # make move
                score = _ai_min_max(board, alpha, beta, competence, depth-1)
                board.pop()  # unmake move
                if score > alpha:
                    alpha = score
                    best_moves_and_alphas.append((move, alpha))
                    if alpha >= beta:
                        break
            if not best_moves_and_alphas:
                input_hash(hsh, depth, alpha, alpha_flag, None)
                return alpha
            best_move_and_alpha = best_moves_and_alphas[
                int(round((len(best_moves_and_alphas)-1) * competence))]
            input_hash(hsh, depth, best_move_and_alpha[1], alpha_flag, best_move_and_alpha[0])
            return best_move_and_alpha[1]

        else:
            best_move = None
            for move in check_best_move(hsh, board.generate_legal_moves()):
                board.push(move)  # make move
                score = _ai_min_max(board, alpha, beta, competence, depth-1)
                board.pop()  # unmake move
                if score < beta:
                    beta = score
                    if alpha >= beta:
                        break
            input_hash(hsh, depth, beta, beta_flag, best_move)
            return beta
'''
b = chess.Board()
b.push(chess.Move.from_uci("a2a3"))
b.push(chess.Move.from_uci("a7a6"))
b.push(chess.Move.from_uci("e2e3"))
b.push(chess.Move.from_uci("b2b4"))
b.push(chess.Move.from_uci("b1c3"))
b.push(chess.Move.from_uci("b8c6"))
b.push()
print(b)
print(ai_min_max(b, .7))
print(min_max(b))
'''