from Generators import OMR_generator
import GUI

data = GUI.OMR_generation_form()
print(data)

if data is None:
    exit()

OMR1 = OMR_generator.GenerateOMR(
    name=data["Name"],
    class_standard=data["Class"],
    class_division=data["Section"],
    admission_number=data["Admission Number"],
    subject=data["Subject"],
    no_of_questions=int(data["No of Questions"]))

OMR1.save_png()