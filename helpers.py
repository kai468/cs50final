from typing import Tuple

def pieceFenToChar(fen: str, marked: bool):
    """ returns char for FEN notation """
    switcher = {
        "k" : "9818",
        "q" : "9819", 
        "n" : "9822",
        "b" : "9821",
        "r" : "x265c", 
        "p" : "9823",
        "K" : "9812",
        "Q" : "9813", 
        "N" : "9816",
        "B" : "9815",
        "R" : "9814", 
        "P" : "9817",
    }
    if marked:
        return switcher.get(fen, "11047")
        # "&#11047;" is unicode for a diamond shape, indicating that the user can move to that square
    else:
        return switcher.get(fen, "8200")
        # "&#8200;" is the unicode for a null character since the null character (&#0000;) might display a weird symbol in some browsers




