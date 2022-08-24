var selected;       // save selected square / -1 = no selection
        
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
    selected = -1;
    updatePieces();
});

// monitor user's clicks on the board
$( 'td' ).click(function(event) {
    if (selected == -1){
        selected = event.target.id;
        getMoves();
    } else if (selected == event.target.id){
        selected = -1;
        deleteMoves();
    } else {
        // try to make move
        makeMove(selected, event.target.id);
        selected = -1;
        // TODO: if not a valid move, select new square and mark valid moves
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
        alert("Data: " + data.action + "\nStatus: " + status);
    });
});



function updatePieces(){
    // TODO
    $.post("/gamestate",
    {}, function(data, status){
        var pieceList = data.pieces;
        for (var i = 0; i < 64; i++){
            $( 'td#' + i).text(pieceList[i]);
        }
        alert("Data: " +  pieceList[0] + "\nStatus: " + status);
    });
}

function makeMove(source, target){
    // TODO 
    $.post("/gamestate",
    {
        source: source,
        target: target
    },
    function(data, status){
        alert("Data: " + data.action + "\nStatus: " + status);
    });
}

function getMoves(){
    // TODO
    $.post("/validMoves",
    {
        selected: selected
    }, 
    function(data, status){
        alert("Data: " + data.action + "\nStatus: " + status);
    });
}

function deleteMoves(){
    // TODO
    alert("delete moves");
}