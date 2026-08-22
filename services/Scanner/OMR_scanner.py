import argparse
import base64
import hashlib
import json
import math
import zlib
from pathlib import Path

import cv2
import fitz
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

INPUT_DIR = (
    BASE_DIR / "Input"
)

OUTPUT_DIR = (
    BASE_DIR / "Output"
)

TEMPLATES_DIR = (
    BASE_DIR / "Templates"
)

JSON_OUTPUT_DIR = (
    OUTPUT_DIR / "json"
)

DEBUG_OUTPUT_DIR = (
    OUTPUT_DIR / "debug"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

JSON_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DEBUG_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DEFAULT INPUT
# ============================================================

DEFAULT_INPUT = (
    INPUT_DIR
    / "OMR_6769_Jhonny_Sins_page_1.png"
)


# ============================================================
# SUPPORTED FORMATS
# ============================================================

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}

SUPPORTED_EXTENSIONS = (
    IMAGE_EXTENSIONS
    | {
        ".pdf"
    }
)


# ============================================================
# QR
# ============================================================

QR_PREFIX = "OMR1:"


# ============================================================
# PDF
# ============================================================

PDF_DPI = 300

PDF_SCALE = (
    PDF_DPI / 72.0
)


# ============================================================
# PAGE SIZES
# ============================================================

PAGE_SIZES = {

    "A4": (
        2480,
        3508
    ),

    "A5": (
        1748,
        2480
    ),

    "A3": (
        3508,
        4961
    ),

    "Letter": (
        2550,
        3300
    ),

    "Legal": (
        2550,
        4200
    ),
}


# ============================================================
# GENERATOR DEFAULTS
# ============================================================

DEFAULT_TEMPLATE = {

    "margin": 100,

    "header_height": 470,

    "start_y": 560,

    "bottom_margin": 180,

    "question_spacing": 105,

    "column_gap": 70,

    "bubble_spacing": 150,

    "bubble_radius": 24,

    "question_bubble_gap": 35,

    "registration_marker_size": 60,

    "registration_marker_margin": 100,
}


# ============================================================
# SAME FONT AS GENERATOR
# ============================================================

FONT_PATHS = [

    (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans.ttf"
    ),

    (
        "/usr/share/fonts/truetype/"
        "liberation2/"
        "LiberationSans-Regular.ttf"
    ),
]


def load_generator_font(
    size=32
):

    for path in FONT_PATHS:

        try:

            return ImageFont.truetype(
                path,
                size
            )

        except Exception:

            continue

    return ImageFont.load_default()


# ============================================================
# TEMPLATE
# ============================================================

