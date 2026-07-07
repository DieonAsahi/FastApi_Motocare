from fastapi import FastAPI, UploadFile, File
import shutil
import os
from ocr.model import read_odometer
from supabase_client import supabase
from math import radians, sin, cos, sqrt, atan2
import uvicorn


app = FastAPI()

# buat folder uploads jika belum ada
os.makedirs("uploads", exist_ok=True)


@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:

        # ambil extension asli
        ext = file.filename.split(".")[-1]

        # nama file baru
        path = f"uploads/temp.{ext}"

        # simpan file
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # OCR
        hasil = read_odometer(path)

        return {
            "success": True,
            "odometer": hasil
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# @app.get("/workshop")
# def get_workshop():

#     response = (
#         supabase
#         .table("workshop")
#         .select("*")
#         .execute()
#     )

#     return {
#         "count": len(response.data)
#     }

def get_all_workshops():
    all_data = []

    start = 0
    page_size = 1000

    while True:

        response = (
            supabase
            .table("workshop")
            .select("*")
            .range(start, start + page_size - 1)
            .execute()
        )

        data = response.data

        if not data:
            break

        all_data.extend(data)

        if len(data) < page_size:
            break

        start += page_size

    return all_data

@app.get("/workshop")
def get_workshop():

    data = get_all_workshops()

    return data

@app.get("/workshop/nearest")
def nearest_workshop(
    lat: float,
    lng: float,
    limit: int = 10
):

    response = (
        supabase
        .table("workshop")
        .select("*")
        .execute()
    )

    workshops = response.data

    result = []

    for w in workshops:

        distance = haversine(
            lat,
            lng,
            w["latitude"],
            w["longitude"]
        )

        result.append({
            "id": w["id"],
            "title": w["title"],
            "category": w["category"],
            "address": w["address"],
            "phone": w["phone"],
            "rating": w["total_score"],
            "review_count": w["review_count"],
            "latitude": w["latitude"],
            "longitude": w["longitude"],
            "image_url": w["image_url"],
            "google_maps_url": w["google_maps_url"],
            "distance_km": round(distance, 2)
        })

    result.sort(
        key=lambda x: x["distance_km"]
    )

    return {
        "user_location": {
            "latitude": lat,
            "longitude": lng
        },
        "count": min(limit, len(result)),
        "data": result[:limit]
    }

@app.get("/workshop/{workshop_id}")
def get_workshop_detail(workshop_id: int):

    response = (
        supabase
        .table("workshop")
        .select("*")
        .eq("id", workshop_id)
        .single()
        .execute()
    )

    return response.data

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )