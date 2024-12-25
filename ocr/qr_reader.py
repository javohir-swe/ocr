from fastapi import UploadFile, HTTPException
from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
import io


# QR kodni dekodlash funksiyasi
def decode_qr_code(file: UploadFile) -> str:
    try:
        # Faylni ochib, PIL image obyektiga o'girish
        image = Image.open(io.BytesIO(file.read()))

        # Tasvirni qayta ishlash
        processed_image = preprocess_image(image)

        # QR kodni o'qish
        decoded_objects = decode(processed_image)
        if decoded_objects:
            return decoded_objects[0].data.decode("utf-8")  # Faqat birinchi QR kodni qaytaradi
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"QR kodni o'qishda xatolik: {str(e)}")


# Tasvirni qayta ishlash funksiyasi
def preprocess_image(image: Image.Image) -> Image.Image:
    # Rasmni kattalashtirish
    resized_image = image.resize((image.width * 2, image.height * 2))

    # Kontrastni oshirish
    enhancer = ImageEnhance.Contrast(resized_image)
    enhanced_image = enhancer.enhance(2)  # Kontrastni 2x oshirish

    return enhanced_image