class OMRTemplate:

    def __init__(
        self,
        metadata
    ):

        self.raw = dict(
            metadata
        )

        self.data = (
            self.normalize(
                metadata
            )
        )

        self.page_size = (
            self.data["page_size"]
        )

        self.orientation = (
            self.data["orientation"]
        )

        self.width = (
            self.data["width"]
        )

        self.height = (
            self.data["height"]
        )

        self.margin = (
            self.data["margin"]
        )

        self.header_height = (
            self.data["header_height"]
        )

        self.start_y = (
            self.data["start_y"]
        )

        self.bottom_margin = (
            self.data["bottom_margin"]
        )

        self.question_spacing = (
            self.data["question_spacing"]
        )

        self.column_gap = (
            self.data["column_gap"]
        )

        self.bubble_spacing = (
            self.data["bubble_spacing"]
        )

        self.bubble_radius = (
            self.data["bubble_radius"]
        )

        self.question_bubble_gap = (
            self.data["question_bubble_gap"]
        )

        self.choices = tuple(
            self.data["choices"]
        )

        self.registration_marker_size = (
            self.data[
                "registration_marker_size"
            ]
        )

        self.registration_marker_margin = (
            self.data[
                "registration_marker_margin"
            ]
        )

        self.template_id = (
            self.data.get(
                "template_id"
            )
        )

        if not self.template_id:

            self.template_id = (
                self.calculate_template_id()
            )

    # ========================================================
    # NORMALIZE
    # ========================================================

    @staticmethod
    def normalize(
        metadata
    ):

        metadata = dict(
            metadata
        )

        # ----------------------------------------------------
        # QR payload wrapper
        # ----------------------------------------------------

        if isinstance(
            metadata.get(
                "template"
            ),
            dict
        ):

            metadata = dict(
                metadata[
                    "template"
                ]
            )

        # ----------------------------------------------------
        # Optional config wrapper
        # ----------------------------------------------------

        if isinstance(
            metadata.get(
                "config"
            ),
            dict
        ):

            config = dict(
                metadata[
                    "config"
                ]
            )

            for key, value in (
                metadata.items()
            ):

                if key != "config":

                    config[
                        key
                    ] = value

            metadata = config

        result = {}

        # ====================================================
        # PAGE SIZE
        # ====================================================

        page_size = metadata.get(
            "page_size",
            metadata.get(
                "ps",
                "A4"
            )
        )

        page_size = str(
            page_size
        ).strip()

        if page_size not in PAGE_SIZES:

            matches = [

                key

                for key in PAGE_SIZES

                if key.lower()
                == page_size.lower()
            ]

            if matches:

                page_size = matches[0]

            else:

                raise ValueError(
                    f"Unsupported page size: "
                    f"{page_size}"
                )

        result[
            "page_size"
        ] = page_size

        # ====================================================
        # ORIENTATION
        # ====================================================

        orientation = metadata.get(
            "orientation",
            metadata.get(
                "o",
                "Portrait"
            )
        )

        orientation = str(
            orientation
        ).strip()

        if (
            orientation.lower()
            == "landscape"
        ):

            orientation = "Landscape"

        else:

            orientation = "Portrait"

        result[
            "orientation"
        ] = orientation

        # ====================================================
        # PAGE DIMENSIONS
        # ====================================================

        width, height = (
            PAGE_SIZES[
                page_size
            ]
        )

        if orientation == "Landscape":

            width, height = (
                height,
                width
            )

        result[
            "width"
        ] = OMRTemplate.get_number(
            metadata,
            "width",
            "w",
            default=width
        )

        result[
            "height"
        ] = OMRTemplate.get_number(
            metadata,
            "height",
            "h",
            default=height
        )

        # ====================================================
        # GEOMETRY
        # ====================================================

        geometry = {

            "margin": (
                "margin",
                "m"
            ),

            "header_height": (
                "header_height",
                "hh"
            ),

            "start_y": (
                "start_y",
                "sy"
            ),

            "bottom_margin": (
                "bottom_margin",
                "bm"
            ),

            "question_spacing": (
                "question_spacing",
                "qs"
            ),

            "column_gap": (
                "column_gap",
                "cg"
            ),

            "bubble_spacing": (
                "bubble_spacing",
                "bs"
            ),

            "bubble_radius": (
                "bubble_radius",
                "br"
            ),

            "question_bubble_gap": (
                "question_bubble_gap",
                "qbg"
            ),

            "registration_marker_size": (
                "registration_marker_size",
                "rms"
            ),

            "registration_marker_margin": (
                "registration_marker_margin",
                "rmm"
            ),
        }

        for field, aliases in (
            geometry.items()
        ):

            result[field] = (
                OMRTemplate.get_number(
                    metadata,
                    *aliases,
                    default=DEFAULT_TEMPLATE[
                        field
                    ]
                )
            )

        # ====================================================
        # CHOICES
        # ====================================================

        choices = metadata.get(
            "choices",
            "ABCD"
        )

        if isinstance(
            choices,
            list
        ):

            choices = "".join(
                str(choice)
                for choice in choices
            )

        choices = str(
            choices
        ).strip().upper()

        if not choices:

            raise ValueError(
                "Template contains no choices."
            )

        if not (
            2
            <= len(choices)
            <= 6
        ):

            raise ValueError(
                "Template must contain "
                "2–6 choices."
            )

        result[
            "choices"
        ] = choices

        # ====================================================
        # TEMPLATE ID
        # ====================================================

        template_id = metadata.get(
            "template_id",
            metadata.get(
                "id"
            )
        )

        if template_id:

            result[
                "template_id"
            ] = str(
                template_id
            )

        return result

    # ========================================================
    # NUMBER HELPER
    # ========================================================

    @staticmethod
    def get_number(
        data,
        *keys,
        default=None
    ):

        for key in keys:

            if key not in data:

                continue

            try:

                return int(
                    round(
                        float(
                            data[key]
                        )
                    )
                )

            except (
                ValueError,
                TypeError
            ):

                continue

        if default is not None:

            return int(
                default
            )

        raise ValueError(
            "Missing template value: "
            + ", ".join(
                keys
            )
        )

    # ========================================================
    # TEMPLATE ID
    # ========================================================

    def calculate_template_id(
        self
    ):

        data = {

            "page_size": (
                self.page_size
            ),

            "orientation": (
                self.orientation
            ),

            "width": (
                self.width
            ),

            "height": (
                self.height
            ),

            "margin": (
                self.margin
            ),

            "start_y": (
                self.start_y
            ),

            "bottom_margin": (
                self.bottom_margin
            ),

            "question_spacing": (
                self.question_spacing
            ),

            "column_gap": (
                self.column_gap
            ),

            "bubble_spacing": (
                self.bubble_spacing
            ),

            "bubble_radius": (
                self.bubble_radius
            ),

            "question_bubble_gap": (
                self.question_bubble_gap
            ),

            "choices": "".join(
                self.choices
            ),
        }

        raw = json.dumps(
            data,
            sort_keys=True,
            separators=(
                ",",
                ":"
            )
        ).encode(
            "utf-8"
        )

        digest = hashlib.sha256(
            raw
        ).hexdigest()

        return (
            "TPL-"
            + digest[:12].upper()
        )

    # ========================================================
    # QUESTION NUMBER WIDTH
    #
    # Same PIL font as generator.
    # ========================================================

    def question_number_width(
        self,
        number
    ):

        text = (
            f"{number}."
        )

        font = (
            load_generator_font(
                32
            )
        )

        temporary = Image.new(
            "RGB",
            (
                1,
                1
            )
        )

        draw = ImageDraw.Draw(
            temporary
        )

        bbox = draw.textbbox(
            (
                0,
                0
            ),
            text,
            font=font
        )

        return (
            bbox[2]
            - bbox[0]
        )

    # ========================================================
    # QUESTIONS PER COLUMN
    # ========================================================

    def questions_per_column(
        self
    ):

        available_height = (
            self.height
            - self.start_y
            - self.bottom_margin
        )

        return max(
            1,
            available_height
            // self.question_spacing
        )

    # ========================================================
    # QUESTION WIDTH
    # ========================================================

    def question_width(
        self
    ):

        number_width = (
            self.question_number_width(
                999
            )
        )

        bubble_area = (

            self.question_bubble_gap

            + (
                self.bubble_radius
                * 2
            )

            + (
                max(
                    0,
                    len(self.choices)
                    - 1
                )
                * self.bubble_spacing
            )
        )

        return (
            number_width
            + bubble_area
        )

    # ========================================================
    # MAX COLUMNS
    # ========================================================

    def max_columns(
        self
    ):

        usable_width = (
            self.width
            - 2 * self.margin
        )

        question_width = (
            self.question_width()
        )

        if question_width <= 0:

            return 1

        columns = (
            usable_width
            + self.column_gap
        ) // (
            question_width
            + self.column_gap
        )

        return max(
            1,
            int(columns)
        )

    # ========================================================
    # GENERATE QUESTION COORDINATES
    #
    # Mirrors draw_questions() from generator.
    # ========================================================

    def generate_questions(
        self,
        first_question,
        question_count
    ):

        rows = (
            self.questions_per_column()
        )

        columns = math.ceil(
            question_count
            / rows
        )

        max_columns = (
            self.max_columns()
        )

        columns = min(
            columns,
            max_columns
        )

        usable_width = (
            self.width
            - 2 * self.margin
        )

        column_width = (
            usable_width
            - (
                columns - 1
            )
            * self.column_gap
        ) // columns

        questions = []

        for local_index in range(
            question_count
        ):

            question_number = (
                first_question
                + local_index
            )

            column = (
                local_index
                // rows
            )

            row = (
                local_index
                % rows
            )

            x = (
                self.margin
                + column
                * (
                    column_width
                    + self.column_gap
                )
            )

            y = (
                self.start_y
                + row
                * self.question_spacing
            )

            question_width = (
                self.question_number_width(
                    question_number
                )
            )

            bubble_start_x = (
                x
                + question_width
                + self.question_bubble_gap
                + self.bubble_radius
            )

            bubbles = []

            for option_index in range(
                len(self.choices)
            ):

                bubble_x = (
                    bubble_start_x
                    + option_index
                    * self.bubble_spacing
                )

                bubbles.append(
                    (
                        bubble_x,
                        y
                    )
                )

            questions.append(
                {
                    "question": (
                        question_number
                    ),

                    "bubbles": bubbles,

                    "column": column,

                    "row": row,
                }
            )

        return questions


