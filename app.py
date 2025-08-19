# == Colab  === 
# !pip install -U diffusers
# !pip install torch
# !pip install flask pyngrok --quiet
# !ngrok config add-authtoken ******
# 



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
import io
import base64
from PIL import Image
import nest_asyncio
import uvicorn
from pyngrok import ngrok

# Allow async in Colab
nest_asyncio.apply()

app = FastAPI(title="Stable Diffusion Image Generator API", version="1.0.0")

# Enable CORS for VS Code frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline globally
pipe = None
def initialize_pipeline():
    global pipe
    if pipe is None:
        print("Loading Stable Diffusion pipeline...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipe.to(device)
        print(f"Pipeline loaded on {device}")

# Request/Response models
class ImageGenerationRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 576
    num_inference_steps: int = 20
    guidance_scale: float = 7.5

class ImageGenerationResponse(BaseModel):
    image_base64: str
    message: str

@app.on_event("startup")
async def startup_event():
    initialize_pipeline()

@app.get("/")
async def root():
    return {"message": "Stable Diffusion API is running!"}

@app.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    if pipe is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    width = (request.width // 8) * 8
    height = (request.height // 8) * 8

    # Generate image
    image = pipe(
        request.prompt,
        width=width,
        height=height,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale
    ).images[0]

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return ImageGenerationResponse(image_base64=img_base64, message="Image generated successfully")

# Start server with ngrok
def start_server():
    public_url = ngrok.connect(8000)
    print(f"Public URL: {public_url}")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
