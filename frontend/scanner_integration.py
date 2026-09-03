from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def scan_answer_sheet_files(files, question_count, templates_directory=None, debug_directory=None):
    """Scan answer-sheet images and return submission-ready records and failures."""
    from services.Scanner.OMR_scanner import OMRScanner, scan_file

    services_directory = Path(__file__).resolve().parent.parent / "services"
    templates_path = Path(templates_directory or services_directory / "Templates")
    debug_path = Path(debug_directory or services_directory / "Output" / "debug")
    scanner = OMRScanner(templates_path)
    submissions = []
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

            pages.sort(key=lambda page: (int(page.get("page", 1)), int(page.get("first_question", 1))))
            sheet_id = str(pages[0].get("sheet_id", "")).strip()
            if not sheet_id:
                raise ValueError("No student ID was found in the sheet QR code.")
            student = normalize_student(pages[0].get("student"), sheet_id)

            answers_by_question = {}
            scan_details = []
            for page in pages:
                if str(page.get("sheet_id", "")).strip() != sheet_id:
                    raise ValueError("The uploaded pages contain different student IDs.")
                if normalize_student(page.get("student"), sheet_id) != student:
                    raise ValueError("The uploaded pages contain different student details.")
                for question in page.get("questions") or []:
                    question_number = int(question["question"])
                    answer = normalize_answer(question.get("answer"))
                    answers_by_question[question_number] = answer
                    scan_details.append({
                        "question": question_number,
                        "answer": answer,
                        "confidence": float(question.get("confidence") or 0),
                        "page": int(page.get("page", 1)),
                    })

            answers = [answers_by_question.get(number) for number in range(1, int(question_count) + 1)]
            missing_questions = [number for number in range(1, int(question_count) + 1) if number not in answers_by_question]
            if missing_questions:
                raise ValueError(f"The scan is missing question(s): {', '.join(map(str, missing_questions[:8]))}.")

            submissions.append({"file": str(path), "sheet_id": sheet_id, "student": student, "answers": answers, "scan": scan_details})
        except Exception as error:
            failures.append({"file": str(path), "error": str(error)})

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