# ============================================================
# QR DECODER
# ============================================================

class QRDecoder:

    def __init__(
        self
    ):

        self.detector = (
            cv2.QRCodeDetector()
        )

    # ========================================================
    # DECODE
    # ========================================================

    def decode(
        self,
        image
    ):

        candidates = []

        # Original
        candidates.append(
            image
        )

        # Grayscale
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        candidates.append(
            gray
        )

        # Enlarged grayscale
        candidates.append(
            cv2.resize(
                gray,
                None,
                fx=1.5,
                fy=1.5,
                interpolation=(
                    cv2.INTER_CUBIC
                )
            )
        )

        # Binary
        candidates.append(
            cv2.threshold(
                gray,
                180,
                255,
                cv2.THRESH_BINARY
            )[1]
        )

        # ----------------------------------------------------
        # Standard detector
        # ----------------------------------------------------

        for candidate in candidates:

            try:

                data, points, _ = (
                    self.detector.detectAndDecode(
                        candidate
                    )
                )

                if data:

                    return self.parse(
                        data
                    )

            except Exception:

                continue

        # ----------------------------------------------------
        # Multi detector
        # ----------------------------------------------------

        try:

            data, points, _ = (
                self.detector.detectAndDecodeMulti(
                    image
                )
            )

            if data:

                for item in data:

                    if item:

                        return self.parse(
                            item
                        )

        except Exception:

            pass

        return None

    # ========================================================
    # PARSE QR
    # ========================================================

    @staticmethod
    def parse(
        data
    ):

        data = str(
            data
        ).strip()

        # ====================================================
        # CURRENT OMR1 FORMAT
        # ====================================================

        if data.startswith(
            QR_PREFIX
        ):

            encoded = data[
                len(QR_PREFIX):
            ]

            compressed = (
                base64.urlsafe_b64decode(
                    encoded.encode(
                        "ascii"
                    )
                )
            )

            raw = (
                zlib.decompress(
                    compressed
                )
                .decode(
                    "utf-8"
                )
            )

            payload = json.loads(
                raw
            )

            if payload.get(
                "v"
            ) != 1:

                raise ValueError(
                    "Unsupported OMR QR version."
                )

            return payload

        # ====================================================
        # LEGACY JSON
        # ====================================================

        if data.startswith(
            "{"
        ):

            old = json.loads(
                data
            )

            return {

                "v": old.get(
                    "version",
                    1
                ),

                "sheet": {

                    "id": old.get(
                        "sheet_id",
                        old.get(
                            "id",
                            ""
                        )
                    ),

                    "page": old.get(
                        "page",
                        1
                    ),

                    "pages": old.get(
                        "pages",
                        1
                    ),

                    "first": old.get(
                        "first_question",
                        1
                    ),

                    "count": old.get(
                        "questions_on_page",
                        0
                    ),
                },

                "template": old,

                "student": {},
            }

        # ====================================================
        # VERY OLD SHEET-ID-ONLY QR
        # ====================================================

        return {

            "v": 0,

            "sheet": {

                "id": data,

                "page": 1,

                "pages": 1,

                "first": 1,

                "count": 0,
            },

            "template": None,

            "student": {},
        }


# ============================================================
# TEMPLATE LIBRARY
# ============================================================

class TemplateLibrary:

    def __init__(
        self,
        directory
    ):

        self.directory = Path(
            directory
        )

        self.templates = {}

        self.load()

    # ========================================================
    # LOAD ALL JSON TEMPLATES
    # ========================================================

    def load(
        self
    ):

        self.templates.clear()

        if not self.directory.exists():

            print(
                "[Template] Directory not found:",
                self.directory
            )

            return

        for path in sorted(
            self.directory.rglob(
                "*.json"
            )
        ):

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(
                        file
                    )

                if not isinstance(
                    data,
                    dict
                ):

                    continue

                template = (
                    OMRTemplate(
                        data
                    )
                )

                self.templates[
                    template.template_id
                ] = {

                    "template": template,

                    "path": path,
                }

            except Exception as error:

                print(
                    "[Template] "
                    f"Skipping {path}: "
                    f"{error}"
                )

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        template_id
    ):

        if not template_id:

            return None

        entry = (
            self.templates.get(
                str(
                    template_id
                )
            )
        )

        if entry is None:

            return None

        return entry[
            "template"
        ]

    # ========================================================
    # ADD
    # ========================================================

    def add(
        self,
        template
    ):

        self.templates[
            template.template_id
        ] = {

            "template": template,

            "path": None,
        }

    # ========================================================
    # PRINT
    # ========================================================

    def print_templates(
        self
    ):

        print()
        print(
            "========== TEMPLATES =========="
        )

        if not self.templates:

            print(
                "No JSON templates found."
            )

            return

        for template_id, entry in (
            self.templates.items()
        ):

            print(
                template_id,
                "->",
                entry["path"]
            )


# ============================================================
# CREATE TEMPLATE FROM QR
# ============================================================

def build_template_from_qr(
    payload
):

    if not payload:

        return None

    template_data = (
        payload.get(
            "template"
        )
    )

    if not isinstance(
        template_data,
        dict
    ):

        return None

    return OMRTemplate(
        template_data
    )


# ============================================================
# REGISTRATION DETECTOR
# ============================================================

