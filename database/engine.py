import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import Config

# Tạo đường dẫn lưu file database tại thư mục gốc của project
DB_PATH = os.path.join(Config.BASE_DIR, "autotest.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Khởi tạo Engine và Session của SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model cho các class table kế thừa
Base = declarative_base()

def get_db():
    """Hàm hỗ trợ lấy session database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()