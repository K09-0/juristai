from fastapi import APIRouter, HTTPException
import structlog
import qrcode
import io
import base64

from app.config import get_settings, is_admin
from app.database import get_supabase_client, activate_premium, save_payment

router = APIRouter()
logger = structlog.get_logger()

@router.post("/create")
async def create_payment(months: int = 1):
    settings = get_settings()
    amount = settings.premium_price_kzt * months
    
    qr_data = f"KASPI_PAY|{settings.kaspi_phone}|{amount}|JuristAI Premium {months}мес"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "status": "pending_payment",
        "kaspi_phone": settings.kaspi_phone,
        "kaspi_cardholder": settings.kaspi_cardholder,
        "amount_kzt": amount,
        "months": months,
        "qr_code_base64": f"data:image/png;base64,{qr_base64}",
        "instructions": f"1. Отсканируйте QR или переведите на {settings.kaspi_phone}\n2. Комментарий: JuristAI Premium {months}мес\n3. Отправьте чек на support@juristai.kz"
    }

@router.post("/verify")
async def verify_payment(user_id: str, amount: int, months: int, admin_username: str, admin_password: str):
    if not is_admin(admin_username, admin_password):
        raise HTTPException(status_code=403, detail="Только админ может активировать")
    
    try:
        supabase = get_supabase_client()
        result = await activate_premium(supabase, user_id, months)
        await save_payment(supabase, user_id, amount, months, "completed")
        
        logger.info("premium_activated", user_id=user_id, months=months, amount=amount)
        return {"status": "activated", "details": result}
    except Exception as e:
        logger.error("activation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin-info")
async def admin_login_info():
    settings = get_settings()
    return {
        "admin_accounts": 2,
        "note": "Админы имеют безлимитный доступ",
        "kaspi": settings.kaspi_phone
    }
