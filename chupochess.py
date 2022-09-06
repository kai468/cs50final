from itertools import filterfalse
from typing import List, Tuple
from enum import Enum
from typing_extensions import Self

class PieceColor(Enum):
    WHITE = 0
    BLACK = 1

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
        self.kingLocation = {}
        pieces = PieceFactory.getPieces(self.fen)
        self.opponent = Chupponnent()
        self.stat = 0
        for loc in range(64):
            self.squares[loc] = Square(loc)
            if loc in pieces:
                self.squares[loc].set(pieces[loc])
                self.pieces[pieces[loc].color].append(pieces[loc])
                if pieces[loc].identifier.upper() == 'K':
                    self.kingLocation[pieces[loc].color] = loc
                self.stat = self.stat + pieces[loc].value if pieces[loc].color == PieceColor.WHITE else self.stat - pieces[loc].value

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
            # update halfmove clock: 
            if self.squares[target].isOccupied or self.squares[source].currentPiece.identifier.upper() == 'P':
                self.fen.halfmoveClock = '0'
            else:
                self.fen.halfmoveClock = str(int(self.fen.halfmoveClock) + 1)
            self.squares[source].currentPiece.makeMove(self, target)
            # update FEN for successful move:
            # 1) piece placement: 
            self.fen.piecePlacement = ''
            emptySquares = 0 
            for loc in range(64):
                if loc % 8 == 0 and loc > 0 :
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
            # move count: 
            if self.fen.activeColor == 'w':
                self.fen.fullMoveNumber = str(int(self.fen.fullMoveNumber) + 1)  # increase full move count after black's move
            return True
        else:
            # not a valid move
            return False

    def removePiece(self, piece: object) -> None:
        if not piece: return
        self.stat = self.stat - piece.value if piece.color == PieceColor.WHITE else self.stat + piece.value
        self.pieces[piece.color].remove(piece)

    def getPGN(self, extendedFens: List[str]) -> str:
        # TODO
        pass

    def removeCastlingRights(self, color: PieceColor, which: str) -> None:
        newFen = ''
        if color == PieceColor.WHITE:
            toBeDeleted = which.upper()
        else:
            toBeDeleted = which.lower()
        for char in self.fen.castlingAvailability:
            if char not in toBeDeleted:
                newFen += char
        if newFen == '': 
            newFen = '-'
        self.fen.castlingAvailability = newFen


