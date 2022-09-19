from cs50 import SQL
from datetime import datetime

# ###### Data Layer: #########
class DataLayer:
    """ This class contains the interface to the database """
    # hint: user is the IP address right now but could be changed to a user name (combined with a login/registration form) anytime

    def getBytes(db: SQL, user: str) -> bytes:
        """ returns the serialized protobuf if there is an active game or None if there isn't """
        try: 
            response = db.execute("SELECT board FROM gamestate WHERE move_id = (SELECT MAX(move_id) FROM gamestate WHERE " + \
                "game_id = (SELECT id FROM active_games WHERE user = '" + user + "'));")
            if response:
                return response[0]['board']            
            else:
                return None
        except:
            return None

    def _createNewGame(db: SQL, user: str, bytes: bytes) -> None:
        # make sure there's only one active game per user:
        db.execute("DELETE FROM active_games WHERE user = '" + user + "';")
        # create new game id:
        id = db.execute("INSERT INTO active_games (user, timestamp) VALUES ('" + user + "', '" + \
             datetime.today().strftime('%Y-%m-%d %H:%M:%S') + "');")
        # create initial gamestate:
        db.execute("INSERT INTO gamestate (game_id, move_id, board) VALUES (" + str(id) + ", 0, ?);", bytes)

    def storeNewMove(db: SQL, user: str, bytes: bytes) -> bool:
        """ stores a new serialized protobuf to the game state data base (and, if necessary, creates a new active game) """
        # check if it's the first move:
        gameId = db.execute("SELECT id FROM active_games WHERE user = '" + user + "';")
        if not gameId:
            DataLayer._createNewGame(db, user, bytes)
            return True
        gameId = str(gameId[0]['id'])
        maxMoveId = db.execute("SELECT MAX(move_id) FROM gamestate WHERE " + \
                "game_id = " + gameId + ";")[0]['MAX(move_id)']
        if maxMoveId == None:
            return False
        # create new entry:
        db.execute("INSERT INTO gamestate (game_id, move_id, board) VALUES (" + gameId + ", " + \
            str(int(maxMoveId) + 1) + ", ?);", bytes)
        return True

    def reverseMove(db: SQL, user: str) -> bytes:
        """ returns the last serialized protobof or None if reversing the move is not possible """
        # hint: one move of white and one move of black has to be reversed so offset is actually 2
        gameId = db.execute("SELECT id FROM active_games WHERE user = '" + user + "';")
        if not gameId:
            return None
        gameId = str(gameId[0]['id'])
        maxMove = db.execute("SELECT MAX(move_id) FROM gamestate WHERE " + \
                "game_id = " + gameId + ";")[0]['MAX(move_id)']
        if not maxMove:
            return None
        response = db.execute("SELECT board FROM gamestate WHERE move_id = " + str(int(maxMove) - 2) + ";")
        if response:
            # Delete other moves 
            db.execute("DELETE FROM gamestate WHERE game_id = " + gameId + " AND move_id > " + str(int(maxMove) - 2) + ";")
            return response[0]['board']
        else:
            return None
        
    def endGame(db: SQL, user: str, pgn: str, status: str) -> bool:
        """ deletes all status entries and adds the game to the finished games """
        gameId = db.execute("SELECT id FROM active_games WHERE user = '" + user + "';")
        if not gameId:
            return False
        gameId = str(gameId[0]['id'])
        # delete entries:
        db.execute("DELETE FROM active_games WHERE id = " + gameId + ";")
        db.execute("DELETE FROM gamestate WHERE game_id = " + gameId + ";")
        # store in finished games:
        db.execute("INSERT INTO finished_games (user, pgn, status, timestamp) VALUES ('" + user + "', '" + pgn + \
            "', '" + status + "', '" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + "');")
        return True


