import base64
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import time
import zlib

import PySimpleGUI as sg
import qrcode

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# OMR GENERATOR ENGINE
# ============================================================

class OMRGenerator:

    # ========================================================
    # PAGE SIZES @ 300 DPI
    # ========================================================

    PAGE_SIZES = {
        "A4": (2480, 3508),
        "A5": (1748, 2480),
        "A3": (3508, 4961),
        "Letter": (2550, 3300),
        "Legal": (2550, 4200),
    }

    DPI = 300

    # ========================================================
    # DEFAULTS
    # ========================================================

    DEFAULTS = {

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

        "border_width": 8,
    }

    # ========================================================
    # QR SETTINGS
    # ========================================================

    QR_SIZE = 300

    QR_GAP = 20

    QR_PREFIX = "OMR1:"

    QR_COMPRESSION_LEVEL = 9

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        config
    ):

        self.config = config

        self.page_size = (
            config["page_size"]
        )

        self.orientation = (
            config["orientation"]
        )

        width, height = self.PAGE_SIZES[
            self.page_size
        ]

        if self.orientation == "Landscape":

            width, height = height, width

        self.WIDTH = width
        self.HEIGHT = height

        # ----------------------------------------------------
        # Layout
        # ----------------------------------------------------

        self.MARGIN = config[
            "margin"
        ]

        self.HEADER_HEIGHT = config[
            "header_height"
        ]

        self.START_Y = config[
            "start_y"
        ]

        self.BOTTOM_MARGIN = config[
            "bottom_margin"
        ]

        self.QUESTION_SPACING = config[
            "question_spacing"
        ]

        self.COLUMN_GAP = config[
            "column_gap"
        ]

        self.BUBBLE_SPACING = config[
            "bubble_spacing"
        ]

        self.BUBBLE_RADIUS = config[
            "bubble_radius"
        ]

        self.QUESTION_BUBBLE_GAP = config[
            "question_bubble_gap"
        ]

        # ----------------------------------------------------
        # Questions
        # ----------------------------------------------------

        self.choices = tuple(
            config["choices"]
        )

        self.questions = config[
            "questions"
        ]

        # ----------------------------------------------------
        # Student information
        # ----------------------------------------------------

        self.name = str(
            config["name"]
        ).strip()

        self.class_standard = str(
            config["class_standard"]
        ).strip()

        self.class_division = str(
            config["class_division"]
        ).strip()

        self.admission_number = str(
            config["admission_number"]
        ).strip()

        self.subject = str(
            config["subject"]
        ).strip()

        # ----------------------------------------------------
        # Sheet ID
        # ----------------------------------------------------

        self.sheet_id = (
            self.subject.upper()[:3]
            + self.admission_number
        )

        # ----------------------------------------------------
        # Template ID
        # ----------------------------------------------------

        self.template_id = (
            self.generate_template_id()
        )

        # ----------------------------------------------------
        # QR
        # ----------------------------------------------------

        self.qr_enabled = bool(
            config["qr_enabled"]
        )

        self.qr_position = config[
            "qr_position"
        ]

        self.qr_size = self.QR_SIZE

        # ----------------------------------------------------
        # Pages
        # ----------------------------------------------------

        self.pages = []

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font_large = (
            self.load_font(55)
        )

        self.font_medium = (
            self.load_font(42)
        )

        self.font_small = (
            self.load_font(32)
        )

        self.font_tiny = (
            self.load_font(26)
        )

    # ========================================================
    # FONT LOADER
    # ========================================================

    def load_font(
        self,
        size
    ):

        paths = [

            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans.ttf",

            "/usr/share/fonts/truetype/"
            "liberation2/"
            "LiberationSans-Regular.ttf",
        ]

        for path in paths:

            try:

                return ImageFont.truetype(
                    path,
                    size
                )

            except Exception:

                continue

        return ImageFont.load_default()

    # ========================================================
    # TEMPLATE ID
    # ========================================================

    def generate_template_id(
        self
    ):

        template_data = {

            "page_size": self.page_size,

            "orientation": self.orientation,

            "width": self.WIDTH,
            "height": self.HEIGHT,

            "margin": self.MARGIN,

            "header_height": (
                self.HEADER_HEIGHT
            ),

            "start_y": self.START_Y,

            "bottom_margin": (
                self.BOTTOM_MARGIN
            ),

            "question_spacing": (
                self.QUESTION_SPACING
            ),

            "column_gap": (
                self.COLUMN_GAP
            ),

            "bubble_spacing": (
                self.BUBBLE_SPACING
            ),

            "bubble_radius": (
                self.BUBBLE_RADIUS
            ),

            "question_bubble_gap": (
                self.QUESTION_BUBBLE_GAP
            ),

            "choices": "".join(
                self.choices
            ),
        }

        raw = json.dumps(
            template_data,
            sort_keys=True,
            separators=(",", ":")
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
    # TEMPLATE DETAILS
    # ========================================================

    def get_template_details(
        self
    ):

        return {

            "id": self.template_id,

            "ps": self.page_size,

            "o": self.orientation,

            "w": self.WIDTH,
            "h": self.HEIGHT,

            "m": self.MARGIN,

            "hh": self.HEADER_HEIGHT,

            "sy": self.START_Y,

            "bm": self.BOTTOM_MARGIN,

            "qs": self.QUESTION_SPACING,

            "cg": self.COLUMN_GAP,

            "bs": self.BUBBLE_SPACING,

            "br": self.BUBBLE_RADIUS,

            "qbg": self.QUESTION_BUBBLE_GAP,

            "choices": "".join(
                self.choices
            ),

            "rms": self.DEFAULTS[
                "registration_marker_size"
            ],

            "rmm": self.DEFAULTS[
                "registration_marker_margin"
            ],
        }

    # ========================================================
    # STUDENT DETAILS
    # ========================================================

    def get_student_details(
        self
    ):

        return {

            "admission": (
                self.admission_number
            ),

            "name": self.name,

            "class": (
                self.class_standard
            ),

            "section": (
                self.class_division
            ),

            "subject": self.subject,
        }

    # ========================================================
    # SHEET DETAILS
    # ========================================================

    def get_sheet_details(
        self,
        page_number,
        total_pages,
        first_question,
        questions_on_page
    ):

        return {

            "id": self.sheet_id,

            "page": page_number,

            "pages": total_pages,

            "first": first_question,

            "count": questions_on_page,
        }

    # ========================================================
    # BUILD QR DATA
    # ========================================================

    def build_qr_payload(
        self,
        page_number,
        total_pages,
        first_question,
        questions_on_page
    ):

        payload = {

            "v": 1,

            "sheet": self.get_sheet_details(
                page_number,
                total_pages,
                first_question,
                questions_on_page
            ),

            "template": (
                self.get_template_details()
            ),

            "student": (
                self.get_student_details()
            ),
        }

        raw_json = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False
        )

        compressed = zlib.compress(
            raw_json.encode(
                "utf-8"
            ),
            level=self.QR_COMPRESSION_LEVEL
        )

        encoded = base64.urlsafe_b64encode(
            compressed
        ).decode(
            "ascii"
        )

        return (
            self.QR_PREFIX
            + encoded
        )

    # ========================================================
    # DECODE QR PAYLOAD
    #
    # Useful for testing the generator itself.
    # ========================================================

    @staticmethod
    def decode_qr_payload(
        payload
    ):

        if not payload.startswith(
            OMRGenerator.QR_PREFIX
        ):

            raise ValueError(
                "Invalid OMR QR prefix."
            )

        encoded = payload[
            len(
                OMRGenerator.QR_PREFIX
            ):
        ]

        compressed = base64.urlsafe_b64decode(
            encoded.encode(
                "ascii"
            )
        )

        raw_json = zlib.decompress(
            compressed
        ).decode(
            "utf-8"
        )

        return json.loads(
            raw_json
        )

    # ========================================================
    # PAGE
    # ========================================================

    def create_page(
        self
    ):

        image = Image.new(
            "RGB",
            (
                self.WIDTH,
                self.HEIGHT
            ),
            "white"
        )

        draw = ImageDraw.Draw(
            image
        )

        return (
            image,
            draw
        )

    # ========================================================
    # REGISTRATION MARKERS
    # ========================================================

    def draw_registration_markers(
        self,
        draw
    ):

        size = self.DEFAULTS[
            "registration_marker_size"
        ]

        margin = self.DEFAULTS[
            "registration_marker_margin"
        ]

        positions = [

            (
                margin,
                margin
            ),

            (
                self.WIDTH
                - margin
                - size,

                margin
            ),

            (
                margin,

                self.HEIGHT
                - margin
                - size
            ),

            (
                self.WIDTH
                - margin
                - size,

                self.HEIGHT
                - margin
                - size
            ),
        ]

        for x, y in positions:

            draw.rectangle(
                [
                    x,
                    y,
                    x + size - 1,
                    y + size - 1
                ],
                fill="black"
            )

    # ========================================================
    # BORDER
    # ========================================================

    def draw_border(
        self,
        draw
    ):

        margin = self.MARGIN

        draw.rectangle(
            [
                margin,
                margin,

                self.WIDTH - margin,
                self.HEIGHT - margin
            ],

            outline="black",

            width=self.DEFAULTS[
                "border_width"
            ]
        )

    # ========================================================
    # HEADER
    # ========================================================

    def draw_header(
        self,
        draw,
        page_number,
        total_pages
    ):

        center_x = (
            self.WIDTH // 2
        )

        title = (
            "OMR ANSWER SHEET"
        )

        bbox = draw.textbbox(
            (0, 0),
            title,
            font=self.font_large
        )

        title_width = (
            bbox[2] - bbox[0]
        )

        draw.text(
            (
                center_x
                - title_width // 2,

                180
            ),

            title,

            fill="black",

            font=self.font_large
        )

        # ----------------------------------------------------
        # Header fields
        # ----------------------------------------------------

        fields = []

        if self.config[
            "header_name"
        ]:

            fields.append(
                f"Name: {self.name}"
            )

        if self.config[
            "header_class"
        ]:

            fields.append(
                f"Class: "
                f"{self.class_standard}"
            )

        if self.config[
            "header_section"
        ]:

            fields.append(
                f"Section: "
                f"{self.class_division}"
            )

        if self.config[
            "header_admission"
        ]:

            fields.append(
                "Admission No: "
                f"{self.admission_number}"
            )

        if self.config[
            "header_subject"
        ]:

            fields.append(
                f"Subject: {self.subject}"
            )

        row_y = 290

        for index in range(
            0,
            len(fields),
            2
        ):

            draw.text(
                (
                    180,
                    row_y
                ),

                fields[index],

                fill="black",

                font=self.font_medium
            )

            if (
                index + 1
                < len(fields)
            ):

                draw.text(
                    (
                        1100,
                        row_y
                    ),

                    fields[index + 1],

                    fill="black",

                    font=self.font_medium
                )

            row_y += 70

        # ----------------------------------------------------
        # Sheet ID
        # ----------------------------------------------------

        draw.text(
            (
                self.WIDTH - 500,
                430
            ),

            f"Sheet ID: {self.sheet_id}",

            fill="black",

            font=self.font_small
        )

        # ----------------------------------------------------
        # Page number
        # ----------------------------------------------------

        page_text = (
            f"Page {page_number} "
            f"of {total_pages}"
        )

        bbox = draw.textbbox(
            (0, 0),
            page_text,
            font=self.font_small
        )

        page_width = (
            bbox[2] - bbox[0]
        )

        draw.text(
            (
                self.WIDTH
                - 180
                - page_width,

                self.HEIGHT - 180
            ),

            page_text,

            fill="black",

            font=self.font_small
        )

        # ----------------------------------------------------
        # Separator
        # ----------------------------------------------------

        draw.line(
            (
                150,

                self.HEADER_HEIGHT + 20,

                self.WIDTH - 150,

                self.HEADER_HEIGHT + 20
            ),

            fill="black",

            width=5
        )

    # ========================================================
    # QR
    # ========================================================

    def draw_qr(
        self,
        image,
        draw,
        page_number,
        total_pages,
        first_question,
        questions_on_page
    ):

        if not self.qr_enabled:

            return

        size = self.qr_size

        marker_size = self.DEFAULTS[
            "registration_marker_size"
        ]

        marker_margin = self.DEFAULTS[
            "registration_marker_margin"
        ]

        gap = self.QR_GAP

        qr_data = self.build_qr_payload(
            page_number,
            total_pages,
            first_question,
            questions_on_page
        )

        qr = qrcode.QRCode(

            error_correction=(
                qrcode.constants.ERROR_CORRECT_H
            ),

            box_size=10,

            border=4
        )

        qr.add_data(
            qr_data
        )

        qr.make(
            fit=True
        )

        qr_image = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert(
            "RGB"
        )

        qr_image = qr_image.resize(
            (
                size,
                size
            ),
            Image.Resampling.NEAREST
        )

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        if (
            self.qr_position
            == "Top Left"
        ):

            x = (
                marker_margin
                + marker_size
                + gap
            )

            y = (
                self.MARGIN
                + gap
            )

        elif (
            self.qr_position
            == "Top Right"
        ):

            x = (
                self.WIDTH
                - marker_margin
                - marker_size
                - gap
                - size
            )

            y = (
                self.MARGIN
                + gap
            )

        elif (
            self.qr_position
            == "Bottom Left"
        ):

            x = (
                self.MARGIN
                + gap
            )

            y = (
                self.HEIGHT
                - marker_margin
                - marker_size
                - gap
                - size
            )

        else:

            x = (
                self.WIDTH
                - marker_margin
                - marker_size
                - gap
                - size
            )

            y = (
                self.HEIGHT
                - marker_margin
                - marker_size
                - gap
                - size
            )

        # ----------------------------------------------------
        # Boundary safety
        # ----------------------------------------------------

        x = max(
            0,
            min(
                x,
                self.WIDTH - size
            )
        )

        y = max(
            0,
            min(
                y,
                self.HEIGHT - size
            )
        )

        image.paste(
            qr_image,
            (
                x,
                y
            )
        )

    # ========================================================
    # BUBBLE
    # ========================================================

    def draw_bubble(
        self,
        draw,
        x,
        y
    ):

        radius = self.BUBBLE_RADIUS

        draw.ellipse(
            [
                x - radius,
                y - radius,

                x + radius,
                y + radius
            ],

            outline="black",

            width=5
        )

    # ========================================================
    # QUESTION NUMBER WIDTH
    # ========================================================

    def get_question_number_width(
        self,
        number
    ):

        text = (
            f"{number}."
        )

        temp_image = Image.new(
            "RGB",
            (
                1,
                1
            )
        )

        temp_draw = ImageDraw.Draw(
            temp_image
        )

        bbox = temp_draw.textbbox(
            (0, 0),
            text,
            font=self.font_small
        )

        return (
            bbox[2] - bbox[0]
        )

    # ========================================================
    # QUESTIONS PER COLUMN
    # ========================================================

    def get_questions_per_column(
        self
    ):

        available_height = (
            self.HEIGHT
            - self.START_Y
            - self.BOTTOM_MARGIN
        )

        return max(
            1,

            available_height
            // self.QUESTION_SPACING
        )

    # ========================================================
    # QUESTION WIDTH
    # ========================================================

    def get_question_width(
        self
    ):

        max_number = max(
            1,
            self.questions
        )

        number_width = (
            self.get_question_number_width(
                max_number
            )
        )

        bubble_area = (

            self.QUESTION_BUBBLE_GAP

            + (
                self.BUBBLE_RADIUS * 2
            )

            + (
                max(
                    0,
                    len(self.choices) - 1
                )
                * self.BUBBLE_SPACING
            )
        )

        return (
            number_width
            + bubble_area
        )

    # ========================================================
    # MAXIMUM COLUMNS
    # ========================================================

    def get_max_columns(
        self
    ):

        usable_width = (
            self.WIDTH
            - 2 * self.MARGIN
        )

        question_width = (
            self.get_question_width()
        )

        if question_width <= 0:

            return 1

        columns = (
            usable_width
            + self.COLUMN_GAP
        ) // (
            question_width
            + self.COLUMN_GAP
        )

        return max(
            1,
            int(columns)
        )

    # ========================================================
    # QUESTIONS PER PAGE
    # ========================================================

    def get_questions_per_page(
        self
    ):

        rows = (
            self.get_questions_per_column()
        )

        columns = (
            self.get_max_columns()
        )

        return (
            rows * columns
        )

    # ========================================================
    # DRAW QUESTIONS
    # ========================================================

    def draw_questions(
        self,
        draw,
        first_question,
        number_of_questions
    ):

        rows = (
            self.get_questions_per_column()
        )

        columns = math.ceil(
            number_of_questions
            / rows
        )

        max_columns = (
            self.get_max_columns()
        )

        columns = min(
            columns,
            max_columns
        )

        usable_width = (
            self.WIDTH
            - 2 * self.MARGIN
        )

        column_width = (
            usable_width
            - (
                columns - 1
            )
            * self.COLUMN_GAP
        ) // columns

        for local_index in range(
            number_of_questions
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
                self.MARGIN
                + column
                * (
                    column_width
                    + self.COLUMN_GAP
                )
            )

            y = (
                self.START_Y
                + row
                * self.QUESTION_SPACING
            )

            # ------------------------------------------------
            # Question number
            # ------------------------------------------------

            question_text = (
                f"{question_number}."
            )

            bbox = draw.textbbox(
                (0, 0),
                question_text,
                font=self.font_small
            )

            question_width = (
                bbox[2] - bbox[0]
            )

            question_height = (
                bbox[3] - bbox[1]
            )

            question_y = (
                y
                - question_height // 2
                - bbox[1]
            )

            draw.text(
                (
                    x + 25,
                    question_y
                ),

                question_text,

                fill="black",

                font=self.font_small
            )

            # ------------------------------------------------
            # Bubble start
            # ------------------------------------------------

            bubble_start_x = (
                x
                + question_width
                + self.QUESTION_BUBBLE_GAP
                + self.BUBBLE_RADIUS
            )

            # ------------------------------------------------
            # Bubbles
            # ------------------------------------------------

            for (
                choice_index,
                choice
            ) in enumerate(
                self.choices
            ):

                bubble_x = (
                    bubble_start_x
                    + choice_index
                    * self.BUBBLE_SPACING
                )

                self.draw_bubble(
                    draw,
                    bubble_x,
                    y
                )

                bbox = draw.textbbox(
                    (0, 0),
                    choice,
                    font=self.font_tiny
                )

                choice_width = (
                    bbox[2] - bbox[0]
                )

                draw.text(
                    (
                        bubble_x
                        - choice_width // 2,

                        y
                        + self.BUBBLE_RADIUS
                        + 8
                    ),

                    choice,

                    fill="black",

                    font=self.font_tiny
                )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self
    ):

        self.pages = []

        rows = (
            self.get_questions_per_column()
        )

        max_columns = (
            self.get_max_columns()
        )

        questions_per_page = (
            rows
            * max_columns
        )

        total_pages = max(
            1,

            math.ceil(
                self.questions
                / questions_per_page
            )
        )

        current_question = 1

        for page_number in range(
            1,
            total_pages + 1
        ):

            remaining = (
                self.questions
                - current_question
                + 1
            )

            questions_on_page = min(
                remaining,
                questions_per_page
            )

            image, draw = (
                self.create_page()
            )

            # ------------------------------------------------
            # Page graphics
            # ------------------------------------------------

            self.draw_border(
                draw
            )

            self.draw_registration_markers(
                draw
            )

            self.draw_header(
                draw,
                page_number,
                total_pages
            )

            self.draw_qr(
                image,
                draw,
                page_number,
                total_pages,
                current_question,
                questions_on_page
            )

            self.draw_questions(
                draw,
                current_question,
                questions_on_page
            )

            self.pages.append(
                image
            )

            current_question += (
                questions_on_page
            )

        return self.pages

    # ========================================================
    # SAVE PNG
    # ========================================================

    def save_png(
        self,
        prefix
    ):

        if not self.pages:

            self.generate()

        for index, page in enumerate(
            self.pages,
            start=1
        ):

            filename = (
                f"{prefix}_page_{index}.png"
            )

            page.save(
                filename,
                format="PNG",
                dpi=(
                    self.DPI,
                    self.DPI
                )
            )

    # ========================================================
    # SAVE JPEG
    # ========================================================

    def save_jpeg(
        self,
        prefix,
        extension=".jpg"
    ):

        if not self.pages:

            self.generate()

        for index, page in enumerate(
            self.pages,
            start=1
        ):

            filename = (
                f"{prefix}_page_{index}"
                f"{extension}"
            )

            jpeg_page = page.convert(
                "RGB"
            )

            jpeg_page.save(
                filename,
                format="JPEG",
                quality=100,
                subsampling=0,
                dpi=(
                    self.DPI,
                    self.DPI
                )
            )

    # ========================================================
    # SAVE PDF
    # ========================================================

    def save_pdf(
        self,
        filename
    ):

        if not self.pages:

            self.generate()

        pages = [
            page.convert("RGB")
            for page in self.pages
        ]

        pages[0].save(
            filename,
            "PDF",
            resolution=self.DPI,
            save_all=True,
            append_images=pages[1:]
        )

    # ========================================================
    # GENERIC OUTPUT
    # ========================================================

    def save_output(
        self,
        output_format,
        prefix
    ):

        output_format = str(
            output_format
        ).strip().upper()

        if output_format == "PDF":

            self.save_pdf(
                f"{prefix}.pdf"
            )

            return

        if output_format == "PNG":

            self.save_png(
                prefix
            )

            return

        if output_format == "JPG":

            self.save_jpeg(
                prefix,
                extension=".jpg"
            )

            return

        if output_format == "JPEG":

            self.save_jpeg(
                prefix,
                extension=".jpeg"
            )

            return

        raise ValueError(
            "Unsupported output format: "
            f"{output_format}"
        )


