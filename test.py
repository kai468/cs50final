
"""
from cs50 import SQL
db = SQL("sqlite:///chupochess.db")

db.execute("DELETE FROM active_games;")
db.execute("DELETE FROM game_state;")
"""

from chupochess import Board, Piece, PieceColor, Location
from anytree import NodeMixin, RenderTree
from typing import Tuple, List


# very helpful website for analysing positions and debugging: https://nextchessmove.com/

ext_fen = '8/8/8/5p2/3P1k2/8/pp4p1/R3K1N1 b - - 0 1 0'


board = Board.fromString(ext_fen)

#board = Board.startingPosition()
# choose statistically best move (from stat only):
# assuming white always makes the 'smartest' move (that is, bringing it in the best position for the given exploration depth)


# this needs to involve some kind of recursion?
# rough idea (brute-force, we can optimize later): 
# - it's black's turn
# - get all possible moves for all of black's pieces (layer 1)
# - get all possible white moves for all of layer1's moves (layer 2)
# - get all possible black moves for all of layer2's moves (layer 3)
# - ... and so on, until layer n
# - simulate each move chain and save the stat
# - for each move chain, assume that white will choose the move that leaves it with
#   the highest stat after n moves (if there is more than one move leading to the
#   same end stat, all of them are relevant for the moment)
# - delete all move paths that became irrelevant due to "dumb moves" of white
# - choose the move resulting in the best stat after n moves from black's perspective
#   (if there is more than one move leading to the same end stat, just take the first one
#   -> this could be improved later: compare the moves regarding the 'dumb-move-probability'
#   of white - that is, if there is one black move leading to fewer good white moves than 
#   the other, choose that one)   



class Halfmove(NodeMixin):
    def __init__(self, color: PieceColor, halfmove: Tuple[int,int], initFen: str, parent=None, children=None) -> None:
        super(Halfmove, self).__init__()
        self.color = color
        self.halfmove = halfmove
        self.board = Board.fromString(initFen)
        initStat = self.board.stat
        self.board.makeMove(halfmove[0], halfmove[1], True)
        self.statDelta = self.board.stat - initStat
        self.initFen = initFen
        self.parent = parent
        if children:
            self.children = children

    def __str__(self) -> str:
        src = Location.absoluteSqToAlgebraicSq(self.halfmove[0])
        tar = Location.absoluteSqToAlgebraicSq(self.halfmove[1])
        clr = 'w' if self.color == PieceColor.WHITE else 'b'
        return clr + ", " + src + ", " + tar + ": " + str(self.statDelta)

def _compareBoards(board1: Board, board2: Board) -> List[int]:
    differences = []
    for i in range(64):
        if board1.squares[i] != board2.squares[i]:
            differences.append(i)
    return differences

def print_node(board: Board) -> str:
    if board.parent:
        # check differences between two boards:
                 # board.squares and board.parent.squares should have 2-3 (3 for pawn promotion, castling, ..)
                # differences -> we can simulate the schnittmenge of these location's valid moves with the 
                # other 1-2 differences to find the made move (that is a max of 9 move simulations which
                # should be fairly quick)
        differences = _compareBoards(board, board.parent)
        for i in differences:
            # simulate moves:
            if board.parent.squares[i].isOccupied:
                for move in board.parent.getMoves(i, True):
                    tmp = Board.fromString(str(board.parent))
                    tmp.makeMove(i, move, True)
                    if not _compareBoards(board, tmp):
                        if tmp.squares[move].currentPiece.color == PieceColor.WHITE:
                            return 'w, ' + Location.absoluteSqToAlgebraicSq(i) + ', ' + Location.absoluteSqToAlgebraicSq(move) + ': ' + str(board.stat)
                        else:
                            return 'b, ' + Location.absoluteSqToAlgebraicSq(i) + ', ' + Location.absoluteSqToAlgebraicSq(move) + ': ' + str(board.stat)
        # if we get here without returning a move, we're not able to identify the move:
        raise Exception("ERROR: can't identify move from " + str(board.parent) + " to " + str(board))
    else:
        # initial position/parent board -> no move to be output:
        return "INIT"

## TEST: print_node
board_parent = Board.startingPosition()
board_child = Board.fromString(str(board_parent), board_parent)
print(_compareBoards(board_parent, board_child))
board_child.makeMove(52, 36)
print(print_node(board_parent))
print(print_node(board_child))

"""
# 1) build up the tree:
upperLayer = []

for blackmove in board.getAllMoves(PieceColor.BLACK):
    upperLayer.append(Halfmove(PieceColor.BLACK, blackmove, str(board)))
    lowerLayer = []
    for whitemove in upperLayer[-1].board.getAllMoves(PieceColor.WHITE):
        lowerLayer.append(Halfmove(PieceColor.WHITE, whitemove, str(upperLayer[-1].board), upperLayer[-1]))
        # TODO: from here on (latest), this has to become a recursive function:
        l3Layer =[]
        for b3move in lowerLayer[-1].board.getAllMoves(PieceColor.BLACK):
            l3Layer.append(Halfmove(PieceColor.BLACK, b3move, str(lowerLayer[-1].board), lowerLayer[-1]))
            l4Layer = []
            for w4move in l3Layer[-1].board.getAllMoves(PieceColor.WHITE):
                l4Layer.append(Halfmove(PieceColor.WHITE, w4move, str(l3Layer[-1].board), l3Layer[-1]))

# TODO: could we just use the board itself as a Node? We'd just need a function that can
#       sort out the move between to boards to get from board to move after all of this
# -> chupponnent move generator could handle the recursion and create new boards/moves

def iterate():
    return

for halfmove in upperLayer:
    if halfmove.children:
        pass




# printing the example tree:
cnt = 0

for branch in upperLayer:
    for pre, fill, node in RenderTree(branch):
        treestr = u"%s%s" % (pre, str(node))
        print(treestr)
        cnt += 1

print(cnt)

"""

# TODO: as a starting point, get all possible moves for black, simulate them, and look at the stats:
# --> this already works pretty good for the example where there are two obviously good moves (
#       both capturing a white rook and promoting to a queen) but does not help at all for e.g. the 
#       starting position (where all moves lead to the same stat)
"""
smart_moves = []
best_stat = 1000            # from black's perspective: the higher, the worse!
for piece in board.pieces[PieceColor.BLACK]:
    possible_moves = board.getMoves(piece.currentSquare.id, True)
    for target in possible_moves:
        temp = Board.fromString(str(board))
        temp.makeMove(piece.currentSquare.id, target, True)
        stat = temp.stat - board.stat
        if stat == best_stat:
            smart_moves.append((piece.currentSquare.id, target))
        elif stat < best_stat:
            best_stat = stat
            smart_moves.clear()
            smart_moves.append((piece.currentSquare.id, target))
print(smart_moves)
"""

# sth like: best case for the move, avg case for the move, worst case for the move
