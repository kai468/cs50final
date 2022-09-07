# can be executed via 'pytest tests_pytest.py' from the root dir.
# good read: https://realpython.com/pytest-python-testing/

import pytest
from chupochess import Board

#### Fixtures #####

@pytest.fixture
def startingPosition():
    return Board.startingPosition()


#### End of Fixtures #####



#### Tests #####

@pytest.mark.parametrize("ext_fen, expected_stat", [
    ('1B6/6P1/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R w - - 1 40 0', 25),
    ('n1br4/6Q1/2Nq4/5p2/3P1k2/8/P1P3pP/Rq2K3 w - - 0 32 0', -10),
    ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 0', 0),
])
def test_board_stat(ext_fen, expected_stat):
    board = Board.fromString(ext_fen)
    assert board.stat == expected_stat


@pytest.mark.parametrize("ext_fen, source, target, expected_ext_fen", [
    ('1B6/6P1/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R w - - 1 40 0', 14, 6, '1B4Q1/8/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R b - - 0 40 0'),
    ('1B6/P4kP1/4N3/8/2p5/8/1PP1P1PP/2KR1B1R w - - 1 44 0', 8, 0, 'QB6/5kP1/4N3/8/2p5/8/1PP1P1PP/2KR1B1R b - - 0 44 0'),
    ('rn3bnr/1bppPkpp/pp3p2/6B1/3P4/8/PPP3PP/RN1QKBNR w KQ - 1 13 0', 12, 5, 'rn3Qnr/1bpp1kpp/pp3p2/6B1/3P4/8/PPP3PP/RN1QKBNR b KQ - 0 13 0'),
    ('8/6Q1/2N5/5p2/3P1k2/8/PpP1Q1pP/R3KBNR b KQ - 1 31 0', 49, 57, '8/6Q1/2N5/5p2/3P1k2/8/P1P1Q1pP/Rq2KBNR w KQ - 0 32 0'),
    ('8/6Q1/8/5p2/1N1P1k2/8/P1P1Q1pP/Rq2KBNR b KQ - 0 31 0', 54, 63, '8/6Q1/8/5p2/1N1P1k2/8/P1P1Q2P/Rq2KBNq w KQ - 0 32 0'),
])
def test_pawn_promotion(ext_fen, source, target, expected_ext_fen):
    # parametrize includes: 0) and 1): white pawn promotion w/o capture; 2): white pawn promotion with capture;
    #                       3): black pawn promotion w/o capture; 4): black pawn promotion w/o capture
    board = Board.fromString(ext_fen)
    board.makeMove(source, target, True)
    assert str(board) == expected_ext_fen

def test_enpassant_capture():
    board = Board.fromString('rnbqkbnr/1ppppppp/p7/4P3/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2 0')
    board.makeMove(13, 29, True)    # black moves pawn from F7 to F5 
    assert str(board) == 'rnbqkbnr/1pppp1pp/p7/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3 0'
    board.makeMove(28, 21)    # white moves pawn from E5 to F6, en passant capturing black pawn on F5
    assert str(board) == 'rnbqkbnr/1pppp1pp/p4P2/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 3 0'

def test_king_movement():
    board = Board.fromString('r2K2B1/5PB1/8/2pp3k/8/8/8/8 w - - 1 45 0')
    validMoves = board.getMoves(3)
    # only valid move for white king (on D8) should be to C7
    assert len(validMoves) == 3
    assert 10 in validMoves
    assert 11 in validMoves
    assert 12 in validMoves    

def test_locationUnderAttack():
    board = Board.fromString('r2K2B1/5PB1/8/2pp3k/8/8/8/8 w - - 1 45 0')
    king = board.squares[3].currentPiece
    assert king._locationUnderAttack(board, 4) == [0]

def test_without_fixture():
    assert True

def test_startingPos(startingPosition):
    assert str(startingPosition) == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 0'




#### End of Tests #####