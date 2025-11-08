import io
import numpy as np
import faiss
from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Form,
    UploadFile,
    File,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from PIL import Image
from jose import jwt
from models import SearchImageRequest

import connect
from connect import (
    get_s3_client,
    DO_SPACE_NAME,
    DO_SPACE_ENDPOINT,
    get_database,
    get_user_database,
)
from Controllers.ModelController import image_processing, get_text_embedding
from database import EnvVariables
from models import UserInDB, CurrentUser
from sklearn.metrics.pairwise import cosine_similarity

# === Initialize clients and databases ===
s3_client = get_s3_client()
images_db = get_database()
user_db = get_user_database()

# === FastAPI app setup ===
app = FastAPI(title="Image Search API", description="CLIP-powered image search with FastAPI")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        print(f"[Startup] Using Images DB: {EnvVariables.images_db_name}")
        print(f"[Startup] Using collection (college): {EnvVariables.college_name}")
    except Exception as e:
        print(f"[Startup] Error printing startup logs: {e}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main UI page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "Backend Working from Server..!!"}

# ============================================================
# ===============  IMAGE UPLOAD ENDPOINT  ===================
# ============================================================

@app.post("/upload-image")
async def upload_image(
    event_name: str = Form(...),
    event_date: str = Form(...),
    folderName: str = Form(""),
    files: List[UploadFile] = File(...),
):
    if images_db is None:
        raise HTTPException(status_code=500, detail="Database not connected. Please configure DATABASE_URL in .env")
    
    print(f"[Upload] Starting upload for event: {event_name}, files: {len(files)}")
    image_collection = images_db[EnvVariables.college_name]
    print(f"[Upload] Using collection: {EnvVariables.college_name}")
    image_docs = []

    storage_ = 0.0
    now = datetime.utcnow()
    for file in files:
        storage_ += file.size / 1024
        print(f"[Upload] Processing file: {file.filename}, Size: {file.size/1024:.2f} KB")

        image_bytes = await file.read()
        object_name = f"{EnvVariables.college_name}/{file.filename}"

        # Upload to S3 / DigitalOcean Space (optional)
        try:
            if s3_client and DO_SPACE_NAME:
                s3_client.put_object(
                    Bucket=DO_SPACE_NAME,
                    Key=object_name,
                    Body=image_bytes,
                    ACL="public-read",
                    ContentType=file.content_type,
                )
                image_url = f"{DO_SPACE_ENDPOINT}/{DO_SPACE_NAME}/{object_name}"
                print(f"[Upload] Uploaded to S3: {image_url}")
            else:
                # Use placeholder URL if S3 not configured
                image_url = f"local://{object_name}"
                print(f"[Upload] S3 not configured, using placeholder URL")
        except Exception as e:
            print(f"[Upload] S3 upload failed: {e}, using placeholder URL")
            image_url = f"local://{object_name}"

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print(f"[Upload] Generating embeddings for {file.filename}...")
        embeddings = image_processing(image)
        
        if embeddings is None:
            print(f"[Upload] ERROR: Failed to generate embeddings for {file.filename}")
            continue


        if folderName and folderName.strip():
            folder_name_path = f"{event_name}/{folderName}"
        else:
            folder_name_path = event_name
        image_docs.append({
            "college": EnvVariables.college_name,
            "filename": f"{EnvVariables.college_name}/{file.filename}",
            "folderName": folder_name_path,
            "content_type": file.content_type,
            "image_url": image_url,
            "event_name": event_name,
            "event_date": event_date,
            "embeddings": embeddings,
            "createdAt": now,
            "updatedAt": now
        })

    if image_docs:
        print(f"[Upload] Inserting {len(image_docs)} documents into MongoDB...")
        result = image_collection.insert_many(image_docs)
        print(f"[Upload] Successfully inserted {len(result.inserted_ids)} documents")
        print(f"[Upload] Inserted IDs: {result.inserted_ids[:3]}...")  # Show first 3 IDs
        return {"message": f"{len(image_docs)} images uploaded successfully!"}

    print(f"[Upload] ERROR: No valid image documents to insert")
    return {"error": "No images received or processed!"}

# ============================================================
# ===============  TEXT-TO-IMAGE SEARCH  ====================
# ============================================================

@app.post("/search-images")
async def search_images(
    payload: SearchImageRequest,
):
    """
    Searches top similar images for a given text query within the same event.
    Returns only images with similarity > 0.7, sorted descending.
    """
    event_name = payload.event_name
    query_text = payload.query_text
    print(f"[Search] Searching for: '{query_text}' in event: '{event_name}'")
    try:
        if images_db is None:
            raise HTTPException(status_code=500, detail="Database not connected. Please configure DATABASE_URL in .env")
        
        image_collection = images_db[EnvVariables.college_name]
        print(f"[Search] Using collection: {EnvVariables.college_name}")

        images = list(image_collection.find({"event_name": event_name}))
        print(f"[Search] Found {len(images)} images in event '{event_name}'")
        if not images:
            raise HTTPException(status_code=404, detail="No images found for this event")

        embeddings = []
        urls = []
        filenames = []
        for img in images:
            if "embeddings" in img and img["embeddings"] is not None:
                embeddings.append(np.array(img["embeddings"], dtype="float32"))
                urls.append(img["image_url"])
                filenames.append(img.get("filename", "unknown"))

        print(f"[Search] Extracted {len(embeddings)} valid embeddings from {len(images)} images")
        if not embeddings:
            raise HTTPException(status_code=404, detail="No embeddings found for event images")

        image_matrix = np.vstack(embeddings)
        dimension = image_matrix.shape[1]

        faiss.normalize_L2(image_matrix)
        index = faiss.IndexFlatIP(dimension)
        index.add(image_matrix)

        text_emb = get_text_embedding(query_text)
        if text_emb is None:
            raise HTTPException(status_code=500, detail="Failed to generate text embedding")

        text_emb = np.array(text_emb, dtype="float32").reshape(1, -1)
        faiss.normalize_L2(text_emb)

        # Search top N matches (e.g., all images)
        k = len(embeddings)
        distances, indices = index.search(text_emb, k)

        # Filter and sort by similarity descending
        results = []
        print(f"[Search] Top 5 similarity scores:")
        for idx, (i, score) in enumerate(zip(indices[0], distances[0])):
            if idx < 5:  # Log top 5
                print(f"  {idx+1}. {filenames[i]}: {score:.4f}")
            if score >= 0.20:  # Lower threshold from 0.26 to 0.20
                results.append({
                    "filename": filenames[i],
                    "image_url": urls[i],
                    "similarity": float(score)
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        print(f"[Search] Returning {len(results)} results above threshold 0.20")

        if not results:
            return {
                "query": query_text,
                "event_name": event_name,
                "results": [],
                "message": "No images match the similarity threshold of 0.20. Try different keywords."
            }

        return {
            "query": query_text,
            "event_name": event_name,
            "results": results,
            "message": f"{len(results)} images matched"
        }

    except Exception as e:
        # print(f"Error searching images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-images-old")
def search_images_old(
    payload: SearchImageRequest,
    ):
    if images_db is None:
        raise HTTPException(status_code=500, detail="Database not connected. Please configure DATABASE_URL in .env")

    event_name = payload.event_name
    query_text = payload.query_text
    query_embedding = get_text_embedding(query_text).reshape(1, -1)

    image_collection = images_db[EnvVariables.college_name]

    images = list(image_collection.find({"event_name": event_name}))
    matches = []
    for user in images :
        image_url = user["image_url"]
        stored_embedding = np.array(user["embeddings"]).reshape(1, -1)  # Convert back to array

        similarity = cosine_similarity(query_embedding, stored_embedding)[0][0]
        # print(similarity)
        if similarity >= 0.26:
            matches.append(image_url)  # Include similarity
        # matches.sort(key=lambda x: x["similarity"], reverse=True)  
        # image_results = [match["image_url"] for match in matches]
        # for image in matches:
        #     print(image)
    return {"reply": "Results", "images": matches}