class Chupponnent:
    def __init__(self) -> None:
        pass

    def generateMove(self, board: Board) -> Tuple[int, int]:
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
            source = piece.currentSquare.id
            target = moves[moveId]
            return (source, target)
        else: 
            return None


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
        # update en passant rights:
        board.fen.enPassantTarget = '-'
    

    def _getMoveCandidatesFromOffsets(self, board: Board, offsets: List[Tuple[int, int]]) -> List[int]:
        moveCandidates = []
        for offset in offsets:
            # explore the field in every possible direction
            next = Location.getLocationsFromOffsets(self.currentSquare.id, [offset])
            while next:
                next = next[0]
                if board.squares[next].isOccupied and board.squares[next].currentPiece.color != self.color:
                    # opponent piece found: 
                    moveCandidates.append(next)
                    break
                elif board.squares[next].isOccupied:
                    # ally piece found:
                    break
                else:
                    # no piece found:
                    moveCandidates.append(next)
                next = Location.getLocationsFromOffsets(next, [offset])
        return moveCandidates

    def _isPinned(self, board: Board) -> bool:
        kingLocation = board.kingLocation[self.color]
        fileOffset = Location.getFileOffset(kingLocation, self.currentSquare.id)
        rankOffset = Location.getRankOffset(kingLocation, self.currentSquare.id)
        # check if self is on an "attack path" relative to king:
        if abs(fileOffset) == abs(rankOffset):
            # potential attackers: bishop and queen
            offset = (int(fileOffset / abs(fileOffset)), int(rankOffset / abs(rankOffset)))
            attackers = ['Q', 'B']
        elif fileOffset == 0:
            # potential attackers: rook and queen
            offset = (0, int(rankOffset / abs(rankOffset)))
            attackers = ['Q', 'R']
        elif rankOffset == 0:
            # potential attackers: rook and queen
            offset = (int(fileOffset / abs(fileOffset)), 0)
            attackers = ['Q', 'R']
        else:
            # no pin possible
            return False
        next = Location.getLocationsFromOffsets(self.currentSquare.id, [offset])
        while next:
            next = next[0]
            if next == self.currentSquare.id:
                pass            
            elif board.squares[next].isOccupied and board.squares[next].currentPiece.color != self.color and board.squares[next].currentPiece.identifier.upper() in attackers:
                # attacker found:
                return True
            elif board.squares[next].isOccupied:
                # king is protected by other ally or opponent piece:
                return False
            next = Location.getLocationsFromOffsets(next, [offset])
        # if we end up here, there was no attacker found:
        return False

    def _getGlobalValidMoves(self, moveCandidates: List[int], board: Board) -> List[int]:
        """ takes into account the global board situation, that is:
            - Pins (remove moves that would lead to a check)
            - Checks (if the king is in check, only moves that prevent that check are valid)
            hint: _getGlobalValidMoves() will not be called by the king itself, so if the king is being checked by
            more than one piece at the same time, this function will just return an empty list (because a double
            check can only be solved by moving the king)
        """
        check = board.squares[board.kingLocation[self.color]].currentPiece.isInCheck(board)
        if len(check) >= 2:
            # a position where the king is checked by 2 or more pieces can only be resolved through moving the king
            return []
        pin = self._isPinned(board)
        if pin == True and len(check) > 0:
            # no movement possible
            return []
        elif len(check) == 1:
            # king is in check -> only moves that block the attack path are valid
            attackerLocation = check[0]
            kingLocation = board.kingLocation[self.color]
            blockingLocations = Location.getLocationsOnPath(kingLocation, attackerLocation)
            blockingLocations.append(attackerLocation)      # capturing the attacker would solve the problem, too
            return list(set(blockingLocations) & set(moveCandidates))
        elif pin == True and self.identifier.upper() == 'N':
            # shortcut to save executing time: a pinned knight can never move:
            return []
        elif pin == True:
            # offsets from piece's point of view:
            kingOffset = Location.getTupleOffset(self.currentSquare.id, board.kingLocation[self.color])
            validMoves = []
            if abs(kingOffset[0]) == abs(kingOffset[1]):
                # diagonal attack path -> only movements on this path are allowed to not end up in check:
                relIndex = 0      # index actually does not matter for diagonal attack paths, just for code reuse; you could as well use 1 here
                allowedNominalOffsets = [Location.nominalizeTuple(kingOffset)]             
            else:
                # linear attack path -> only movements on this path are allowed to not end up in check:
                relIndex = 0 if kingOffset[1] == 0 else 1
                allowedNominalOffsets = tuple(ti/kingOffset[relIndex] for ti in kingOffset)
            # movements in the opposite direction are also valid:
            allowedNominalOffsets.append(tuple(-ti for ti in allowedNominalOffsets[0]))
            # check if move candidates are on the attack path:
            for move in moveCandidates:
                offset = Location.getTupleOffset(self.currentSquare.id, move)
                if tuple(ti/abs(offset[relIndex]) for ti in offset) in allowedNominalOffsets:
                    # legal move on the attack path -> do nothing
                    validMoves.append(move)
            return validMoves
        else:
            return moveCandidates

