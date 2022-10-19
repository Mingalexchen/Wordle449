# Science Fiction Novel API - Quart Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

from pickle import NONE
import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml
import json

from quart_schema import validate_request

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request
from secrets import compare_digest



app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

#############---DB schema---#############
@dataclasses.dataclass
class UserInfo:
    user_id: int
    user_name: str
    user_password: str
class GameStats:
    game_id: int
    user_id: int
    game_result: int   #0: in progress 1:win 2:lose
    answer_attempted: int   #number of attemped answers
    secret_word: str   #answer word
    attempt_1: str
    attempt_2: str
    attempt_3: str
    attempt_4: str
    attempt_5: str
    attempt_6: str
class SecretWords:
    secret_word: str
#############################################


#############---helper functions---#############

#############################################






#############---DB connection---#############
async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()
#############################################


#############---main page---#############
@app.route("/", methods=["GET"])
def front_page():
    return textwrap.dedent(
        """
        <h1>welcoe to wordy</h1>
        <p>Register if you are new. \nAlready have an account? Login here.</p>\n
    """
    )
#############################################

#TBD
#@app.route("/register", methods=["POST"])



#############---login---#############
@app.route("/login")
async def auth():
    login = request.authorization
    name = login.username
    password = login.password
    if (name == "alex" and
        compare_digest(password, "cpsc449")
        ):
        return {"authorization": True}
    else:
        abort(401)
##############################################


#############---user games---#############
#---returns all games played by the user
@app.route("/<int:id>/games", methods=["GET"])
async def user_games(id):
    db = await _get_db()
    all_game = await db.fetch_all("SELECT * FROM GameStats WHERE user_id = :id;", values={"id":id})
    if all_game:
        return list(map(dict, all_game))
    else:
        abort(404)

#tbd: user who have not played any game

##############################################




#############---answer attempt block---#############
#
#############---compare string function---#############
#--- compare two 5 char words  answer  and  attempt
#--- and returns a json in formate {str1,str2,str3,str4,str5}
#--- where stri = "correct" if attempt[i] = answer[i]
# ---           = "almost there"  if attempt[i] != answer[i]
# ---                                && attempt[i] exist in answer  
# ---           = "incorrect" if word[i] not exist in answer 
async def compare_answer_str(attempt, answer):
    result_dict = {0:"error",1:"error",2:"error",3:"error",4:"error"}
    for i in range(5):
        if attempt[i] == answer[i]:
            result_dict[i] = "correct"
        elif attempt[i] in answer:
            result_dict[i] = "valid"
        else: 
            result_dict[i] = "incorrect"
    
    result_json = json.dumps(result_dict)
    return result_json
#
#############---check range function---#############
#--- a function that returns game_result in GameStats
async def get_game_result(game_id):
    db = await _get_db()
    game_result = await db.fetch_one("SELECT game_result FROM GameStats WHERE game_id = :id;", values={"id":game_id}) 
    return game_result
#
#############---check attempted function---#############
#--- a function that returns answer_attempted in GameStats
async def get_attempt_number(game_id):
    db = await _get_db()
    answer_attempts = await db.fetch_one("SELECT answer_attempted FROM GameStats WHERE game_id = :id;", values={"id":game_id}) 
    return answer_attempts
#
#############---insert attempt function---#############
#--- a function that insert user entry to GameStats attempt_i
async def enter_answer(game_id,user_entry,attempt_number):
    db = await _get_db()
    if attempt_number == 0:
        insert_content = {'attempt_1': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_1 = :attempt_1
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"1st attempt": "finished"}
    elif attempt_number == 1:
        insert_content = {'attempt_2': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_2 = :attempt_2
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"2nd attempt": "finished"}
    elif attempt_number == 2:
        insert_content = {'attempt_3': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_3 = :attempt_3
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"3rd attempt": "finished"}
    elif attempt_number == 3:
        insert_content = {'attempt_4': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_4 = :attempt_4
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"4th attempt": "finished"}
    elif attempt_number == 4:
        insert_content = {'attempt_5': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_5 = :attempt_5
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"5th attempt": "finished"}
    elif attempt_number == 5:
        insert_content = {'attempt_6': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_6 = :attempt_6
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"6th attempt": "finished"}
    else:
        return {"attempt": "failed"}
 
