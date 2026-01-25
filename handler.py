"""
FLUX.2 Klein Image-to-Image Handler for RunPod Serverless
"""

import runpod
import torch
import base64
import os
from io import BytesIO

# Set cache directories for local testing
# Models will be stored in /home/caches
os.environ["HF_HOME"] = "/home/caches/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/home/caches/huggingface"
os.environ["HF_HUB_CACHE"] = "/home/caches/huggingface/hub"
os.environ["TORCH_HOME"] = "/home/caches/torch"

# Create cache directories if they don't exist
os.makedirs("/home/caches/huggingface/hub", exist_ok=True)
os.makedirs("/home/caches/torch", exist_ok=True)

# Load the model outside the handler for efficiency
# Model is loaded once when the worker starts
print("Loading FLUX.2 Klein model...")
print(f"Cache directory: {os.environ['HF_HOME']}")

from diffusers import Flux2KleinPipeline
from diffusers.utils import load_image

# Determine device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Load the FLUX.2 Klein pipeline
pipe = Flux2KleinPipeline.from_pretrained(
    "black-forest-labs/FLUX.2-klein-4B",
    torch_dtype=torch.bfloat16,
)
pipe.enable_model_cpu_offload()  # Save VRAM by offloading to CPU

print("Model loaded successfully!")


def handler(job):
    """
    Handler function for FLUX.2 Klein text-to-image and image-to-image generation.
    
    Expected input:
    {
        "input": {
            "prompt": "Your prompt here",
            "image": "base64_encoded_image OR url",  # optional for img2img/editing
            "height": 1024,               # optional, default 1024
            "width": 1024,                # optional, default 1024
            "num_inference_steps": 4,     # optional, default 4 (FLUX.2 Klein is distilled)
            "guidance_scale": 1.0,        # optional, default 1.0
            "seed": 42                    # optional, for reproducibility
        }
    }
    
    Returns:
    {
        "image": "base64_encoded_output_image",
        "seed": seed_used
    }
    """
    job_input = job["input"]
    
    # Required parameters
    prompt = job_input.get("prompt")
    if not prompt:
        return {"error": "Missing required parameter: 'prompt'"}
    
    # Optional parameters
    input_image = job_input.get("image")
    height = job_input.get("height", 1024)
    width = job_input.get("width", 1024)
    num_inference_steps = job_input.get("num_inference_steps", 4)  # FLUX.2 Klein is distilled, 4 steps is default
    guidance_scale = job_input.get("guidance_scale", 1.0)
    seed = job_input.get("seed")
    
    try:
        # Load input image if provided (for image-to-image editing)
        image = None
        if input_image:
            if input_image.startswith(("http://", "https://")):
                # Load from URL
                print(f"Loading image from URL: {input_image[:50]}...")
                image = load_image(input_image)
            else:
                # Decode base64 image
                print("Decoding base64 image...")
                from PIL import Image
                image_data = base64.b64decode(input_image)
                image = Image.open(BytesIO(image_data)).convert("RGB")
        
        # Set up generator for reproducibility
        if seed is not None:
            generator = torch.Generator(device="cpu").manual_seed(seed)
        else:
            seed = torch.randint(0, 2**32, (1,)).item()
            generator = torch.Generator(device="cpu").manual_seed(seed)
        
        print(f"Generating image with prompt: '{prompt[:50]}...' using seed: {seed}")
        
        # Build pipeline arguments
        pipe_kwargs = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "generator": generator,
        }
        
        # Add image for image-to-image editing if provided
        if image is not None:
            pipe_kwargs["image"] = image
        
        # Run the pipeline
        output = pipe(**pipe_kwargs)
        
        output_image = output.images[0]
        
        # Convert output image to base64
        buffered = BytesIO()
        output_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        print("Image generation complete!")
        
        return {
            "image": img_base64,
            "seed": seed
        }
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        return {"error": str(e)}


# Configure and start the RunPod serverless function
runpod.serverless.start({
    "handler": handler,
})
