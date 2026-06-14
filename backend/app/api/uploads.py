"""文件上传API"""
import os
import uuid
import subprocess
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.config import settings
from app.security import get_current_user

router = APIRouter()

ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
MAX_PHOTO_COUNT = 5
MAX_VIDEO_COUNT = 3
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_DURATION = 60  # seconds


def generate_filename(original_name: str, category: str) -> str:
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "jpg"
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"{category}_{now}_{uid}.{ext}"


def get_video_duration(file_path: str) -> float:
    """使用 ffprobe 获取视频时长（秒），不存在则返回0"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "json", file_path],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout:
            info = json.loads(result.stdout)
            return float(info.get("format", {}).get("duration", 0))
    except Exception:
        return 0
    return 0


@router.post("/photo")
async def upload_photos(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="请选择文件")
    if len(files) > MAX_PHOTO_COUNT:
        raise HTTPException(status_code=400, detail=f"最多上传 {MAX_PHOTO_COUNT} 张照片")

    saved = []
    for f in files:
        if f.content_type not in ALLOWED_PHOTO_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {f.content_type}，仅支持 JPEG/PNG/WebP")
        content = await f.read()
        if len(content) > MAX_PHOTO_SIZE:
            raise HTTPException(status_code=400, detail=f"照片 {f.filename} 超过 5MB 限制")

        filename = generate_filename(f.filename, "photo")
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as fp:
            fp.write(content)
        saved.append({"filename": filename, "url": f"/uploads/{filename}", "size": len(content)})

    return {"files": saved, "count": len(saved)}


@router.post("/video")
async def upload_videos(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="请选择文件")
    if len(files) > MAX_VIDEO_COUNT:
        raise HTTPException(status_code=400, detail=f"最多上传 {MAX_VIDEO_COUNT} 个视频")

    saved = []
    for f in files:
        if f.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {f.content_type}，仅支持 MP4/MOV/WebM")

        content = await f.read()
        if len(content) > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail=f"视频 {f.filename} 超过 50MB 限制")

        filename = generate_filename(f.filename, "video")
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as fp:
            fp.write(content)

        duration = get_video_duration(filepath)
        if duration > 0 and duration > MAX_VIDEO_DURATION:
            os.remove(filepath)
            raise HTTPException(status_code=400, detail=f"视频 {f.filename} 时长 {duration:.0f}s 超过 60s 限制")

        saved.append({"filename": filename, "url": f"/uploads/{filename}", "size": len(content), "duration": round(duration, 1)})

    return {"files": saved, "count": len(saved)}