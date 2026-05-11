from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/v1/home", tags=["home"])


@router.get("/slider")
async def get_slider():
    return [
        {
            "id": 1,
            "image_url": "",
            "link_type": "page",
            "link_payload": "price",
        }
    ]


@router.get("/tutorial")
async def get_tutorial():
    return {
        "image_url": "",
        "title": "Print Tutorial",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
