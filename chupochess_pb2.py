# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chupochess.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x63hupochess.proto\"I\n\x05Piece\x12\x1a\n\x05\x63olor\x18\x01 \x01(\x0e\x32\x0b.PieceColor\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\x10\n\x08location\x18\x03 \x01(\x05\"F\n\x06Square\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x12\n\nisOccupied\x18\x02 \x01(\x08\x12\x1c\n\x0c\x63urrentPiece\x18\x03 \x01(\x0b\x32\x06.Piece\"\xc1\x03\n\x05\x42oard\x12\x0b\n\x03\x66\x65n\x18\x01 \x01(\t\x12\x15\n\runmakeCounter\x18\x02 \x01(\x05\x12,\n\x0bwhitePieces\x18\x03 \x03(\x0b\x32\x17.Board.WhitePiecesEntry\x12,\n\x0b\x62lackPieces\x18\x04 \x03(\x0b\x32\x17.Board.BlackPiecesEntry\x12\x19\n\x11whiteKingLocation\x18\x05 \x01(\x05\x12\x19\n\x11\x62lackKingLocation\x18\x06 \x01(\x05\x12\x0c\n\x04stat\x18\x07 \x01(\x05\x12$\n\x07squares\x18\x08 \x03(\x0b\x32\x13.Board.SquaresEntry\x12\x1d\n\tgameState\x18\t \x01(\x0e\x32\n.GameState\x1a:\n\x10WhitePiecesEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\x15\n\x05value\x18\x02 \x01(\x0b\x32\x06.Piece:\x02\x38\x01\x1a:\n\x10\x42lackPiecesEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\x15\n\x05value\x18\x02 \x01(\x0b\x32\x06.Piece:\x02\x38\x01\x1a\x37\n\x0cSquaresEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\x16\n\x05value\x18\x02 \x01(\x0b\x32\x07.Square:\x02\x38\x01*<\n\nPieceColor\x12\x18\n\x14UNDEFINED_PIECECOLOR\x10\x00\x12\t\n\x05WHITE\x10\x01\x12\t\n\x05\x42LACK\x10\x02*X\n\tGameState\x12\x17\n\x13UNDEFINED_GAMESTATE\x10\x00\x12\x08\n\x04IDLE\x10\x01\x12\x08\n\x04\x44RAW\x10\x02\x12\x0e\n\nWHITE_WINS\x10\x03\x12\x0e\n\nBLACK_WINS\x10\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chupochess_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _BOARD_WHITEPIECESENTRY._options = None
  _BOARD_WHITEPIECESENTRY._serialized_options = b'8\001'
  _BOARD_BLACKPIECESENTRY._options = None
  _BOARD_BLACKPIECESENTRY._serialized_options = b'8\001'
  _BOARD_SQUARESENTRY._options = None
  _BOARD_SQUARESENTRY._serialized_options = b'8\001'
  _PIECECOLOR._serialized_start=619
  _PIECECOLOR._serialized_end=679
  _GAMESTATE._serialized_start=681
  _GAMESTATE._serialized_end=769
  _PIECE._serialized_start=20
  _PIECE._serialized_end=93
  _SQUARE._serialized_start=95
  _SQUARE._serialized_end=165
  _BOARD._serialized_start=168
  _BOARD._serialized_end=617
  _BOARD_WHITEPIECESENTRY._serialized_start=442
  _BOARD_WHITEPIECESENTRY._serialized_end=500
  _BOARD_BLACKPIECESENTRY._serialized_start=502
  _BOARD_BLACKPIECESENTRY._serialized_end=560
  _BOARD_SQUARESENTRY._serialized_start=562
  _BOARD_SQUARESENTRY._serialized_end=617
# @@protoc_insertion_point(module_scope)