class RegistrationDetector:

    def __init__(
        self,
        marker_size
    ):

        self.marker_size = (
            marker_size
        )

    # ========================================================
    # MAIN
    # ========================================================

    def detect(
        self,
        image,
        template
    ):

        height, width = (
            image.shape[:2]
        )

        # ====================================================
        # METHOD 1:
        # EXACT CANONICAL IMAGE
        # ====================================================

        if (
            width
            == template.width

            and

            height
            == template.height
        ):

            print(
                "[Geometry] "
                "Canonical image dimensions detected."
            )

            return {

                "type": "canonical",

                "points": np.array(
                    [
                        [
                            0,
                            0
                        ],

                        [
                            width - 1,
                            0
                        ],

                        [
                            width - 1,
                            height - 1
                        ],

                        [
                            0,
                            height - 1
                        ],
                    ],

                    dtype=np.float32
                )
            }

        # ====================================================
        # METHOD 2:
        # REGISTRATION MARKERS
        # ====================================================

        markers = (
            self.detect_markers(
                image
            )
        )

        if markers is not None:

            print(
                "[Geometry] "
                "Registration markers detected."
            )

            return {

                "type": "markers",

                "points": markers
            }

        # ====================================================
        # METHOD 3:
        # PAGE BORDER
        # ====================================================

        border = (
            self.detect_page_border(
                image
            )
        )

        if border is not None:

            print(
                "[Geometry] "
                "Page border detected."
            )

            return {

                "type": "page_border",

                "points": border
            }

        return None

    # ========================================================
    # MARKERS
    # ========================================================

    def detect_markers(
        self,
        image
    ):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        threshold = cv2.threshold(
            gray,
            100,
            255,
            cv2.THRESH_BINARY_INV
        )[1]

        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        h, w = gray.shape

        candidates = []

        expected = float(
            self.marker_size
        )

        minimum = (
            expected * 0.35
        )

        maximum = (
            expected * 2.8
        )

        for contour in contours:

            x, y, cw, ch = (
                cv2.boundingRect(
                    contour
                )
            )

            if (
                cw < minimum
                or ch < minimum
            ):

                continue

            if (
                cw > maximum
                or ch > maximum
            ):

                continue

            aspect = (
                cw
                / float(
                    max(
                        1,
                        ch
                    )
                )
            )

            if not (
                0.65
                <= aspect
                <= 1.35
            ):

                continue

            candidates.append(
                (
                    x + cw / 2,
                    y + ch / 2,
                    cw,
                    ch
                )
            )

        if len(
            candidates
        ) < 4:

            return None

        corners = [

            ("TL", 0, 0),

            ("TR", w, 0),

            ("BR", w, h),

            ("BL", 0, h),
        ]

        selected = {}

        for name, cx, cy in corners:

            selected[
                name
            ] = min(

                candidates,

                key=lambda item:
                (
                    item[0] - cx
                ) ** 2

                +

                (
                    item[1] - cy
                ) ** 2
            )

        return np.array(
            [

                [
                    selected["TL"][0],
                    selected["TL"][1]
                ],

                [
                    selected["TR"][0],
                    selected["TR"][1]
                ],

                [
                    selected["BR"][0],
                    selected["BR"][1]
                ],

                [
                    selected["BL"][0],
                    selected["BL"][1]
                ],
            ],

            dtype=np.float32
        )

    # ========================================================
    # PAGE BORDER
    # ========================================================

    @staticmethod
    def detect_page_border(
        image
    ):

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        blurred = cv2.GaussianBlur(
            gray,
            (
                5,
                5
            ),
            0
        )

        edges = cv2.Canny(
            blurred,
            40,
            150
        )

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        height, width = (
            gray.shape
        )

        image_area = (
            width
            * height
        )

        candidates = []

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area < (
                image_area
                * 0.30
            ):

                continue

            perimeter = (
                cv2.arcLength(
                    contour,
                    True
                )
            )

            if perimeter <= 0:

                continue

            polygon = (
                cv2.approxPolyDP(
                    contour,
                    0.02
                    * perimeter,
                    True
                )
            )

            if len(
                polygon
            ) != 4:

                continue

            points = (
                polygon
                .reshape(
                    4,
                    2
                )
                .astype(
                    np.float32
                )
            )

            candidates.append(
                (
                    area,
                    points
                )
            )

        if not candidates:

            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return (
            self.order_points(
                candidates[0][1]
            )
        )

    # ========================================================
    # ORDER FOUR POINTS
    # ========================================================

    @staticmethod
    def order_points(
        points
    ):

        points = np.asarray(
            points,
            dtype=np.float32
        )

        result = np.zeros(
            (
                4,
                2
            ),
            dtype=np.float32
        )

        sums = (
            points[:, 0]
            + points[:, 1]
        )

        differences = (
            points[:, 0]
            - points[:, 1]
        )

        result[0] = (
            points[
                np.argmin(
                    sums
                )
            ]
        )

        result[1] = (
            points[
                np.argmax(
                    differences
                )
            ]
        )

        result[2] = (
            points[
                np.argmax(
                    sums
                )
            ]
        )

        result[3] = (
            points[
                np.argmin(
                    differences
                )
            ]
        )

        return result


# ============================================================
# PAGE RECTIFIER
# ============================================================

class PageRectifier:

    def rectify(
        self,
        image,
        template
    ):

        detector = (
            RegistrationDetector(
                template.registration_marker_size
            )
        )

        detection = detector.detect(
            image,
            template
        )

        if detection is None:

            raise RuntimeError(
                "Could not determine page geometry."
            )

        geometry_type = (
            detection["type"]
        )

        source = (
            detection["points"]
        )

        # ====================================================
        # CANONICAL
        # ====================================================

        if geometry_type == "canonical":

            return (
                image.copy(),
                source,
                geometry_type
            )

        # ====================================================
        # PAGE BORDER
        # ====================================================

        if (
            geometry_type
            == "page_border"
        ):

            target = np.array(
                [
                    [
                        0,
                        0
                    ],

                    [
                        template.width - 1,
                        0
                    ],

                    [
                        template.width - 1,
                        template.height - 1
                    ],

                    [
                        0,
                        template.height - 1
                    ],
                ],
                dtype=np.float32
            )

        # ====================================================
        # REGISTRATION MARKERS
        # ====================================================

        else:

            marker_size = (
                template.registration_marker_size
            )

            marker_margin = (
                template.registration_marker_margin
            )

            half = (
                marker_size
                / 2.0
            )

            target = np.array(
                [

                    [
                        marker_margin
                        + half,

                        marker_margin
                        + half
                    ],

                    [
                        template.width
                        - marker_margin
                        - half,

                        marker_margin
                        + half
                    ],

                    [
                        template.width
                        - marker_margin
                        - half,

                        template.height
                        - marker_margin
                        - half
                    ],

                    [
                        marker_margin
                        + half,

                        template.height
                        - marker_margin
                        - half
                    ],
                ],
                dtype=np.float32
            )

        matrix = (
            cv2.getPerspectiveTransform(
                source,
                target
            )
        )

        corrected = (
            cv2.warpPerspective(
                image,
                matrix,
                (
                    template.width,
                    template.height
                ),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=255
            )
        )

        return (
            corrected,
            source,
            geometry_type
        )


