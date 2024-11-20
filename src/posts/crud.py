from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import PostCreate
from .models import Post, Category, Comment
from src.auth.models import User, UserRole


class CategoryDoesNotExist(Exception):
    pass


def get_category(session: AsyncSession, category_slug):
    return session.scalar(select(Category).filter_by(slug=category_slug))


def get_posts(session: AsyncSession):
    return paginate(session, select(Post).filter_by(is_pubished=True))


def get_post(post_id, session: AsyncSession):
    return session.scalar(select(Post).filter_by(id=post_id))


def create_post(author_id: int, data: PostCreate, session: AsyncSession):
    if data.category and not get_category(session,
                                          category_slug=data.category):
        raise CategoryDoesNotExist

    db_post = Post(
        **data.model_dump,
        author=author_id,
    )
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


def update_post(post: Post, data: PostCreate, session: AsyncSession):
    if data.category and not get_category(session,
                                          category_slug=data.category):
        raise CategoryDoesNotExist

    update_data = data.model_dump(exclude_unset=True)
    if 'category' in update_data:
        update_data['category_slug'] = update_data.pop('category')

    for field, value in update_data.items():
        setattr(post, field, value)

    session.add(post)
    session.commit()
    session.refresh(post)
    return post


def delete_post(post: Post, session: AsyncSession):
    session.delete(post)
    session.commit()


def get_comment(comment_id: int, post: Post, session: AsyncSession):
    return session.scalar(
        select(Comment).where(
            Comment.id == comment_id, Comment.post_id == post.id
        )
    )


# def get_comments_of_post(post: models.Post):
#     return post.comments


# def create_comment(
#     session: Session, data: schemas.CommentCreate, post: models.Post, author_id: int
# ):
#     comment = models.Comment(
#         **data.model_dump(), post_id=post.id, author_id=author_id
#     )
#     session.add(comment)
#     session.commit()
#     session.refresh(comment)
#     return comment


# def delete_comment(db: Session, comment: models.Comment):
#     db.delete(comment)
#     db.commit()


# def update_comment(
#     db: Session,
#     comment: models.Comment,
#     data: schemas.PostUpdate | schemas.PostCreate,
# ):
#     update_data = data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(comment, field, value)

#     db.add(comment)
#     db.commit()
#     db.refresh(comment)
#     return comment