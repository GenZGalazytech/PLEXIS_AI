import io
import torch
from PIL import Image
from clip import load, tokenize
from torchvision import transforms


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = load("ViT-B/32", device=device)

print(f"[ModelController] Using device: {device}")
print(f"[ModelController] CLIP model: ViT-B/32")


def image_processing(image_file):
    try:
        if isinstance(image_file, bytes):
            image = Image.open(io.BytesIO(image_file)).convert("RGB")
        elif isinstance(image_file, str):
            image = Image.open(image_file).convert("RGB")
        elif isinstance(image_file, Image.Image):
            image = image_file
        else:
            raise ValueError("Unsupported image format")

        with torch.no_grad():
            image = preprocess(image).unsqueeze(0).to(device)
            embedding = model.encode_image(image).cpu().numpy().flatten()

        return embedding.tolist()

    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def get_text_embedding(text):
    try:
        text_tokenized = tokenize([text]).to(device)
        with torch.no_grad():
            embedding = model.encode_text(text_tokenized).cpu().numpy().flatten()
        return embedding
    except Exception as e:
        print(f"Error processing text: {e}")
        return None
