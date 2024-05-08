import enum
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Boolean,
    Column,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_photos: Mapped[relationship] = relationship(
        "Photo", back_populates="photos_user", cascade="all, delete-orphan"
    )
    user_comments: Mapped[relationship] = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    user_ratings: Mapped[relationship] = relationship(
        "Rating", back_populates="user", cascade="all, delete-orphan"
    )
    friends: Mapped[relationship] = relationship(
        "Friendship",
        primaryjoin="User.id == Friendship.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ban_users: Mapped[relationship] = relationship(
        "BanUser", back_populates="user", cascade="all, delete-orphan"
    )


class Friendship(Base):
    __tablename__ = "friendships"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    friend_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    created_at: Mapped[date] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    user: Mapped[relationship] = relationship(
        "User", primaryjoin="User.id == Friendship.user_id", back_populates="friends"
    )


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String)
    file_path_transform: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=False
    )

    photos_user: Mapped["User"] = relationship("User", back_populates="user_photos")
    commented_photos: Mapped[relationship] = relationship(
        "Comment", back_populates="photo_commented", cascade="all, delete-orphan"
    )
    ratings_photos: Mapped[relationship] = relationship(
        "Rating", back_populates="photo", cascade="all, delete-orphan"
    )
    photo_tags: Mapped[relationship] = relationship(
        "PhotoTag", back_populates="photo", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"))
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), nullable=False, onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="user_comments")
    photo_commented: Mapped["Photo"] = relationship(
        "Photo", back_populates="commented_photos"
    )


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"))
    rating: Mapped[int] = mapped_column(Integer) 
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="user_ratings")
    photo: Mapped["Photo"] = relationship("Photo", back_populates="ratings_photos")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    photo_tags: Mapped[relationship] = relationship("PhotoTag", back_populates="tag")


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    photo_id: Mapped[int] = Column(Integer, ForeignKey("photos.id"), primary_key=True)
    tag_id: Mapped[int] = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    photo: Mapped["Photo"] = relationship("Photo", back_populates="photo_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="photo_tags")


class BanUser(Base):
    __tablename__ = "ban_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="ban_users")

