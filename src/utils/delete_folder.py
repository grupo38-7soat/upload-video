import shutil
import os

def delete_folder(folder_pathlist):
    for folder_path in folder_pathlist:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Pasta '{folder_path}' apagada com sucesso.")
        else:
            print(f"Pasta '{folder_path}' não encontrada.")
