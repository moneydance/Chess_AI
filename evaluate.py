import chess
from piece_tables import *

OFFSET_WHITE = 0
OFFSET_BLACK = 8

bishop_count = [0, 0]
pawn_columns = [0] * 16


def action_value(piece_type):
    """
    computes action value for piece_type
    """
    if piece_type == chess.PAWN:
        return Pa
    elif piece_type == chess.BISHOP or piece_type == chess.KNIGHT:
        return BNa
    elif piece_type == chess.ROOK:
        return Ra
    else:
        return QKa


def p_val_b(piece, square, board, end_game):
    global bishop_count
    global pawn_columns
    value, a_value, d_value = 0, 0, 0
    index, pawn_columns_offset, bishop_index = square, OFFSET_BLACK, 1
    # score for defending and attacking pieces
    # find attacking pieces
    attacker_positions = board.attackers(chess.WHITE, square)
    # find defensive pieces
    defender_positions = board.attackers(chess.BLACK, square)
    for position in attacker_positions:
        a_value += action_value(board.piece_type_at(position))
    # score defensive pieces based on corresponding action value
    for position in defender_positions:
        d_value += action_value(board.piece_type_at(position))
    # find the action value of the position
    actn_value = d_value - a_value
    value += actn_value
    if actn_value < 0:  # double penalty for hanging pieces ie. more attacking
        value += actn_value * 5
    # score for pieces and piece positions
    if piece.piece_type == chess.PAWN:
        r = chess.rank_index(square)
        value += (P + pawn_table[index])
        # add or subtract weights for pawn position:
        # pawns on sides lose 15% of value
        if square % 8 == 0 or square % 8 == 7:
            value -= 15
        # 2 pawns on same file lose value
        if pawn_columns[(square % 8) + pawn_columns_offset] > 0:
            value -= 16
        if r == 3:  # pawns that are moved forward potentially gain value
            if a_value == 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 100
            elif d_value != 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 25
        elif r == 2:  # same as above
            if a_value == 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 200
            elif d_value != 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 50
        pawn_columns[(square % 8) + pawn_columns_offset] += 10
    elif piece.piece_type == chess.KNIGHT:
        value += (N + knight_table[index])
        if end_game:
            value -= 10  # Knights are strong mid-game and weak endgame
    elif piece.piece_type == chess.BISHOP:
        bishop_count[bishop_index] += 1
        value += (B + bishop_table[index])
        if bishop_count[bishop_index] >= 2:
            value += 10  # having 2 bishops is good for board control
        elif end_game:
            value += 10  # bishops are more valuable in the end game
    elif piece.piece_type == chess.ROOK:
        value += (R + rook_table[index])
    elif piece.piece_type == chess.QUEEN:
        value += (Q + queen_table[index])
    else:
        if not end_game:
            value += (K + king_table_early[index])
        else:
            value += (K + king_table_late[index])
    return value


def p_val_w(piece, square, board, end_game):
    value, a_value, d_value = 0, 0, 0
    index, pawn_columns_offset, bishop_index = 63 - square, OFFSET_WHITE, 0
    # score for defending and attacking pieces
    # find attacking pieces
    attacker_positions = board.attackers(chess.BLACK, square)
    # find defensive pieces
    defender_positions = board.attackers(chess.WHITE, square)
    # score attacking pieces based on corresponding action value
    for position in attacker_positions:
        a_value += action_value(board.piece_type_at(position))
    # score defensive pieces based on corresponding action value
    for position in defender_positions:
        d_value += action_value(board.piece_type_at(position))
    # find the action value of the position
    actn_value = d_value - a_value
    value += actn_value
    if actn_value < 0:  # double penalty for hanging pieces ie. more attacking
        value += actn_value * 5
    # score for pieces and piece positions
    if piece.piece_type == chess.PAWN:
        r = chess.rank_index(square)
        value += (P + pawn_table[index])
        # set bools for pawn positioning
        # add or subtract weights for bools:
        # pawns on sides lose 15% of value
        if square % 8 == 0 or square % 8 == 7:
            value -= 15
        # 2 pawns on same file lose value
        if pawn_columns[(square % 8) + pawn_columns_offset] > 0:
            value -= 16
        if r == 6:  # pawns that are moved forward potentially gain value
            if a_value == 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 100
            elif d_value != 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 25
        elif r == 7:  # same as above
            if a_value == 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 200
            elif d_value != 0:
                pawn_columns[(square % 8) + pawn_columns_offset] += 50
        pawn_columns[(square % 8) + pawn_columns_offset] += 10
    elif piece.piece_type == chess.KNIGHT:
        value += (N + knight_table[index])
        if end_game:
            value -= 10  # Knights are strong mid-game and weak endgame
    elif piece.piece_type == chess.BISHOP:
        bishop_count[bishop_index] += 1
        value += (B + bishop_table[index])
        if bishop_count[bishop_index] >= 2:
            value += 10  # having 2 bishops is good for board control
        elif end_game:
            value += 10  # bishops are more valuable in the end game
    elif piece.piece_type == chess.ROOK:
        value += (R + rook_table[index])
    elif piece.piece_type == chess.QUEEN:
        value += (Q + queen_table[index])
    else:
        if not end_game:
            value += (K + king_table_early[index])
        else:
            value += (K + king_table_late[index])
    return value


def evaluate(board):
    """
    return score of the board
    """
    if board.can_claim_draw() or board.is_insufficient_material():
        return 0
    score = 0
    global bishop_count
    global pawn_columns
    bishop_count = [0, 0]
    pawn_columns = [0] * 16
    end_game = board.pieces_len <= 10
    castling_w = bool(board.castling_rights & chess.CASTLING_WHITE)
    castling_b = bool(board.castling_rights & chess.CASTLING_BLACK)
    if castling_w:   # encourages ai to keep castling as an option
        score += 50
    if castling_b:
        score -= 50
    if board.castled[0]:  # encourages ai to castle when can
        score += 75
    if board.castled[1]:
        score -= 75
    if not castling_w and not board.castled[0]:
        score -= 100
    if not castling_b and not board.castled[1]:
        score += 100
    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 75
            if end_game:
                score -= 10
        else:
            score += 75
            if end_game:
                score += 75
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            score -= 20000
        else:
            score += 20000
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += p_val_w(piece, square, board, end_game)
            else:
                score -= p_val_b(piece, square, board, end_game)
    return score