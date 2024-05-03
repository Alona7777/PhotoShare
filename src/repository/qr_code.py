import qrcode
import cloudinary
import cloudinary.uploader
from io import BytesIO
from src.conf.config import config


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_arr = BytesIO()
    img.save(img_byte_arr)
    img_byte_arr.seek(0)

    return img_byte_arr


async def upload_qr_to_cloudinary(img_byte_arr, file_name):
    response = cloudinary.uploader.upload(
        file=img_byte_arr,
        public_id=f"qr_codes/{file_name}",
        resource_type='image'
    )
    return response['secure_url']