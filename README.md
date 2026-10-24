# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend for a workout tracking
application used by personal trainers. Tracks workouts and the
exercises performed in each one, including reps, sets, and duration.

## Description

The API has three entities:

- **Exercise** — a reusable exercise (e.g. "Squat"), with a name,
  category, and whether equipment is needed.
- **Workout** — a single workout session, with a date, duration, and
  notes.
- **WorkoutExercise** — the join table connecting a `Workout` to an
  `Exercise`, recording the reps/sets/duration for that exercise
  within that specific workout.

A `Workout` has many `Exercises` through `WorkoutExercise`, and an
`Exercise` has many `Workouts` through `WorkoutExercise` — the same
exercise can be reused across multiple workouts.

Validation happens at three layers:

- **Table constraints** — e.g. `duration_minutes` on `Workout` must
  be positive, `reps`/`sets` on `WorkoutExercise` must be positive,
  and `Exercise.name` is unique, all enforced at the database level.
- **Model validations** — e.g. `Exercise.category` must be one of a
  known set of categories, `Exercise.name` can't be blank.
- **Schema validations** — Marshmallow schemas re-check the same
  rules (and a few extras, like max name length) before data ever
  reaches the model.

## Installation

```bash
# from the project root
pipenv install
pipenv shell
```

Then, from inside `server/`:

```bash
cd server
flask db init
flask db migrate -m "initial migration"
flask db upgrade head
```

Seed the database with example data:

```bash
python seed.py
```

You can re-run `seed.py` any time to reset the data back to a known
state.

## Running the app

From the `server/` directory:

```bash
python app.py
```

The API runs at `http://localhost:5555`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/workouts` | List all workouts |
| GET    | `/workouts/<id>` | Show a single workout, including its exercises (with reps/sets/duration) |
| POST   | `/workouts` | Create a workout. Body: `{"date", "duration_minutes", "notes"}` |
| DELETE | `/workouts/<id>` | Delete a workout (also deletes its `WorkoutExercise` rows) |
| GET    | `/exercises` | List all exercises |
| GET    | `/exercises/<id>` | Show a single exercise, including the workouts it's been used in |
| POST   | `/exercises` | Create an exercise. Body: `{"name", "category", "equipment_needed"}` |
| DELETE | `/exercises/<id>` | Delete an exercise (also deletes its `WorkoutExercise` rows) |
| POST   | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout. Body: `{"reps", "sets", "duration_seconds"}` |

### Example requests

```bash
# Create an exercise
curl -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Bench Press", "category": "Strength", "equipment_needed": true}'

# Create a workout
curl -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-10-20", "duration_minutes": 50, "notes": "Upper body day"}'

# Add an exercise to a workout (IDs from the responses above)
curl -X POST http://localhost:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps": 8, "sets": 4, "duration_seconds": null}'

# View a workout with its exercises
curl http://localhost:5555/workouts/1

# View an exercise with the workouts it appears in
curl http://localhost:5555/exercises/1

# Delete a workout
curl -X DELETE http://localhost:5555/workouts/1
```

## Project Structure

```
.
├── Pipfile
├── README.md
├── .gitignore
└── server/
    ├── app.py          # Flask app and routes
    ├── models.py        # SQLAlchemy models, relationships, validations
    ├── schemas.py        # Marshmallow schemas for (de)serialization
    └── seed.py           # Populates the database with example data
```

## Verifying relationships and validations

From `server/`, open a shell:

```bash
flask shell
```

```python
>>> from models import Exercise, Workout, WorkoutExercise
>>> w = Workout.query.first()
>>> w.exercises            # exercises linked to this workout, via the association proxy
>>> e = Exercise.query.first()
>>> e.workouts              # workouts this exercise appears in

# Validations prevent bad data:
>>> Exercise(name="", category="Strength")
# raises ValueError: Exercise name must not be empty.
>>> Workout(date=None, duration_minutes=-5)
# raises ValueError: duration_minutes must be a positive integer.
```

## Test files

No automated test suite is included in this submission. The stretch
goal in Task 4 (writing a pytest suite for model validations and
endpoint status codes) was not implemented.
