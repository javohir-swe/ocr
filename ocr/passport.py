import re
import os
import random
import shutil
import pytesseract
from PIL import Image
from datetime import datetime


def save_file_to_media(file_path):
    media_folder = "media"
    if not os.path.exists(media_folder):
        os.makedirs(media_folder)

    random_number = random.randint(100000, 999999)

    file_format = os.path.splitext(file_path)[-1]
    new_filename = f"image_{random_number}{file_format}"
    new_file_path = os.path.join(media_folder, new_filename)

    shutil.copy(file_path, new_file_path)
    # print(f"File saved to {new_file_path}")
    return new_file_path


def get_data_from_passport(file_path):

    saved_file_path = save_file_to_media(file_path)
    """
    Tasvir ichidagi MRZ matnlarini OCR yordamida o'qish.
    """
    try:
        # Tasvirni ochish
        image = Image.open(saved_file_path)
        # OCR yordamida matnni o'qish
        text = pytesseract.image_to_string(image)
        clean_text = get_clean_data(text)

# ================= Get FullName ================= #
        name_pattern = r"[A-Z]{2}[A-Z]+<<[A-Z]+"
        name_match = re.search(name_pattern, clean_text)
        if name_match:
            name_parts = name_match.group().split("<<")
            last_name = name_parts[0][3:]
            first_name = name_parts[1].replace("<", " ") if len(name_parts) > 1 else ""
            print(f"last_name: {last_name.title()}")
            print(f"first_name: {first_name.title()}")
        else:
            return "Ism Familiyani topishda muammo bo'ldi!!!"

# =============== Get Passport data =============== #
        passport_number_pattern = r"[A-Z]{2}[0-9]{7}"

        match = re.search(passport_number_pattern, clean_text)
        if match:
            passport_number = match.group()  # Topilgan passport raqamini olamiz
            passport_id = passport_number
        else:
            passport_id = ""
        print(f"passport_id: {passport_id}")

# =============== Get Birth Date =============== #
        birth_date_pattern = r"[0-9]{2}[A-Z]{3}[0-9]{6}"  # 2 raqam + 3 harf + 6 raqam
        birth_date_match = re.search(birth_date_pattern, clean_text)
        if birth_date_match:
            birth_date = birth_date_match.group()[-6:]  # Oxirgi 6 ta raqamni olamiz
            current_year = datetime.now().year
            current_century = current_year // 100  # Masalan, 2024 -> 20
            current_year_last_two = current_year % 100  # Masalan, 2024 -> 24

            # Yilni 6 belgi ichidan olish
            birth_year_last_two = int(birth_date[:2])
            birth_month = birth_date[2:4]
            birth_day = birth_date[4:6]

            # Yilni to'liq qilish
            if birth_year_last_two > current_year_last_two:
                birth_year = (current_century - 1) * 100 + birth_year_last_two
            else:
                birth_year = current_century * 100 + birth_year_last_two
            # To'liq sana formatida natija
            birth_date = f"{birth_year:04d}-{birth_month}-{birth_day}"

            # print(f"Date of birth: {birth_date}")
        else:
            birth_date = ""
            print("Tug'ilgan sana topilmadi.")

# =============== Get Gender =============== #
        gender_pattern = r"[0-9]{6}(M|F)"  # 6 raqam + "M" yoki "F"
        gender_match = re.search(gender_pattern, clean_text)
        if gender_match:
            gender = "Male" if gender_match.group()[-1] == "M" else "Female"
            # print(f"Gender: {gender}")
        else:
            gender = ""
            print("Gender topilmadi.")

