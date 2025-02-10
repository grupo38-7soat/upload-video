import pytest
import os
from src.utils.delete_folder import delete_folder

@pytest.fixture
def create_folders(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = tmp_path / "folder2"
    folder1.mkdir()
    folder2.mkdir()
    return [str(folder1), str(folder2)]

def test_delete_existing_folders(create_folders):
    delete_folder(create_folders)
    for folder in create_folders:
        assert not os.path.exists(folder)

def test_delete_non_existing_folder():
    non_existing_folder = ["non_existing_folder"]
    delete_folder(non_existing_folder)
    assert not os.path.exists(non_existing_folder[0])