from hashlib import new
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy import text

router = APIRouter(
    prefix="/users",
    tags=['Users']
)



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    # print("====================", user.dict())
    new_user = models.User(**user.dict())
    print(new_user)
    sql_insert = text("""
                        SET NOCOUNT ON;
                        DECLARE @NEWID TABLE(ID INT);
                        
                        insert into users(email, password) 
                        OUTPUT inserted.id INTO @NEWID(ID) 
                        values(:email, :password);

                        SELECT ID FROM @NEWID;
                        """)
    sql_select = text("""SELECT id, email, created_at FROM users WHERE id = :id""")
    rs_id = db.execute(sql_insert, user.dict())
    new_id = rs_id.fetchone()[0]
    ##commit() should happen after the fetch
    db.commit()    
    print(new_id)
    # conn.execute(text("""insert into users(email, password) values(:email, :password)"""), {"email":user.email, "password":user.password})
    rs  = db.execute(sql_select,{"id":new_id})
    print("============")        
    # print(rs)
    new_user = rs.mappings().first()
    print(new_user)
    return new_user
    



@router.post("/orm", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user_orm(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # print(new_user)
    return new_user


@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), ):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user
