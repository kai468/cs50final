from flask import Flask, flash, redirect, render_template, request, session
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

@app.route("/")
def index():
    """Play chess"""
    # white perspective:
    cols = []
    for i in range(65,73):
        cols.append(chr(i))
    board = Board()
    pieces = board.getOutput()
    for i in range(64):
        pieces[i] = h.pieceFenToChar(pieces[i])
    return render_template("index.html", cols=cols, pieces=pieces)

@app.route("/about")
def about():
    return render_template("about.html")


