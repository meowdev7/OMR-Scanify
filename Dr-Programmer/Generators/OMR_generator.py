from PIL import Image, ImageDraw, ImageFont
import qrcode


class GenerateOMR:

    # ============================================================
    # A4 @ 300 DPI
    # ============================================================

    WIDTH = 2480
    HEIGHT = 3508
    DPI = 300

    # ============================================================
    # Layout settings
    # ============================================================

    MARGIN = 100

    HEADER_HEIGHT = 470

    START_Y = 560
    BOTTOM_MARGIN = 180

    QUESTION_SPACING = 105

    # Space between question columns
    COLUMN_GAP = 70

    # Distance between bubbles
    BUBBLE_SPACING = 150
    BUBBLE_RADIUS = 24


    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self, name="", class_standard="XII", class_division="", admission_number="", no_of_questions=20, choices=("A", "B", "C", "D"), subject=""):
        self.name = name
        self.class_standard = class_standard
        self.class_division = class_division
        self.admission_number = str(admission_number)

        self.no_of_questions = no_of_questions
        self.choices = choices
        self.subject = subject
        self.sheet_id = self.subject.upper()[:3] + self.admission_number
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction helps readability
            box_size=10,
            border=4,
        )
        self.qr.add_data(self.sheet_id)
        self.qr.make(fit=True)

        self.qr_img = self.qr.make_image().convert("RGB")

        self.pages = []        # Every generated page will be stored here


        # Fonts
        self.font_large = self.load_font(55)
        self.font_medium = self.load_font(42)
        self.font_small = self.load_font(32)
        self.font_tiny = self.load_font(26)


    # ============================================================
    # Font loader
    # ============================================================

    def load_font(self, size):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
        ]

        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)

            except:
                pass

        return ImageFont.load_default()

    # ============================================================
    # Create a new blank A4 page
    # ============================================================

    def create_page(self):

        image = Image.new(
            "RGB",
            (self.WIDTH, self.HEIGHT),
            "white"
        )

        draw = ImageDraw.Draw(image)

        return image, draw

    # ============================================================
    # Registration markers
    # ============================================================

    def draw_registration_markers(self, draw):

        size = 60
        margin = self.MARGIN

        positions = [
            # Top-left
            (margin, margin),

            # Top-right
            (self.WIDTH - margin - size, margin),

            # Bottom-left
            (margin, self.HEIGHT - margin - size),

            # Bottom-right
            (self.WIDTH - margin - size, self.HEIGHT - margin - size)
        ]

        for x, y in positions:
            draw.rectangle(
                [x,
                 y,
                 x + size,
                 y + size
                 ],
                fill="black"
            )

    # ============================================================
    # Page border
    # ============================================================

    def draw_border(self, draw):

        margin = self.MARGIN

        draw.rectangle(
            [
                margin,
                margin,
                self.WIDTH - margin,
                self.HEIGHT - margin
            ],
            outline="black",
            width=8
        )

    # ============================================================
    # Header
    # ============================================================

    def draw_header(self, draw, page_number, total_pages):
        center_x = self.WIDTH // 2

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------

        title = "OMR ANSWER SHEET"

        bbox = draw.textbbox((0, 0), title, font=self.font_large)

        title_width = bbox[2] - bbox[0]

        draw.text(
            (
                center_x - title_width // 2,
                180 # 180 default
            ),
            title,
            fill="black",
            font=self.font_large
        )

        # --------------------------------------------------------
        # Student information
        # --------------------------------------------------------

        y = 290

        draw.text(
            (180, y),
            f"Name: {self.name}",
            fill="black",
            font=self.font_medium
        )

        draw.text(
            (1100, y),
            f"Class: {self.class_standard}",
            fill="black",
            font=self.font_medium
        )

        # draw.text(
        #     (180, y + 70),
        #     f"Class: {self.class_standard}",
        #     fill="black",
        #     font=self.font_medium
        # )

        draw.text(
            (1550, y),
            f"Section: {self.class_division}",
            fill="black",
            font=self.font_medium
        )

        draw.text(
            (180, y + 70),
            f"Admission No: {self.admission_number}",
            fill="black",
            font=self.font_medium
        )

        draw.text(
            (1100, y + 70),
            f"Subject: {self.subject}",
            fill="black",
            font=self.font_medium
        )

        # --------------------------------------------------------
        # Page indicator
        # --------------------------------------------------------

        page_text = f"Page {page_number} of {total_pages}"

        bbox = draw.textbbox(
            (0, 0),
            page_text,
            font=self.font_small
        )

        page_width = bbox[2] - bbox[0]

        draw.text(
            (
                self.WIDTH - 180 - page_width,
                self.HEIGHT - 180 # originat: y
            ),
            page_text,
            fill="black",
            font=self.font_small
        )

        # --------------------------------------------------------
        # Sheet identifier
        # --------------------------------------------------------

        sheet_id_str = f"Sheet ID: {self.sheet_id}"


        draw.text(
            (
                self.WIDTH - 300 - page_width,
                y + 100  # Original y + 70
            ),
            sheet_id_str,
            fill="black",
            font=self.font_small
        )



        # --------------------------------------------------------
        # Separator
        # --------------------------------------------------------

        draw.line(
            (
                150,
                self.HEADER_HEIGHT,
                self.WIDTH - 150,
                self.HEADER_HEIGHT
            ),
            fill="black",
            width=5
        )


    # ============================================================
    # Draw a bubble
    # ============================================================

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

    # ============================================================
    # Calculate how many questions fit vertically
    # ============================================================

    def get_questions_per_column(self):

        available_height = (
            self.HEIGHT
            - self.START_Y
            - self.BOTTOM_MARGIN
        )

        questions = (
            available_height
            // self.QUESTION_SPACING
        )

        return max(1, questions)

    # ============================================================
    # Calculate number of columns required
    # ============================================================

    def get_columns(self):

        questions_per_column = (
            self.get_questions_per_column()
        )

        columns = (
            self.no_of_questions
            + questions_per_column
            - 1
        ) // questions_per_column

        return columns

    # ============================================================
    # Draw questions on a page
    # ============================================================

    def draw_questions(self, draw, first_question, number_of_questions):

        # Maximum vertical capacity
        questions_per_column = ( self.get_questions_per_column())

        # Number of columns required for THIS page
        columns = (
            number_of_questions
            + questions_per_column
            - 1
        ) // questions_per_column

        # --------------------------------------------------------
        # Calculate column width
        # --------------------------------------------------------

        usable_width = (
            self.WIDTH
            - 2 * self.MARGIN
        )

        column_width = (
            usable_width
            - (columns - 1) * self.COLUMN_GAP
        ) // columns

        # --------------------------------------------------------
        # Draw every question
        # --------------------------------------------------------

        for local_index in range(number_of_questions):

            question_number = (
                first_question
                + local_index
            )

            column = (
                local_index
                // questions_per_column
            )

            row = (
                local_index
                % questions_per_column
            )

            x = (
                self.MARGIN + 100
                + column * (
                    column_width
                    + self.COLUMN_GAP
                )
            )

            y = (
                self.START_Y
                + row * self.QUESTION_SPACING
            )

            # ----------------------------------------------------
            # Question number
            # ----------------------------------------------------

            question_text = f"{question_number}."

            draw.text(
                (
                    x,
                    y - 25
                ),
                question_text,
                fill="black",
                font=self.font_small
            )

            # ----------------------------------------------------
            # Bubbles
            # ----------------------------------------------------

            bubble_start_x = x + 100

            for choice_index, choice in enumerate(
                self.choices
            ):

                bubble_x = (
                    bubble_start_x
                    + choice_index
                    * self.BUBBLE_SPACING
                )

                bubble_y = y

                self.draw_bubble(
                    draw,
                    bubble_x,
                    bubble_y
                )

                # Choice letter
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
                        bubble_y + 32
                    ),
                    choice,
                    fill="black",
                    font=self.font_tiny
                )

    # ============================================================
    # Generate pages
    # ============================================================

    def generate(self):

        self.pages = []

        # --------------------------------------------------------
        # Determine page capacity
        # --------------------------------------------------------

        questions_per_column = (
            self.get_questions_per_column()
        )

        # We use 2 columns by default.
        #
        # If more questions exist than can fit in two
        # columns, we create another page instead.
        #
        # This keeps the sheet readable.
        max_questions_per_page = (
            questions_per_column * 2
        )

        # --------------------------------------------------------
        # Determine number of pages
        # --------------------------------------------------------

        total_pages = (
            self.no_of_questions
            + max_questions_per_page
            - 1
        ) // max_questions_per_page

        # --------------------------------------------------------
        # Generate each page
        # --------------------------------------------------------

        current_question = 1

        for page_number in range(
            1,
            total_pages + 1
        ):

            remaining = (
                self.no_of_questions
                - current_question
                + 1
            )

            questions_on_page = min(
                remaining,
                max_questions_per_page
            )

            # Create page
            image, draw = self.create_page()

            # Page components
            self.draw_border(draw)

            self.draw_registration_markers(draw)

            image.paste(self.qr_img, (self.WIDTH - self.MARGIN - 400, 110) )

            self.draw_header(
                draw,
                page_number,
                total_pages
            )



            # Questions
            self.draw_questions(
                draw,
                current_question,
                questions_on_page
            )

            # Store page
            self.pages.append(image)

            # Move to next question
            current_question += (
                questions_on_page
            )

        return self.pages

    # ============================================================
    # Save every page as PNG
    # ============================================================

    def save_png(self, prefix="omr"):

        if not self.pages:

            self.generate()

        for index, page in enumerate(self.pages, start=1):
            filename = (f"{prefix}_page_{index}.png")

            page.save(
                filename,
                dpi=(self.DPI, self.DPI)
            )

            print(f"Saved: {filename}")

    # ============================================================
    # Save all pages as one PDF
    # ============================================================

    def save_pdf(self, filename="omr_sheet.pdf"):

        if not self.pages:

            self.generate()

        # Convert RGB pages to RGB
        pages = [
            page.convert("RGB")
            for page in self.pages
        ]

        first_page = pages[0]

        remaining_pages = pages[1:]

        first_page.save(
            filename,
            "PDF",
            resolution=self.DPI,
            save_all=True,
            append_images=remaining_pages
        )

        print(f"Saved PDF: {filename}")


# ================================================================
# Example
# ================================================================
if __name__ == "__main__":
    OMR = GenerateOMR(subject="Physics",name="Seraphine", class_standard="XI", class_division="C1", admission_number="3122", no_of_questions=80)

    OMR.generate()

    OMR.save_png("Seraphine_OMR")

    OMR.save_pdf("Seraphine_OMR.pdf")


