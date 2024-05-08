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
    """
    The generate_qr_code function takes in a string of data and returns a QR code image.
    
    :param data: Generate the qr code
    :return: A bytesio object, which is a stream of bytes
    """
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
    """
    The upload_qr_to_cloudinary function takes in a byte array of an image and the name of the file.
    It then uploads that image to cloudinary, using the public_id parameter as a unique identifier for each QR code.
    The function returns a secure url to access that QR code.
    
    :param img_byte_arr: Pass in the image data that is to be uploaded
    :param file_name: Name the file in cloudinary
    :return: A url to the qr code image
    """
    response = cloudinary.uploader.upload(
        file=img_byte_arr,
        public_id=f"qr_codes/{file_name}",
        resource_type='image'
    )
    return response['secure_url']