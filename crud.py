from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash, verify_password

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Task CRUD
def get_tasks(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).all()

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_data: schemas.TaskCreate, user_id: int):
    task = db.query(models.Task).filter_by(id=task_id, owner_id=user_id).first()
    if task:
        for key, value in task_data.dict().items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
    return task

def delete_task(db: Session, task_id: int, user_id: int):
    task = db.query(models.Task).filter_by(id=task_id, owner_id=user_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task
