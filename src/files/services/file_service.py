from urllib.parse import urlparse
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import get_settings
from src.core.s3_client import s3_client
from src.files.exceptions import (
    ImageTooLargeException,
    InvalidImageTypeException,
)

settings = get_settings()

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class FileService:
    async def validate_image(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise InvalidImageTypeException("Unsupported image type")

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise ImageTooLargeException("Image is too large")

        await file.seek(0)

    def build_object_key(self, filename: str) -> str:
        extension = filename.rsplit(".", 1)[-1].lower()

        return f"posts/{uuid4()}.{extension}"

    async def upload_image(self, file: UploadFile) -> str:
        await self.validate_image(file)

        object_key = self.build_object_key(file.filename or "image")

        s3_client.upload_fileobj(
            file.file,
            settings.s3_bucket_name,
            object_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        return object_key

    def build_public_url(self, object_key: str) -> str:
        return f"{settings.s3_public_url}/{settings.s3_bucket_name}/{object_key}"

    def delete_object(self, object_key: str) -> None:
        s3_client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
        )

    def extract_object_key(self, image_url: str) -> str:
        path = urlparse(image_url).path.lstrip("/")

        prefix = f"{settings.s3_bucket_name}/"

        if not path.startswith(prefix):
            raise ValueError("Invalid image URL")

        return path[len(prefix) :]

    def delete_image(self, image_url: str) -> None:
        object_key = self.extract_object_key(image_url)

        self.delete_object(object_key)
