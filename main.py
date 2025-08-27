from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, crud, auth
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401)
        return user
    except:
        raise HTTPException(status_code=401)

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/token", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/tasks", response_model=list[schemas.Task])
def read_tasks(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_tasks(db, current_user.id)

@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_task(db, task, current_user.id)

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.update_task(db, task_id, task, current_user.id)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.delete_task(db, task_id, current_user.id)
