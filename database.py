"""
Database configuration and session management for SQLAlchemy.
Supports in-memory SQLite (testing), MySQL (production), and GCP Secret Manager.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging
from google.cloud import secretmanager
from dotenv import load_dotenv

# 1. 加载 .env 文件 (解决本地运行的环境变量问题)
load_dotenv()

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
Base = declarative_base()

# ==============================================================================
# 1. Define function to fetch Secret from Google Cloud
# ==============================================================================
def get_secret(secret_name: str):
    """
    Fetch database password from GCP Secret Manager.
    Requires GCP_PROJECT_ID environment variable to be set.
    """
    project_id = os.environ.get("GCP_PROJECT_ID")
    
    if not project_id:
        # 仅在非 SQLite 模式下警告，避免测试干扰
        if os.environ.get("USE_SQLITE") != "True":
            logger.warning("GCP_PROJECT_ID not set, cannot fetch secret.")
        return None
        
    if not secret_name:
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to fetch secret '{secret_name}': {e}")
        return None

# ==============================================================================
# 2. Database Configuration
# ==============================================================================

# 优先读取队友规定的 CATALOG_ 前缀，读不到再读标准的 DB_ 前缀
DB_USER = os.environ.get("CATALOG_DB_USER", os.environ.get("DB_USER", "ms1_user"))
DB_HOST = os.environ.get("CATALOG_DB_HOST", os.environ.get("DB_HOST", "localhost"))
DB_PORT = os.environ.get("CATALOG_DB_PORT", os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("CATALOG_DB_NAME", os.environ.get("DB_NAME", "ms1_db"))

# 密码逻辑：优先从 Secret Manager 获取
secret_name = os.environ.get("DB_PASSWORD_SECRET")
raw_password = os.environ.get("CATALOG_DB_PASSWORD", os.environ.get("DB_PASSWORD"))

DB_PASSWORD = "password123" # 默认兜底

if secret_name:
    logger.info(f"Attempting to fetch password from Secret Manager: {secret_name}")
    fetched_password = get_secret(secret_name)
    if fetched_password:
        DB_PASSWORD = fetched_password
        logger.info("Successfully loaded password from Secret Manager.")
elif raw_password:
    DB_PASSWORD = raw_password

# SQLite 开关
USE_SQLITE = os.environ.get("USE_SQLITE", "False").lower() == "true"

# ==============================================================================
# 3. Create Engine
# ==============================================================================

if not USE_SQLITE:
    # 打印最终使用的 Host，方便确认是否连上了云端 IP
    logger.info(f"Database config: {DB_HOST}:{DB_PORT}/{DB_NAME} (user: {DB_USER})")

if USE_SQLITE:
    DATABASE_URL = "sqlite:///:memory:"
    logger.info("Using SQLite in-memory database")
    engine = create_engine(
        DATABASE_URL,
        echo=os.environ.get("SQL_ECHO", "False").lower() == "true",
        connect_args={"check_same_thread": False},
    )
else:
    # MySQL Production Configuration
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    engine = create_engine(
        DATABASE_URL,
        echo=os.environ.get("SQL_ECHO", "False").lower() == "true",
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        # 修正了之前的错误：pymysql 使用 connect_timeout 而不是 timeout
        connect_args={"connect_timeout": 10}, 
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def drop_db():
    Base.metadata.drop_all(bind=engine)