#
#########---update answer_attempted function---#########
#--- a function that increases answer_attempted by 1
async def increase_attempt_number(game_id):
    db = await _get_db()
    game_id_dict = {'game_id': game_id} 
    try:
        await db.execute(
        '''
        UPDATE GameStats SET answer_attempted = answer_attempted + 1
        WHERE game_id = :game_id;
        ''',
        game_id_dict
    )
    except sqlite3.IntegrityError as e:
        abort(409,e)
    return {"attempt number": "updated"}
#
#############---respond to answer---#############
@app.route("/user/games/<int:game_id>", methods=["POST"])
async def respond_to_an_entry(game_id):
    if get_game_result(game_id) != 0:  #check if game has ended
        abort(400)     #return {"Attempt failed":"Game already ended!"}
    data = await request.get_json()  #receive user entry attempt 
    if not data:                    #check if received data
        abort(404)
    attempt = f"{data['attempt']}"  #convert user entry to string
    if attempt.len() != 5:  #if attempt not a length 5 word, return error
        abort(409)  
    db = await _get_db()   #connect to DB
    attempt_number = get_attempt_number(game_id)  
    if attempt_number > 5:      #check if the user have less than 6 answers
        abort(400)
    secret_word = await db.fetch_one("SELECT secret_word FROM GameStats WHERE game_id = :id;", values={"id":game_id}) 
    if not secret_word:     #if get secret_word fail return 400
        abort(400)
    answer = f'{secret_word}'
    return_json = await compare_answer_str(attempt, answer)  #compare user entry with secret word    
    enter_answer(game_id, attempt, attempt_number)
    increase_attempt_number(game_id)
    return return_json
   

##############################################







#############---DB content helpers---#############
@app.route("/games/info", methods=["GET"])
async def all_games():
    db = await _get_db()
    all_game = await db.fetch_all("SELECT * FROM GameStats;")

    return list(map(dict, all_game))

@app.route("/user/info", methods=["GET"])
async def all_users():
    db = await _get_db()
    all_user = await db.fetch_all("SELECT * FROM UserInfo;")

    return list(map(dict, all_user))

@app.route("/word/info", methods=["GET"])
async def all_words():
    db = await _get_db()
    all_word = await db.fetch_all("SELECT * FROM SecretWords;")

    return list(map(dict, all_word))
##############################################








#############---new game---#############
@app.route("/<int:user_id>/newgame", methods=["POST"])
async def new_game(user_id):
    db = await _get_db()
    new_secret_word = await db.fetch_one("SELECT secret_word FROM SecretWords ORDER BY RANDOM() LIMIT 1;")
    new_secret_word = new_secret_word[0]
    insert_content = {'game_id': None, 'user_id': user_id, 'game_result':None,
            'answer_attempted':0, 'secret_word':new_secret_word,
            'attempt_1':None, 'attempt_2':None, 'attempt_3':None,
            'attempt_4':None, 'attempt_5':None, 'attempt_6':None}    
    insert_content = dict(insert_content)

    try:
        await db.execute(
            '''
            INSERT INTO GameStats(game_id, user_id, game_result,
            answer_attempted, secret_word,
            attempt_1, attempt_2, attempt_3,
            attempt_4, attempt_5, attempt_6)
            VALUES(:game_id,:user_id, :game_result,
            :answer_attempted, :secret_word,
            :attempt_1, :attempt_2, :attempt_3,
            :attempt_4, :attempt_5, :attempt_6);
            ''',
            insert_content
        )
    except sqlite3.IntegrityError as e:
        abort(409,e)
    return {"New Game Started": "success"}

##############################################





#############---modify game helper---#############
@app.route("/<int:game_id>/increaseattempt", methods=["PUT"])
async def increase_attempt_val(game_id):
    db = await _get_db()
    game_id_dict = {'game_id': game_id} 
    try:
        await db.execute(
        '''
        UPDATE GameStats SET answer_attempted = answer_attempted + 1
        WHERE game_id = :game_id;
        ''',
        game_id_dict
    )
    except sqlite3.IntegrityError as e:
        abort(409,e)
    return {"update": "success"}





