import os
from datetime import datetime, timedelta
from database import SessionLocal
import models

def cleanup_sold_products(days_to_keep=7):
    """
    Cleanup sold products to save storage:
    - Removes product images from filesystem
    - Removes product records from database after specified days
    - Keeps transaction history in messages for reference
    """
    db = SessionLocal()
    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Get sold products older than cutoff date
        old_sold_products = db.query(models.Product).filter(
            models.Product.is_sold == 1,
            models.Product.created_at < cutoff_date
        ).all()
        
        cleaned_count = 0
        for product in old_sold_products:
            # Delete product image if exists
            if product.image_url and product.image_url.startswith("/static/images/products/"):
                image_path = os.path.join(".", product.image_url.lstrip("/"))
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"Deleted image: {image_path}")
                    except Exception as e:
                        print(f"Error deleting image {image_path}: {str(e)}")
            
            # Delete the product record completely to save database space
            db.delete(product)
            cleaned_count += 1
            print(f"Removed sold product: {product.name}")
        
        db.commit()
        return cleaned_count
    
    except Exception as e:
        print(f"Error in cleanup: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()

def cleanup_orphaned_images():
    """Remove orphaned images that don't have corresponding products"""
    db = SessionLocal()
    try:
        # Get all product image URLs from database
        products = db.query(models.Product).all()
        used_images = set()
        for product in products:
            if product.image_url and product.image_url.startswith("/static/images/products/"):
                used_images.add(product.image_url.lstrip("/"))
        
        # Check all images in the directory
        images_dir = "static/images/products"
        if os.path.exists(images_dir):
            removed_count = 0
            for filename in os.listdir(images_dir):
                file_path = os.path.join(images_dir, filename)
                relative_path = f"static/images/products/{filename}"
                
                if relative_path not in used_images and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Removed orphaned image: {filename}")
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {filename}: {str(e)}")
            
            return removed_count
        return 0
    
    finally:
        db.close()

def get_storage_stats():
    """Get storage usage statistics"""
    stats = {
        'total_products': 0,
        'sold_products': 0,
        'active_products': 0,
        'total_images': 0,
        'storage_size_mb': 0
    }
    
    db = SessionLocal()
    try:
        # Product statistics
        stats['total_products'] = db.query(models.Product).count()
        stats['sold_products'] = db.query(models.Product).filter(models.Product.is_sold == 1).count()
        stats['active_products'] = stats['total_products'] - stats['sold_products']
        
        # Image statistics
        images_dir = "static/images/products"
        if os.path.exists(images_dir):
            total_size = 0
            image_count = 0
            for filename in os.listdir(images_dir):
                file_path = os.path.join(images_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    image_count += 1
            
            stats['total_images'] = image_count
            stats['storage_size_mb'] = round(total_size / (1024 * 1024), 2)
    
    finally:
        db.close()
    
    return stats

if __name__ == "__main__":
    print("CIRCLEBUY Storage Cleanup")
    print("=" * 30)
    
    # Show current stats
    stats = get_storage_stats()
    print(f"Current Statistics:")
    print(f"- Total Products: {stats['total_products']}")
    print(f"- Active Products: {stats['active_products']}")
    print(f"- Sold Products: {stats['sold_products']}")
    print(f"- Total Images: {stats['total_images']}")
    print(f"- Storage Used: {stats['storage_size_mb']} MB")
    print()
    
    # Cleanup sold products
    print("Cleaning up sold products...")
    cleaned = cleanup_sold_products(days_to_keep=7)
    print(f"Cleaned up {cleaned} sold products")
    
    # Cleanup orphaned images
    print("\nCleaning up orphaned images...")
    orphaned = cleanup_orphaned_images()
    print(f"Removed {orphaned} orphaned images")
    
    # Show updated stats
    print("\nUpdated Statistics:")
    stats = get_storage_stats()
    print(f"- Total Products: {stats['total_products']}")
    print(f"- Active Products: {stats['active_products']}")
    print(f"- Sold Products: {stats['sold_products']}")
    print(f"- Total Images: {stats['total_images']}")
    print(f"- Storage Used: {stats['storage_size_mb']} MB")
    
    print("\nCleanup completed!")