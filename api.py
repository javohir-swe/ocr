from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ocr.id_card import get_passport_data
from ocr.passport import get_data_from_passport
from ocr.qr_reader import decode_qr_code


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:40675", "http://localhost:40675", "https://movo.uz"],  # Frontend’ning to‘liq URL'ini qo‘shing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    print(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

@app.post("/api/v1/passport")
async def upload_image(file: UploadFile = File(...)):
    result = get_data_from_passport(file.file)

    return JSONResponse(content=result, status_code=200)


@app.post("/api/v1/id_card")
async def upload_id_card(file: UploadFile = File(...)):
    """
    ID Card QR kod tasvirini yuklash va QR kodni o'qish orqali ma'lumotlarni qayta ishlash.
    """
    try:
        # QR kodni o'qish
        qr_data = decode_qr_code(file.file)

        if qr_data:
            result = get_passport_data(data=qr_data)
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="QR kod topilmadi yoki noto'g'ri.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ID Cardni o'qishda xatolik: {str(e)}")
