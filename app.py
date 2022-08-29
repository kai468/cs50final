from select import select
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from chupochess import Board
from helpers import pieceFenToChar
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
    if request.form.get("source") and request.form.get("target"):
        # TODO: 1) check if valid Move 2) if yes: make Move; if no: return valid Moves for target sqare
        action = 'Move from ' + request.form.get("source") + ' to ' + request.form.get("target") + '.'
        response['action'] = action 
    else:
        # print pieces:
        board = getBoard(request.environ['REMOTE_ADDR'])
        pieces = board.getOutput()
        for i in range(64):
            pieces[i] = pieceFenToChar(pieces[i])
        response['moveMade'] = 0
        response['pieces'] = pieces
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
    # TODO
    action = "unmake Move"
    return jsonify({'action': action}), 200

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

def getBoard(user: str) -> Board:
    """ helper function to get the existing Game (board) or initiate a new one """
    fen = dl.getExtFen(db, user)
    if fen:
        # load existing game: 
        board = Board.fromString(fen)
    else: 
        # create new game:
        board = Board.startingPosition()
        dl.storeNewMove(db, user, str(board))
    return board

