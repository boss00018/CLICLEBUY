import os
import sys
import uvicorn
from database import engine, Base
import models

def init_db():
    """Initialize the database with tables only - no demo data"""
    print("Initializing database...")
    
    # Create tables
    try:
        models.Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        sys.exit(1)
    
    # Check if we need to add categories (essential data only)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if categories exist
    categories = session.query(models.Category).all()
    if not categories:
        print("Adding essential categories...")
        essential_categories = [
            models.Category(name="Textbooks", description="Academic textbooks and study materials"),
            models.Category(name="Stationery", description="Notebooks, pens, and office supplies"),
            models.Category(name="Electronics", description="Calculators, laptops, and tech items"),
            models.Category(name="Furniture", description="Desks, chairs, and room furniture"),
            models.Category(name="Other", description="Other student essentials")
        ]
        session.add_all(essential_categories)
        session.commit()
        print("✓ Essential categories added!")
    else:
        print("Database already initialized")
    
    session.close()
    print("✓ Database initialized successfully!")

def main():
    print("=" * 50)
    print("CIRCLEBUY - Student E-commerce Platform")
    print("=" * 50)
    
    print("\nInitializing database...")
    init_db()
    
    print("\nStarting web server...")
    print("✓ Server running at http://127.0.0.1:8000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()