# ============================================================
# BUBBLE READER
# ============================================================

class BubbleReader:

    def __init__(
        self,
        blank_threshold=0.055,
        ambiguity_margin=0.020
    ):

        self.blank_threshold = (
            blank_threshold
        )

        self.ambiguity_margin = (
            ambiguity_margin
        )

    # ========================================================
    # SCORE
    # ========================================================

    @staticmethod
    def score(
        gray,
        x,
        y,
        radius
    ):

        x = int(
            round(x)
        )

        y = int(
            round(y)
        )

        inner_radius = max(
            3,
            int(
                radius
                * 0.42
            )
        )

        outer_radius = max(
            inner_radius + 3,
            int(
                radius
                * 0.82
            )
        )

        x1 = max(
            0,
            x - outer_radius
        )

        y1 = max(
            0,
            y - outer_radius
        )

        x2 = min(
            gray.shape[1],
            x + outer_radius + 1
        )

        y2 = min(
            gray.shape[0],
            y + outer_radius + 1
        )

        roi = gray[
            y1:y2,
            x1:x2
        ]

        if roi.size == 0:

            return 0.0

        center_x = (
            x - x1
        )

        center_y = (
            y - y1
        )

        yy, xx = np.ogrid[
            0:roi.shape[0],
            0:roi.shape[1]
        ]

        distance_squared = (
            (
                xx
                - center_x
            ) ** 2
            +
            (
                yy
                - center_y
            ) ** 2
        )

        inner_mask = (
            distance_squared
            <= inner_radius ** 2
        )

        outer_mask = (
            distance_squared
            <= outer_radius ** 2
        )

        inner_pixels = (
            roi[
                inner_mask
            ]
        )

        outer_pixels = (
            roi[
                outer_mask
                & ~inner_mask
            ]
        )

        if (
            inner_pixels.size == 0
            or outer_pixels.size == 0
        ):

            return 0.0

        inner_mean = float(
            np.mean(
                inner_pixels
            )
        )

        outer_mean = float(
            np.mean(
                outer_pixels
            )
        )

        contrast = (
            outer_mean
            - inner_mean
        )

        return max(
            0.0,
            float(
                contrast
                / 255.0
            )
        )

    # ========================================================
    # READ QUESTION
    # ========================================================

    def read_question(
        self,
        gray,
        question,
        template
    ):

        scores = []

        for x, y in (
            question[
                "bubbles"
            ]
        ):

            scores.append(
                self.score(
                    gray,
                    x,
                    y,
                    template.bubble_radius
                )
            )

        if not scores:

            return {

                "answer": "?",

                "scores": [],

                "confidence": 0.0,
            }

        ranked = np.argsort(
            scores
        )[::-1]

        best_index = int(
            ranked[0]
        )

        best_score = float(
            scores[
                best_index
            ]
        )

        if len(
            scores
        ) > 1:

            second_score = float(
                scores[
                    ranked[1]
                ]
            )

        else:

            second_score = 0.0

        confidence = (
            best_score
            - second_score
        )

        if (
            best_score
            < self.blank_threshold
        ):

            answer = "-"

        elif (
            confidence
            < self.ambiguity_margin
        ):

            answer = "?"

        else:

            answer = (
                template.choices[
                    best_index
                ]
            )

        return {

            "answer": answer,

            "scores": [
                round(
                    float(score),
                    4
                )
                for score in scores
            ],

            "confidence": round(
                float(confidence),
                4
            ),
        }


# ============================================================
# OMR SCANNER
# ============================================================

