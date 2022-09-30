from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from chupochess import Board, GameState
from helpers import DataLayer as dl
from cs50 import SQL 

INVALID_LOC = 255

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure database:
db = SQL("sqlite:///chupochess.db")

def getBoardFromDb(user: str) -> Board:
    """ helper function to get the existing Game (board) or initiate a new one """
    bytes = dl.getBytes(db, user)
    if bytes:
        # load existing game: 
        board = Board.fromBytes(bytes)
    else: 
        # create new game:
        board = Board.startingPosition()
        dl.storeNewMove(db, user, board.toBytes())
    return board

@app.route("/", methods=["GET"])
def index():
    """Play chess"""
    cols = []
    for i in range(65,73):
        cols.append(chr(i))
    return render_template("index.html", cols=cols)

@app.route("/about")
def about():
    return render_template("about.html")


## new, refactored from here on downwards:


def requestHandler(endpoint, request):
    # TODO: if EOG -> move to finished games

    src = int(request.form.get("source"))
    tar = int(request.form.get("target"))
    if src < 0 or src > 63:
        src = INVALID_LOC
    if tar < 0 or tar > 63:
        tar = INVALID_LOC
    # initialize JSON response: 
    response = {}
    response['pieces'] = {}
    response['validMoves'] = []
    response['eogMessage'] = None
    response['notification'] = None
    # add initial request to response:
    response['request'] = {}
    response['request']['endpoint'] = endpoint
    response['request']['source'] = src
    response['request']['target'] = tar

    # get board representation:
    print(request.environ['REMOTE_ADDR'])
    board = getBoardFromDb(request.environ['REMOTE_ADDR'])

    # check the request type:
    if endpoint == "/drawRequest":
        if board.suggestDraw():
            response['pieces'] = board.getOutput() 
            response['eogMessage'] = 'DRAW'
        else:
            response['notification'] = 'Draw rejected by opponnent.'
    elif endpoint == "/surrender":
        response['pieces'] = board.getOutput() 
        board.whiteSurrenders()
        response['eogMessage'] = 'BLACK_WINS'
    elif endpoint == "/unmakeMove":
        bytes = dl.reverseMove(db, request.environ['REMOTE_ADDR'])
        if bytes: 
            board = Board.fromBytes(bytes)
        else: 
            board = getBoardFromDb(request.environ['REMOTE_ADDR']) 
        response['pieces'] = board.getOutput()
        if not bytes:
            response['notification'] = 'Unmake not possible.'
    elif endpoint == "/getBoard":
        # TODO
        # there are four types of requests arriving here:
        # 1) no source, no target -> just the piece list is requested
        # 2) source but no target -> valid moves for source piece requested
        # 3) source + target but not a valid move -> valid moves for source piece requested
        # 4) source + target which form a valid move -> make move requested (could lead to EOG or not)
        if src == INVALID_LOC and tar == INVALID_LOC:
            response['pieces'] = board.getOutput()
        elif src != INVALID_LOC and tar == INVALID_LOC:
            response['pieces'] = board.getOutput()
            response['validMoves'] = board.getMoves(src)
        elif src != INVALID_LOC and tar != INVALID_LOC and not (tar in board.getMoves(src)):
            response['pieces'] = board.getOutput()
            response['validMoves'] = board.getMoves(src)
        elif src != INVALID_LOC and tar != INVALID_LOC and (tar in board.getMoves(src)):
            # make white move: 
            board.makeMove(src, tar)
            dl.storeNewMove(db, request.environ['REMOTE_ADDR'], board.toBytes())
            # generate black move: 
            generateMove = board.opponent.generateMove(board)
            if generateMove:
                board.makeMove(generateMove[0], generateMove[1], True)
                dl.storeNewMove(db, request.environ['REMOTE_ADDR'], board.toBytes())
            response['pieces'] = board.getOutput()
            if board.gameState != GameState.IDLE:
                if board.gameState == GameState.UNDEFINED:
                    response['eogMessage'] = 'ERROR'
                else:
                    response['eogMessage'] = board.gameState.name             

    return jsonify(response), 200 


@app.route("/getBoard", methods=["POST"])
def getBoard():
    return requestHandler("/getBoard", request)

@app.route("/unmakeMove", methods=["POST"])
def unmakeMove():
    return requestHandler("/unmakeMove", request)

@app.route("/drawRequest", methods=["POST"])
def drawRequest():
    return requestHandler("/drawRequest", request)

@app.route("/surrender", methods=["POST"])
def surrender():
    return requestHandler("/surrender", request)
