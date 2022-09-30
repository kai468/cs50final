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
    requestHandler("/getBoard", NULL_LOC, NULL_LOC);
});

// monitor user's clicks on the board
$( 'td' ).click(function(event) {
    if (selected == NULL_LOC){
        // request valid moves for selected square and marks them on the board
        selected = event.target.id;
        requestHandler("/getBoard", selected, NULL_LOC);
    } else if (selected == event.target.id){
        // reset valid moves visualisation for selected piece
        selected = NULL_LOC;
        deleteMoves();
    } else {
        // try to make move
        requestHandler("/getBoard", selected, event.target.id);
    }
});

// Buttons:
$( '#btn_giveUp').click(function() {
    requestHandler("/surrender", NULL_LOC, NULL_LOC);
});

$( '#btn_draw').click(function() {
    requestHandler("/drawRequest", NULL_LOC, NULL_LOC);
});

$( '#btn_unmakeMove').click(function() {
    requestHandler("/unmakeMove", NULL_LOC, NULL_LOC);
});


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


function deleteMoves(){
    // delete all markers for valid Moves (that is, color via class and content for empty squares)
    for (var i = 0; i < 64; i++){
        $( 'td#' + i).attr('class', 'unmarked');
        if ($('td#' + i).html() == '\u2b27') {
            $('td#' + i).html('\u2008');
        }
    }
}


function showEOG(message){
    // show End-Of-Game pop up
    // TODO
    // inspo: https://www.w3docs.com/snippets/html/how-to-overlay-one-div-over-another.html

    alert("Message: " + message);
}

function requestHandler(endpoint, src, tar){
    // central orchestrator for handling requests to BE
    $.post(endpoint,
    {
        source: src,
        target: tar
    }, 
    function(data, status){
        responseHandler(endpoint, src, tar, data, status);
    });
}

function validateResponse(endpoint, source, target, data, status){

    // check if request successful:
    if (status != 'success'){
        return 'Failed Request';
    }
    // check if request and response add up:
    if (data.request.endpoint != endpoint){
        return 'Mismatch: Endpoints';
    }
    if (data.request.source != source){
        return 'Mismatch: Source';
    }
    if (data.request.target != target){
        return 'Mismatch: Target';
    }

    return 'valid';
}

function updateBoard(pieces, validMoves){
    // update the board visualisation: 
    var marker = false;
    var id = 255;
    $('.chess_table td').each(function() {
        marker = false;
        id = $(this).attr('id');
        // update the piece: 
        $(this).text(pieceFenToUnicode(pieces[id]));
        // check if the square is in the validMoves list:
        for (var i = 0; i < validMoves.length; i++){
            if (validMoves[i] == id) {
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


function responseHandler(endpoint, source, target, data, status){
    // central orchestrator for handling the BE response for every type of request

    // 1) check if request successful:
    var responseValidation = validateResponse(endpoint, source, target, data, status);
    if (responseValidation != 'valid'){
        showEOG(responseValidation);
    }

    // 2) update Board:
    updateBoard(data.pieces, data.validMoves);

    // 3) update selected:
    // TODO: see if this works!
    if (data.validMoves.length == 0){
        /*  no valid moves means that a move was made successfully, or that a square without 
        valid moves (e.g. empty, opponent piece, or ally piece with no possible moves) was selected */
        selected = NULL_LOC;
    } else if (endpoint  == '/getBoard' && target != NULL_LOC) {
        // user selected new piece while another one was selected 
        selected = target;
    }
    
    // 4) check for notification:
    if (data.notification != null){
        alert(data.notification);
    }

    // 5) check for EOG:
    // TODO 
    // showEOG(data.action, status)  

}