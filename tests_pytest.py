# can be executed via 'pytest tests_pytest.py' from the root dir.
# good read: https://realpython.com/pytest-python-testing/

import pytest
from chupochess import Board, Location, TrainingHelper, GameState
import chupochess_pb2

#### Fixtures #####

@pytest.fixture
def startingPosition():
    return Board.startingPosition()


#### End of Fixtures #####



#### Tests #####

def test_protobuf():
    board1 = Board.startingPosition()
    board2 = Board.fromBytes(board1.toBytes())
    for i in range(64):
        assert board1.squares[i] == board2.squares[i]


@pytest.mark.parametrize("ext_fen, expected_stat", [
    ('1B6/6P1/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R w - - 1 40 0', 25),
    ('n1br4/6Q1/2Nq4/5p2/3P1k2/8/P1P3pP/Rq2K3 w - - 0 32 0', -10),
    ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 0', 0),
])
def test_board_stat(ext_fen, expected_stat):
    board = Board.fromString(ext_fen)
    assert board.stat == expected_stat

@pytest.mark.parametrize("ext_fen, expected_stat", [
    ('1B6/6P1/4Nk2/8/2p5/8/PPP1P1PP/2KR1B1R w - - 1 40 0', 25),
    ('n1br4/6Q1/2Nq4/5p2/3P1k2/8/P1P3pP/Rq2K3 w - - 0 32 0', -10),
    ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 0', 0),
])
def test_TrainingHelper_fenToStat(ext_fen, expected_stat):
    assert TrainingHelper.fenToStat(ext_fen) == expected_stat

@pytest.mark.parametrize("ext_fen, source, expected_result", [
    ('4k3/4B3/8/b3r3/8/2R5/4N3/r1Q1KP1q w - - 0 1 0', 42, True),
    ('4k3/4B3/8/b3r3/8/2R5/4N3/r1Q1KP1q w - - 0 1 0', 52, True),
    ('4k3/4B3/8/b3r3/8/2R5/4N3/r1Q1KP1q w - - 0 1 0', 58, True),
    ('4k3/4B3/8/b3r3/8/2R5/4N3/r1Q1KP1q w - - 0 1 0', 61, True),
    ('4k3/4B3/8/b3r3/8/2R5/4N3/r1Q1KP1q w - - 0 1 0', 12, False),
    ('8/8/6B1/8/4p3/3k4/8/4K3 w - - 0 1 0', 36, True),
    ('8/8/8/8/3k4/4p3/8/4K1B1 w - - 0 1 0', 44, True),
    ('7k/8/8/4r3/8/8/8/Q4K2 w - - 0 1 0', 28, True),
    ('8/8/8/5p2/3P1k2/8/p5p1/Rq2K1N1 w - - 0 1 0', 56, False)
])
def test_Piece_isPinned(ext_fen, source, expected_result):
    board = Board.fromString(ext_fen)
    assert board.squares[source].currentPiece._isPinned(board) == expected_result


@pytest.mark.parametrize("ext_fen, source, target, expected_state", [
    ('8/8/8/8/3q4/5k2/8/4K3 b - - 0 1 0', 35, 43, GameState.DRAW),
    ('8/8/8/8/3q4/5k2/8/4K3 b - - 0 1 0', 35, 44, GameState.IDLE),
    ('8/8/8/3r4/8/5k2/3p4/2NK4 b - - 0 1 0', 51, 58, GameState.IDLE),
    ('8/8/5k2/8/8/8/4r3/3K4 w - - 0 1 0', 59, 52, GameState.DRAW),
    ('8/8/5k2/8/8/1N6/4r3/3K4 w - - 0 1 0', 59, 52, GameState.DRAW),
    ('rnbqkbnr/p1p2ppp/3p4/1p2p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1 0', 45, 13, GameState.WHITE_WINS),
    ('Q7/8/8/5K1k/8/8/8/8 w - - 0 1 0', 0, 63, GameState.WHITE_WINS),
    ('3b4/8/8/4k3/4p3/3pK3/6r1/8 b - - 0 1 0', 3, 30, GameState.BLACK_WINS),
    ('4r3/8/7k/7b/6n1/2q5/8/3K4 b - - 0 1 0', 38, 53, GameState.BLACK_WINS)  
])
def test_board_gameState(ext_fen, source, target, expected_state):
    board = Board.fromString(ext_fen)
    board.makeMove(source, target, True)
    assert board.gameState == expected_state


@pytest.mark.parametrize("ext_fen, location, expected_len", [
    ('8/8/8/8/8/3q1k2/8/4K3 w - - 0 1 0', 60, 0),
    ('8/8/8/8/8/5k2/4q3/4K3 w - - 0 1 0', 60, 0),
])
def test_king_validMoves(ext_fen, location, expected_len):
    board = Board.fromString(ext_fen)
    assert len(board.getMoves(location, True)) == expected_len


@pytest.mark.parametrize("rank, expected_locations", [
    (1, [56, 57, 58, 59, 60, 61, 62, 63]),
    (2, [48, 49, 50, 51, 52, 53, 54, 55]),
    (3, [40, 41, 42, 43, 44, 45, 46, 47]),
    (8, [0, 1, 2, 3, 4, 5, 6, 7])
])
def test_locationsOnRank(rank, expected_locations):
    assert Location.getLocationsOnRank(rank) == expected_locations


