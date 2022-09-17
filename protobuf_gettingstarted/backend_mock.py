import communication_pb2
from enum import Enum
from cs50 import SQL

db = SQL("sqlite:///protobuf_gettingstarted/database.db")

class PieceColor(Enum):
    WHITE = 0
    BLACK = 1

    def serialize(self) -> communication_pb2.PieceColor:
        return self.value

    @classmethod
    def deserialize(cls, proto: communication_pb2.PieceColor):
        return cls(proto)

class Board:
    def __init__(self, squares: dict = None) -> None:
        self.squares = {}
        if squares == None:
            for i in range(64):
                self.squares[i] = Square(i)
        else:
            for key in squares.keys():
                self.squares[key] = Square.deserialize(squares[key])


    def __str__(self) -> str:
        s = "Board {squares: [" 
        for i in range(64):
            s += str(i) + ': ' + str(self.squares[i]) + ", "
        s = s[:-2] + "]}"
        return s

    def serialize(self) -> communication_pb2.Board:
        proto = communication_pb2.Board()
        for key in self.squares.keys():
            proto.squares[key].CopyFrom(self.squares[key].serialize())
        return proto

    @classmethod
    def deserialize(cls, proto: communication_pb2.Board):
        return cls(proto.squares)


class Piece:
    def __init__(self, color: PieceColor = PieceColor.BLACK, identifier: str = 't', value: int = 2, location: int = 63) -> None:
        self.color = color
        self.identifier = identifier
        self.value = value
        self.location = location
    
    def serialize(self) -> communication_pb2.Piece:
        proto = communication_pb2.Piece()
        proto.color = self.color.serialize()
        proto.identifier = self.identifier
        proto.value = self.value
        proto.location = self.location
        return proto

    @classmethod
    def deserialize(cls, proto: communication_pb2.Piece):
        return cls(PieceColor.deserialize(proto.color), proto.identifier, proto.value, proto.location)

    def __str__(self) -> str:
        return "Piece {color : " + str(self.color) + ", identifier : " + str(self.identifier) + ", value : " + str(self.value) + ", location : " + str(self.location) + "}"

class Square:
    def __init__(self, id: int = 23, isOccupied: bool = False, currentPiece: Piece = None) -> None:
        self.id = id
        self.isOccupied = isOccupied
        self.currentPiece = currentPiece

    def serialize(self) -> communication_pb2.Square:
        proto = communication_pb2.Square()
        proto.id = self.id
        if self.isOccupied:
            proto.currentPiece.CopyFrom(self.currentPiece.serialize())
        proto.isOccupied = self.isOccupied
        return proto
    
    @classmethod
    def deserialize(cls, proto: communication_pb2.Square):
        if proto.isOccupied:
            return cls(proto.id, proto.isOccupied, Piece.deserialize(proto.currentPiece))
        else: 
            return cls(proto.id, proto.isOccupied, None)

    def __str__(self) -> str:
        return "Square {id : " + str(self.id) + ", isOccupied : " + str(self.isOccupied) + ", currentPiece : " + str(self.currentPiece) + "}"


## WRITE/SERIALIZE: ###
board = Board()

print(board.squares[12])

square = Square()
piece = Piece()
square.currentPiece = piece
square.isOccupied = True
board.squares[12] = square

print(board.squares[12])

dbId = db.execute("INSERT INTO binary_storage (board_protobuf) VALUES (?);", board.serialize().SerializeToString())

## READ/DESERIALIZE: ###
database_mock = communication_pb2.Board()
response = db.execute("SELECT board_protobuf FROM binary_storage WHERE id = ?;", dbId)[0]['board_protobuf']
database_mock.ParseFromString(response)


# deserialize protobuf class to "real" class object:
read_board = Board.deserialize(database_mock)

print(read_board.squares[12])