# ============================================================
# DEFAULT CONFIG
# ============================================================

CONFIG = {

    "page_size": "A4",

    "orientation": "Portrait",

    "questions": 80,

    "choices": (
        "A",
        "B",
        "C",
        "D"
    ),

    "name": "Student",

    "class_standard": "XII",

    "class_division": "A",

    "admission_number": "0000",

    "subject": "Physics",

    "margin": 100,

    "header_height": 470,

    "start_y": 560,

    "bottom_margin": 180,

    "question_spacing": 105,

    "column_gap": 70,

    "bubble_spacing": 150,

    "bubble_radius": 24,

    "question_bubble_gap": 35,

    "qr_enabled": True,

    "qr_position": "Top Right",

    "output_format": "PDF",

    "header_name": True,

    "header_class": True,

    "header_section": True,

    "header_admission": True,

    "header_subject": True,
}


# ============================================================
# GUI THEME
# ============================================================

BG = "#000000"

BUTTON_BG = "#212121"

FG = "#FFFFFF"

SECONDARY_FG = "#BDBDBD"


sg.theme(
    "Black"
)


sg.set_options(

    font=(
        "Arial",
        10
    ),

    background_color=BG,

    element_background_color=BG,

    text_color=FG,

    input_text_color=FG,

    input_elements_background_color=(
        BUTTON_BG
    ),

    button_color=(
        FG,
        BUTTON_BG
    ),
)


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(
    value,
    default
):

    try:

        value = str(
            value
        ).strip()

        if not value:

            return default

        return int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        return default


