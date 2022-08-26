from typing import Tuple

def pieceFenToChar(fen: str):
    """ returns char for FEN notation """
    switcher = {
        "k" : "\u265a",
        "q" : "\u265b", 
        "n" : "\u265e",
        "b" : "\u265d",
        "r" : "\u265c", 
        "p" : "\u265f",
        "K" : "\u2654",
        "Q" : "\u2655", 
        "N" : "\u2658",
        "B" : "\u2657",
        "R" : "\u2656", 
        "P" : "\u2659",
    }
    return switcher.get(fen, "\u2008")
    # "&#8200;" is the unicode for a null character since the null character (&#0000;) might display a weird symbol in some browsers




