import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.core.config import settings
from app.models.market_data import Base

def init_db():
    """Initialize the database with required tables."""
    try:
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_db() 