from src.files.services.file_service import FileService


def get_file_service() -> FileService:
    return FileService()
