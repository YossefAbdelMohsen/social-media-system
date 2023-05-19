from flask import Blueprint, request , jsonify
import jwt
from db import mysql
import bcrypt

routes = Blueprint("routes", __name__,url_prefix='/api/users')

def check_token(token):
    try:
        data = jwt.decode(token , "secret" , algorithms=['HS256'])
        return data["user_id"]
    except:
        raise Exception("Invalid Token")



@routes.route('/<int:user_id>')
def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE id = %s', (str(user_id)))
    data = cur.fetchall()
    cur.close()
    user = 3
    return jsonify({ "user" : user_id})


@routes.route('/login', methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]

    if not username and not password:
         return jsonify({"error": "Invalid username or password"})
    # Check if the user exists and the password is correct
    print(username)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    data =cursor.fetchall()
    if not len(data) :
        return jsonify({"error": "Invalid username or password"})
    user = data[0]
    cursor.close()
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid username or password"})
    token = jwt.encode({"id": user["id"],"username" : user["username"]}, "secret", algorithm="HS256")
    return {"id": user["id"],"username" : user["username"],"token": token}





@routes.route("/register", methods=["POST"])
def register():
    username = request.json["username"]
    password = request.json["password"]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    data = cursor.fetchall()
    cursor.close()    
    if len(data):
        return {"error": "username already exists"}
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username , hashed_password))
    data = mysql.connection.commit()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    data = cursor.fetchall()
    cursor.close()
    user = (data[0])
    token = jwt.encode({"id": user["id"],"username" : user["username"]}, "secret", algorithm="HS256")
    # Return the token to the user
    return {"id": user["id"],"username" : user["username"],"token": token}