import random
import string
import cloudinary
import cloudinary.uploader
from fastapi import Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from typing import List

from src.conf.config import config
from src.conf import messages
from src.database.db import get_db
from src.entity.models import User, Photo, PhotoTag, Tag, Comment, Rating
from src.schemas.photo import PhotoTagResponse, ViewAllPhotos, SortDirection, UserRatingContents
from src.repository import tags as repositories_tags
from src.repository import qr_code as repositories_qr_code

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


async def get_photo_by_id(
        photo_id: int, user: User, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Get a photo by its id.

    :param user:
    :param photo_id: int: The id of the photo to get
    :param db: AsyncSession: The database session
    :return: Photo: The photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO
        )
    return photo


async def get_photos(
        skip: int, limit: int, user: User, db: AsyncSession = Depends(get_db)
) -> List[Photo]:
    """
    Get photos for a given user.

    :param skip: int: Skip a number of photos
    :param limit: int: Limit the number of photos returned
    :param user: User: The user to get photos for
    :param db: AsyncSession: The database session
    :return: List[Photo]: A list of photo objects
    """
    expression = select(Photo).filter_by(user_id=user.id).offset(skip).limit(limit)
    photos = await db.execute(expression)
    photos = photos.all()
    return photos


async def create_photo(
        title: str,
        description: str | None,
        user: User,
        db: AsyncSession = Depends(get_db),
        file: UploadFile = File(),
) -> Photo:
    """
    The create_photo function creates a new photo in the database.
    It takes three arguments: title, description and user. The title is a string that will be used as the name of the photo,
    the description is an optional string that can be used to describe what's on the picture and user is an object containing information about who uploaded it.
    The function also accepts two keyword arguments: db which contains our database session and file which contains information about our image file.
    
    :param title: str: Set the title of the photo
    :param description: str | None: Specify that the description is optional
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Get the database session
    :param file: UploadFile: Get the file from the request
    :param : Get the current user from the database
    :return: A photo object
    """
    letters = string.ascii_lowercase
    random_name = "".join(random.choice(letters) for _ in range(20))
    public_id = f"PhotoShare/{user.email}/{random_name}"
    res_photo = cloudinary.uploader.upload(
        file.file, public_id=public_id, overwrite=True
    )
    photo = Photo(
        title=title,
        description=description,
        file_path=res_photo.get("url"),
        user_id=user.id,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def update_photo_description(
        photo_id: int, description: str, user: User, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    The update_photo_description function updates the description of a photo.
    
    :param photo_id: int: Specify the photo to update
    :param description: str: Pass the new description of the photo
    :param user: User: Get the user_id from the token
    :param db: AsyncSession: Get a database connection from the pool
    :return: A photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO
        )
    photo.description = description
    await db.commit()
    await db.refresh(photo)
    return photo


async def remove_photo(
        photo_id: int, user: User, db: AsyncSession = Depends(get_db)
) -> Photo:
    """
    Remove a photo.

    :param photo_id: int: The id of the photo to remove
    :param user: User: The user removing the photo
    :param db: AsyncSession: The database session
    :return: Photo: The removed photo object
    """
    photo_expression = select(Photo).filter_by(id=photo_id, user_id=user.id)
    photos = await db.execute(photo_expression)
    photo = photos.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_PHOTO
        )
    await db.delete(photo)
    await db.commit()
    return photo


async def create_tag_photo(photo_id: int,
                           tags: str,
                           user: User,
                           db: AsyncSession = Depends(get_db)) -> PhotoTagResponse:
    result = await db.execute(select(Photo).where(Photo.id == photo_id, Photo.user_id == user.id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found!")

    find_photo_tag = select(PhotoTag).filter(PhotoTag.photo_id == photo_id)
    result = await db.execute(find_photo_tag)
    photo_tags = result.scalars().all()
    for photo_tag in photo_tags:
        await db.delete(photo_tag)

    tag_list = tags.split(',')
    if len(tag_list) > 5:
        tag_list = tag_list[:5]

    for tag_name in tag_list:
        find_tag = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = find_tag.scalar_one_or_none()
        if not tag:
            add_tag = Tag(name=tag_name)
            db.add(add_tag)
            await db.commit()
            await db.refresh(add_tag)
            tag = add_tag

        photo_tag = PhotoTag(photo_id=photo_id, tag_id=tag.id)
        db.add(photo_tag)
        await db.commit()
        await db.refresh(photo_tag)

    await db.commit()
    await db.refresh(photo)

    return PhotoTagResponse(
        id=photo.id,
        title=photo.title,
        description=photo.description,
        tags=tag_list,
    )


async def view_all_info_photo(photo_id: int,
                              user: User,
                              db: AsyncSession = Depends(get_db)) -> ViewAllPhotos:
    # выбрать фото
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found!")

    # выборка тегов
    list_tags = []
    find_photo_tag = select(PhotoTag).filter(PhotoTag.photo_id == photo_id)
    result = await db.execute(find_photo_tag)
    photo_tags = result.scalars().all()
    for photo_tag in photo_tags:
        find_tag = await db.execute(select(Tag).where(Tag.id == photo_tag.tag_id))
        tag = find_tag.scalar_one_or_none()
        if tag:
            list_tags.append(tag.name)

    # выборка комментариев
    ratings_data = []
    select_comments = select(Comment).filter(Comment.photo_id == photo_id)
    query = select_comments.order_by(Comment.created_at.desc())
    result = await db.execute(query)
    comments = result.scalars().all()
    for user_comment in comments:
        user_name = "unknown"
        content = user_comment.content

        # находим пользователя комментария
        find_user = await db.execute(select(User).where(User.id == user_comment.user_id))
        comment_user = find_user.scalar_one_or_none()
        content = ""
        rating = 0
        if comment_user:
            user_name = comment_user.username

            # находим оценку фото от пользователя
            result = await db.execute(
                select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == comment_user.id))
            existing_rating = result.scalar_one_or_none()
            if existing_rating:
                rating = existing_rating.rating

            ratings_data.append({"user_name": user_name, "comment": content, "rating": rating})

    result = await db.execute(select(Rating).where(Rating.photo_id == photo_id))
    ratings = result.scalars().all()
    number_of_ratings = len(ratings)
    average_rating = 0
    if number_of_ratings != 0:
        total_rating = sum(rating.rating for rating in ratings)
        average_rating = total_rating / number_of_ratings

    list_rating_contents: List[UserRatingContents] = []
    for data in ratings_data:
        rating_content = UserRatingContents(**data)
        list_rating_contents.append(rating_content)

    # gr
    data = photo.file_path
    img_byte_arr = await repositories_qr_code.generate_qr_code(data)
    file_path_gr = await repositories_qr_code.upload_qr_to_cloudinary(
        img_byte_arr, f"{photo.title}"
    )

    return ViewAllPhotos(
        id=photo.id,
        title=photo.title,
        description=photo.description,
        file_path=photo.file_path,
        file_path_gr=file_path_gr,
        average_rating=average_rating,
        tags=list_tags,
        comments=list_rating_contents
    )
