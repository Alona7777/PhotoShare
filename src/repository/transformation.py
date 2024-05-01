import random
import string
import cloudinary
import cloudinary.uploader
from fastapi import Depends, UploadFile, File, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from typing import List

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import User, Photo
from src.schemas.photo import PhotoSchema
from src.repository.tags import create_or_get_tag

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)

async def create_crop_transformation(original_photo, body, user):
   letters = string.ascii_lowercase
   random_name = ''.join(random.choice(letters) for _ in range(20))
   public_id = f"PhotoShare/{user.email}/{random_name}"
   res_photo = cloudinary.uploader.upload(
        file=original_photo.file_path,
        public_id=public_id,
        overwrite=True)
   print(res_photo)
   transform = cloudinary.CloudinaryImage(res_photo.get("url")).build_url(transformation=[
  {'aspect_ratio': f"{body.aspect_ratio}", 'width': body.width, 'crop': body.crop},
  {'radius': "max"},
  {'fetch_format': "auto"}
  ], version=res_photo.get("version"))
   print(body)
   print(transform)