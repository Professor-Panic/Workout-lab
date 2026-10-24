from marshmallow import Schema, fields, validate

ALLOWED_CATEGORIES = ["Strength", "Cardio", "Flexibility", "Balance"]


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(ALLOWED_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(required=True, validate=validate.Range(min=1))
    sets = fields.Int(required=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(validate=validate.Range(min=0), allow_none=True)


# --- Nested schemas used only for the single-resource detail views ---

class WorkoutExerciseForWorkoutSchema(Schema):
    """A WorkoutExercise row as shown inside GET /workouts/<id>."""

    id = fields.Int(dump_only=True)
    reps = fields.Int()
    sets = fields.Int()
    duration_seconds = fields.Int()
    exercise = fields.Nested(ExerciseSchema)


class WorkoutExerciseForExerciseSchema(Schema):
    """A WorkoutExercise row as shown inside GET /exercises/<id>."""

    id = fields.Int(dump_only=True)
    reps = fields.Int()
    sets = fields.Int()
    duration_seconds = fields.Int()
    workout = fields.Nested(WorkoutSchema)


class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseForWorkoutSchema), dump_only=True
    )


class ExerciseDetailSchema(ExerciseSchema):
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseForExerciseSchema), dump_only=True
    )


# Ready-to-use instances
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()
