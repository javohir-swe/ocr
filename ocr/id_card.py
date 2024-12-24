from datetime import datetime
import re
import pprint

def get_birth_date(data):
    current_year = datetime.now().year
    current_century = current_year // 100  # Masalan, 2024 -> 20
    current_year_last_two = current_year % 100  # Masalan, 2024 -> 24

    # Yilni 6 belgi ichidan olish
    birth_year_last_two = int(data[:2])
    birth_month = data[2:4]
    birth_day = data[4:6]

    # Yilni to'liq qilish
    if birth_year_last_two > current_year_last_two:
        birth_year = (current_century - 1) * 100 + birth_year_last_two
    else:
        birth_year = current_century * 100 + birth_year_last_two
    # To'liq sana formatida natija
    result_date = f"{birth_year:04d}-{birth_month}-{birth_day}"

    return result_date


def get_expiry_date(data):
    """
    MRZ qatoridan amal qilish muddatini to'g'ri ajratib olish va tahlil qilish.
    """
    # Amal qilish muddati MRZ qatoridagi "320109" qismida joylashgan
    expiry_date_raw = data[38:44]  # Indekslar bo'yicha: 28 dan 34 gacha
    print(expiry_date_raw)
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
    return f"{year}-{month:02d}-{day:02d}"


def extract_gender(data):
    """
    MRZ qatoridan jinsni aniqlash funksiyasi.
    """
    # Jins MRZ qatorining 22-indeksi bo'yicha joylashgan
    gender_char = data[37]
    if gender_char == "M":
        return "Male"
    elif gender_char == "F":
        return "Female"
    else:
        raise ValueError(f"Noto'g'ri jins belgisi: {gender_char}")

def get_passport_data(data):
    """
    Main Function()


    Parses the given MRZ data from a passport and returns extracted information as a dictionary.

    :param data: The raw MRZ data string from the passport
    :return: A dictionary containing the extracted passport information
    """
    try:
        cleaned_data = data.replace('\n', '')
        if len(cleaned_data):

# =============== Get Birth date =============== #
            first_angle_index = cleaned_data.find('<')
            data_for_birth_date = cleaned_data[first_angle_index + 1: first_angle_index + 7]

            birth_date = get_birth_date(data=data_for_birth_date)

# =============== Get Passport data =============== #
            passport_number_pattern = r"[A-Z]{2}[0-9]{7}"

            match = re.search(passport_number_pattern, cleaned_data)
            print(cleaned_data)
            if match:
                passport_number = match.group()  # Topilgan passport raqamini olamiz
                passport = passport_number
            else:
                passport = "Passport raqami topilmadi."

# =============== Get FullName data =============== #

            name_pattern = r"[A-Z]{2}[A-Z]+<<[A-Z]+"
            name_match = re.search(name_pattern, cleaned_data)
            if name_match:
                name_parts = name_match.group().split("<<")
                last_name = name_parts[0]
                first_name = name_parts[1].replace("<", " ") if len(name_parts) > 1 else ""
            else:
                return "Ism Familiyani topishda muammo bo'ldi!!!"
# =============== Get FullName data =============== #
            expiry_date = get_expiry_date(data=cleaned_data)

# =============== Get FullName data =============== #
            gender = extract_gender(data=cleaned_data)
            pass_last_name = last_name.title()
            pass_first_name = first_name.title()
            pass_date_of_birth = birth_date
            pass_passport_id = passport
            pass_expiry_date = expiry_date
            pass_gender = gender
            print_data = f"""\n\n\nLastname: {pass_last_name}\nFirstname: {pass_first_name}\nDate of birth: {pass_date_of_birth}\nPassport ID: {pass_passport_id}\nExpiry date: {pass_expiry_date}\nGender: {pass_gender}\n\n\n"""
            print(print_data)
            result_data = {
                "last_name": last_name.title(),
                "first_name": first_name.title(),
                "date_of_birth": birth_date,
                "passport_id": passport,
                "expiry_date": expiry_date,
                "sex": gender,
            }
            return print_data
        else:
            return "Berilayotgan ma'lumot noto'g'ri bo'lishi mumkin!\n\nIltimos ma'lumot sifatini yaxshilab qayta urinib ko'ring."

    except Exception as e:
        return {"error": str(e)}



# Example usage
# passport_data = """IUUZBAD5241719230409995420014<
# 9909047M3311260UZBUZB<<<<<<<<6
# YARASHEV<<BURXONIDDIN<<<<<<<<<"""
# parsed_data = parse_passport_data(data=passport_data)
# # print(passport_data)
# print("\n\n")
# pprint.pprint(parsed_data, width=1)
# print("\n\n")
