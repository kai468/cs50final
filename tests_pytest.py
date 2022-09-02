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



@pytest.mark.parametrize("ext_fen, source, target, expected_ext_fen", [
    ('1B6/6P1/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R w - - 1 40 0', 14, 6, '1B4Q1/8/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R b - - 0 40 0'),
    ('1B6/P4kP1/4N3/8/2p5/8/1PP1P1PP/2KR1B1R w - - 1 44 0', 8, 0, 'QB6/5kP1/4N3/8/2p5/8/1PP1P1PP/2KR1B1R b - - 0 44 0'),
])
def test_pawn_promotion(ext_fen, source, target, expected_ext_fen):
    board = Board.fromString(ext_fen)
    board.makeMove(source, target)
    assert str(board) == expected_ext_fen


"""
@pytest.mark.parametrize("extended_fen, expected_result", [
    ('FEN', 55),
    ('fen2', 13),
])
def test_board_stat(extended_fen, expected_result):
    assert Board.fromString(extended_fen).stat == expected_result
"""


def test_without_fixture():
    assert True

def test_startingPos(startingPosition):
    assert str(startingPosition) == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 0'




#### End of Tests #####