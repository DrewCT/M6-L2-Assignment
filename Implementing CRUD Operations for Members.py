from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

def get_db_connection():
    db_name = "fitness_center_db"
    user = "root"
    password = "ur_pw" 
    host = "localhost"

    try:
        conn = mysql.connector.connect(
            database=db_name,
            user=user,
            password=password,
            host=host
        )
        print("Connected to MySQL database successfully")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "id")

class WorkoutSessionSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    duration = fields.Integer(required=True)

    class Meta:
        fields = ("member_id", "duration", "id", "session_date")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSessionSchema()
workouts_schema = WorkoutSessionSchema(many=True)

@app.route('/')
def home():
    return "Welcome to the Fitness Center API"

@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()

        return members_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_member = (member_data['name'], member_data['email'])
        cursor.execute("INSERT INTO members (name, email) VALUES (%s, %s)", new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['name'], member_data['email'], id)
        cursor.execute("UPDATE members SET name = %s, email = %s WHERE id = %s", updated_member)
        conn.commit()

        return jsonify({"message": "Updated member successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM members WHERE id = %s", (id,))
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404

        cursor.execute("DELETE FROM members WHERE id = %s", (id,))
        conn.commit()

        return jsonify({"message": "Member removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workouts", methods=["POST"])
def schedule_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_workout = (workout_data['member_id'], workout_data['duration'])
        cursor.execute("INSERT INTO workout_sessions (member_id, duration) VALUES (%s, %s)", new_workout)
        conn.commit()

        return jsonify({"message": "New workout session scheduled successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workouts/<int:id>", methods=["PUT"])
def update_workout(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workout = (workout_data['member_id'], workout_data['duration'], id)
        cursor.execute("UPDATE workout_sessions SET member_id = %s, duration = %s WHERE id = %s", updated_workout)
        conn.commit()

        return jsonify({"message": "Updated workout session successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:member_id>/workouts", methods=["GET"])
def get_workouts_for_member(member_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM workout_sessions WHERE member_id = %s", (member_id,))
        workouts = cursor.fetchall()

        return workouts_schema.jsonify(workouts)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)