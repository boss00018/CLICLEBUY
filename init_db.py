from database import SessionLocal, engine
import models
from models import Category

def init_db():
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if categories already exist
    existing_categories = db.query(Category).all()
    if existing_categories:
        print("Database already initialized")
        db.close()
        return
    
    # Create categories
    categories = [
        Category(name="Textbooks", description="New and used textbooks for all courses"),
        Category(name="Stationery", description="Notebooks, pens, pencils, and other writing supplies"),
        Category(name="Electronics", description="Calculators, laptops, and other electronic devices"),
        Category(name="Course Materials", description="Lab equipment, art supplies, and other course-specific materials"),
        Category(name="Furniture", description="Desks, chairs, and other dorm/apartment furniture"),
        Category(name="Clothing", description="University apparel and other clothing items"),
        Category(name="Other", description="Miscellaneous items not fitting other categories")
    ]
    
    for category in categories:
        db.add(category)
    
    db.commit()
    print("Database initialized with categories")
    db.close()

if __name__ == "__main__":
    init_db()