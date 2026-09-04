from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def scan_answer_sheet_files(files, question_count, templates_directory=None, debug_directory=None):
    """Scan answer-sheet images and return submission-ready records and failures."""
    from services.Scanner.OMR_scanner import OMRScanner, scan_file

    services_directory = Path(__file__).resolve().parent.parent / "services"
    templates_path = Path(templates_directory or services_directory / "Templates")
    debug_path = Path(debug_directory or services_directory / "Output" / "debug")
    scanner = OMRScanner(templates_path)
    scanned_sheets = {}
    failures = []

    for file_path in files:
        path = Path(file_path)
        try:
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                raise ValueError("Only PNG, JPG, and JPEG answer sheets are supported.")
            document = scan_file(scanner, path, debug_path, None)
            pages = document.get("pages") or []
            if not pages:
                raise ValueError("The scanner did not produce a page result.")

            sheet_id = str(next((page.get("sheet_id") for page in pages if page.get("sheet_id")), "")).strip()
            if not sheet_id:
                raise ValueError("No student ID was found in the sheet QR code.")
            scanned_sheets.setdefault(sheet_id, {"files": [], "pages": []})["files"].append(str(path))
            scanned_sheets[sheet_id]["pages"].extend(pages)
        except Exception as error:
            failures.append({"file": str(path), "error": str(error)})

    submissions = []
    for sheet_id, sheet in scanned_sheets.items():
        pages = sorted(sheet["pages"], key=lambda page: (int(page.get("page", 1)), int(page.get("first_question", 1))))
        student = normalize_student(pages[0].get("student"), sheet_id)
        identity_page = next((page for page in pages if page.get("page_type") == "identity"), pages[0])
        student_details = normalize_student_details(identity_page.get("student_details"))
        identity_mismatches = compare_identity(student, student_details)
        answers_by_question = {}
        scan_details = []
        for page in pages:
            if str(page.get("sheet_id", "")).strip() != sheet_id:
                failures.append({"file": ", ".join(sheet["files"]), "error": "The uploaded pages contain different student IDs."})
                continue
            for question in page.get("questions") or []:
                question_number = int(question["question"])
                answers_by_question[question_number] = normalize_answer(question.get("answer"))
                scan_details.append({"question": question_number, "answer": answers_by_question[question_number], "confidence": float(question.get("confidence") or 0), "page": int(page.get("page", 1))})
        missing_questions = [number for number in range(1, int(question_count) + 1) if number not in answers_by_question]
        if missing_questions:
            failures.append({"file": ", ".join(sheet["files"]), "error": f"The scan is missing question(s): {', '.join(map(str, missing_questions[:8]))}."})
            continue
        submissions.append({"file": ", ".join(sheet["files"]), "sheet_id": sheet_id, "student": student, "student_details": student_details, "identity_status": "mismatch" if identity_mismatches else "verified", "identity_mismatches": identity_mismatches, "answers": [answers_by_question[number] for number in range(1, int(question_count) + 1)], "scan": scan_details})

    return submissions, failures


def normalize_answer(value):
    answer = str(value or "").strip().upper()
    if answer in {"", "-", "?"}:
        return None
    if answer not in {"A", "B", "C", "D"}:
        raise ValueError(f"Unsupported scanned answer '{answer}'.")
    return answer


def normalize_student(value, sheet_id=""):
    student = value if isinstance(value, dict) else {}
    details = {
        "id": str(student.get("id", "")).strip() or sheet_id,
        "name": str(student.get("name", "")).strip(),
        "class": str(student.get("class", "")).strip(),
        "section": str(student.get("section", "")).strip(),
        "roll_no": str(student.get("roll_no", student.get("admission", ""))).strip(),
    }
    if not details["id"] or not details["name"]:
        raise ValueError("The sheet QR code does not contain a student name.")
    return details


def normalize_student_details(value):
    details = value if isinstance(value, dict) else {}
    return {
        key: str(details.get(key) or "").strip()
        for key in ("name", "subject", "roll_no", "class", "section", "set")
    }


def compare_identity(student, details):
    pairs = {
        "name": "name",
        "class": "class",
        "section": "section",
        "roll_no": "roll_no",
    }
    return [
        field
        for field, student_field in pairs.items()
        if details.get(field) and details[field] != "?" and details[field].upper() != str(student.get(student_field, "")).upper()
    ]