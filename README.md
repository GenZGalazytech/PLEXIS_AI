# Image Search API - FastAPI Server

A FastAPI-based backend service for AI-powered image search using CLIP (Contrastive Language-Image Pre-Training) embeddings. This service allows users to upload images and search them using natural language queries with semantic understanding.

## Features

- 🖼️ **Image Upload**: Upload multiple images with event metadata (event name, date, folder)
- 🔍 **Text-to-Image Search**: Search images using natural language queries (e.g., "people smiling", "wedding cake")
- 🤖 **CLIP Embeddings**: Powered by OpenAI's CLIP ViT-B/32 model for semantic image-text matching
- 🎨 **Modern Web UI**: Clean, responsive interface for easy image management
- ☁️ **Cloud Storage**: Optional DigitalOcean Spaces (S3-compatible) integration
- 🏢 **Multi-Tenant**: Support for multiple collections via environment configuration
- 🚀 **No Authentication**: Simplified setup for local development and testing

## Tech Stack

- **Framework**: FastAPI (Python web framework)
- **Database**: MongoDB (document storage for image metadata and embeddings)
- **ML Model**: CLIP ViT-B/32 (OpenAI's vision-language model)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Storage**: DigitalOcean Spaces / S3-compatible (optional for image hosting)
- **Image Processing**: PyTorch, PIL, torchvision

## Prerequisites

- Python 3.8 or higher
- MongoDB instance (local or MongoDB Atlas)
- GPU recommended for faster embedding generation (optional, CPU works too)
- 4GB+ RAM

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/GenZGalazytech/FastAPI_Server.git
cd FastAPI_Server
```

### 2. Create virtual environment (recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web server)
- PyTorch and CLIP (AI model)
- MongoDB driver (pymongo)
- FAISS (vector search)
- Other required packages

### 4. Set up environment variables
Create a `.env` file in the root directory:

```env
# MongoDB Configuration (Required)
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
IMAGES_DB_NAME=ImagesDB
COLLEGE_NAME=TestImages

# DigitalOcean Spaces (Optional - for cloud image storage)
DO_SPACE_KEY=your_space_key
DO_SPACE_SECRET=your_space_secret
DO_SPACE_REGION=nyc3
DO_SPACE_NAME=your_space_name
DO_ORIGIN=https://your-space.nyc3.digitaloceanspaces.com

# JWT Configuration (Optional - not used in current version)
JWT_SECRET=your_jwt_secret
ALGORITHM=HS256
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**MongoDB Setup Options:**

**Option A: MongoDB Atlas (Cloud - Free Tier)**
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string and add to `.env`

**Option B: Local MongoDB**
1. Install MongoDB locally
2. Use: `DATABASE_URL=mongodb://localhost:27017/`

## Running the Server

### Development Mode (Local)

**Windows:**
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Run server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Linux/Mac:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://127.0.0.1:8000**

You should see:
```
[MongoDB] Ping successful. Connected to MongoDB cluster.
[MongoDB] Using database: ImagesDB
[MongoDB] Using collection: TestImages
[ModelController] Using device: cpu
[ModelController] CLIP model: ViT-B/32
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Production Mode (Linux Server)

```bash
# Run in background
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > nohup.out 2>&1 &

# View logs
tail -f nohup.out

# Check running process
ps -ef | grep uvicorn

# Stop server
pkill -9 -f uvicorn
```

### Verify Installation

1. **Check API health:**
   ```bash
   curl http://127.0.0.1:8000/api/health
   ```
   Should return: `{"status":"ok"}`

2. **Open Web UI:**
   Navigate to http://127.0.0.1:8000 in your browser

3. **Check API docs:**
   Visit http://127.0.0.1:8000/docs for interactive API documentation

## Using the Application

### Web UI (Recommended for Testing)

The application includes a built-in web interface:

1. **Access the UI**: Open http://127.0.0.1:8000 in your browser

2. **Upload Images**:
   - Enter **Event Name** (e.g., "Wedding 2024")
   - Enter **Event Date** (e.g., "2024-11-08")
   - (Optional) Enter **Folder Name** for organization
   - Click **"Choose Files"** and select one or more images
   - Click **"Upload Images"**
   - Wait for confirmation message

3. **Search Images**:
   - Enter the **Event Name** (must match uploaded event)
   - Enter your **search query** using natural language:
     - ✅ Good: "people smiling at camera"
     - ✅ Good: "bride in white dress"
     - ✅ Good: "food on table"
     - ❌ Avoid: single words like "smile" (less accurate)
   - Click **"Search"**
   - Results show matching images with similarity scores

### Search Tips

- **Be descriptive**: "group of people dancing" works better than "dance"
- **Use context**: "wedding cake with flowers" is better than "cake"
- **Similarity threshold**: Results above 20% similarity are shown
- **Higher scores = better matches**: 30%+ is usually a good match

## API Endpoints

Full API documentation available at: http://127.0.0.1:8000/docs

### Health Check
```http
GET /api/health
```
Response: `{"status": "ok"}`

### Upload Images
```http
POST /upload-image
Content-Type: multipart/form-data

Parameters:
- event_name: string (required) - Event identifier
- event_date: string (required) - Event date
- folderName: string (optional) - Subfolder for organization
- files: file[] (required) - Image files to upload
```

Example using curl:
```bash
curl -X POST "http://127.0.0.1:8000/upload-image" \
  -F "event_name=Wedding2024" \
  -F "event_date=2024-11-08" \
  -F "folderName=Reception" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg"
```

### Search Images
```http
POST /search-images
Content-Type: application/json

Body:
{
  "event_name": "Wedding2024",
  "query_text": "people smiling at camera"
}
```

Example using curl:
```bash
curl -X POST "http://127.0.0.1:8000/search-images" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Wedding2024",
    "query_text": "bride in white dress"
  }'