class OMRScanner:

    def __init__(
        self,
        templates_directory=TEMPLATES_DIR
    ):

        self.template_library = (
            TemplateLibrary(
                templates_directory
            )
        )

        self.qr_decoder = (
            QRDecoder()
        )

        self.rectifier = (
            PageRectifier()
        )

        self.reader = (
            BubbleReader()
        )

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    @staticmethod
    def load_image(
        path
    ):

        image = cv2.imread(
            str(path)
        )

        if image is None:

            raise RuntimeError(
                f"Could not read image:\n"
                f"{path}"
            )

        return image

    # ========================================================
    # DECODE QR
    # ========================================================

    def decode_qr(
        self,
        image
    ):

        try:

            payload = (
                self.qr_decoder.decode(
                    image
                )
            )

            if payload:

                return payload

        except Exception as error:

            print(
                "[QR] Decode error:",
                error
            )

        return None

    # ========================================================
    # RESOLVE TEMPLATE
    # ========================================================

    def resolve_template(
        self,
        payload,
        forced_template_id=None
    ):

        # ----------------------------------------------------
        # Explicit template override
        # ----------------------------------------------------

        if forced_template_id:

            template = (
                self.template_library.get(
                    forced_template_id
                )
            )

            if template is None:

                raise RuntimeError(
                    "Template not found:\n"
                    f"{forced_template_id}"
                )

            print(
                "[Template] Forced:",
                forced_template_id
            )

            return template

        # ----------------------------------------------------
        # Template embedded in QR
        # ----------------------------------------------------

        if payload:

            qr_template = (
                build_template_from_qr(
                    payload
                )
            )

            if qr_template:

                local = (
                    self.template_library.get(
                        qr_template.template_id
                    )
                )

                if local:

                    print(
                        "[Template] "
                        "Using local:",
                        qr_template.template_id
                    )

                    return local

                print(
                    "[Template] "
                    "Using embedded QR:",
                    qr_template.template_id
                )

                self.template_library.add(
                    qr_template
                )

                return qr_template

        raise RuntimeError(
            "No usable template available."
        )

    # ========================================================
    # PAGE METADATA
    # ========================================================

    @staticmethod
    def get_page_metadata(
        payload
    ):

        if not payload:

            return {

                "sheet_id": "",

                "page": 1,

                "pages": 1,

                "first_question": 1,

                "questions_on_page": 0,

                "student": {},
            }

        sheet = payload.get(
            "sheet",
            {}
        )

        student = payload.get(
            "student",
            {}
        )

        return {

            "sheet_id": str(
                sheet.get(
                    "id",
                    ""
                )
            ),

            "page": int(
                sheet.get(
                    "page",
                    1
                )
            ),

            "pages": int(
                sheet.get(
                    "pages",
                    1
                )
            ),

            "first_question": int(
                sheet.get(
                    "first",
                    1
                )
            ),

            "questions_on_page": int(
                sheet.get(
                    "count",
                    0
                )
            ),

            "student": student,
        }

    # ========================================================
    # FALLBACK COUNT
    # ========================================================

    @staticmethod
    def fallback_question_count(
        template
    ):

        return (
            template.questions_per_column()
            * template.max_columns()
        )

    # ========================================================
    # SCAN ONE PAGE
    # ========================================================

    def scan_page(
        self,
        image,
        forced_template_id=None,
        debug_path=None
    ):

        print()
        print(
            "========================================"
        )

        print(
            "SCANNING PAGE"
        )

        print(
            "========================================"
        )

        print(
            "Input:",
            image.shape[1],
            "x",
            image.shape[0]
        )

        # ====================================================
        # QR
        # ====================================================

        payload = (
            self.decode_qr(
                image
            )
        )

        print(
            "[QR]:",
            "DETECTED"
            if payload
            else "NOT DETECTED"
        )

        # ====================================================
        # TEMPLATE
        # ====================================================

        template = (
            self.resolve_template(
                payload,
                forced_template_id
            )
        )

        print(
            "[Template]:",
            template.template_id
        )

        print(
            "[Template]:",
            template.page_size,
            template.orientation
        )

        print(
            "[Template]:",
            template.width,
            "x",
            template.height
        )

        print(
            "[Template] Choices:",
            "".join(
                template.choices
            )
        )

        # ====================================================
        # PAGE METADATA
        # ====================================================

        page_info = (
            self.get_page_metadata(
                payload
            )
        )

        first_question = (
            page_info[
                "first_question"
            ]
        )

        question_count = (
            page_info[
                "questions_on_page"
            ]
        )

        if question_count <= 0:

            question_count = (
                self.fallback_question_count(
                    template
                )
            )

            print(
                "[Page] "
                "Using fallback capacity:",
                question_count
            )

        print(
            "[Page]:",
            page_info["page"],
            "/",
            page_info["pages"]
        )

        print(
            "[Page] First question:",
            first_question
        )

        print(
            "[Page] Questions:",
            question_count
        )

        # ====================================================
        # RECTIFY
        # ====================================================

        (
            corrected,
            geometry_points,
            geometry_type
        ) = (
            self.rectifier.rectify(
                image,
                template
            )
        )

        print(
            "[Geometry]:",
            geometry_type
        )

        print(
            "[Working image]:",
            corrected.shape[1],
            "x",
            corrected.shape[0]
        )

        # ====================================================
        # EXPECTED QUESTIONS
        # ====================================================

        questions = (
            template.generate_questions(
                first_question,
                question_count
            )
        )

        print(
            "[Layout] Questions generated:",
            len(questions)
        )

        print(
            "[Layout] Rows:",
            template.questions_per_column()
        )

        print(
            "[Layout] Columns:",
            max(
                (
                    question[
                        "column"
                    ]
                    for question
                    in questions
                ),
                default=0
            ) + 1
        )

        # ====================================================
        # GRAYSCALE
        # ====================================================

        gray = cv2.cvtColor(
            corrected,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (
                3,
                3
            ),
            0
        )

        # ====================================================
        # READ ANSWERS
        # ====================================================

        results = []

        print()
        print(
            "========== ANSWERS =========="
        )

        for question in questions:

            measurement = (
                self.reader.read_question(
                    gray,
                    question,
                    template
                )
            )

            result = {

                "question": (
                    question[
                        "question"
                    ]
                ),

                "answer": (
                    measurement[
                        "answer"
                    ]
                ),

                "scores": (
                    measurement[
                        "scores"
                    ]
                ),

                "confidence": (
                    measurement[
                        "confidence"
                    ]
                ),

                "column": (
                    question[
                        "column"
                    ]
                ),

                "row": (
                    question[
                        "row"
                    ]
                ),
            }

            results.append(
                result
            )

            print(
                f"Q{result['question']:03d}: "
                f"{result['answer']:<2} "
                f"{result['scores']}"
            )

        # ====================================================
        # DEBUG IMAGE
        # ====================================================

        if debug_path is not None:

            debug_path = Path(
                debug_path
            )

            debug_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            debug = corrected.copy()

            for question, result in zip(
                questions,
                results
            ):

                answer = (
                    result[
                        "answer"
                    ]
                )

                for option_index, (
                    x,
                    y
                ) in enumerate(
                    question[
                        "bubbles"
                    ]
                ):

                    x = int(
                        round(x)
                    )

                    y = int(
                        round(y)
                    )

                    choice = (
                        template.choices[
                            option_index
                        ]
                    )

                    if answer == choice:

                        color = (
                            0,
                            255,
                            0
                        )

                    elif answer == "?":

                        color = (
                            0,
                            255,
                            255
                        )

                    else:

                        color = (
                            255,
                            0,
                            0
                        )

                    cv2.circle(
                        debug,

                        (
                            x,
                            y
                        ),

                        max(
                            8,
                            int(
                                template.bubble_radius
                                * 0.55
                            )
                        ),

                        color,

                        2
                    )

                    cv2.putText(
                        debug,

                        choice,

                        (
                            x - 6,
                            y + 6
                        ),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.45,

                        (
                            0,
                            0,
                            255
                        ),

                        1,

                        cv2.LINE_AA
                    )

                first_x = int(
                    round(
                        question[
                            "bubbles"
                        ][0][0]
                    )
                )

                first_y = int(
                    round(
                        question[
                            "bubbles"
                        ][0][1]
                    )
                )

                cv2.putText(
                    debug,

                    str(
                        result[
                            "question"
                        ]
                    ),

                    (
                        first_x - 55,
                        first_y + 6
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.55,

                    (
                        255,
                        0,
                        0
                    ),

                    1,

                    cv2.LINE_AA
                )

            cv2.imwrite(
                str(
                    debug_path
                ),
                debug
            )

            print(
                "[Debug] Saved:",
                debug_path
            )

        # ====================================================
        # RESULT
        # ====================================================

        return {

            "success": True,

            "sheet_id": (
                page_info[
                    "sheet_id"
                ]
            ),

            "page": (
                page_info[
                    "page"
                ]
            ),

            "pages": (
                page_info[
                    "pages"
                ]
            ),

            "first_question": (
                first_question
            ),

            "questions_on_page": (
                question_count
            ),

            "template_id": (
                template.template_id
            ),

            "template": {

                "page_size": (
                    template.page_size
                ),

                "orientation": (
                    template.orientation
                ),

                "width": (
                    template.width
                ),

                "height": (
                    template.height
                ),

                "choices": "".join(
                    template.choices
                ),

                "bubble_radius": (
                    template.bubble_radius
                ),

                "bubble_spacing": (
                    template.bubble_spacing
                ),

                "question_spacing": (
                    template.question_spacing
                ),

                "column_gap": (
                    template.column_gap
                ),
            },

            "student": (
                page_info[
                    "student"
                ]
            ),

            "questions": results,

            "qr_detected": (
                payload is not None
            ),

            "geometry": geometry_type,

            "geometry_points": (
                geometry_points.tolist()
            ),
        }


# ============================================================
# FILE INPUT HANDLING
# ============================================================

def load_image_file(
    path
):

    path = Path(
        path
    )

    image = cv2.imread(
        str(path)
    )

    if image is None:

        raise RuntimeError(
            f"Could not read image:\n"
            f"{path}"
        )

    return image


# ============================================================
# PDF PAGE RENDERER
# ============================================================

def render_pdf_page(
    document,
    page_index
):

    page = document.load_page(
        page_index
    )

    matrix = fitz.Matrix(
        PDF_SCALE,
        PDF_SCALE
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        colorspace=fitz.csRGB,
        alpha=False
    )

    channels = (
        pixmap.n
    )

    array = np.frombuffer(
        pixmap.samples,
        dtype=np.uint8
    )

    array = array.reshape(
        pixmap.height,
        pixmap.width,
        channels
    )

    if channels >= 3:

        array = cv2.cvtColor(
            array,
            cv2.COLOR_RGB2BGR
        )

    return array


# ============================================================
# FIND INPUT FILES
# ============================================================

def find_input_files(
    path
):

    path = Path(
        path
    )

    # --------------------------------------------------------
    # Single file
    # --------------------------------------------------------

    if path.is_file():

        extension = (
            path.suffix.lower()
        )

        if extension not in (
            SUPPORTED_EXTENSIONS
        ):

            raise ValueError(
                f"Unsupported file type: "
                f"{extension}\n"
                "Supported: "
                ".png, .jpg, .jpeg, .pdf"
            )

        return [
            path
        ]

    # --------------------------------------------------------
    # Directory
    # --------------------------------------------------------

    if path.is_dir():

        files = []

        for file in sorted(
            path.rglob("*")
        ):

            if not file.is_file():

                continue

            if (
                file.suffix.lower()
                in SUPPORTED_EXTENSIONS
            ):

                files.append(
                    file
                )

        return files

    raise FileNotFoundError(
        f"Input does not exist:\n"
        f"{path}"
    )


# ============================================================
# OUTPUT JSON PATH
# ============================================================

def get_json_path(
    input_file,
    output_directory
):

    input_file = Path(
        input_file
    )

    output_directory = Path(
        output_directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output = (
        output_directory
        / (
            input_file.stem
            + ".json"
        )
    )

    # --------------------------------------------------------
    # Prevent collisions:
    #
    # exam.pdf
    # exam.png
    #
    # --------------------------------------------------------

    if output.exists():

        output = (
            output_directory
            / (
                input_file.stem
                + "_"
                + input_file.suffix
                .lower()
                .replace(
                    ".",
                    ""
                )
                + ".json"
            )
        )

    return output


# ============================================================
# IMAGE FILE
# ============================================================

def scan_image_file(
    scanner,
    input_file,
    debug_directory,
    forced_template_id
):

    input_file = Path(
        input_file
    )

    print()
    print(
        "========================================"
    )

    print(
        "FILE:",
        input_file
    )

    print(
        "TYPE: IMAGE"
    )

    print(
        "========================================"
    )

    image = load_image_file(
        input_file
    )

    debug_path = (
        Path(debug_directory)
        / (
            input_file.stem
            + "_page_1_debug.png"
        )
    )

    result = scanner.scan_page(

        image,

        forced_template_id=(
            forced_template_id
        ),

        debug_path=debug_path
    )

    return {

        "success": bool(
            result.get(
                "success",
                False
            )
        ),

        "source": {

            "file": str(
                input_file
            ),

            "type": "image",

            "format": (
                input_file.suffix
                .lower()
                .lstrip(".")
            ),
        },

        "pages": [

            result
        ],
    }


# ============================================================
# PDF FILE
# ============================================================

def scan_pdf_file(
    scanner,
    input_file,
    debug_directory,
    forced_template_id
):

    input_file = Path(
        input_file
    )

    print()
    print(
        "========================================"
    )

    print(
        "FILE:",
        input_file
    )

    print(
        "TYPE: PDF"
    )

    print(
        "========================================"
    )

    document = fitz.open(
        str(input_file)
    )

    try:

        page_count = (
            document.page_count
        )

        if page_count <= 0:

            raise RuntimeError(
                "PDF contains no pages."
            )

        print(
            "PDF pages:",
            page_count
        )

        page_results = []

        for page_index in range(
            page_count
        ):

            page_number = (
                page_index + 1
            )

            print()
            print(
                "----------------------------------------"
            )

            print(
                f"PDF PAGE "
                f"{page_number} "
                f"/ "
                f"{page_count}"
            )

            print(
                "----------------------------------------"
            )

            image = render_pdf_page(
                document,
                page_index
            )

            debug_path = (
                Path(debug_directory)
                / (
                    input_file.stem
                    + f"_page_{page_number}_debug.png"
                )
            )

            result = scanner.scan_page(

                image,

                forced_template_id=(
                    forced_template_id
                ),

                debug_path=debug_path
            )

            page_results.append(
                result
            )

        return {

            "success": all(
                page.get(
                    "success",
                    False
                )
                for page in page_results
            ),

            "source": {

                "file": str(
                    input_file
                ),

                "type": "pdf",

                "format": "pdf",

                "page_count": (
                    page_count
                ),
            },

            "pages": page_results,
        }

    finally:

        document.close()


# ============================================================
# SCAN FILE
# ============================================================

def scan_file(
    scanner,
    input_file,
    debug_directory,
    forced_template_id
):

    extension = (
        Path(
            input_file
        )
        .suffix
        .lower()
    )

    if extension == ".pdf":

        return scan_pdf_file(

            scanner,

            input_file,

            debug_directory,

            forced_template_id
        )

    if extension in IMAGE_EXTENSIONS:

        return scan_image_file(

            scanner,

            input_file,

            debug_directory,

            forced_template_id
        )

    raise ValueError(
        f"Unsupported file type: "
        f"{extension}"
    )


# ============================================================
# DOCUMENT SUMMARY
# ============================================================

def build_document_summary(
    document
):

    pages = document.get(
        "pages",
        []
    )

    first_page = (
        pages[0]
        if pages
        else {}
    )

    student = (
        first_page.get(
            "student",
            {}
        )
    )

    sheet_id = (
        first_page.get(
            "sheet_id",
            ""
        )
    )

    template_id = (
        first_page.get(
            "template_id",
            ""
        )
    )

    answers = {}

    for page in pages:

        for question in page.get(
            "questions",
            []
        ):

            number = str(
                question[
                    "question"
                ]
            )

            answers[
                number
            ] = question[
                "answer"
            ]

    return {

        "success": (
            document.get(
                "success",
                False
            )
        ),

        "source": document.get(
            "source",
            {}
        ),

        "sheet_id": sheet_id,

        "template_id": template_id,

        "student": student,

        "page_count": len(
            pages
        ),

        "answers": answers,

        "pages": pages,
    }


# ============================================================
# SAVE JSON
# ============================================================

def save_document_json(
    document,
    output_path
):

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary = (
        build_document_summary(
            document
        )
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            summary,

            file,

            indent=4,

            ensure_ascii=False
        )

    return output_path


# ============================================================
# BATCH SCANNER
# ============================================================

def scan_input(
    input_path,
    output_directory=JSON_OUTPUT_DIR,
    debug_directory=DEBUG_OUTPUT_DIR,
    templates_directory=TEMPLATES_DIR,
    forced_template_id=None
):

    input_files = find_input_files(
        input_path
    )

    if not input_files:

        print(
            "No supported files found."
        )

        return []

    print()
    print(
        "========================================"
    )

    print(
        "BATCH INPUT"
    )

    print(
        "========================================"
    )

    print(
        "Input:",
        input_path
    )

    print(
        "Files:",
        len(input_files)
    )

    for file in input_files:

        print(
            "  -",
            file
        )

    # --------------------------------------------------------
    # One scanner for entire batch.
    # --------------------------------------------------------

    scanner = OMRScanner(
        templates_directory
    )

    scanner.template_library.print_templates()

    results = []

    for input_file in input_files:

        try:

            document = scan_file(

                scanner,

                input_file,

                debug_directory,

                forced_template_id
            )

            json_path = (
                get_json_path(
                    input_file,
                    output_directory
                )
            )

            save_document_json(
                document,
                json_path
            )

            results.append({

                "input": str(
                    input_file
                ),

                "output": str(
                    json_path
                ),

                "success": bool(
                    document.get(
                        "success",
                        False
                    )
                ),

                "pages": len(
                    document.get(
                        "pages",
                        []
                    )
                ),
            })

            print()
            print(
                "[JSON] Saved:",
                json_path
            )

        except Exception as error:

            print()
            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

            print(
                "[ERROR]:",
                input_file
            )

            print(
                error
            )

            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

            error_document = {

                "success": False,

                "source": {

                    "file": str(
                        input_file
                    )
                },

                "error": str(
                    error
                ),

                "pages": [],
            }

            json_path = (
                get_json_path(
                    input_file,
                    output_directory
                )
            )

            with open(
                json_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    error_document,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            results.append({

                "input": str(
                    input_file
                ),

                "output": str(
                    json_path
                ),

                "success": False,

                "pages": 0,

                "error": str(
                    error
                ),
            })

    # ========================================================
    # BATCH SUMMARY
    # ========================================================

    successful = sum(

        1

        for item in results

        if item[
            "success"
        ]
    )

    failed = (
        len(results)
        - successful
    )

    total_pages = sum(

        item.get(
            "pages",
            0
        )

        for item in results
    )

    print()
    print(
        "========================================"
    )

    print(
        "BATCH SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        "Files:",
        len(results)
    )

    print(
        "Successful:",
        successful
    )

    print(
        "Failed:",
        failed
    )

    print(
        "Pages scanned:",
        total_pages
    )

    print(
        "JSON output:",
        output_directory
    )

    print(
        "Debug output:",
        debug_directory
    )

    return results


# ============================================================
# COMMAND LINE
# ============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "OMR scanner supporting PNG, "
            "JPG, JPEG, PDF and directory "
            "batch scanning."
        )
    )

    parser.add_argument(

        "input",

        nargs="?",

        default=str(
            DEFAULT_INPUT
        ),

        help=(
            "Image, PDF or directory."
        )
    )

    parser.add_argument(

        "--template",

        dest="template_id",

        default=None,

        help=(
            "Force a template ID from "
            "Templates/."
        )
    )

    parser.add_argument(

        "--templates",

        default=str(
            TEMPLATES_DIR
        ),

        help=(
            "Template directory."
        )
    )

    parser.add_argument(

        "--output",

        default=str(
            JSON_OUTPUT_DIR
        ),

        help=(
            "JSON output directory."
        )
    )

    parser.add_argument(

        "--debug-dir",

        default=str(
            DEBUG_OUTPUT_DIR
        ),

        help=(
            "Debug-image output directory."
        )
    )

    args = parser.parse_args()

    scan_input(

        input_path=(
            Path(
                args.input
            )
        ),

        output_directory=(
            Path(
                args.output
            )
        ),

        debug_directory=(
            Path(
                args.debug_dir
            )
        ),

        templates_directory=(
            Path(
                args.templates
            )
        ),

        forced_template_id=(
            args.template_id
        )
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()