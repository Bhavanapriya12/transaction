import zipfile
import os

def zip_folder(folder_path, zip_path, password=None):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))
    if password:
        with zipfile.ZipFile(zip_path, 'a') as zipf:
            zipf.setpassword(password.encode())
            zipf.close()

folder_to_zip = "collection_data"
zip_file = 'col.zip'
password = 'collection'
zip_folder(folder_to_zip, zip_file, password)