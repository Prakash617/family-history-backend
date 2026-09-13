"""
Storage abstraction layer for local media and remote cloud providers (Cloudinary, S3).
"""
from django.core.files.storage import default_storage


class StorageService:
    """
    Unified storage service interface.
    """
    @staticmethod
    def save(file_obj, path: str) -> str:
        saved_path = default_storage.save(path, file_obj)
        return saved_path

    @staticmethod
    def get_url(path: str) -> str:
        if not path:
            return ""
        return default_storage.url(path)

    @staticmethod
    def delete(path: str) -> bool:
        if default_storage.exists(path):
            default_storage.delete(path)
            return True
        return False