# ============================================================
# MAKE GENERATOR
# ============================================================

def make_generator(
    values,
    candidate=None
):

    config = CONFIG.copy()

    config["page_size"] = values.get(
        "page_size",
        CONFIG["page_size"]
    )

    config["orientation"] = values.get(
        "orientation",
        CONFIG["orientation"]
    )

    config["questions"] = max(
        1,

        safe_int(
            values.get(
                "questions"
            ),

            CONFIG[
                "questions"
            ]
        )
    )

    options = max(
        2,

        min(
            6,

            safe_int(
                values.get(
                    "options"
                ),

                4
            )
        )
    )

    config["choices"] = tuple(
        "ABCDEF"[
            :options
        ]
    )

    candidate = (
        candidate
        or {}
    )

    config["name"] = str(
        candidate.get(
            "name",
            values.get(
                "name",
                CONFIG["name"]
            )
        )
    ).strip()

    config[
        "class_standard"
    ] = str(
        candidate.get(
            "class_standard",
            values.get(
                "class_standard",
                CONFIG[
                    "class_standard"
                ]
            )
        )
    ).strip()

    config[
        "class_division"
    ] = str(
        candidate.get(
            "class_division",
            values.get(
                "section",
                CONFIG[
                    "class_division"
                ]
            )
        )
    ).strip()

    config[
        "admission_number"
    ] = str(
        candidate.get(
            "admission_number",
            values.get(
                "admission",
                CONFIG[
                    "admission_number"
                ]
            )
        )
    ).strip()

    config[
        "subject"
    ] = str(
        candidate.get(
            "subject",
            values.get(
                "subject",
                CONFIG[
                    "subject"
                ]
            )
        )
    ).strip()

    config[
        "column_gap"
    ] = max(
        1,

        safe_int(
            values.get(
                "column_gap"
            ),

            CONFIG[
                "column_gap"
            ]
        )
    )

    config[
        "bubble_spacing"
    ] = max(
        1,

        safe_int(
            values.get(
                "bubble_spacing"
            ),

            CONFIG[
                "bubble_spacing"
            ]
        )
    )

    config[
        "bubble_radius"
    ] = max(
        1,

        safe_int(
            values.get(
                "bubble_radius"
            ),

            CONFIG[
                "bubble_radius"
            ]
        )
    )

    config[
        "question_spacing"
    ] = max(
        1,

        safe_int(
            values.get(
                "question_spacing"
            ),

            CONFIG[
                "question_spacing"
            ]
        )
    )

    config[
        "margin"
    ] = max(
        1,

        safe_int(
            values.get(
                "margin"
            ),

            CONFIG[
                "margin"
            ]
        )
    )

    config[
        "qr_enabled"
    ] = bool(
        values.get(
            "qr_enabled",
            CONFIG[
                "qr_enabled"
            ]
        )
    )

    config[
        "qr_position"
    ] = values.get(
        "qr_position",
        CONFIG[
            "qr_position"
        ]
    )

    config[
        "output_format"
    ] = values.get(
        "output_format",
        CONFIG[
            "output_format"
        ]
    )

    config[
        "header_name"
    ] = bool(
        values.get(
            "header_name"
        )
    )

    config[
        "header_class"
    ] = bool(
        values.get(
            "header_class"
        )
    )

    config[
        "header_section"
    ] = bool(
        values.get(
            "header_section"
        )
    )

    config[
        "header_admission"
    ] = bool(
        values.get(
            "header_admission"
        )
    )

    config[
        "header_subject"
    ] = bool(
        values.get(
            "header_subject"
        )
    )

    return OMRGenerator(
        config
    )


