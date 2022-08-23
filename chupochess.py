import abc
from typing import List, Tuple
from enum import Enum

from helpers import pieceFenToChar

class PieceColor(Enum):
    WHITE = 0
    BLACK = 1
    def Not(self):
        if self == self.WHITE:
            return PieceColor.BLACK
        else:
            return PieceColor.WHITE

class FEN:
    """ https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation """
    def __init__(self) -> None:
        self.piecePlacement = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        self.activeColor = 'w'
        self.castlingAvailability = 'KQkq'
        self.enPassantTarget = '-'
        self.halfmoveClock = 0
        self.fullMoveNumber = 1

    def __str__(self) -> str:
        return self.piecePlacement + ' ' + self.activeColor + ' ' + self.castlingAvailability + \
            ' ' + self.castlingAvailability + ' ' + self.enPassantTarget + ' ' + str(self.halfmoveClock) + \
            ' ' + str(self.fullMoveNumber)

class Piece:
    def __init__(self, color: PieceColor) -> None:
        self.color = color
        self.identifier = ''
    def __str__(self) -> str:
        if self.color == PieceColor.WHITE:
            return self.identifier.upper()
        else:
            return self.identifier.lower()

class King(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 0
        self.identifier = 'K'

class Queen(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 9
        self.identifier = 'Q'

class Rook(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 5
        self.identifier = 'R'

class Bishop(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 3
        self.identifier = 'B'

class Knight(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 3
        self.identifier = 'N'

class Pawn(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color)
        self.value = 1
        self.identifier = 'P'

class Square:
    def __init__(self, id: int) -> None:
        self.id = id
        self.location = Location(id)
        self.isOccupied = False
        self.currentPiece = None

    def reset(self) -> object:
        piece = self.currentPiece
        self.isOccupied = False
        self.currentPiece = None
        return piece

    def set(self, piece: Piece) -> None:
        self.isOccupied = True
        self.currentPiece = piece


class Board:
    def __init__(self) -> None:
        self.FEN = FEN()
        self.squares = {}
        self.whitePieces = []
        self.blackPieces = []
        self.locationSquareMap = LocationDictionary()
        pieces = PieceFactory.getPieces(self.FEN)
        for i in range(64):
            self.squares[i] = Square(i)
            if self.squares[i].location in pieces:
                self.squares[i].set(pieces[self.squares[i].location])
                if self.squares[i].currentPiece.color == PieceColor.WHITE:
                    self.whitePieces.append(self.squares[i].currentPiece)
                else:
                    self.blackPieces.append(self.squares[i].currentPiece)
            self.locationSquareMap[self.squares[i].location] = self.squares[i]

    def getOutput(self) -> dict:
        output = {}
        for i in range(64):
            piece = self.squares[i].currentPiece
            if piece:
                output[i] = str(piece)
            else:
                output[i] = ''
        return output

class Location:
    def __init__(self, absolute: int) -> None:
        self.absolute = absolute
        self.tuple = Location.absoluteSqToTuple(absolute)
        self.algebraic = Location.tupleToAlgebraicSq(self.tuple)

    @classmethod
    def fromTuple(cls, tpl: Tuple[int, int]):
        return cls(Location.tupleToAbsoluteSq(tpl))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Location):
            return self.tuple == __o.tuple
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.tuple)

    def __str__(self) -> str:
        return self.algebraic

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


class PieceFactory:
    switcher = {
        'p' : Pawn,
        'b' : Bishop,
        'n' : Knight,
        'r' : Rook,
        'q' : Queen,
        'k' : King
    }

    def getPieces(fen: FEN) -> LocationDictionary:
        pieces = LocationDictionary()
        location = 0
        for c in fen.piecePlacement:
            if c.isnumeric():
                location += int(c)
            elif c != '/':
                color = PieceColor.WHITE if c.isupper() else PieceColor.BLACK
                cls = PieceFactory.switcher.get(c.lower())
                pieces[Location(location)] = cls(color)
                location += 1
        return pieces
            