class King(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'K', 0)

    def getValidMoves(self, board: Board, currentLocation: int = -1) -> List[int]:
        offsets = [(-1,1), (1,1), (-1, -1), (1,-1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        if currentLocation == -1:
            currentLocation = self.currentSquare.id
        moveCandidates = Location.getLocationsFromOffsets(currentLocation, offsets)
        # filter out move candidates with ally pieces and move candidates that would lead to a check:
        moveCandidates[:] = filterfalse(lambda candidate : \
            True if (board.squares[candidate].isOccupied and board.squares[candidate].currentPiece.color == self.color) else (
                True if (len(self._locationUnderAttack(board, candidate, 1)) > 0) else False), moveCandidates)
        # add castling rights:
        if not self.isInCheck(board):
            moveCandidates.extend(self._getCastlingRights(board))
        return moveCandidates

    def makeMove(self, board: Board, target: int) -> None:
        source = self.currentSquare.id
        self._switchSquaresAndCapture(board, target)
        board.kingLocation[self.color] = target
        board.removeCastlingRights(self.color, 'KQ')
        # castling: move rook, too
        if abs(Location.getFileOffset(source, target)) > 1:
            rank = 0 if self.color == PieceColor.WHITE else 7
            file = 0 if Location.absoluteSqToTuple(target)[0] == 2 else 7
            tarFile = 3 if Location.absoluteSqToTuple(target)[0] == 2 else 5
            board.squares[Location.tupleToAbsoluteSq((file, rank))].currentPiece.makeMove(board, Location.tupleToAbsoluteSq((tarFile, rank)))

    def isInCheck(self, board: Board) -> List[int]:
        """ returns List of locations of attacking opponents or empty list, if not in check """
        return self._locationUnderAttack(board, self.currentSquare.id)

    def _locationUnderAttack(self, board: Board, location: int, cap: int = 2) -> List[int]:
        """ This function checks if a location is under attack by an opponent piece and 
            returns the locations of attacking opponents
            hint: at the moment, the returned list is capped at a length of 2 to save executing time
        """
        attackerLocations = []
        # 1) the "just check one field"s: Knight, Pawn, King 
        oneSquareAttackers = {}
        oppPawnRankOffset = 1 if self.color == PieceColor.WHITE else -1 
        oneSquareAttackers['N'] = [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)] 
        oneSquareAttackers['P'] = [(-1,oppPawnRankOffset),(1,oppPawnRankOffset)]

        for attacker in oneSquareAttackers:
            attackerLocs = Location.getLocationsFromOffsets(location, oneSquareAttackers[attacker])
            for attackerLoc in attackerLocs:
                if board.squares[attackerLoc].isOccupied and board.squares[attackerLoc].currentPiece.color != self.color and board.squares[attackerLoc].currentPiece.identifier.upper() == attacker:
                    attackerLocations.append(attackerLoc)
                    if len(attackerLocations) >= cap:
                        # save executing time since more than 2 attackers make no difference for the game logic
                        return attackerLocations
        
        # 2) the "check the whole attack path"s: Queen, Rook, Bishop
        pathAttackers = {}
        pathAttackers['B'] = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        pathAttackers['R'] = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for attacker in pathAttackers:
            for nominalOffset in pathAttackers[attacker]:
                next = Location.getLocationsFromOffsets(location, [nominalOffset])
                while next:
                    next = next[0]
                    if board.squares[next].isOccupied and board.squares[next].currentPiece.identifier != self.identifier:
                        if board.squares[next].currentPiece.color != self.color and board.squares[next].currentPiece.identifier.upper() in [attacker, 'Q']:
                            attackerLocations.append(next)
                            if len(attackerLocations) >= cap:
                                # save executing time since more than 2 attackers make no difference for the game logic
                                return attackerLocations
                        # if one square is occupied, that means we found the attacker or there is no more risk:
                        break
                    next = Location.getLocationsFromOffsets(next, [nominalOffset])
        return attackerLocations

    def _getCastlingRights(self, board: Board) -> List[int]:
        fen = set(board.fen.castlingAvailability)
        options = list(fen & set('KQ')) if self.color == PieceColor.WHITE else list(fen & set('kq'))
        if len(options) == 0:
            return []
        options = (option.upper() for option in options)
        rank = 0 if self.color == PieceColor.WHITE else 7
        castlingRights = []
        # add kingside castling -> if f/g are not under attack (file 5,6) and f/g are not occupied
        if ('K' in options) and \
            (len(self._locationUnderAttack(board, Location.tupleToAbsoluteSq((5, rank)))) == 0) and \
            (len(self._locationUnderAttack(board, Location.tupleToAbsoluteSq((6, rank)))) == 0) and \
            (board.squares[Location.tupleToAbsoluteSq((5, rank))].isOccupied == False) and \
            (board.squares[Location.tupleToAbsoluteSq((6, rank))].isOccupied == False):
            castlingRights.append(Location.tupleToAbsoluteSq((6, rank)))
        # add queenside castling -> if c/d are not under attack (file 2/3) and b, c, d are not occupied
        if ('Q' in options) and \
            (len(self._locationUnderAttack(board, Location.tupleToAbsoluteSq((2, rank)))) == 0) and \
            (len(self._locationUnderAttack(board, Location.tupleToAbsoluteSq((3, rank)))) == 0) and \
            (board.squares[Location.tupleToAbsoluteSq((1, rank))].isOccupied == False) and \
            (board.squares[Location.tupleToAbsoluteSq((2, rank))].isOccupied == False) and \
            (board.squares[Location.tupleToAbsoluteSq((3, rank))].isOccupied == False):
            castlingRights.append(Location.tupleToAbsoluteSq((2, rank)))
        return castlingRights

class Queen(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'Q', 9)

    def getValidMoves(self, board: Board) -> List[int]:
        offsets = [(-1,1), (1,1), (-1, -1), (1,-1), (-1, 0), (1, 0), (0, -1), (0, 1)]
        moveCandidates = self._getMoveCandidatesFromOffsets(board, offsets)
        return self._getGlobalValidMoves(moveCandidates, board)

    def makeMove(self, board: Board, target: int) -> None:
        self._switchSquaresAndCapture(board, target)

class Rook(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'R', 5)

    def getValidMoves(self, board: Board) -> List[int]:
        offsets = [(-1,0), (1,0), (0, -1), (0, 1)]
        moveCandidates = self._getMoveCandidatesFromOffsets(board, offsets)
        return self._getGlobalValidMoves(moveCandidates, board)

    def makeMove(self, board: Board, target: int) -> None:
        # update castling rights
        location = Location.absoluteSqToTuple(self.currentSquare.id)[0]
        defaultRank = 0 if self.color == PieceColor.WHITE else 7
        if location == (0, defaultRank):
            board.removeCastlingRights(self.color, 'Q')
        elif location == (7, defaultRank):
            board.removeCastlingRights(self.color, 'K')
        self._switchSquaresAndCapture(board, target)

class Bishop(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'B', 3)

    def getValidMoves(self, board: Board) -> List[int]:
        offsets = [(-1,1), (1,1), (-1, -1), (1,-1)]
        moveCandidates = self._getMoveCandidatesFromOffsets(board, offsets)
        return self._getGlobalValidMoves(moveCandidates, board)

    def makeMove(self, board: Board, target: int) -> None:
        self._switchSquaresAndCapture(board, target)

class Knight(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'N', 3)

    def getValidMoves(self, board: Board) -> List[int]:
        offsets = [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)]
        currentLocation = self.currentSquare.id
        moveCandidates = Location.getLocationsFromOffsets(currentLocation, offsets)
        moveCandidates[:] = filterfalse(lambda candidate : \
            True if (board.squares[candidate].isOccupied and board.squares[candidate].currentPiece.color == self.color) else False, moveCandidates)
        return self._getGlobalValidMoves(moveCandidates, board)

    def makeMove(self, board: Board, target: int) -> None:
        self._switchSquaresAndCapture(board, target)
    

