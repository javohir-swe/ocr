import subprocess
from uuid import uuid4

def scan_to_file(output_file, resolution=300, mode="color"):
    """
    Skaner orqali rasmni faylga saqlash.
    
    :param output_file: Saqlanadigan fayl nomi (masalan, 'my_passport.pnm')
    :param resolution: Skan qilish rezolyutsiyasi (DPI), odatiy 300
    :param mode: Skan rejimi ('color', 'gray', 'lineart'), odatiy 'color'
    :return: True muvaffaqiyatli bo'lsa, aks holda False
    """
    try:
        # `scanimage` buyruqni shakllantirish
        command = [
            "scanimage",
            f"--resolution={resolution}",
            f"--mode={mode}",
            f"--format=pnm",
            f"--output-file={output_file}"
        ]

        # Buyruqni ishga tushirish
        subprocess.run(command, check=True)
        print(f"Skan qilingan rasm '{output_file}' fayliga saqlandi.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Skan qilishda xato: {e}")
        return False
    except FileNotFoundError:
        print("`scanimage` o'rnatilmagan yoki tizimda mavjud emas.")
        return False

# Funksiyani chaqirish
if __name__ == "__main__":
    output_file = str(uuid4())
    if scan_to_file(f"Image-{output_file[:6]}.pnm"):
        print("Skan qilish muvaffaqiyatli bajarildi.")
    else:
        print("Skan qilishda xatolik yuz berdi.")

