import os
import zipfile
from pathlib import Path

def create_zip():
    source_dir = Path(r"c:\Users\varsh\smart-debugging")
    desktop_dir = Path(r"c:\Users\varsh\Desktop")
    zip_path = desktop_dir / "smart-debugging-backup.zip"
    
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                # Ensure we don't zip the script itself if it's run from within the dir, though it's negligible
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                
    print(f"Successfully created backup at: {zip_path}")

if __name__ == "__main__":
    create_zip()
