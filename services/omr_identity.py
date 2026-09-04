"""Shared schema and coordinates for the CBSE-style identity bubble block."""

IDENTITY_SCHEMA_VERSION = 1
NAME_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
SUBJECT_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
CLASS_VALUES = ("IX", "X", "XI", "XII")
SECTION_VALUES = tuple("ABCDEFGH")
SET_VALUES = ("A", "B", "C", "D")

IDENTITY_SCHEMA = {
    "version": IDENTITY_SCHEMA_VERSION,
    "name_columns": 20,
    "name_alphabet": NAME_ALPHABET,
    "subject_columns": 16,
    "subject_alphabet": SUBJECT_ALPHABET,
    "roll_digits": 8,
    "class_values": CLASS_VALUES,
    "section_values": SECTION_VALUES,
    "set_values": SET_VALUES,
    "bubble_radius": 22,
    "bubble_x_spacing": 54,
    "bubble_y_spacing": 50,
    "origin_x": 170,
    "name_origin_y": 650,
    "subject_origin_x": 1320,
    "roll_origin_y": 2070,
    "choice_origin_y": 2070,
}


def identity_schema():
    """Return a JSON-friendly copy of the identity schema."""
    return {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in IDENTITY_SCHEMA.items()
    }


def grid_coordinates(origin_x, origin_y, columns, rows, x_spacing=None, y_spacing=None):
    x_spacing = x_spacing or IDENTITY_SCHEMA["bubble_x_spacing"]
    y_spacing = y_spacing or IDENTITY_SCHEMA["bubble_y_spacing"]
    return [
        [
            (origin_x + column * x_spacing, origin_y + row * y_spacing)
            for row in range(rows)
        ]
        for column in range(columns)
    ]


def identity_coordinates(schema=None):
    schema = schema or IDENTITY_SCHEMA
    name_alphabet = schema["name_alphabet"]
    subject_alphabet = schema["subject_alphabet"]
    return {
        "name": grid_coordinates(
            schema["origin_x"], schema["name_origin_y"],
            schema["name_columns"], len(name_alphabet),
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        ),
        "subject": grid_coordinates(
            schema["subject_origin_x"], schema["name_origin_y"],
            schema["subject_columns"], len(subject_alphabet),
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        ),
        "roll": grid_coordinates(
            schema["origin_x"], schema["roll_origin_y"],
            schema["roll_digits"], 10,
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        ),
        "class": grid_coordinates(
            790, schema["choice_origin_y"], 1, len(schema["class_values"]),
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        )[0],
        "section": grid_coordinates(
            1120, schema["choice_origin_y"], 1, len(schema["section_values"]),
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        )[0],
        "set": grid_coordinates(
            1510, schema["choice_origin_y"], 1, len(schema["set_values"]),
            schema["bubble_x_spacing"], schema["bubble_y_spacing"],
        )[0],
    }
