import cv2
import numpy as np


# ==========================================
# LOAD IMAGE
# ==========================================

img = cv2.imread("test2.png")

if img is None:
    print("Image not found!")
    exit()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)

print("Image:", gray.shape)


# ==========================================
# FIND CIRCLES
# ==========================================

circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=25,
    param1=100,
    param2=28,
    minRadius=15,
    maxRadius=28
)

if circles is None:
    print("No circles found!")
    exit()

circles = np.round(circles[0]).astype(int)

print("Circles found:", len(circles))


# ==========================================
# GROUP X POSITIONS
# ==========================================

x_values = sorted(c[0] for c in circles)

x_groups = []
group = [x_values[0]]

for x in x_values[1:]:

    if x - group[-1] <= 25:
        group.append(x)
    else:
        x_groups.append(group)
        group = [x]

x_groups.append(group)

x_centers = [
    round(np.mean(group))
    for group in x_groups
]

print("\nX centers:")
print(x_centers)


# ==========================================
# FIND 4 EQUALLY SPACED COLUMNS
# ==========================================

column_groups = []

for i in range(len(x_centers)):

    for j in range(i + 1, len(x_centers)):

        gap = x_centers[j] - x_centers[i]

        if gap < 100:
            continue

        expected = [
            x_centers[i],
            x_centers[i] + gap,
            x_centers[i] + gap * 2,
            x_centers[i] + gap * 3
        ]

        found = []

        for value in expected:

            nearest = min(
                x_centers,
                key=lambda x: abs(x - value)
            )

            if abs(nearest - value) <= 20:
                found.append(nearest)

        if len(found) == 4:

            gaps = np.diff(found)

            if max(gaps) - min(gaps) < 20:

                if found not in column_groups:
                    column_groups.append(found)


# Remove duplicate versions of the same group
unique_columns = []

for group in column_groups:

    if not any(
        max(abs(a - b) for a, b in zip(group, old)) < 10
        for old in unique_columns
    ):
        unique_columns.append(group)

column_groups = unique_columns


print("\nColumn groups:")

for group in column_groups:
    print(group)


if len(column_groups) < 2:
    print("Could not find two OMR blocks!")
    exit()


# IMPORTANT:
# Sort blocks by their X position.

column_groups.sort(
    key=lambda group: group[0]
)

left_x = column_groups[0]
right_x = column_groups[-1]

print("\nLEFT :", left_x)
print("RIGHT:", right_x)


# ==========================================
# GET Y VALUES FOR A BLOCK
# ==========================================

def get_y_values(x_columns):

    ys = []

    for x, y, r in circles:

        for column_x in x_columns:

            if abs(x - column_x) <= 25:
                ys.append(y)
                break

    return sorted(ys)


# ==========================================
# MERGE DUPLICATE Y DETECTIONS
# ==========================================

def merge_y_values(ys):

    if not ys:
        return []

    rows = []
    group = [ys[0]]

    for y in ys[1:]:

        if abs(y - np.mean(group)) <= 15:
            group.append(y)
        else:
            rows.append(round(np.mean(group)))
            group = [y]

    rows.append(round(np.mean(group)))

    return rows


# ==========================================
# FIND THE REGULAR ROW SEQUENCE
# ==========================================

def find_regular_rows(ys):

    rows = merge_y_values(ys)

    if len(rows) < 2:
        return rows

    gaps = np.diff(rows)

    # Ignore tiny gaps caused by false detections.
    real_gaps = [
        gap for gap in gaps
        if gap > 50
    ]

    spacing = np.median(real_gaps)

    print("Estimated row spacing:", round(spacing, 1))

    best = []

    # Try every detected row as a starting point.
    for start in rows:

        sequence = [start]
        current = start

        while True:

            target = current + spacing

            candidates = [
                y for y in rows
                if y > current + 50
            ]

            if not candidates:
                break

            next_y = min(
                candidates,
                key=lambda y: abs(y - target)
            )

            if abs(next_y - target) <= 20:
                sequence.append(next_y)
                current = next_y
            else:
                break

        if len(sequence) > len(best):
            best = sequence

    return best


# ==========================================
# FIND ROWS
# ==========================================

left_y = find_regular_rows(
    get_y_values(left_x)
)

right_y = find_regular_rows(
    get_y_values(right_x)
)

print("\nLEFT rows:")
print(left_y)

print("\nRIGHT rows:")
print(right_y)

print(
    "\nLeft question count:",
    len(left_y)
)

print(
    "Right question count:",
    len(right_y)
)


# ==========================================
# MEASURE BUBBLE
# ==========================================

def bubble_score(x, y):

    radius = 8

    roi = gray[
        y - radius:y + radius,
        x - radius:x + radius
    ]

    if roi.size == 0:
        return 255

    return np.mean(roi)


# ==========================================
# READ ANSWERS
# ==========================================

letters = "ABCD"


def scan_block(xs, ys, first_question):

    for i, y in enumerate(ys):

        scores = []

        for x in xs:

            scores.append(
                bubble_score(x, y)
            )

        darkest = np.argmin(scores)

        # All bubbles are bright
        if scores[darkest] > 200:
            answer = "-"

        else:
            answer = letters[darkest]

        question = first_question + i

        print(
            f"Q{question:02d}: "
            f"{answer} "
            f"{[round(s, 1) for s in scores]}"
        )


print("\n========== ANSWERS ==========")

scan_block(
    left_x,
    left_y,
    1
)

scan_block(
    right_x,
    right_y,
    27
)


# ==========================================
# DRAW GRID
# ==========================================

for xs, ys, first_question in [
    (left_x, left_y, 1),
    (right_x, right_y, 27)
]:

    for i, y in enumerate(ys):

        question = first_question + i

        for option, x in enumerate(xs):

            cv2.circle(
                img,
                (x, y),
                12,
                (0, 255, 0),
                2
            )

            cv2.putText(
                img,
                letters[option],
                (x - 5, y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 255),
                1
            )

        cv2.putText(
            img,
            str(question),
            (xs[0] - 40, y + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            1
        )


# ==========================================
# SHOW RESULT
# ==========================================

cv2.namedWindow(
    "OMR",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "OMR",
    800,
    600
)

cv2.imshow(
    "OMR",
    img
)

cv2.waitKey(0)
cv2.destroyAllWindows()