from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

ALLOWED_CATEGORIES = {"Strength", "Cardio", "Flexibility", "Balance"}


class Exercise(db.Model):
    __tablename__ = "exercises"

    __table_args__ = (
        UniqueConstraint("name", name="uq_exercise_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # An Exercise has many WorkoutExercises; deleting an Exercise removes
    # its join-table rows too (cascade), matching the stretch goal.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    # An Exercise has many Workouts through WorkoutExercises.
    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name must not be empty.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(ALLOWED_CATEGORIES)}")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name} ({self.category})>"


class Workout(db.Model):
    __tablename__ = "workouts"

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # A Workout has many WorkoutExercises; deleting a Workout removes its
    # join-table rows too (cascade), matching the stretch goal.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    # A Workout has many Exercises through WorkoutExercises.
    exercises = association_proxy("workout_exercises", "exercise")

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id} on {self.date}>"


class WorkoutExercise(db.Model):
    """Join table: an Exercise performed as part of a Workout, with its
    own reps/sets/duration data."""

    __tablename__ = "workout_exercises"

    __table_args__ = (
        CheckConstraint("reps > 0", name="ck_we_reps_positive"),
        CheckConstraint("sets > 0", name="ck_we_sets_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps")
    def validate_reps(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("reps must be a positive integer.")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("sets must be a positive integer.")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("duration_seconds must be a non-negative integer.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise {self.id} workout={self.workout_id} "
            f"exercise={self.exercise_id}>"
        )
