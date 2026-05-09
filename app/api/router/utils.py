from fastapi import HTTPException, status, APIRouter, UploadFile, File

from app.utils.image import save_image

router = APIRouter()
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and JPG are allowed."
        )
    try:
        image_url = await save_image(file, folder="cnic")
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )