import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.entity.models import Photo


cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def save_transformation(trans_url: str, photo: Photo, db: AsyncSession):
    """Save the transformation to the database."""
    photo.file_path_transform = trans_url
    await db.commit()
    await db.refresh(photo)
    return photo


async def create_crop_transformation(original_photo, body, db):
    """
    The create_crop_transformation function takes in the original photo, body of the request, and database connection.
    It then creates a public_id for the transformed image by splitting up the file path of the original photo into a list
    and using that to create a new public_id with PhotoShare/{list[-2]}/{list[-3]}. It then creates an empty dictionary 
    called size_param which will be used to store any transformations that are being applied. The trans_actions variable is 
    a list containing dictionaries with transformation actions such as fetching format automatically and cropping. If there is 
    a width
    """
    list_base_url = original_photo.file_path.split("/")
    public_id = f"PhotoShare/{list_base_url[-2]}/{list_base_url[-1]}"
    size_param = {}
    trans_actions = [{"fetch_format": "auto"}]
    if body.width > 0:
        size_param["width"] = body.width
    if body.crop != "":
        size_param["crop"] = body.crop
    if body.aspect_ratio > 1:
        size_param["aspect_ratio"] = body.aspect_ratio
    if size_param:
        trans_actions.append(size_param)
    if body.is_rounded:
        trans_actions.append({"radius": "max"})
    if body.angle != 0:
        trans_actions.append({"angle": 20})
    if body.effect != "":
        trans_actions.append({"effect": body.effect})
    transform = cloudinary.CloudinaryImage(public_id).build_url(
        transformation=trans_actions
    )
    trans_photo = await save_transformation(transform, original_photo, db)
    return {
        "id": trans_photo.id,
        "title": trans_photo.title,
        "description": trans_photo.description,
        "file_path_transform": trans_photo.file_path_transform,
    }
