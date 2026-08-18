# from Generators import OMR_generator
# import GUI
#
# data = GUI.OMR_generation_form()
# print(data)
#
# if data is None:
#     exit()
#
# OMR1 = OMR_generator.GenerateOMR(
#     name=data["Name"],
#     class_standard=data["Class"],
#     class_division=data["Section"],
#     admission_number=data["Admission Number"],
#     subject=data["Subject"],
#     no_of_questions=int(data["No of Questions"]))

# OMR1.save_png("test.png")
# from Generators.OMR_generator import GenerateOMR
# from GUI import OMR_generation_form
# # import csv
# # import os
# #
# #
# # def generate_student(data, output_dir="output"):
# #     os.makedirs(output_dir, exist_ok=True)
# #
# #     omr = GenerateOMR(
# #         name=data["Name"],
# #         class_standard=data["Class"],
# #         class_division=data["Section"],
# #         admission_number=data["Admission Number"],
# #         subject=data["Subject"],
# #         no_of_questions=int(data["No of Questions"])
# #     )
# #
# #     filename = (
# #         f"{data['Name']}_{data['Admission Number']}_OMR.pdf"
# #     )
# #
# #     filepath = os.path.join(output_dir, filename)
# #
# #     omr.save_pdf(filepath)
# #
# #     return filepath
# #
# #
# # def generate_from_csv(csv_file, output_dir="output"):
# #     generated_files = []
# #
# #     with open(csv_file, newline="", encoding="utf-8-sig") as file:
# #         reader = csv.DictReader(file)
# #
# #         for student in reader:
# #             filepath = generate_student(student, output_dir)
# #             generated_files.append(filepath)
# #
# #     return generated_files
# #
# #
# # if __name__ == "__main__":
# #
# #     data = OMR_generation_form()
# #
# #     if data is None:
# #         exit()
# #
# #     if data["mode"] == "single":
# #
# #         generate_student(data)
# #
# #     elif data["mode"] == "csv":
# #
# #         generate_from_csv(data["csv_file"])
#
#
#
# from Generators.OMR_generator import GenerateOMR
# from GUI import OMR_generation_form
#
# import csv
# import os
#
#
# OUTPUT_DIR = "output"
#
#
# def generate_student(data):
#
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#
#     omr = GenerateOMR(
#         name=data["Name"],
#         class_standard=data["Class"],
#         class_division=data["Section"],
#         admission_number=data["Admission Number"],
#         subject=data["Subject"],
#         no_of_questions=int(data["No of Questions"])
#     )
#
#     filename = (
#         f"{data['Name']}_"
#         f"{data['Admission Number']}_OMR.pdf"
#     )
#
#     filepath = os.path.join(
#         OUTPUT_DIR,
#         filename
#     )
#
#     omr.save_pdf(filepath)
#
#     print(f"Generated: {filepath}")
#
#
# def generate_from_csv(csv_file):
#
#     with open(
#         csv_file,
#         newline="",
#         encoding="utf-8-sig"
#     ) as file:
#
#         reader = csv.DictReader(file)
#
#         for student in reader:
#
#             generate_student(student)
#
#
# if __name__ == "__main__":
#
#     data = OMR_generation_form()
#
#     if data is None:
#         exit()
#
#     # =========================================================
#     # CSV
#     # =========================================================
#
#     if data["mode"] == "csv":
#
#         generate_from_csv(
#             data["csv_file"]
#         )
#

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Main code
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++






from Generators.OMR_generator import GenerateOMR
from GUI import OMR_generation_form

import csv
import os


OUTPUT_DIR = "output"


def generate_student(data):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    omr = GenerateOMR(
        name=data["Name"],
        class_standard=data["Class"],
        class_division=data["Section"],
        admission_number=data["Admission Number"],
        subject=data["Subject"],
        no_of_questions=int(data["No of Questions"])
    )

    filename = (
        f"{data['Name']}_"
        f"{data['Admission Number']}_OMR.pdf"
    )

    filepath = os.path.join(OUTPUT_DIR, filename)

    omr.save_pdf(filepath)

    print(f"Generated: {filepath}")


def generate_from_csv(csv_file):

    with open(csv_file, newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for student in reader:

            generate_student(student)


if __name__ == "__main__":

    data = OMR_generation_form()

    if data is None:
        exit()

    # =========================================================
    # CSV
    # =========================================================

    if data["mode"] == "csv":

        generate_from_csv(
            data["csv_file"]
        )

    # =========================================================
    # SINGLE STUDENT
    # =========================================================

    elif data["mode"] == "single":

        generate_student(data)

