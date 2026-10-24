from datetime import date

from server.app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    push_up = Exercise(name="Push-Up", category="Strength", equipment_needed=False)
    squat = Exercise(name="Squat", category="Strength", equipment_needed=False)
    running = Exercise(name="Running", category="Cardio", equipment_needed=False)
    deadlift = Exercise(name="Deadlift", category="Strength", equipment_needed=True)
    stretching = Exercise(
        name="Hamstring Stretch", category="Flexibility", equipment_needed=False
    )

    exercises = [push_up, squat, running, deadlift, stretching]
    db.session.add_all(exercises)
    db.session.commit()

    print("Seeding workouts...")
    leg_day = Workout(
        date=date(2026, 10, 1), duration_minutes=45, notes="Leg day, felt strong."
    )
    cardio_day = Workout(
        date=date(2026, 10, 3), duration_minutes=30, notes="Easy recovery run."
    )
    full_body = Workout(
        date=date(2026, 10, 5),
        duration_minutes=60,
        notes="Full body strength session.",
    )

    workouts = [leg_day, cardio_day, full_body]
    db.session.add_all(workouts)
    db.session.commit()

    print("Linking exercises to workouts...")
    links = [
        WorkoutExercise(workout=leg_day, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=leg_day, exercise=deadlift, reps=5, sets=5),
        WorkoutExercise(
            workout=leg_day, exercise=stretching, reps=1, sets=1, duration_seconds=120
        ),
        WorkoutExercise(
            workout=cardio_day, exercise=running, reps=1, sets=1, duration_seconds=1800
        ),
        WorkoutExercise(workout=full_body, exercise=push_up, reps=15, sets=3),
        WorkoutExercise(workout=full_body, exercise=squat, reps=12, sets=3),
        WorkoutExercise(
            workout=full_body, exercise=running, reps=1, sets=1, duration_seconds=600
        ),
    ]
    db.session.add_all(links)
    db.session.commit()

    print("Done seeding!")