class Pawn(Piece):
    def __init__(self, color: PieceColor) -> None:
        Piece.__init__(self, color, 'P', 1)

    def isFirstMove(self) -> bool:
        if (self.color == PieceColor.WHITE and self.currentSquare.id >= 48 and self.currentSquare.id <= 55) or \
            (self.color == PieceColor.BLACK and self.currentSquare.id >= 8 and self.currentSquare.id <= 15):
            return True
        else:
            return False

    def _isPawnPromotion(self, target: int) -> bool:
        if self.color == PieceColor.WHITE:
            return (target <= 7)
        else:
            return (target >= 56)
    
    def getValidMoves(self, board: Board) -> List[int]:
        currentLocation = self.currentSquare.id
        if self.color == PieceColor.WHITE:
            offsets = [(0,1),(1,1),(-1,1)]
        else:
            offsets = [(0,-1),(1,-1),(-1,-1)]
        if self.isFirstMove():
            offsets.append((0,2*offsets[0][1]))
        moveCandidates = Location.getLocationsFromOffsets(currentLocation, offsets)
        # remove candidates with a file offset if there is no opponent piece
        # and candidates without file offset if there is any piece:
        moveCandidates[:] = filterfalse(lambda candidate : \
            True if (Location.getFileOffset(self.currentSquare.id, candidate) != 0 and (board.squares[candidate].isOccupied == False or board.squares[candidate].currentPiece.color == self.color)) else (
                True if (Location.getFileOffset(self.currentSquare.id, candidate) == 0 and board.squares[candidate].isOccupied) else False
            ), moveCandidates)
        # if square in front of the pawn is blocked, the next square (rank offset 2) is also not a valid move :
        if offsets[0] not in [Location.getTupleOffset(candidate, self.currentSquare.id) for candidate in moveCandidates]:
            moveCandidates[:] = filterfalse(lambda candidate : \
                True if (abs(Location.getRankOffset(self.currentSquare.id, candidate)) == 2) else False, moveCandidates)
        # add en passant moves (if applicable):
        if board.fen.enPassantTarget != '-':
            target = Location.algebraicSqToAbsoluteSq(board.fen.enPassantTarget)
            if target in Location.getLocationsFromOffsets(currentLocation, offsets):
                moveCandidates.append(target)
        return self._getGlobalValidMoves(moveCandidates, board)

    def makeMove(self, board: Board, target: int) -> None:
        source = self.currentSquare.id
        self._switchSquaresAndCapture(board, target)
        # pawn promotion - TODO: selective (atm only queens are possible)
        if self._isPawnPromotion(target):
            # remove self from target
            board.squares[target].reset()
            board.removePiece(self)
            promotedPiece = Queen(self.color)
            board.squares[target].set(promotedPiece)
            board.stat = board.stat + promotedPiece.value if promotedPiece.color == PieceColor.WHITE else board.stat - promotedPiece.value
            board.pieces[promotedPiece.color].append(promotedPiece)
        # update en passant rights:
        if abs(Location.getRankOffset(source, target)) == 2:
            if self.color == PieceColor.WHITE:
                skipped = source - 8
            else:
                skipped = source + 8
            board.fen.enPassantTarget = Location.absoluteSqToAlgebraicSq(skipped)


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
        > the tuple notation with two 0-based indices for file and rank, e.g. (0,7) or (2,5) (=A8/C6)
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

    def absoluteSqToAlgebraicSq(absoluteSq: int) -> str:
        """ absolute to algebraic notation, e.g. 7 -> 'h8'; 36 -> 'e4' """
        return Location.tupleToAlgebraicSq(Location.absoluteSqToTuple(absoluteSq))

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

    def getFileOffset(current: int, target: int) -> int:
        return Location.absoluteSqToTuple(current)[0] - Location.absoluteSqToTuple(target)[0]

    def getRankOffset(current: int, target: int) -> int:
        return Location.absoluteSqToTuple(current)[1] - Location.absoluteSqToTuple(target)[1]

    def getTupleOffset(current: int, target: int) -> Tuple[int, int]:
        # returns a (file, rank) offset tuple
        return (Location.getFileOffset(current, target), Location.getRankOffset(current, target))

    def nominalizeTuple(tpl: Tuple[int, int]) -> Tuple[int, int]:
        # nominalizes tpl (-> every element will have the absolute value 1 or 0):
        return tuple((int(ti/abs(ti)) if abs(ti) != 0 else 0) for ti in tpl)

    def getLocationsOnPath(loc1: int, loc2: int) -> List[int]:
        # returns a list of locations on the path between loc1 and loc2

        # TODO refactoring idea: where we call this method, the attacker location is explicitly appended to the List afterwards;
        # in this method itself, we explicitly exclude the attacker's (or king's) location (i == 0) -> if there is no other 
        # use for this method, we should change that. 
        locations = []
        offset = Location.getTupleOffset(loc1, loc2)
        tpl1 = Location.absoluteSqToTuple(loc1)
        tpl2 = Location.absoluteSqToTuple(loc2)
        if not ((abs(offset[0]) == abs(offset[1])) or (0 in offset)):
            # no direct path -> return empty list
            return []
        # diagonal path/linear path:
        relevantIndex = 1 if offset[0] == 0 else 0
        nominalOffset = Location.nominalizeTuple(offset)
        for i in range(abs(offset[relevantIndex])):
            if i == 0:
                continue
            loc = (tpl2[0] + i * nominalOffset[0], tpl2[1] + i * nominalOffset[1])
            if loc == tpl1:
                break
            locations.append(Location.tupleToAbsoluteSq(loc))
        return locations


class PieceFactory:
    switcher = {
        'P' : Pawn,
        'B' : Bishop,
        'N' : Knight,
        'R' : Rook,
        'Q' : Queen,
        'K' : King
    }

    def getPieces(fen: FEN) -> dict:
        pieces = {}
        location = 0
        for c in fen.piecePlacement:
            if c.isnumeric():
                location += int(c)
            elif c != '/':
                color = PieceColor.WHITE if c.isupper() else PieceColor.BLACK
                cls = PieceFactory.switcher.get(c.upper())
                pieces[location] = cls(color)
                location += 1
        return pieces
            


