import argparse
import base64
import hashlib
import json
import math
import zlib
from pathlib import Path

import cv2
from services.omr_identity import identity_coordinates
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def _load_pdf_library():
    try:
        import pymupdf as pdf_library
    except ImportError:
        import fitz as pdf_library
    return pdf_library


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
    / "Jhonny_Sheet_1.png" # "OMR_6769_Jhonny_Sins_page_1.png"
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

# QR/geometry robustness settings. These are deliberately generous so
# downscaled JPEGs and ordinary scanner output are still readable.
QR_CORNER_FRACTION = 0.32
QR_UPSCALE_FACTORS = (2.0, 3.0, 4.0)
ASPECT_RATIO_TOLERANCE = 0.035
AUTO_TEMPLATE_MIN_FIT = 0.12
AUTO_TEMPLATE_MIN_SEPARATION = 1.15


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

        self.identity = self.data.get("identity")

        self.template_id = (
            self.data.get(
                "template_id"
            )
        )

        if not self.template_id:

            self.template_id = (
                self.calculate_template_id()
            )

        self.question_count = self.data.get(
            "question_count"
        )

        self.student = dict(
            self.data.get(
                "student",
                {}
            )
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
        # QUESTION COUNT
        # ====================================================

        question_count = metadata.get(
            "question_count",
            metadata.get(
                "question_count_on_sheet",
                metadata.get(
                    "questions",
                    None
                )
            )
        )

        if question_count is not None:

            try:
                question_count = max(
                    0,
                    int(round(float(question_count)))
                )
            except (ValueError, TypeError):
                question_count = None

        result[
            "question_count"
        ] = question_count

        # ====================================================
        # CHOICES
        # ====================================================

        choices = metadata.get(
            "choices",
            None
        )

        # The GUI-friendly schema may specify only a number of options.
        # Preserve explicit labels when they exist; otherwise generate
        # the conventional A/B/C/D/E/F labels.
        if choices is None:

            options = metadata.get(
                "options",
                4
            )

            if isinstance(options, (list, tuple)):
                choices = "".join(
                    str(choice)
                    for choice in options
                )

            else:
                options_text = str(options).strip()
                if options_text.isdigit():
                    option_count = int(options_text)
                    choices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:option_count]
                else:
                    choices = options_text

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

        if isinstance(metadata.get("identity"), dict):
            result["identity"] = dict(metadata["identity"])

        # ====================================================
        # STUDENT/METADATA ALIASES
        # ====================================================

        result[
            "student"
        ] = {
            "name": str(metadata.get("name", "")).strip(),
            "class": str(metadata.get(
                "class",
                metadata.get("class_standard", "")
            )).strip(),
            "section": str(metadata.get(
                "section",
                metadata.get("class_division", "")
            )).strip(),
            "admission": str(metadata.get(
                "admission",
                metadata.get("admission_number", "")
            )).strip(),
            "subject": str(metadata.get("subject", "")).strip(),
        }

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

            "identity": self.identity,
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
        self,
        max_number=None
    ):

        if max_number is None:
            max_number = self.question_count or 999

        number_width = (
            self.question_number_width(
                max(1, int(max_number))
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
                    len(self.choices) - 1
                )
                * self.bubble_spacing
            )
        )

        return number_width + bubble_area

    # ========================================================
    # MAX COLUMNS
    # ========================================================

    def max_columns(
        self,
        max_number=None
    ):

        usable_width = (
            self.width
            - 2 * self.margin
        )

        question_width = (
            self.question_width(max_number)
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

        max_number = (
            self.question_count
            or (first_question + max(0, question_count - 1))
            or 1
        )

        max_columns = (
            self.max_columns(max_number)
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

        """Decode the OMR QR using whole-image and corner-focused passes.

        Generated sheets place the QR at one of the four page corners.
        A QR that is too small for the full-page detector can still be
        decoded reliably from a corner crop after enlargement.
        """

        if image is None or image.size == 0:
            return None

        candidates = []
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # Whole page first.
        candidates.append(image)
        candidates.append(gray)

        for scale in QR_UPSCALE_FACTORS:
            candidates.append(
                cv2.resize(
                    gray,
                    None,
                    fx=scale,
                    fy=scale,
                    interpolation=cv2.INTER_CUBIC
                )
            )

        candidates.append(
            cv2.threshold(
                gray,
                180,
                255,
                cv2.THRESH_BINARY
            )[1]
        )

        candidates.append(
            cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                5
            )
        )

        payload = self._try_candidates(candidates)
        if payload:
            return payload

        # Focus on each corner. This is the important fallback for
        # downscaled sheets such as 1131x1600 JPEGs.
        h, w = gray.shape[:2]
        frac = QR_CORNER_FRACTION
        corners = (
            (0, 0, int(w * frac), int(h * frac)),
            (int(w * (1 - frac)), 0, w, int(h * frac)),
            (int(w * (1 - frac)), int(h * (1 - frac)), w, h),
            (0, int(h * (1 - frac)), int(w * frac), h),
        )

        for x1, y1, x2, y2 in corners:
            crop = gray[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            crop_candidates = [crop]

            # CLAHE helps with uneven scanner/camera lighting.
            try:
                clahe = cv2.createCLAHE(
                    clipLimit=2.0,
                    tileGridSize=(8, 8)
                )
                crop_candidates.append(
                    clahe.apply(crop)
                )
            except Exception:
                pass

            crop_candidates.append(
                cv2.threshold(
                    crop,
                    180,
                    255,
                    cv2.THRESH_BINARY
                )[1]
            )

            crop_candidates.append(
                cv2.adaptiveThreshold(
                    crop,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    31,
                    5
                )
            )

            enlarged = []
            for candidate in crop_candidates:
                enlarged.append(candidate)
                for scale in QR_UPSCALE_FACTORS:
                    enlarged.append(
                        cv2.resize(
                            candidate,
                            None,
                            fx=scale,
                            fy=scale,
                            interpolation=cv2.INTER_CUBIC
                        )
                    )

            payload = self._try_candidates(enlarged)
            if payload:
                return payload

        # Last attempt with detectAndDecodeMulti.
        for candidate in candidates[:2]:
            try:
                data, _, _ = self.detector.detectAndDecodeMulti(
                    candidate
                )
                if data:
                    for item in data:
                        if item:
                            try:
                                return self.parse(item)
                            except Exception:
                                continue
            except Exception:
                continue

        return None

    def _try_candidates(
        self,
        candidates
    ):

        for candidate in candidates:
            try:
                data, _, _ = self.detector.detectAndDecode(
                    candidate
                )
                if data:
                    try:
                        return self.parse(data)
                    except Exception:
                        continue
            except Exception:
                continue

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

        self.template = template

        height, width = (
            image.shape[:2]
        )

        # ====================================================
        # METHOD 1:
        # EXACT CANONICAL IMAGE
        # ====================================================

        if (
            width == template.width
            and height == template.height
        ):

            print(
                "[Geometry] "
                "Canonical image dimensions detected."
            )

            return {
                "type": "canonical",
                "points": np.array(
                    [
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1],
                    ],
                    dtype=np.float32
                )
            }

        # A resized copy of the full page has the same aspect ratio even
        # though its pixel dimensions differ. Treat it as a scaled
        # canonical page. This is the exact case of a 2480x3508 sheet
        # saved as an 1131x1600 JPEG.
        image_ratio = width / float(max(1, height))
        template_ratio = template.width / float(max(1, template.height))

        ratio_error = abs(image_ratio - template_ratio) / max(
            template_ratio, 1e-9
        )

        if ratio_error <= ASPECT_RATIO_TOLERANCE:

            print(
                "[Geometry] Full-page aspect ratio match; "
                "rescaling to template dimensions."
            )

            return {
                "type": "scaled",
                "points": np.array(
                    [
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1],
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

        # Estimate the image scale relative to the canonical template.
        # This prevents a 60 px marker from being rejected when a page
        # has been resized to roughly half resolution.
        template = getattr(self, "template", None)
        scale_candidates = []
        if template is not None:
            if template.width > 0 and template.height > 0:
                scale_candidates.append(
                    width / float(template.width)
                )
                scale_candidates.append(
                    height / float(template.height)
                )

        scale = float(np.median(scale_candidates)) if scale_candidates else 1.0
        expected_scaled = max(4.0, expected * scale)

        minimum = max(4.0, expected_scaled * 0.35)
        maximum = max(minimum + 2.0, expected_scaled * 3.5)

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
                * 0.20
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
        # SCALED FULL PAGE
        # ====================================================

        if geometry_type == "scaled":

            corrected = cv2.resize(
                image,
                (template.width, template.height),
                interpolation=cv2.INTER_CUBIC
            )

            return (
                corrected,
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
        blank_threshold=0.30,
        ambiguity_margin=0.020,
        mark_threshold=0.30
    ):

        self.blank_threshold = (
            blank_threshold
        )

        self.ambiguity_margin = (
            ambiguity_margin
        )

        # Scores above this value represent substantial ink inside a
        # bubble. If more than one option crosses it, the question is
        # treated as ambiguous instead of forcing a false answer.
        self.mark_threshold = (
            mark_threshold
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

        """Score actual ink inside the bubble, not just its printed outline."""

        x = int(round(x))
        y = int(round(y))
        radius = max(3, int(round(radius)))

        # The old detector compared the bubble center with the ring around
        # it. That works for a faint scribble, but a fully filled bubble
        # darkens both regions and can therefore look blank. Use a compact
        # inner disk for ink density and a wider background annulus for local
        # illumination compensation.
        inner_radius = max(3, int(radius * 0.55))
        background_inner = max(inner_radius + 2, int(radius * 1.20))
        background_outer = max(background_inner + 2, int(radius * 1.70))

        x1 = max(0, x - background_outer)
        y1 = max(0, y - background_outer)
        x2 = min(gray.shape[1], x + background_outer + 1)
        y2 = min(gray.shape[0], y + background_outer + 1)

        roi = gray[y1:y2, x1:x2]
        if roi.size == 0:
            return 0.0

        center_x = x - x1
        center_y = y - y1

        yy, xx = np.ogrid[:roi.shape[0], :roi.shape[1]]
        distance_squared = (
            (xx - center_x) ** 2
            + (yy - center_y) ** 2
        )

        inner_mask = distance_squared <= inner_radius ** 2
        background_mask = (
            distance_squared >= background_inner ** 2
        ) & (
            distance_squared <= background_outer ** 2
        )

        inner_pixels = roi[inner_mask]
        background_pixels = roi[background_mask]

        if inner_pixels.size == 0 or background_pixels.size == 0:
            return 0.0

        inner_darkness = float(
            np.mean(255.0 - inner_pixels) / 255.0
        )
        background_darkness = float(
            np.mean(255.0 - background_pixels) / 255.0
        )

        # Local-background corrected ink density. Clamp to zero so text or
        # page shading cannot create a negative answer score.
        score = (
            inner_darkness
            - 0.35 * background_darkness
        )

        return max(0.0, float(score))

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

        marked_options = sum(
            score >= self.mark_threshold
            for score in scores
        )

        if (
            best_score
            < self.blank_threshold
        ):

            answer = "-"

        elif (
            marked_options > 1
        ):

            answer = "?"

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

    def read_identity(self, gray, template):
        if not template.identity:
            return None

        schema = template.identity
        coordinates = identity_coordinates(schema)
        radius = int(schema.get("bubble_radius", 11))

        def read_value(bubbles, values):
            scores = [self.reader.score(gray, x, y, radius) for x, y in bubbles]
            if not scores:
                return None
            ranked = np.argsort(scores)[::-1]
            best = float(scores[int(ranked[0])])
            second = float(scores[int(ranked[1])]) if len(scores) > 1 else 0.0
            marked = sum(score >= self.reader.mark_threshold for score in scores)
            if best < self.reader.blank_threshold:
                return None
            if marked > 1 or best - second < self.reader.ambiguity_margin:
                return "?"
            return values[int(ranked[0])]

        def read_grid(grid, alphabet):
            characters = [read_value(column, alphabet) for column in grid]
            return "".join(character for character in characters if character not in (None, "?")).strip() or None

        roll = []
        for column in coordinates["roll"]:
            value = read_value(column, [str(digit) for digit in range(10)])
            roll.append(value if value is not None else "?")

        return {
            "name": read_grid(coordinates["name"], schema["name_alphabet"]),
            "subject": read_grid(coordinates["subject"], schema["subject_alphabet"]),
            "roll_no": "".join(roll) if any(value != "?" for value in roll) else None,
            "class": read_value(coordinates["class"], schema["class_values"]),
            "section": read_value(coordinates["section"], schema["section_values"]),
            "set": read_value(coordinates["set"], schema["set_values"]),
        }

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
        forced_template_id=None,
        image=None
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

        # ----------------------------------------------------
        # No QR: use a single local template automatically.
        # If there are several, prefer the best aspect-ratio match.
        # ----------------------------------------------------

        local_templates = [
            entry["template"]
            for entry in self.template_library.templates.values()
        ]

        if local_templates:

            if len(local_templates) == 1:
                template = local_templates[0]
                print(
                    "[Template] QR unavailable; using only local template:",
                    template.template_id
                )
                return template

            if image is not None:
                template = self.auto_select_template(image, local_templates)
                if template is not None:
                    return template

        raise RuntimeError(
            "No usable template available. "
            "Provide --template TEMPLATE_ID when the QR cannot be read."
        )

    # ========================================================
    # AUTO TEMPLATE SELECTION
    # ========================================================

    @staticmethod
    def bubble_layout_score(
        gray,
        template,
        max_questions=30
    ):

        """Estimate how well a template's bubble grid matches an image.

        This is used only when QR metadata is unavailable and more than one
        local template exists. A correct template places its expected bubble
        centers directly over the printed bubble rings, producing a much
        higher annulus-darkness score than a wrong layout.
        """

        question_count = (
            template.question_count
            or template.questions_per_column() * template.max_columns()
        )

        question_count = max(
            1,
            min(int(question_count), int(max_questions))
        )

        questions = template.generate_questions(
            1,
            question_count
        )

        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0
        )

        values = []

        for question in questions:
            for x, y in question["bubbles"]:
                x = int(round(x))
                y = int(round(y))
                radius = max(3, int(template.bubble_radius))

                outer = max(
                    radius + 2,
                    int(radius * 1.20)
                )
                inner = max(
                    2,
                    int(radius * 0.72)
                )

                x1 = max(0, x - outer)
                y1 = max(0, y - outer)
                x2 = min(gray.shape[1], x + outer + 1)
                y2 = min(gray.shape[0], y + outer + 1)

                roi = gray[y1:y2, x1:x2]
                if roi.size == 0:
                    continue

                cx = x - x1
                cy = y - y1
                yy, xx = np.ogrid[:roi.shape[0], :roi.shape[1]]
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                annulus = (
                    d2 <= outer ** 2
                ) & (
                    d2 >= inner ** 2
                )

                pixels = roi[annulus]
                if pixels.size:
                    darkness = float(
                        np.mean(255.0 - pixels) / 255.0
                    )
                    values.append(darkness)

        if not values:
            return 0.0

        return float(np.mean(values))

    def auto_select_template(
        self,
        image,
        templates
    ):

        scored = []

        image_ratio = image.shape[1] / float(max(1, image.shape[0]))

        for template in templates:
            try:
                ratio = template.width / float(max(1, template.height))
                ratio_error = abs(image_ratio - ratio) / max(ratio, 1e-9)

                # Reject templates whose page shape clearly cannot match.
                # Perspective/scanner distortion can account for a few percent.
                if ratio_error > ASPECT_RATIO_TOLERANCE:
                    continue

                corrected, _, _ = self.rectifier.rectify(
                    image,
                    template
                )

                gray = cv2.cvtColor(
                    corrected,
                    cv2.COLOR_BGR2GRAY
                )

                fit = self.bubble_layout_score(
                    gray,
                    template
                )

                scored.append(
                    (
                        fit,
                        -ratio_error,
                        template
                    )
                )

            except Exception as error:
                print(
                    "[Template] Auto-test failed for",
                    template.template_id,
                    ":",
                    error
                )

        if not scored:
            return None

        scored.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True
        )

        best = scored[0]

        second_fit = (
            scored[1][0]
            if len(scored) > 1
            else 0.0
        )

        if best[0] < AUTO_TEMPLATE_MIN_FIT:
            print(
                "[Template] No local template produced a reliable layout match."
            )
            return None

        if (
            len(scored) > 1
            and second_fit > 0.0
            and best[0] < second_fit * AUTO_TEMPLATE_MIN_SEPARATION
        ):
            print(
                "[Template] Local templates are too similar to select safely; "
                "use --template TEMPLATE_ID."
            )
            return None

        print(
            "[Template] QR unavailable; auto-selected:",
            best[2].template_id,
            f"(fit={best[0]:.4f})"
        )

        if len(scored) > 1:
            print(
                "[Template] Alternatives:",
                ", ".join(
                    f"{item[2].template_id}={item[0]:.4f}"
                    for item in scored[1:]
                )
            )

        return best[2]

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

                "page_type": "answers",

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

            "page_type": str(sheet.get("type", "answers")),

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
                forced_template_id,
                image=image
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

        if not page_info["student"] and template.student:
            page_info["student"] = dict(
                template.student
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

        if page_info["page_type"] != "identity" and question_count <= 0:

            if template.question_count:
                question_count = template.question_count
                print(
                    "[Page] Using template question count:",
                    question_count
                )
            else:
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

        student_details = self.read_identity(gray, template)

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

            "page_type": page_info["page_type"],

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

                "question_count": (
                    template.question_count
                ),
            },

            "student": (
                page_info[
                    "student"
                ]
            ),

            "student_details": student_details,

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

    pdf_library = _load_pdf_library()

    page = document.load_page(
        page_index
    )

    matrix = pdf_library.Matrix(
        PDF_SCALE,
        PDF_SCALE
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        colorspace=pdf_library.csRGB,
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

    pdf_library = _load_pdf_library()
    document = pdf_library.open(
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
