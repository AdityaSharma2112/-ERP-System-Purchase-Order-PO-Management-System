from sqlmodel import SQLModel
from database import engine
from model import *

def init_db():
    SQLModel.metadata.create_all(bind=engine)
    print("Database & tables created")
if __name__ == "__main__":
    init_db()