@pytest.mark.parametrize("pgn, expected_len, expected_last_fen", [
    ('[Event "IBM Kasparov vs. Deep Blue Rematch"][Site "New York, NY USA"][Date "1997.05.11"][Round "6"][White "Deep Blue"][Black "Kasparov, Garry"][Opening "Caro-Kann: 4...Nd7"][ECO "B17"][Result "1-0"] 1.e4 c6 2.d4 d5 3.Nc3 dxe4 4.Nxe4 Nd7 5.Ng5 Ngf6 6.Bd3 e6 7.N1f3 h6 8.Nxe6 Qe7 9.O-O fxe6 10.Bg6+ Kd8 {Kasparov schüttelt kurz den Kopf} 11.Bf4 b5 12.a4 Bb7 13.Re1 Nd5 14.Bg3 Kc8 15.axb5 cxb5 16.Qd3 Bc6 17.Bf5 exf5 18.Rxe7 Bxe7 19.c4 1-0', 38, 'r1k4r/p2nb1p1/2b4p/1p1n1p2/2PP4/3Q1NB1/1P3PPP/R5K1 b - c3 0 19'),
    ('[Event "Varna ol (Men) fin-A"][Site "Varna"][Date "1962.??.??"][Round "10"][White "Botvinnik, Mikhail"][Black "Fischer, Robert James"[Result "1/2-1/2"][ECO "D98"][PlyCount "135"][EventDate "1962.09.16"][EventType "team"][EventRounds "11"][EventCountry "BUL"][Source "ChessBase"][SourceDate "1999.07.01"][WhiteTeam "Soviet Union"][BlackTeam "US of America"][WhiteTeamCountry "URS"][BlackTeamCountry "USA"]1. c4 g6 2. d4 Nf6 3. Nc3 d5 4. Nf3 Bg7 5. Qb3 dxc4 6. Qxc4 O-O 7. e4 Bg4 8.Be3 Nfd7 9. Be2 Nc6 10. Rd1 Nb6 11. Qc5 Qd6 12. h3 Bxf3 13. gxf3 Rfd8 14. d5 Ne5 15. Nb5 Qf6 16. f4 Ned7 17. e5 Qxf4 18. Bxf4 Nxc5 19. Nxc7 Rac8 20. d6 exd6 21. exd6 Bxb2 22. O-O Nbd7 23. Rd5 b6 24. Bf3 Ne6 25. Nxe6 fxe6 26. Rd3 Nc5 27.Re3 e5 28. Bxe5 Bxe5 29. Rxe5 Rxd6 30. Re7 Rd7 31. Rxd7 Nxd7 32. Bg4 Rc7 33.Re1 Kf7 34. Kg2 Nc5 35. Re3 Re7 36. Rf3+ Kg7 37. Rc3 Re4 38. Bd1 Rd4 39. Bc2 Kf6 40. Kf3 Kg5 41. Kg3 Ne4+ 42. Bxe4 Rxe4 43. Ra3 Re7 44. Rf3 Rc7 45. a4 Rc5 46. Rf7 Ra5 47. Rxh7 Rxa4 48. h4+ Kf5 49. Rf7+ Ke5 50. Rg7 Ra1 51. Kf3 b5 52.h5 Ra3+ 53. Kg2 gxh5 54. Rg5+ Kd6 55. Rxb5 h4 56. f4 Kc6 57. Rb8 h3+ 58. Kh2 a5 59. f5 Kc7 60. Rb5 Kd6 61. f6 Ke6 62. Rb6+ Kf7 63. Ra6 Kg6 64. Rc6 a4 65. Ra6 Kf7 66. Rc6 Rd3 67. Ra6 a3 68. Kg1 1/2-1/2', 136, '8/5k2/R4P2/8/8/p2r3p/8/6K1 b - - 1 68'),
    ('[Event "Ischia ITA"][Site "Ischia 64/548"][Date "????.??.??"][Round "0"][White "Naumkin, Igor"][Black "Smirin, Ilia"][Result "0-1"][ECO "E90"][Opening "Kings Indian: 5.Nf3"]1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 Na6 7. O-O e5 8. d5 Nc5 9. Qc2 a5 10. Bg5 h6 11. Be3 b6 12. Nd2 Bg4 13. f3 Bd7 14. b3 Nh5 15. Rfe1 Bf6 16. Bxh6 Bg5 17. Bxg5 Qxg5 18. Nf1 f5 19. exf5 gxf5 20. a3 a4 21. b4 Nb3 22. Ra2 Rf7 23. g3 Kh8 24. Bd1 Rg8 25. Qb1 Qh4 26. Bxb3 axb3 27. Rg2 Qd4+ 28. Re3 f4 29. Ne2 Qxc4 30. gxf4 Rxg2+ 31. Kxg2 exf4 32. Re4 Qxd5 33. Kf2 Qg5 34. Ke1 Nf6 35. Qb2 Kg8 36. Rxf4 Bb5 37. Nfg3 Bxe2 38. Nxe2 Re7 39. Qxb3+ Kg7 40. Rc4 Qg1+ 41. Kd2 Qxh2 42. Qd3 c5 43. Rc1 Kf7 44. bxc5 bxc5 45. a4 Re5 46. Qb5 Qf2 47. Rc3 d5 {#R} 0-1', 95, '8/5k2/5n2/1Qppr3/P7/2R2P2/3KNq2/8 w - - 0 48')
])
def test_TrainingHelper_pgnToFen(pgn, expected_len, expected_last_fen):
    """ source example PGN's: https://www.chess.com/library """
    fenlist = TrainingHelper.pgnToFen(pgn)
    assert len(fenlist) == expected_len
    assert fenlist[-1] == expected_last_fen

@pytest.mark.parametrize("file, expected_locations", [
    ('a', [0, 8, 16, 24, 32, 40, 48, 56]),
    ('b', [1, 9, 17, 25, 33, 41, 49, 57]),
    ('g', [6, 14, 22, 30, 38, 46, 54, 62]),
    ('h', [7, 15, 23, 31, 39, 47, 55, 63])
])
def test_locationsOnFile(file, expected_locations):
    assert Location.getLocationsOnFile(file) == expected_locations


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