```

Response:
```json
{
  "query": "bride in white dress",
  "event_name": "Wedding2024",
  "results": [
    {
      "filename": "image1.jpg",
      "image_url": "https://...",
      "similarity": 0.42
    }
  ],
  "message": "5 images matched"
}
```

## Project Structure

```
FastAPI_Server/
├── main.py                      # Main FastAPI application & API endpoints
├── auth.py                      # JWT authentication (legacy, not used)
├── database.py                  # Environment variables & DB config
├── connect.py                   # MongoDB and S3 client initialization
├── models.py                    # Pydantic data models
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration (create this)
├── README.md                    # This file
├── templates/                   # HTML templates
│   └── index.html              # Web UI interface
├── static/                      # Static assets
│   ├── style.css               # UI styling
│   └── script.js               # Frontend JavaScript
└── Controllers/
    └── ModelController.py       # CLIP model & embedding generation
```

## How It Works

1. **Image Upload**:
   - Images are uploaded and stored in MongoDB
   - CLIP model generates 512-dimensional embeddings for each image
   - Embeddings capture semantic meaning of image content
   - Optional: Images can be stored in DigitalOcean Spaces

2. **Text Search**:
   - User query is converted to embedding using CLIP
   - FAISS performs fast similarity search across all image embeddings
   - Results are ranked by cosine similarity
   - Only matches above 20% threshold are returned

3. **Multi-Tenant Support**:
   - Different collections can be used via `COLLEGE_NAME` env variable
   - Each tenant's images are stored separately
   - Useful for managing multiple clients/events

## Troubleshooting

### Server won't start
- Check if MongoDB connection string is correct in `.env`
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use

### Images not uploading
- Check MongoDB connection in terminal logs
- Verify `IMAGES_DB_NAME` and `COLLEGE_NAME` in `.env`
- Check file size (very large images may take time)

### Search returns no results
- Verify event name matches exactly (case-sensitive)
- Try more descriptive queries
- Check terminal logs for similarity scores
- Images may have low similarity (< 20%)

### Slow performance
- First run downloads CLIP model (~350MB) - this is normal
- CPU mode is slower than GPU
- Consider using GPU for production

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | - | MongoDB connection string |
| `IMAGES_DB_NAME` | No | `ImagesDB` | MongoDB database name |
| `COLLEGE_NAME` | No | `TestImages` | MongoDB collection name (tenant ID) |
| `DO_SPACE_KEY` | No | - | DigitalOcean Spaces access key |
| `DO_SPACE_SECRET` | No | - | DigitalOcean Spaces secret key |
| `DO_SPACE_REGION` | No | - | DigitalOcean Spaces region |
| `DO_SPACE_NAME` | No | - | DigitalOcean Spaces bucket name |

## Performance Notes

- **First run**: CLIP model download (~350MB) takes a few minutes
- **CPU mode**: ~2-5 seconds per image for embedding generation
- **GPU mode**: ~0.5-1 second per image (10x faster)
- **Search**: Near-instant with FAISS (< 100ms for 1000s of images)

## Contributing

This is an internal project for GenZGalazytech. For issues or improvements, contact the development team.

## License

Proprietary - GenZGalazytech © 2024