#############---game update---#############
@app.route("/<int:game_id>/newmove", methods=["PUT"])
async def update_game(game_id):
    db = await _get_db()

    data = await request.get_json()
    user_entry = f"{data['entry']}"
    attempt_number = int(f"{data['attempt_number']}")
    if attempt_number == 0:
        insert_content = {'attempt_1': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_1 = :attempt_1
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"1st attempt": "finished"}
    elif attempt_number == 1:
        insert_content = {'attempt_2': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_2 = :attempt_2
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"2nd attempt": "finished"}
    elif attempt_number == 2:
        insert_content = {'attempt_3': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_3 = :attempt_3
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"3rd attempt": "finished"}
    elif attempt_number == 3:
        insert_content = {'attempt_4': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_4 = :attempt_4
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"4th attempt": "finished"}
    elif attempt_number == 4:
        insert_content = {'attempt_5': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_5 = :attempt_5
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"5th attempt": "finished"}
    elif attempt_number == 5:
        insert_content = {'attempt_6': user_entry, 'game_id': game_id}    
        insert_content = dict(insert_content)
        try:
            await db.execute(
            '''
            UPDATE GameStats 
            SET attempt_6 = :attempt_6
            WHERE game_id = :game_id;
            ''',
            insert_content
        )
        except sqlite3.IntegrityError as e:
            abort(409,e)
        return {"6th attempt": "finished"}
    else:
        return {"attempt": "failed"}
##############################################










#############---error handlers---#############
@app.errorhandler(404)
def not_found(e):
    return {"error": "The resource could not be found"}, 404

@app.errorhandler(RequestSchemaValidationError)
def bad_request(e):
    return {"error": str(e.validation_error)}, 400


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409

@app.errorhandler(401)
def conflict(e):
    return {"error": "Authorization failed!"}, 401
#############################################



'''
dictA = json.loads('{"6th attempt": "finished"}')
        dictB = json.loads('{"entry": "finished"}')
        merged_dict = {**dictA, **dictB}
        jsonString_merged = json.dumps(merged_dict)




@app.route("/books/all", methods=["GET"])
async def all_books():
    db = await _get_db()
    all_books = await db.fetch_all("SELECT * FROM books;")

    return list(map(dict, all_books))


@app.route("/books/<int:id>", methods=["GET"])
async def one_book(id):
    db = await _get_db()
    book = await db.fetch_one("SELECT * FROM books WHERE id = :id", values={"id": id})
    if book:
        return dict(book)
    else:
        abort(404)





@app.route("/books/", methods=["POST"])
@validate_request(Book)
async def create_book(data):
    db = await _get_db()
    book = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO books(published, author, title, first_sentence)
            VALUES(:published, :author, :title, :first_sentence)
            """,
            book,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    book["id"] = id
    return book, 201, {"Location": f"/books/{id}"}


SearchParam = collections.namedtuple("SearchParam", ["name", "operator"])
SEARCH_PARAMS = [
    SearchParam(
        "author",
        "LIKE",
    ),
    SearchParam(
        "published",
        "=",
    ),
    SearchParam(
        "title",
        "LIKE",
    ),
    SearchParam(
        "first_sentence",
        "LIKE",
    ),
]


@app.route("/books/search", methods=["GET"])
async def search():
    query_parameters = request.args

    sql = "SELECT * FROM books"

    conditions = []
    values = {}

    for param in SEARCH_PARAMS:
        app.logger.debug(f"{param}=")
        if query_parameters.get(param.name):
            if param.operator == "=":
                conditions.append(f"{param.name} = :{param.name}")
                values[param.name] = query_parameters[param.name]
            else:
                conditions.append(f"{param.name} LIKE :{param.name}")
                values[param.name] = f"%{query_parameters[param.name]}%"

    if conditions:
        sql += " WHERE "
        sql += " AND ".join(conditions)

    app.logger.debug(sql)

    db = await _get_db()
    results = await db.fetch_all(sql, values)

    return list(map(dict, results))
'''