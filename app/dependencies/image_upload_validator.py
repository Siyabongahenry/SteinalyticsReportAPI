from fastapi import UploadFile, File, HTTPException
from PIL import Image

async def ImageUploadValidator(file: UploadFile = File(...)) -> UploadFile:
    """
    Dependency that validates uploaded image files in a production-safe way.
    - Ensures the file is a real image (not just mislabeled).
    - Supports JPEG, PNG, WEBP.
    """
    try:
        # Try opening the file with Pillow
        image = Image.open(file.file)
        image.verify()  # verifies integrity
        file.file.seek(0)  # reset pointer after verify
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image"
        )

    if image.format not in {"JPEG", "PNG", "WEBP"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format: {image.format}. Allowed: JPEG, PNG, WEBP"
        )

    return file
