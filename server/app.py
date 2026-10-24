from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from models import Exercise, Workout, WorkoutExercise, db
from server.schemas import (
    exercise_detail_schema,
    exercise_schema,
    exercises_schema,
    workout_detail_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)

db.init_app(app)


def commit_or_error(obj):
    """Add + commit a new object, translating model/DB-level failures
    into a (message, 400) pair instead of letting them raise."""
    db.session.add(obj)
    try:
        db.session.commit()
        return None
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return str(err)


# ---------------------------------------------------------------------
# Workouts
# ---------------------------------------------------------------------
@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    try:
        data = workout_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    workout = Workout(**data)
    error = commit_or_error(workout)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(workout_schema.dump(workout)), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)  # cascades to associated WorkoutExercises
    db.session.commit()
    return jsonify({"message": f"Workout {id} deleted"}), 200


# ---------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------
@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = Exercise(**data)
    error = commit_or_error(exercise)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(exercise_schema.dump(exercise)), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    db.session.delete(exercise)  # cascades to associated WorkoutExercises
    db.session.commit()
    return jsonify({"message": f"Exercise {id} deleted"}), 200


# ---------------------------------------------------------------------
# Adding an exercise to a workout
# ---------------------------------------------------------------------
@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    payload = {
        **(request.get_json() or {}),
        "workout_id": workout_id,
        "exercise_id": exercise_id,
    }

    try:
        data = workout_exercise_schema.load(payload)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    workout_exercise = WorkoutExercise(**data)
    error = commit_or_error(workout_exercise)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
