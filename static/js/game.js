var selected;           // save selected square 
var NULL_LOC = 255;     // no selection
        
// responsive chess board:
$(window).on( 'load resize', function(){
    $('.chess_table').width('auto').height('auto');
    $('.chess_table td, .chess_table th').width('auto').height('auto').css({'font-size':0.1+'em'});
    var tableSize = Math.min( window.innerHeight - 250, window.innerWidth);
    var squareSize = tableSize / 10;
    $('.chess_table').width(tableSize).height(tableSize);
    $('.chess_table td, .chess_table th').width(squareSize).height(squareSize)
    $('.chess_table td').css({ 'font-size':Math.floor(100*squareSize/16/1.4)/100+'em' });
    $('.chess_table th').css({ 'font-size':Math.floor(100*squareSize/16/2.5)/100+'em' });
});

// init: 
$(document).ready(function() {
    selected = NULL_LOC;
    updatePieces();
});

// monitor user's clicks on the board
$( 'td' ).click(function(event) {
    if (selected == NULL_LOC){
        selected = event.target.id;
        getMoves();
    } else if (selected == event.target.id){
        selected = NULL_LOC;
        deleteMoves();
    } else {
        // try to make move
        makeMove(selected, event.target.id);
    }
});

// Buttons:
$( '#btn_giveUp').click(function() {
    $.post("/giveUp",{}, function(data, status){
        alert("Data: " + data.action + "\nStatus: " + status);
    });
});

$( '#btn_draw').click(function() {
    $.post("/draw",
    {}, function(data, status){
        alert("Data: " + data.action + "\nStatus: " + status);
    });
});

$( '#btn_unmakeMove').click(function() {
    $.post("/unmakeMove",
    {}, function(data, status){
        if (status == 'success'){
            var pieceList = data.pieces;
            for (var i = 0; i < 64; i++){
                $( 'td#' + i).text(pieceFenToUnicode(pieceList[i]));
                $( 'td#' + i).attr('class', 'unmarked');
            }
        } 
    });
});

// TODO: End of Game (Display Popup / Overlaying shape)


function pieceFenToUnicode(fen){
    switch(fen) {
        case 'k': 
            return '\u265a';
        case 'q': 
            return '\u265b'; 
        case 'n': 
            return '\u265e';
        case 'b': 
            return '\u265d';
        case 'r': 
            return '\u265c'; 
        case 'p': 
            return '\u265f';
        case 'K': 
            return '\u2654';
        case 'Q': 
            return '\u2655'; 
        case 'N': 
            return '\u2658';
        case 'B': 
            return '\u2657';
        case 'R': 
            return '\u2656'; 
        case 'P': 
            return '\u2659';
        default:
            return '\u2008';
    }
}


function updatePieces(){
    $.post("/gamestate",
    {}, function(data, status){
        if (status == 'success'){
            var pieceList = data.pieces;
            for (var i = 0; i < 64; i++){
                $( 'td#' + i).text(pieceFenToUnicode(pieceList[i]));
            }
        } 
    });
}

function makeMove(source, target){
    $.post("/gamestate",
    {
        source: source,
        target: target
    },
    function(data, status){
        if (status == 'success'){
            if (data.moveMade == 1) {
                // valid Move: 
                selected = NULL_LOC;
                // update pieces:
                var pieceList = data.pieces;
                for (var i = 0; i < 64; i++){
                    $( 'td#' + i).text(pieceFenToUnicode(pieceList[i]));
                    $( 'td#' + i).attr('class', 'unmarked');
                }
            } else {
                // not a valid move -> select new square and mark valid moves
                selected = target;
                var validMoves = data.validMoves;
                var marker = false; 
                // check for each square if it's in the 'validMoves' List:
                $('.chess_table td').each(function() {
                    marker = false;
                    for (var i = 0; i < validMoves.length; i++){
                        if (validMoves[i] == $(this).attr('id')) {
                            marker = true;
                            // if there are only whitespace characters, output a diamond shape:
                            if ($(this).html().trim().length == 0) {
                                $(this).html('\u2b27');
                            } 
                            // mark the cell: 
                            $(this).attr('class', 'marked');
                            break;
                        }
                    }
                    // reset cell if it's not in the 'validMoves' list:
                    if (marker == false) {
                        $(this).attr('class', 'unmarked');
                        if ($(this).html() == '\u2b27') {
                            $(this).html('\u2008');
                        }
                    }
                }); 
            }
        } 
    });
}

function getMoves(){
    // requests valid moves for selected square and marks them on the board
    $.post("/validMoves",
    {
        selected: selected
    }, 
    function(data, status){
        if (status == 'success'){
            // if there is no white piece on the selected square, 'bad request' is returned by backend
            var validMoves = data.validMoves;
            var marker = false;
            // check for each square if it's in the 'validMoves' List:
            $('.chess_table td').each(function() {
                marker = false;
                for (var i = 0; i < validMoves.length; i++){
                    if (validMoves[i] == $(this).attr('id')) {
                        marker = true;
                        // if there are only whitespace characters, output a diamond shape:
                        if ($(this).html().trim().length == 0) {
                            $(this).html('\u2b27');
                        } 
                        // mark the cell: 
                        $(this).attr('class', 'marked');
                        break;
                    }
                }
                // reset cell if it's not in the 'validMoves' list:
                if (marker == false) {
                    $(this).attr('class', 'unmarked');
                    if ($(this).html() == '\u2b27') {
                        $(this).html('\u2008');
                    }
                }
            });
        } 
    });
}

function deleteMoves(){
    // delete all markers for valid Moves (that is, color via class and content for empty squares)
    for (var i = 0; i < 64; i++){
        $( 'td#' + i).attr('class', 'unmarked');
        if ($('td#' + i).html() == '\u2b27') {
            $('td#' + i).html('\u2008');
        }
    }
}