from select import select
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from chupochess import Board
import helpers as h 

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# start chess engine
board = Board()
selected = -1           # marker for selected square (absolute location) -> -1 = no square selected 
squaresMarked = []

@app.route("/", methods=["GET", "POST"])
def index():
    """Play chess"""

    # check user input
    if request.method == "POST":
        
        inp = int(request.form.get("square"))

        print("input: " + str(inp))

        if selected == inp:
            # unselect square
            selected = -1
            squaresMarked.clear()
        elif selected == -1:
            # try to select square (if there is a piece of the player)
            selected = inp
            squaresMarked.clear()
            squaresMarked.extend(board.getMoves(selected))
        elif inp in squaresMarked:
            # make Move
            selected = -1
            squaresMarked.clear()
            # TODO: trigger makeMove
        else:
            # unselect square
            selected = -1 
            squaresMarked.clear()


    # generate output for white perspective:
    cols = []
    for i in range(65,73):
        cols.append(chr(i))
    pieces = board.getOutput()
    for i in range(64):
        pieces[i] = h.pieceFenToChar(pieces[i], (i in squaresMarked))
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
        # return piece List
        pieces = board.getOutput()
        for i in range(64):
            pieces[i] = h.pieceFenToChar(pieces[i], (i in squaresMarked))
        response['moveMade'] = 0
        response['pieces'] = pieces
    return jsonify(response), 200
    return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200
    
    # returns: {"ip":"127.0.0.1"}


@app.route("/validMoves", methods = ["POST"])
def validMoves():
    response = {}
    if request.form.get("selected"):
        selected = int(request.form.get("selected"))
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

