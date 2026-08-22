# from PIL import Image, ImageDraw, ImageFont
# import qrcode
#
#
# class GenerateOMR:
#
#     # ============================================================
#     # A4 @ 300 DPI
#     # ============================================================
#
#     WIDTH = 2480
#     HEIGHT = 3508
#     DPI = 300
#
#     # ============================================================
#     # Layout settings
#     # ============================================================
#
#     MARGIN = 100
#
#     HEADER_HEIGHT = 470
#
#     START_Y = 560
#     BOTTOM_MARGIN = 180
#
#     QUESTION_SPACING = 105
#
#     # Space between question columns
#     COLUMN_GAP = 70
#
#     # Distance between bubbles
#     BUBBLE_SPACING = 150
#     BUBBLE_RADIUS = 24
#
#
#     # ============================================================
#     # Constructor
#     # ============================================================
#
#     def __init__(self, name="", class_standard="XII", class_division="", admission_number="", no_of_questions=20, choices=("A", "B", "C", "D"), subject=""):
#         self.name = name
#         self.class_standard = class_standard
#         self.class_division = class_division
#         self.admission_number = str(admission_number)
#
#         self.no_of_questions = no_of_questions
#         self.choices = choices
#         self.subject = subject
#         self.sheet_id = self.subject.upper()[:3] + self.admission_number
#         self.qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction helps readability
#             box_size=10,
#             border=4,
#         )
#         self.qr.add_data(self.sheet_id)
#         self.qr.make(fit=True)
#
#         self.qr_img = self.qr.make_image().convert("RGB")
#
#         self.pages = []        # Every generated page will be stored here
#
#
#         # Fonts
#         self.font_large = self.load_font(55)
#         self.font_medium = self.load_font(42)
#         self.font_small = self.load_font(32)
#         self.font_tiny = self.load_font(26)
#
#
#     # ============================================================
#     # Font loader
#     # ============================================================
#
#     def load_font(self, size):
#         font_paths = [
#             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
#             "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
#         ]
#
#         for path in font_paths:
#             try:
#                 return ImageFont.truetype(path, size)
#
#             except:
#                 pass
#
#         return ImageFont.load_default()
#
#     # ============================================================
#     # Create a new blank A4 page
#     # ============================================================
#
#     def create_page(self):
#
#         image = Image.new(
#             "RGB",
#             (self.WIDTH, self.HEIGHT),
#             "white"
#         )
#
#         draw = ImageDraw.Draw(image)
#
#         return image, draw
#
#     # ============================================================
#     # Registration markers
#     # ============================================================
#
#     def draw_registration_markers(self, draw):
#
#         size = 60
#         margin = self.MARGIN
#
#         positions = [
#             # Top-left
#             (margin, margin),
#
#             # Top-right
#             (self.WIDTH - margin - size, margin),
#
#             # Bottom-left
#             (margin, self.HEIGHT - margin - size),
#
#             # Bottom-right
#             (self.WIDTH - margin - size, self.HEIGHT - margin - size)
#         ]
#
#         for x, y in positions:
#             draw.rectangle(
#                 [x,
#                  y,
#                  x + size,
#                  y + size
#                  ],
#                 fill="black"
#             )
#
#     # ============================================================
#     # Page border
#     # ============================================================
#
#     def draw_border(self, draw):
#
#         margin = self.MARGIN
#
#         draw.rectangle(
#             [
#                 margin,
#                 margin,
#                 self.WIDTH - margin,
#                 self.HEIGHT - margin
#             ],
#             outline="black",
#             width=8
#         )
#
#     # ============================================================
#     # Header
#     # ============================================================
#
#     def draw_header(self, draw, page_number, total_pages):
#         center_x = self.WIDTH // 2
#
#         # --------------------------------------------------------
#         # Title
#         # --------------------------------------------------------
#
#         title = "OMR ANSWER SHEET"
#
#         bbox = draw.textbbox((0, 0), title, font=self.font_large)
#
#         title_width = bbox[2] - bbox[0]
#
#         draw.text(
#             (
#                 center_x - title_width // 2,
#                 180 # 180 default
#             ),
#             title,
#             fill="black",
#             font=self.font_large
#         )
#
#         # --------------------------------------------------------
#         # Student information
#         # --------------------------------------------------------
#
#         y = 290
#
#         draw.text(
#             (180, y),
#             f"Name: {self.name}",
#             fill="black",
#             font=self.font_medium
#         )
#
#         draw.text(
#             (1100, y),
#             f"Class: {self.class_standard}",
#             fill="black",
#             font=self.font_medium
#         )
#
#         # draw.text(
#         #     (180, y + 70),
#         #     f"Class: {self.class_standard}",
#         #     fill="black",
#         #     font=self.font_medium
#         # )
#
#         draw.text(
#             (1550, y),
#             f"Section: {self.class_division}",
#             fill="black",
#             font=self.font_medium
#         )
#
#         draw.text(
#             (180, y + 70),
#             f"Admission No: {self.admission_number}",
#             fill="black",
#             font=self.font_medium
#         )
#
#         draw.text(
#             (1100, y + 70),
#             f"Subject: {self.subject}",
#             fill="black",
#             font=self.font_medium
#         )
#
#         # --------------------------------------------------------
#         # Page indicator
#         # --------------------------------------------------------
#
#         page_text = f"Page {page_number} of {total_pages}"
#
#         bbox = draw.textbbox(
#             (0, 0),
#             page_text,
#             font=self.font_small
#         )
#
#         page_width = bbox[2] - bbox[0]
#
#         draw.text(
#             (
#                 self.WIDTH - 180 - page_width,
#                 self.HEIGHT - 180 # original: y
#             ),
#             page_text,
#             fill="black",
#             font=self.font_small
#         )
#
#         # --------------------------------------------------------
#         # Sheet identifier
#         # --------------------------------------------------------
#
#         sheet_id_str = f"Sheet ID: {self.sheet_id}"
#
#
#         draw.text(
#             (
#                 self.WIDTH - 300 - page_width,
#                 y + 100  # Original y + 70
#             ),
#             sheet_id_str,
#             fill="black",
#             font=self.font_small
#         )
#
#
#
#         # --------------------------------------------------------
#         # Separator
#         # --------------------------------------------------------
#
#         draw.line(
#             (
#                 150,
#                 self.HEADER_HEIGHT,
#                 self.WIDTH - 150,
#                 self.HEADER_HEIGHT
#             ),
#             fill="black",
#             width=5
#         )
#
#
#     # ============================================================
#     # Draw a bubble
#     # ============================================================
#
#     def draw_bubble(
#         self,
#         draw,
#         x,
#         y
#     ):
#
#         radius = self.BUBBLE_RADIUS
#
#         draw.ellipse(
#             [
#                 x - radius,
#                 y - radius,
#                 x + radius,
#                 y + radius
#             ],
#             outline="black",
#             width=5
#         )
#
#     # ============================================================
#     # Calculate how many questions fit vertically
#     # ============================================================
#
#     def get_questions_per_column(self):
#
#         available_height = (
#             self.HEIGHT
#             - self.START_Y
#             - self.BOTTOM_MARGIN
#         )
#
#         questions = (
#             available_height
#             // self.QUESTION_SPACING
#         )
#
#         return max(1, questions)
#
#     # ============================================================
#     # Calculate number of columns required
#     # ============================================================
#
#     def get_columns(self):
#
#         questions_per_column = (
#             self.get_questions_per_column()
#         )
#
#         columns = (
#             self.no_of_questions
#             + questions_per_column
#             - 1
#         ) // questions_per_column
#
#         return columns
#
#     # ============================================================
#     # Draw questions on a page
#     # ============================================================
#
#     def draw_questions(self, draw, first_question, number_of_questions):
#
#         # Maximum vertical capacity
#         questions_per_column = ( self.get_questions_per_column())
#
#         # Number of columns required for THIS page
#         columns = (
#             number_of_questions
#             + questions_per_column
#             - 1
#         ) // questions_per_column
#
#         # --------------------------------------------------------
#         # Calculate column width
#         # --------------------------------------------------------
#
#         usable_width = (
#             self.WIDTH
#             - 2 * self.MARGIN
#         )
#
#         column_width = (
#             usable_width
#             - (columns - 1) * self.COLUMN_GAP
#         ) // columns
#
#         # --------------------------------------------------------
#         # Draw every question
#         # --------------------------------------------------------
#
#         for local_index in range(number_of_questions):
#
#             question_number = (
#                 first_question
#                 + local_index
#             )
#
#             column = (
#                 local_index
#                 // questions_per_column
#             )
#
#             row = (
#                 local_index
#                 % questions_per_column
#             )
#
#             x = (
#                 self.MARGIN + 100
#                 + column * (
#                     column_width
#                     + self.COLUMN_GAP
#                 )
#             )
#
#             y = (
#                 self.START_Y
#                 + row * self.QUESTION_SPACING
#             )
#
#             # ----------------------------------------------------
#             # Question number
#             # ----------------------------------------------------
#
#             question_text = f"{question_number}."
#
#             draw.text(
#                 (
#                     x,
#                     y - 25
#                 ),
#                 question_text,
#                 fill="black",
#                 font=self.font_small
#             )
#
#             # ----------------------------------------------------
#             # Bubbles
#             # ----------------------------------------------------
#
#             bubble_start_x = x + 100
#
#             for choice_index, choice in enumerate(
#                 self.choices
#             ):
#
#                 bubble_x = (
#                     bubble_start_x
#                     + choice_index
#                     * self.BUBBLE_SPACING
#                 )
#
#                 bubble_y = y
#
#                 self.draw_bubble(
#                     draw,
#                     bubble_x,
#                     bubble_y
#                 )
#
#                 # Choice letter
#                 bbox = draw.textbbox(
#                     (0, 0),
#                     choice,
#                     font=self.font_tiny
#                 )
#
#                 choice_width = (
#                     bbox[2] - bbox[0]
#                 )
#
#                 draw.text(
#                     (
#                         bubble_x
#                         - choice_width // 2,
#                         bubble_y + 32
#                     ),
#                     choice,
#                     fill="black",
#                     font=self.font_tiny
#                 )
#
#     # ============================================================
#     # Generate pages
#     # ============================================================
#
#     def generate(self):
#
#         self.pages = []
#
#         # --------------------------------------------------------
#         # Determine page capacity
#         # --------------------------------------------------------
#
#         questions_per_column = (
#             self.get_questions_per_column()
#         )
#
#         # We use 2 columns by default.
#         #
#         # If more questions exist than can fit in two
#         # columns, we create another page instead.
#         #
#         # This keeps the sheet readable.
#         max_questions_per_page = (
#             questions_per_column * 2
#         )
#
#         # --------------------------------------------------------
#         # Determine number of pages
#         # --------------------------------------------------------
#
#         total_pages = (
#             self.no_of_questions
#             + max_questions_per_page
#             - 1
#         ) // max_questions_per_page
#
#         # --------------------------------------------------------
#         # Generate each page
#         # --------------------------------------------------------
#
#         current_question = 1
#
#         for page_number in range(
#             1,
#             total_pages + 1
#         ):
#
#             remaining = (
#                 self.no_of_questions
#                 - current_question
#                 + 1
#             )
#
#             questions_on_page = min(
#                 remaining,
#                 max_questions_per_page
#             )
#
#             # Create page
#             image, draw = self.create_page()
#
#             # Page components
#             self.draw_border(draw)
#
#             self.draw_registration_markers(draw)
#
#             image.paste(self.qr_img, (self.WIDTH - self.MARGIN - 400, 110) )
#
#             self.draw_header(
#                 draw,
#                 page_number,
#                 total_pages
#             )
#
#
#
#             # Questions
#             self.draw_questions(
#                 draw,
#                 current_question,
#                 questions_on_page
#             )
#
#             # Store page
#             self.pages.append(image)
#
#             # Move to next question
#             current_question += (
#                 questions_on_page
#             )
#
#         return self.pages
#
#     # ============================================================
#     # Save every page as PNG
#     # ============================================================
#
#     def save_png(self, prefix="omr"):
#
#         if not self.pages:
#
#             self.generate()
#
#         for index, page in enumerate(self.pages, start=1):
#             filename = (f"{prefix}_page_{index}.png")
#
#             page.save(
#                 filename,
#                 dpi=(self.DPI, self.DPI)
#             )
#
#             print(f"Saved: {filename}")
#
#     # ============================================================
#     # Save all pages as one PDF
#     # ============================================================
#
#     def save_pdf(self, filename="omr_sheet.pdf"):
#
#         if not self.pages:
#
#             self.generate()
#
#         # Convert RGB pages to RGB
#         pages = [
#             page.convert("RGB")
#             for page in self.pages
#         ]
#
#         first_page = pages[0]
#
#         remaining_pages = pages[1:]
#
#         first_page.save(
#             filename,
#             "PDF",
#             resolution=self.DPI,
#             save_all=True,
#             append_images=remaining_pages
#         )
#
#         print(f"Saved PDF: {filename}")
#
#
# # ================================================================
# # Example
# # ================================================================
# if __name__ == "__main__":
#     OMR = GenerateOMR(subject="Physics",name="Seraphine", class_standard="XI", class_division="C1", admission_number="3122", no_of_questions=80)
#
#     OMR.generate()
#
#     OMR.save_png("Seraphine_OMR")
#
#     OMR.save_pdf("Seraphine_OMR.pdf")
#
#

import base64
import hashlib
import json
import math
from pathlib import Path
import zlib
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

        self.font_student = (
            self.load_font(60)
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

            Path("C:/Windows/Fonts/segoeui.ttf"),

            Path("C:/Windows/Fonts/arial.ttf"),

            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans.ttf",

            "/usr/share/fonts/truetype/"
            "liberation2/"
            "LiberationSans-Regular.ttf",
        ]

        for path in paths:

            try:

                return ImageFont.truetype(path, size)

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

                font=self.font_student
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

                    font=self.font_student
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
