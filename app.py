from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from chupochess import Board
from helpers import DataLayer as dl
from cs50 import SQL 

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

def getBoard(user: str) -> Board:
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

# TODO:
@app.route("/gamestate", methods=["POST"])
def gamestate():
    response = {}
    board = getBoard(request.environ['REMOTE_ADDR'])
    if request.form.get("source") and request.form.get("target"):
        # TODO: 1) check if valid Move 2) if yes: make Move; if no: return valid Moves for target sqare
        # check if valid move
        source = int(request.form.get("source"))
        target = int(request.form.get("target"))
        # do some input validation:
        if source >= 0 and source <= 64 and target >= 0 and target <= 64 and target != source:
            response['moveMade'] = int(board.makeMove(source, target))
            dl.storeNewMove(db, request.environ['REMOTE_ADDR'], board.toBytes())
            board = Board.fromString(str(board))
            generateMove = board.opponent.generateMove(board)
            board.makeMove(generateMove[0], generateMove[1], True)
            dl.storeNewMove(db, request.environ['REMOTE_ADDR'], board.toBytes())
        else:
            response['moveMade'] = 0
            response['validMoves'] = board.getMoves(target)
        response['pieces'] = board.getOutput()     
    else:
        # print pieces:
        response['moveMade'] = 0
        response['pieces'] = board.getOutput()
    return jsonify(response), 200


@app.route("/validMoves", methods = ["POST"])
def validMoves():
    response = {}
    if request.form.get("selected"):
        selected = int(request.form.get("selected"))
        board = getBoard(request.environ['REMOTE_ADDR'])
        if board.getMoves(selected):
            response['selected'] = selected
            response['validMoves'] = board.getMoves(selected)
        else:
            # no white piece on the selected square -> return -1:
            response['selected'] = -1
            response['validMoves'] = []
        return jsonify(response), 200
    else:
        return jsonify({}), 400

@app.route("/unmakeMove", methods=["POST"])
def unmakeMove():
    response = {}
    bytes = dl.reverseMove(db, request.environ['REMOTE_ADDR'])
    if bytes: 
        board = Board.fromBytes(bytes)
    else: 
        board = getBoard(request.environ['REMOTE_ADDR']) 
    response['pieces'] = board.getOutput()
    return jsonify(response), 200

@app.route("/draw", methods=["POST"])
def draw():
    # TODO
    action = "draw"
    return jsonify({'action': action}), 200

@app.route("/giveUp", methods=["POST"])
def giveUp():
    # TODO
    action = "give up"
    return jsonify({'action': action}), 200



