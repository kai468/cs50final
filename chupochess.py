from typing import List, Tuple
from enum import Enum

class PieceColor(Enum):
    WHITE = 0
    BLACK = 1
    def Not(self):
        # TODO: refactoring -> is .Not() still required or != comparison sufficient? 
        return PieceColor(not bool(self.value))

class FEN:
    """ https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation """
    def __init__(self, fen: str) -> None:
        inp = fen.split()
        self.piecePlacement = inp[0]
        self.activeColor = inp[1]
        self.castlingAvailability = inp[2]
        self.enPassantTarget = inp[3]
        self.halfmoveClock = inp[4]
        self.fullMoveNumber = inp[5]

    @classmethod
    def startingPosition(cls):
        # FEN for starting position:
        return cls('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    def __str__(self) -> str:
        return self.piecePlacement + ' ' + self.activeColor + ' ' + self.castlingAvailability + \
            ' ' + self.enPassantTarget + ' ' + str(self.halfmoveClock) + \
            ' ' + str(self.fullMoveNumber)

class Board:
    def __init__(self, fen: FEN, unmakeCounter: int) -> None:
        self.fen = fen
        self.squares = {}
        self.unmakeCounter = unmakeCounter
        self.pieces = {}
        self.pieces[PieceColor.WHITE] = []
        self.pieces[PieceColor.BLACK] = []
        pieces = PieceFactory.getPieces(self.fen)
        self.opponent = Chupponnent()
        for loc in range(64):
            self.squares[loc] = Square(loc)
            if loc in pieces:
                self.squares[loc].set(pieces[loc])
                self.pieces[pieces[loc].color].append(pieces[loc])

    @classmethod
    def startingPosition(cls):
        return cls(FEN.startingPosition(), 0)

    @classmethod
    def fromString(cls, string: str):
        # split 'extended FEN' into FEN and unmake counter:
        i = string.rindex(' ')
        return cls(FEN(string[:i]), int(string[i+1:]))

    def __str__(self) -> str:
        # extended FEN: FEN + unmake counter:
        return str(self.fen) + ' ' + str(self.unmakeCounter)

    def getOutput(self) -> dict:
        output = {}
        for i in range(64):
            piece = self.squares[i].currentPiece
            if piece:
                output[i] = str(piece)
            else:
                output[i] = ''
        return output

    def getMoves(self, location: int, chupponnentMove: bool = False) -> List[int]:
        if self.squares[location].isOccupied and self.squares[location].currentPiece.color == PieceColor.WHITE:
            return self.squares[location].currentPiece.getValidMoves(self)
        elif chupponnentMove:    # we trust our chupponnent to just query for occupied squares
            return self.squares[location].currentPiece.getValidMoves(self)
        else:
            return []

    def makeMove(self, source: int, target: int, chupponnentMove: bool = False) -> bool:
        # returns true/false whether move was made successfully
        if target in self.getMoves(source, chupponnentMove):
            self.squares[source].currentPiece.makeMove(self, target)
            # update FEN for successful move:
            # 1) piece placement: 
            self.fen.piecePlacement = ''
            emptySquares = 0 
            for loc in range(64):
                if loc % 8 == 0:
                    if emptySquares != 0 :
                        self.fen.piecePlacement += str(emptySquares)
                        emptySquares = 0
                    self.fen.piecePlacement += '/'
                if not self.squares[loc].isOccupied:
                    emptySquares += 1
                elif emptySquares == 0:
                    self.fen.piecePlacement += str(self.squares[loc].currentPiece)
                else:
                    self.fen.piecePlacement += str(emptySquares)
                    emptySquares = 0
                    self.fen.piecePlacement += str(self.squares[loc].currentPiece)
            # 2) active color: 
            self.fen.activeColor = 'b' if self.fen.activeColor == 'w' else 'w'
            # 3) TODO: castling rights, en passant, half moves
            # move count: 
            if self.fen.activeColor == 'w':
                self.fen.fullMoveNumber = str(int(self.fen.fullMoveNumber) + 1)  # increase full move count after black's move
            return True
        else:
            # not a valid move
            return False

    def removePiece(self, piece: object) -> None:
        if not piece: return
        self.pieces[piece.color].remove(piece)

    def getPGN(self) -> str:
        # TODO
        pass

class Chupponnent:
    def __init__(self) -> None:
        pass

    def makeMove(self, board: Board) -> None:
        # TODO
        # just for getting everything else on track: at the moment, this only selects a random black piece and (also randomly) one
        # of its valid moves and does this move without any intelligence -> this is only a mock up 
        from random import seed, randint
        seed(1)
        moves = []
        cnt = 0
        while len(moves) == 0:
            pieceId = randint(0, len(board.pieces[PieceColor.BLACK]) - 1)
            moves = board.pieces[PieceColor.BLACK][pieceId].getValidMoves(board)
            cnt += 1
            if cnt >= 100:
                break
        if len(moves) > 0: 
            moveId = randint(0, len(moves) - 1)
            piece = board.pieces[PieceColor.BLACK][pieceId]
            board.makeMove(piece.currentSquare.id, moves[moveId], True)


class Piece:
    def __init__(self, color: PieceColor, identifier: str, value: int) -> None:
        self.color = color
        if color == PieceColor.WHITE:
            self.identifier = identifier.upper()
        else: 
            self.identifier = identifier.lower()
        self.value = value
        self.currentSquare = None

    def __str__(self) -> str:
        return self.identifier

    def _switchSquaresAndCapture(self, board: Board, target: int) -> None:
        self.currentSquare.reset()
        self.currentSquare = board.squares[target]
        board.removePiece(board.squares[target].reset())    # make capture if there is sth to capture
        board.squares[target].set(self)

    def makeMove(self, board: Board, target: int):
        # TODO: implement for the remaining pieces
        pass

    def getValidMoves(self, board: Board) -> List[int]:
        # TODO: implement for the remaining pieces
        return []

class King(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'K', 0)

class Queen(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'Q', 9)

class Rook(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'R', 5)

class Bishop(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'B', 3)

class Knight(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'N', 3)

class Pawn(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'P', 1)

    def isFirstMove(self) -> bool:
        if (self.color == PieceColor.WHITE and self.currentSquare.id >= 48 and self.currentSquare.id <= 55) or \
            (self.color == PieceColor.BLACK and self.currentSquare.id >= 8 and self.currentSquare.id <= 15):
            return True
        else:
            return False
    
    def getValidMoves(self, board: Board) -> List[int]:
        moveCandidates = []
        currentLocation = self.currentSquare.id
        if self.color == PieceColor.WHITE:
            offsets = [(0,1),(1,1),(-1,1)]
        else:
            offsets = [(0,-1),(1,-1),(-1,-1)]
        if self.isFirstMove():
            offsets.append((0,2*offsets[0][1]))
        moveCandidates = Location.getLocationsFromOffsets(currentLocation, offsets)
        # TODO: en passant
        return moveCandidates

    def makeMove(self, board: Board, target: int) -> None:
        self._switchSquaresAndCapture(board, target)


class Square:
    def __init__(self, id: int) -> None:
        self.id = id
        self.isOccupied = False
        self.currentPiece = None

    def reset(self) -> object:
        piece = self.currentPiece
        self.isOccupied = False
        self.currentPiece = None
        if piece:
            piece.currentSquare = None
        return piece

    def set(self, piece: Piece) -> None:
        self.isOccupied = True
        self.currentPiece = piece
        piece.currentSquare = self


class Location:
    def __init__(self) -> None:
        pass

    """ 
    There will be three different notations for identifying a square on the chess board:
        > the human-friendly notation, e.g. "A8" or "C6" -> it is also used for the algebraic notation and PGN so let's call it "algebraic"
        > the tuple notation with two 0-based indices for rank and file, e.g. (0,7) or (2,5) (=A8/C6)
        > the absolute notation, giving each square a value between 0 and 63 (starting with 0 for A8, completing the current
        rank until 7 for H8, then switching to the next rank, and so on, until 63 for H1) -> e.g. 0 or 18 (=A8/C6)
        (it would maybe be more intuitive to start with 0 for A1 - however, the chosen concept maps really good to the FEN notation)
    Hint: exclusively lower case letters are used for the algebraic notation (in accordance with PGN state-of-the-art)
    Hint: (another design decision): It is noted that the attributes of this class have redundant information since it's always the same
        position in a different notation - however, since locations themselves won't change during the game, this slows down the initialisation
        insignificantly but has to be done only once and therefore has the potential to speed up the execution during the game compared to
        a strict on-demand calculation of the differing notations
    """
    def absoluteSqToTuple(absoluteSq: int) -> Tuple[int, int]:
        """ absolute to tuple notation, e.g. 7 -> (7,7); 36 -> (4,3) """
        return (absoluteSq % 8, 7 - int(absoluteSq / 8))

    def tupleToAlgebraicSq(tpl: Tuple[int, int]) -> str:
        """ tuple to algebraic notation, e.g. (7,7) -> 'h8'; (4,3) -> 'e4' """
        return chr(tpl[0] + 97) + str(tpl[1] + 1)

    def algebraicSqToAbsoluteSq(algebraicSq: str) -> int:
        """ algebraic to absolute notation, e.g. 'h8' -> 7; 'e4' -> 36 """
        return (ord(algebraicSq[0]) - 97) + ((8 - int(algebraicSq[1])) * 8)

    def tupleToAbsoluteSq(tpl: Tuple[int, int]) -> int:
        """ tuple to absolute notation, e.g. (7,7) -> 7; (4,3) -> 36 """
        return tpl[0] + (7 - tpl[1]) * 8

    def getLocationsFromOffsets(current: int, offsets: List[Tuple[int,int]]) -> List[int]:
        locations = []
        currentTpl = Location.absoluteSqToTuple(current)
        for offset in offsets:
            file = currentTpl[0] + offset[0]
            rank = currentTpl[1] + offset[1]
            if file >= 0 and file <= 7 and rank >= 0 and rank <= 7:
                # valid new location -> add to list:
                locations.append(Location.tupleToAbsoluteSq((file, rank)))
        return locations


"""
class LocationDictionary(dict):
    def __contains__(self, __o: Location) -> bool:
        # must be overwritten to make 'in' operator work for Location comparison
        for key in self.keys():
            if key == __o: 
                return True
        return False

    def __getitem__(self, __k: Location) -> object:
        # must be overwritten to make getting an item via dict[key] possible
        for key in self.keys():
            if key == __k:
                return super().__getitem__(key)
"""


class PieceFactory:
    switcher = {
        'p' : Pawn,
        'b' : Bishop,
        'n' : Knight,
        'r' : Rook,
        'q' : Queen,
        'k' : King
    }

    def getPieces(fen: FEN) -> dict:
        pieces = {}
        location = 0
        for c in fen.piecePlacement:
            if c.isnumeric():
                location += int(c)
            elif c != '/':
                color = PieceColor.WHITE if c.isupper() else PieceColor.BLACK
                cls = PieceFactory.switcher.get(c.lower())
                pieces[location] = cls(color)
                location += 1
        return pieces
            


