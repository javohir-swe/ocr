import os
from ocr.id_card import get_passport_data
from ocr.passport import get_data_from_passport

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from pyzbar.pyzbar import decode
from PIL import Image, ImageEnhance

BOT_TOKEN = "7595943647:AAFvmJYbc1l71l-aiNmnrMjxQTKLcJ-q-Qc"  # Bot tokeningizni kiriting

# /start komandasi uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("ID Card", callback_data="id_card")],
        [InlineKeyboardButton("Passport", callback_data="passport")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Iltimos, kerakli tugmani tanlang:", reply_markup=reply_markup)

# Tugma bosilganda handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    context.user_data["doc_type"] = query.data  # Foydalanuvchi tanlovini saqlaydi
    if query.data == "id_card":
        await query.edit_message_text("ID Card uchun QR kodning rasmini yuboring.")
    elif query.data == "passport":
        await query.edit_message_text("Passport uchun rasmini yuboring.")

# Rasm yuborilganda handler
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "doc_type" not in context.user_data:
        await update.message.reply_text("Iltimos, avval /start komandasini ishlating.")
        return

    # Rasmni yuklash
    photo = update.message.photo[-1]  # Eng yuqori sifatdagi rasmni olamiz
    file = await photo.get_file()
    file_path = await file.download_to_drive()

    if context.user_data["doc_type"] == "id_card":
        # QR kodni o'qish
        try:
            qr_data = decode_qr_code(file_path)
            result = get_passport_data(data=qr_data)

            if qr_data:
                await update.message.reply_text(f"QR kod ma'lumotlari:\n{result}")
            else:
                await update.message.reply_text("QR kod topilmadi yoki noto'g'ri.\nIltimos Sifatni yaxshilab qayta urinib ko'ring.")
        except Exception as e:
            await update.message.reply_text(f"QR kodni o'qishda xatolik: {e}")
    elif context.user_data["doc_type"] == "passport":
        # Passport rasmini qayta ishlash
        try:
            result = get_data_from_passport(file_path)
            await update.message.reply_text(f"Passportdan olingan ma'lumotlar:\n{result}")
        except Exception as e:
            await update.message.reply_text(f"Passportni o'qishda xatolik: {e}")

    # Faylni o'chirish
    os.remove(file_path)

# QR kodni dekodlash funksiyasi
def decode_qr_code(image_path: str) -> str:
    image = preprocess_image(image_path)
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode("utf-8")  # Faqat birinchi QR kodni qaytaradi
    return None

# Rasmni qayta ishlash funksiyasi
def preprocess_image(image_path: str) -> Image:
    image = Image.open(image_path)

    # Rasmni kattalashtirish
    resized_image = image.resize((image.width * 2, image.height * 2))

    # Kontrastni oshirish
    enhancer = ImageEnhance.Contrast(resized_image)
    enhanced_image = enhancer.enhance(2)  # Kontrastni 2x oshirish

    return enhanced_image

# Xatoliklarni qayta ishlash
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Botda xatolik yuz berdi. Keyinroq urinib ko'ring.")

if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushirildi!")  # Bu qator bot run bo'lganini bildiradi

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))

    app.run_polling()