# =============== Get Expiry Date =============== #
        expiry_date_pattern = r"[0-9]{6}[M|F][0-9]{6}"  # Amal qilish sanasi yaqinidagi tuzilma
        expiry_date_match = re.search(expiry_date_pattern, clean_text)
        if expiry_date_match:
            expiry_date_raw = expiry_date_match.group()[-6:]  # Oxirgi 6 raqamni olish
            if len(expiry_date_raw) != 6 or not expiry_date_raw.isdigit():
                raise ValueError("MRZ qatoridagi amal qilish muddati noto'g'ri.")

            # Yilni aniqlash
            year = int(expiry_date_raw[:2]) + (2000 if int(expiry_date_raw[:2]) < 50 else 1900)

            # Oyni va kunni aniqlash
            month = int(expiry_date_raw[2:4])
            day = int(expiry_date_raw[4:6])

            # Oy va kunni tekshirish
            if not (1 <= month <= 12):
                raise ValueError(f"Noto'g'ri oy: {month}")
            if not (1 <= day <= 31):
                raise ValueError(f"Noto'g'ri kun: {day}")

            # To'g'ri formatda qaytarish
            result_expiry_date = f"{year}-{month:02d}-{day:02d}"
            # print(f"expiry_date: {result_expiry_date}")
        else:
            result_expiry_date = ""
            print("Amal qilish muddati topilmadi.")

        pass_last_name = last_name.title()
        pass_first_name = first_name.title()
        pass_date_of_birth = birth_date
        pass_passport_id = passport_id
        pass_expiry_date = result_expiry_date
        pass_gender = gender
        print_data = f"""\n\n\nLastname: {pass_last_name}\nFirstname: {pass_first_name}\nDate of birth: {pass_date_of_birth}\nPassport ID: {pass_passport_id}\nExpiry date: {pass_expiry_date}\nGender: {pass_gender}\n\n\n"""

        print(print_data)
        print("\n\n\n\n")
        # print(text.strip())
        print(clean_text)
        print("\n\n\n\n")
        return print_data
    except Exception as e:
        print(f"Xato yuz berdi: {e}")

    return "Ma'lumotlar topilmadi!!!"

    # print(f"Processing file: {saved_file_path}")


# Test uchun
# test_file = "images/passport2.jpg"  # Bu test uchun fayl yo'lini kiriting
# get_data_from_passport(test_file)
def get_clean_data(text):
    """
    MRZ (Machine-Readable Zone) qismini matndan ajratib olish.
    """
    # MRZ qismi uchun regex
    mrz_pattern = r"P<UZB.*"

    # Matnni tozalash (keraksiz bo'shliqlarni olib tashlash)
    cleaned_data = text.replace('\n', '').replace(' ', '')

    # MRZ qismni topish uchun regexni qo'llash
    mrz_match = re.search(mrz_pattern, cleaned_data)

    # MRZ topilgan bo'lsa qaytarish
    if mrz_match:
        return mrz_match.group()
    else:
        raise ValueError("MRZ qismi topilmadi!")















# Matnni kiriting
# input_text = """
# If MMi | GIVEN NAMES:
# JAVOKHIR
#
# FUQAROLIGI / NATIONALITY
#
# UZBEKISTAN
#
# TUGILGAN SANASI/ DATE OF BIRTH
# 22 02 2002
# F
#
# SEX |TUG'ILGAN JCYI / PLACE OF BIRTH
#
# TASHKENT REGION
#
# BERILGAN SANASI/ DATE OF ISSUE |PERSONALLASHTIRISH ORGANI/AUTHORITY
# ~ 04 03 2018 STATE PERSONALIZATION
# ‘AMAL GILISH MUDDATI/ DATE OF EXPIRY ‘CENTRE
#
# 03-03 2028
#
# P<UZBKHAMIDULLAEV<<JAVOKHIR<<<<<<<<<<<<icec<
# AB90144225UZB0202228M28030325220202679002506
# """
#
# # MRZ qismni ajratib olish
# try:
#     mrz_section = extract_mrz_section(input_text)
#     print("MRZ qismi:")
#     print(mrz_section)
# except ValueError as e:
#     print(f"Xato: {e}")