# ============================================================
# CSV STUDENT IMPORT
# ============================================================

CSV_REQUIRED_COLUMNS = {

    "name": "name",

    "class": "class_standard",

    "section": "class_division",

    "admission": "admission_number",

    "subject": "subject",
}


def normalize_csv_header(
    header
):

    header = str(
        header
    ).strip().lower()

    header = re.sub(
        r"[^a-z0-9]+",
        "_",
        header
    )

    return header.strip(
        "_"
    )


def load_student_csv(
    filename
):

    if not filename:

        raise ValueError(
            "No CSV file was selected."
        )

    with open(
        filename,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        if not reader.fieldnames:

            raise ValueError(
                "The CSV file has no header row."
            )

        normalized_headers = {

            normalize_csv_header(
                header
            ): header

            for header in reader.fieldnames

            if header is not None
        }

        missing = [

            required

            for required
            in CSV_REQUIRED_COLUMNS

            if required
            not in normalized_headers
        ]

        if missing:

            raise ValueError(

                "Missing required CSV "
                "column(s): "

                + ", ".join(
                    missing
                )

                + "\n\nRequired columns:\n"

                "Name, Class, Section, "
                "Admission, Subject"
            )

        students = []

        seen_admissions = set()

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            if not any(
                str(
                    value
                    or ""
                ).strip()

                for value
                in row.values()
            ):

                continue

            student = {

                "name": str(
                    row.get(
                        normalized_headers[
                            "name"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "class_standard": str(
                    row.get(
                        normalized_headers[
                            "class"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "class_division": str(
                    row.get(
                        normalized_headers[
                            "section"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "admission_number": str(
                    row.get(
                        normalized_headers[
                            "admission"
                        ],
                        ""
                    )
                    or ""
                ).strip(),

                "subject": str(
                    row.get(
                        normalized_headers[
                            "subject"
                        ],
                        ""
                    )
                    or ""
                ).strip(),
            }

            missing_values = [

                field

                for field, value
                in student.items()

                if not value
            ]

            if missing_values:

                raise ValueError(
                    f"Row {row_number} "
                    f"is incomplete. "
                    f"Missing: "
                    + ", ".join(
                        missing_values
                    )
                )

            admission_key = (
                student[
                    "admission_number"
                ].casefold()
            )

            if admission_key in seen_admissions:

                raise ValueError(
                    "Duplicate admission "
                    "number found: "
                    f"{student['admission_number']} "
                    f"(row {row_number})"
                )

            seen_admissions.add(
                admission_key
            )

            students.append(
                student
            )

    if not students:

        raise ValueError(
            "The CSV file contains no "
            "student records."
        )

    return students


def sanitize_filename(
    value
):

    value = str(
        value
    ).strip()

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value
    )

    return (
        value.strip("._")
        or "Candidate"
    )


# ============================================================
# GUI SETTINGS
# ============================================================

settings = [

    [
        sg.Frame(
            "📄 Page",
            [

                [
                    sg.Text(
                        "Size",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "A4",
                            "A5",
                            "A3",
                            "Letter",
                            "Legal"
                        ],

                        default_value="A4",

                        key="page_size",

                        readonly=True,

                        enable_events=True,

                        size=(12, 1)
                    )
                ],

                [
                    sg.Text(
                        "Orientation",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "Portrait",
                            "Landscape"
                        ],

                        default_value="Portrait",

                        key="orientation",

                        readonly=True,

                        enable_events=True,

                        size=(12, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📝 Questions",
            [

                [
                    sg.Text(
                        "No. questions",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "80",

                        key="questions",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Options",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "2",
                            "3",
                            "4",
                            "5",
                            "6"
                        ],

                        default_value="4",

                        readonly=True,

                        key="options",

                        enable_events=True,

                        size=(12, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "⚪ Layout",
            [

                [
                    sg.Text(
                        "Bubble radius",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "24",

                        key="bubble_radius",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Bubble spacing",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "150",

                        key="bubble_spacing",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Question spacing",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "105",

                        key="question_spacing",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Column gap",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "70",

                        key="column_gap",

                        size=(12, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Margin",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "100",

                        key="margin",

                        size=(12, 1),

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📥 Candidate Source",
            [

                [
                    sg.Radio(
                        "Manual",
                        "candidate_source",

                        default=True,

                        key="input_mode_manual",

                        enable_events=True
                    ),

                    sg.Radio(
                        "CSV",
                        "candidate_source",

                        default=False,

                        key="input_mode_csv",

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "CSV file",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "",

                        key="csv_file",

                        size=(30, 1),

                        readonly=True
                    ),

                    sg.Button(
                        "Load CSV",

                        key="load_csv",

                        size=(12, 1),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "Candidate",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [],

                        key="csv_candidate",

                        size=(30, 1),

                        readonly=True,

                        enable_events=True,

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "CSV format:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "Name, Class, Section, Admission, Subject",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "👤 Student Information",
            [

                [
                    sg.Text(
                        "Name",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "Student",

                        key="name",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Class",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "XII",

                        key="class_standard",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Section",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "A",

                        key="section",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Admission",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "0000",

                        key="admission",

                        size=(20, 1),

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Subject",
                        size=(16, 1)
                    ),

                    sg.Input(
                        "Physics",

                        key="subject",

                        size=(20, 1),

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "🔲 QR",
            [

                [
                    sg.Checkbox(
                        "Enable QR",

                        default=True,

                        key="qr_enabled",

                        enable_events=True
                    )
                ],

                [
                    sg.Text(
                        "Position",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "Top Left",
                            "Top Right",
                            "Bottom Left",
                            "Bottom Right"
                        ],

                        default_value="Top Right",

                        readonly=True,

                        key="qr_position",

                        enable_events=True,

                        size=(15, 1)
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📋 Header",
            [

                [
                    sg.Checkbox(
                        "Name",

                        default=True,

                        key="header_name",

                        enable_events=True
                    ),

                    sg.Checkbox(
                        "Class",

                        default=True,

                        key="header_class",

                        enable_events=True
                    )
                ],

                [
                    sg.Checkbox(
                        "Section",

                        default=True,

                        key="header_section",

                        enable_events=True
                    ),

                    sg.Checkbox(
                        "Admission No.",

                        default=True,

                        key="header_admission",

                        enable_events=True
                    )
                ],

                [
                    sg.Checkbox(
                        "Subject",

                        default=True,

                        key="header_subject",

                        enable_events=True
                    )
                ]
            ],

            expand_x=True
        )
    ],

    [
        sg.Frame(
            "📤 Output",
            [

                [
                    sg.Text(
                        "Format",
                        size=(16, 1)
                    ),

                    sg.Combo(
                        [
                            "PDF",
                            "PNG",
                            "JPG",
                            "JPEG"
                        ],

                        default_value="PDF",

                        key="output_format",

                        readonly=True,

                        enable_events=True,

                        size=(15, 1)
                    )
                ],

                [
                    sg.Text(
                        "PDF:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "One multi-page file",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ],

                [
                    sg.Text(
                        "PNG/JPG:",
                        size=(16, 1)
                    ),

                    sg.Text(
                        "One file per page",

                        text_color=(
                            SECONDARY_FG
                        )
                    )
                ]
            ],

            expand_x=True
        )
    ]
]


# ============================================================
# MAIN LAYOUT
# ============================================================

layout = [

    [
        sg.Text(
            "OMR SHEET GENERATOR",

            font=(
                "Arial",
                22,
                "bold"
            ),

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.Text(
            "Configure your OMR sheet",

            font=(
                "Arial",
                12
            ),

            text_color=(
                SECONDARY_FG
            ),

            justification="center",

            expand_x=True
        )
    ],

    [
        sg.HorizontalSeparator()
    ],

    [

        sg.Column(
            settings,

            scrollable=True,

            vertical_scroll_only=True,

            size=(
                1000,
                780
            ),

            expand_y=True,

            pad=(
                (5, 15),
                (5, 5)
            )
        ),

        sg.VSeparator(),

        sg.Column(
            [

                [
                    sg.Text(
                        "LIVE PREVIEW",

                        font=(
                            "Arial",
                            16,
                            "bold"
                        ),

                        justification="center",

                        expand_x=True
                    )
                ],

                [
                    sg.Image(
                        key="preview",

                        size=(
                            800,
                            900
                        ),

                        background_color="#333333",

                        expand_x=True,

                        expand_y=True
                    )
                ],

                [
                    sg.Button(
                        "◀ Previous",

                        key="previous_page",

                        size=(14, 2),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    ),

                    sg.Text(
                        "Page 1 of 1",

                        key="page_info",

                        text_color=FG,

                        justification="center",

                        size=(16, 1)
                    ),

                    sg.Button(
                        "Next ▶",

                        key="next_page",

                        size=(14, 2),

                        font=(
                            "Arial",
                            10
                        ),

                        button_color=(
                            FG,
                            BUTTON_BG
                        ),

                        disabled=True
                    )
                ],

                [
                    sg.Text(
                        "Loading preview...",

                        key="layout_info",

                        text_color=(
                            SECONDARY_FG
                        ),

                        justification="center",

                        expand_x=True
                    )
                ]
            ],

            expand_x=True,

            expand_y=True,

            justification="center",

            element_justification="center"
        )
    ],

    [
        sg.HorizontalSeparator()
    ],

    [
        sg.Button(
            "Load Template",

            key="load_template",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Save Template",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Generate",

            size=(15, 2),

            font=(
                "Arial",
                10,
                "bold"
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Button(
            "Reset",

            size=(15, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        ),

        sg.Push(),

        sg.Button(
            "Exit",

            size=(10, 2),

            font=(
                "Arial",
                10
            ),

            button_color=(
                FG,
                BUTTON_BG
            )
        )
    ]
]


# ============================================================
# WINDOW
# ============================================================

window = sg.Window(

    "OMR Generator",

    layout,

    size=(
        1950,
        1500
    ),

    resizable=True,

    finalize=True
)


# ============================================================
# CANDIDATE STATE
# ============================================================

csv_students = []

csv_candidate_labels = []


# ============================================================
# PREVIEW STATE
# ============================================================

preview_pages = []

preview_page_index = 0


# ============================================================
# SHOW PREVIEW PAGE
# ============================================================

def show_preview_page():

    global preview_page_index

    if not preview_pages:

        return

    preview_page_index = max(
        0,

        min(
            preview_page_index,

            len(preview_pages) - 1
        )
    )

    page = preview_pages[
        preview_page_index
    ].copy()

    page.thumbnail(
        (
            800,
            900
        ),

        Image.Resampling.LANCZOS
    )

    buffer = io.BytesIO()

    page.save(
        buffer,
        format="PNG"
    )

    window[
        "preview"
    ].update(
        data=buffer.getvalue()
    )

    window[
        "page_info"
    ].update(
        f"Page "
        f"{preview_page_index + 1}"
        f" of "
        f"{len(preview_pages)}"
    )

    window[
        "previous_page"
    ].update(
        disabled=(
            preview_page_index <= 0
        )
    )

    window[
        "next_page"
    ].update(
        disabled=(
            preview_page_index
            >= len(preview_pages) - 1
        )
    )


# ============================================================
# UPDATE PREVIEW
# ============================================================

def update_preview(
    values
):

    global preview_pages
    global preview_page_index

    try:

        candidate = None

        selected_index = 0

        if values.get(
            "input_mode_csv"
        ):

            if not csv_students:

                window[
                    "layout_info"
                ].update(

                    "Load a CSV file "
                    "to preview candidates...",

                    text_color="#FF9800"
                )

                return

            selected_label = values.get(
                "csv_candidate",
                ""
            )

            try:

                selected_index = (
                    csv_candidate_labels.index(
                        selected_label
                    )
                )

            except ValueError:

                selected_index = 0

            candidate = (
                csv_students[
                    selected_index
                ]
            )

        generator = make_generator(
            values,
            candidate
        )

        preview_pages = (
            generator.generate()
        )

        preview_page_index = 0

        show_preview_page()

        if candidate is None:

            candidate_info = (
                "Manual candidate"
            )

        else:

            candidate_info = (

                f"Candidate "
                f"{selected_index + 1}"
                f" of "
                f"{len(csv_students)}"
                f"  |  "
                f"{candidate['name']}"
                f"  | Admission "
                f"{candidate['admission_number']}"
            )

        window[
            "layout_info"
        ].update(

            f"{candidate_info}"
            f"  |  "
            f"{len(preview_pages)}"
            f" page(s)"
            f"  |  "
            f"{generator.get_questions_per_column()}"
            f" questions/column"
            f"  |  "
            f"{generator.get_max_columns()}"
            f" max columns"
            f"  |  "
            f"Template "
            f"{generator.template_id}"
        )

    except Exception as error:

        window[
            "layout_info"
        ].update(

            "Preview waiting for "
            "valid settings...",

            text_color="#FF9800"
        )

        print(
            "Preview error:",
            error
        )


# ============================================================
# CANDIDATE SOURCE UI
# ============================================================

def update_candidate_source_ui(
    values
):

    manual_mode = bool(
        values.get(
            "input_mode_manual",
            True
        )
    )

    csv_mode = not manual_mode

    manual_keys = [

        "name",

        "class_standard",

        "section",

        "admission",

        "subject",
    ]

    for key in manual_keys:

        window[
            key
        ].update(
            disabled=csv_mode
        )

    window[
        "load_csv"
    ].update(
        disabled=not csv_mode
    )

    window[
        "csv_candidate"
    ].update(

        values=csv_candidate_labels,

        value=(

            csv_candidate_labels[0]

            if csv_students

            else ""
        ),

        disabled=(
            not csv_mode
        )
        or not csv_students
    )


# ============================================================
# LOAD CSV INTO GUI
# ============================================================

def load_csv_into_gui(
    filename
):

    global csv_students

    global csv_candidate_labels

    students = load_student_csv(
        filename
    )

    csv_students = students

    csv_candidate_labels = [

        (
            f"{student['admission_number']}"
            f" — "
            f"{student['name']}"
        )

        for student in students
    ]

    window[
        "csv_file"
    ].update(
        value=filename
    )

    window[
        "csv_candidate"
    ].update(

        values=csv_candidate_labels,

        value=csv_candidate_labels[0],

        disabled=False
    )

    return students


# ============================================================
# INITIAL PREVIEW
# ============================================================

event, values = window.read(
    timeout=50
)

if event != sg.WIN_CLOSED:

    update_candidate_source_ui(
        values
    )

    update_preview(
        values
    )


# ============================================================
# PREVIEW DEBOUNCE
# ============================================================

preview_pending = False

preview_deadline = 0


# ============================================================
# LOAD TEMPLATE
# ============================================================

def load_template():

    filename = sg.popup_get_file(

        "Load OMR template",

        file_types=(

            (
                "JSON Files",
                "*.json"
            ),
        )
    )

    if not filename:

        return None

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            template = json.load(
                file
            )

        if not isinstance(
            template,
            dict
        ):

            raise ValueError(
                "Template file must contain "
                "a JSON object."
            )

        return template

    except (
        OSError,
        json.JSONDecodeError,
        ValueError
    ) as error:

        sg.popup_error(

            "Could not load template:\n\n"
            f"{error}"
        )

        return None


# ============================================================
# EVENT LOOP
# ============================================================

while True:

    event, values = window.read(
        timeout=50
    )

    if event in (
        sg.WIN_CLOSED,
        "Exit"
    ):

        break

    # ========================================================
    # MANUAL / CSV MODE
    # ========================================================

    if event in (
        "input_mode_manual",
        "input_mode_csv"
    ):

        update_candidate_source_ui(
            values
        )

        preview_pending = True

        preview_deadline = (
            time.monotonic()
            + 0.05
        )

    # ========================================================
    # LOAD CSV
    # ========================================================

    if event == "load_csv":

        try:

            filename = sg.popup_get_file(

                "Select student CSV",

                file_types=(

                    (
                        "CSV Files",
                        "*.csv"
                    ),

                    (
                        "All Files",
                        "*.*"
                    )
                )
            )

            if filename:

                students = (
                    load_csv_into_gui(
                        filename
                    )
                )

                window[
                    "input_mode_csv"
                ].update(
                    value=True
                )

                window[
                    "input_mode_manual"
                ].update(
                    value=False
                )

                current_values = (
                    window.read(
                        timeout=0
                    )[1]
                )

                update_candidate_source_ui(
                    current_values
                )

                update_preview(
                    current_values
                )

                sg.popup(

                    f"Loaded "
                    f"{len(students)} "
                    f"candidate(s).",

                    title="CSV Loaded"
                )

        except Exception as error:

            sg.popup_error(

                "Could not load CSV:\n\n"
                f"{error}"
            )

    # ========================================================
    # CSV CANDIDATE SELECTION
    # ========================================================

    if event == "csv_candidate":

        update_preview(
            values
        )

    # ========================================================
    # PREVIOUS PAGE
    # ========================================================

    if event == "previous_page":

        if preview_page_index > 0:

            preview_page_index -= 1

            show_preview_page()

    # ========================================================
    # NEXT PAGE
    # ========================================================

    if event == "next_page":

        if (
            preview_page_index
            < len(preview_pages) - 1
        ):

            preview_page_index += 1

            show_preview_page()

    # ========================================================
    # SETTINGS CHANGED
    # ========================================================

    if (

        event

        not in (
            sg.TIMEOUT_EVENT,
            None
        )

        and event

        not in (
            "Generate",
            "Save Template",
            "Reset",
            "load_template",
            "load_csv",
            "csv_candidate",
            "input_mode_manual",
            "input_mode_csv",
            "previous_page",
            "next_page"
        )
    ):

        preview_pending = True

        preview_deadline = (
            time.monotonic()
            + 0.20
        )

    # ========================================================
    # DEBOUNCED PREVIEW
    # ========================================================

    if (

        preview_pending

        and time.monotonic()
        >= preview_deadline
    ):

        update_preview(
            values
        )

        preview_pending = False

    # ========================================================
    # LOAD TEMPLATE
    # ========================================================

    if event == "load_template":

        template = load_template()

        if template is not None:

            try:

                for key, value in (
                    template.items()
                ):

                    if (
                        key
                        in window.AllKeysDict
                    ):

                        window[
                            key
                        ].update(
                            value
                        )

                _, restored_values = (
                    window.read(
                        timeout=0
                    )
                )

                update_candidate_source_ui(
                    restored_values
                )

                if restored_values.get(
                    "input_mode_csv"
                ):

                    csv_filename = (
                        restored_values.get(
                            "csv_file",
                            ""
                        )
                    )

                    if (

                        csv_filename

                        and os.path.exists(
                            csv_filename
                        )
                    ):

                        try:

                            load_csv_into_gui(
                                csv_filename
                            )

                            restored_values = (
                                window.read(
                                    timeout=0
                                )[1]
                            )

                        except Exception as csv_error:

                            sg.popup_error(

                                "Template loaded, "
                                "but its CSV file "
                                "could not be loaded:\n\n"
                                f"{csv_error}"
                            )

                update_preview(
                    restored_values
                )

                preview_pending = False

                sg.popup(

                    "Template loaded successfully!",

                    title="OMR Template"
                )

            except Exception as error:

                sg.popup_error(

                    "Could not apply template:\n\n"
                    f"{error}"
                )

    # ========================================================
    # GENERATE
    # ========================================================

    if event == "Generate":

        try:

            output_format = str(
                values.get(
                    "output_format",
                    "PDF"
                )
            ).strip().upper()

            if output_format not in {

                "PDF",
                "PNG",
                "JPG",
                "JPEG"
            }:

                raise ValueError(
                    "Please select a valid "
                    "output format."
                )

            # ------------------------------------------------
            # Candidate source
            # ------------------------------------------------

            if values.get(
                "input_mode_csv"
            ):

                if not csv_students:

                    raise ValueError(

                        "CSV mode is selected, "
                        "but no student CSV "
                        "has been loaded."
                    )

                candidates = (
                    csv_students
                )

            else:

                candidates = [

                    {

                        "name": values.get(
                            "name",
                            ""
                        ),

                        "class_standard": values.get(
                            "class_standard",
                            ""
                        ),

                        "class_division": values.get(
                            "section",
                            ""
                        ),

                        "admission_number": values.get(
                            "admission",
                            ""
                        ),

                        "subject": values.get(
                            "subject",
                            ""
                        ),
                    }
                ]

            # ------------------------------------------------
            # Validate candidates
            # ------------------------------------------------

            for (
                candidate_index,
                candidate
            ) in enumerate(
                candidates,
                start=1
            ):

                missing = [

                    field

                    for field, value
                    in candidate.items()

                    if not str(
                        value
                    ).strip()
                ]

                if missing:

                    raise ValueError(

                        f"Candidate "
                        f"{candidate_index} "
                        f"is missing: "

                        + ", ".join(
                            missing
                        )
                    )

            # ------------------------------------------------
            # Output folder
            # ------------------------------------------------

            folder = sg.popup_get_folder(
                "Select output folder"
            )

            if folder:

                generated_count = 0

                for candidate in candidates:

                    generator = make_generator(
                        values,
                        candidate
                    )

                    generator.generate()

                    safe_admission = (
                        sanitize_filename(
                            candidate[
                                "admission_number"
                            ]
                        )
                    )

                    safe_name = (
                        sanitize_filename(
                            candidate[
                                "name"
                            ]
                        )
                    )

                    prefix = os.path.join(

                        folder,

                        (
                            "OMR_"
                            f"{safe_admission}_"
                            f"{safe_name}"
                        )
                    )

                    generator.save_output(
                        output_format,
                        prefix
                    )

                    generated_count += 1

                sg.popup(

                    f"Generated sheets for "
                    f"{generated_count} "
                    f"candidate(s).\n\n"

                    f"Format: "
                    f"{output_format}",

                    title="OMR Generated"
                )

        except Exception as error:

            sg.popup_error(

                "Generation failed:\n\n"
                f"{error}"
            )

    # ========================================================
    # SAVE TEMPLATE
    # ========================================================

    if event == "Save Template":

        try:

            filename = sg.popup_get_file(

                "Save OMR template",

                save_as=True,

                default_extension=".json",

                file_types=(

                    (
                        "JSON Files",
                        "*.json"
                    ),

                    (
                        "All Files",
                        "*.*"
                    ),
                )
            )

            if filename:

                if not filename.lower().endswith(
                    ".json"
                ):

                    filename += ".json"

                config = values.copy()

                with open(
                    filename,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(

                        config,

                        file,

                        indent=4
                    )

                sg.popup(

                    "Template saved "
                    "successfully!\n\n"
                    f"{filename}",

                    title="OMR Template"
                )

        except Exception as error:

            sg.popup_error(

                "Could not save template:\n\n"
                f"{error}"
            )

    # ========================================================
    # RESET
    # ========================================================

    if event == "Reset":

        answer = sg.popup_yes_no(
            "Reset the generator?"
        )

        if answer == "Yes":

            window.close()

            os.execl(

                sys.executable,

                sys.executable,

                *sys.argv
            )


# ============================================================
# CLOSE
# ============================================================

window.close()