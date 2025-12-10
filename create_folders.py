"""Створення необхідних папок для файлів."""
import os

def create_folders():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    folders = [
        os.path.join(base_dir, 'app', 'static', 'uploads', 'books'),
        os.path.join(base_dir, 'app', 'static', 'uploads', 'covers'),
        os.path.join(base_dir, 'app', 'static', 'images'),
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Створено папку: {folder}")
        
        # Створити .gitkeep файл
        gitkeep = os.path.join(folder, '.gitkeep')
        if not os.path.exists(gitkeep):
            open(gitkeep, 'w').close()
    
    print("\n✅ Всі папки створено!")

if __name__ == '__main__':
    create_folders()
