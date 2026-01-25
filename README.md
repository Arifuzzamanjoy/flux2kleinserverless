# FLUX.2 Klein - RunPod Serverless Worker

A serverless worker for running [FLUX.2 Klein 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) text-to-image and image-to-image generation on RunPod.

## 🚀 Features

- **Text-to-image generation** using FLUX.2 Klein 4B
- **Image-to-image editing** with optional input images
- Fast inference with distilled model (4 steps default)
- Runs on consumer GPUs (~13GB VRAM)
- Configurable inference parameters
- Reproducible results with seed control

## 📁 Project Structure

```
.
├── handler.py          # Main serverless handler
├── Dockerfile          # Docker image configuration
├── requirements.txt    # Python dependencies
├── test_input.json     # Local test input
├── test_handler.py     # Test utilities
├── build.sh           # Build and push script
├── .runpod/
│   └── tests.json     # RunPod automated tests
└── README.md
```

## 🛠️ Setup & Development

### Prerequisites

- Python 3.10+
- Docker
- RunPod account (for deployment)
- Docker Hub account (for image hosting)

### Local Development

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test locally with test_input.json:**
   ```bash
   python handler.py
   ```

4. **Test with local API server:**
   ```bash
   # Start local server
   python handler.py --rp_serve_api
   
   # In another terminal, send a request
   python test_handler.py --mode local
   ```

## 🐳 Building & Pushing Docker Image

### Using the build script:
```bash
chmod +x build.sh
./build.sh <your_dockerhub_username> latest
```

### Manual build:
```bash
# Build
docker build --platform linux/amd64 -t <username>/flux2-klein-serverless:latest .

# Push
docker push <username>/flux2-klein-serverless:latest
```

## 🚀 Deploying to RunPod

### Option 1: Deploy via Docker Hub

1. Go to [RunPod Serverless Console](https://www.runpod.io/console/serverless)
2. Click **New Endpoint**
3. Click **Import from Docker Registry**
4. Enter your Docker image URL: `docker.io/<username>/flux2-klein-serverless:latest`
5. Configure endpoint:
   - **Endpoint Type:** Queue
   - **GPU:** Select GPU with at least 24GB VRAM (recommended: A100, A6000, or RTX 4090)
   - **Active Workers:** 0 (scale to zero when idle)
   - **Max Workers:** Based on your needs
6. Click **Deploy Endpoint**

### Option 2: Deploy via GitHub Integration

1. Push this repository to GitHub
2. Go to RunPod Serverless Console
3. Click **New Endpoint** → **Import from GitHub**
4. Connect your GitHub account and select this repository
5. Configure endpoint settings
6. RunPod will automatically build and deploy on push

## 📡 API Usage

### Input Schema

```json
{
    "input": {
        "prompt": "A cat holding a sign that says hello world",
        "image": "https://example.com/image.jpg OR base64_encoded_string",
        "height": 1024,
        "width": 1024,
        "num_inference_steps": 4,
        "guidance_scale": 1.0,
        "seed": 42
    }
}
```

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ | - | Text description for image generation/transformation |
| `image` | string | ❌ | - | Input image for editing (URL or base64) |
| `height` | int | ❌ | 1024 | Output image height |
| `width` | int | ❌ | 1024 | Output image width |
| `num_inference_steps` | int | ❌ | 4 | Number of denoising steps (FLUX.2 Klein is distilled) |
| `guidance_scale` | float | ❌ | 1.0 | Classifier-free guidance scale |
| `seed` | int | ❌ | random | Seed for reproducibility |

### Output Schema

```json
{
    "image": "base64_encoded_png",
    "seed": 42
}
```

### Example: Send Request with cURL

```bash
# Text-to-image
curl -X POST "https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
        "prompt": "A cat holding a sign that says hello world",
        "height": 1024,
        "width": 1024,
        "seed": 42
    }
}'

# Image-to-image editing
curl -X POST "https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
        "prompt": "Turn this cat into a dog",
        "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png",
        "seed": 42
    }
}'
```

### Example: Python Client

```python
import runpod
import base64
from PIL import Image
from io import BytesIO

runpod.api_key = "YOUR_RUNPOD_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Send request
result = endpoint.run_sync({
    "prompt": "Turn this cat into a dog",
    "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png",
    "num_inference_steps": 28,
    "seed": 42
})

# Save output image
if "image" in result:
    img_data = base64.b64decode(result["image"])
    img = Image.open(BytesIO(img_data))
    img.save("output.png")
    print(f"Saved output.png (seed: {result['seed']})")
```

## 🧪 Testing

### Local Testing
```bash
# Test with default test_input.json
python handler.py

# Test with custom input
python handler.py --test_input '{"input": {"prompt": "Make it blue", "image": "https://example.com/img.jpg"}}'

# Run local API server
python handler.py --rp_serve_api
```

### Test Against Deployed Endpoint
```bash
python test_handler.py --mode runpod --endpoint-id YOUR_ID --api-key YOUR_KEY
```

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `HF_HOME` | Hugging Face cache directory |
| `TRANSFORMERS_CACHE` | Transformers cache directory |
| `HF_TOKEN` | Hugging Face token (if model requires authentication) |

## 🔧 Optimization Tips

1. **Reduce Cold Start Time:**
   - Use RunPod Network Volumes for model caching
   - Enable FlashBoot in endpoint settings
   - Keep minimum active workers > 0 for production

2. **Memory Optimization:**
   - FLUX.2 Klein 4B requires ~10GB VRAM
   - Use 24GB+ VRAM GPUs for best results

3. **Cost Optimization:**
   - Set active workers to 0 for development
   - Use `num_inference_steps` of 20-28 for good quality/speed balance

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Black Forest Labs](https://blackforestlabs.ai/) for FLUX.2
- [RunPod](https://runpod.io/) for serverless GPU infrastructure
- [Hugging Face](https://huggingface.co/) for model hosting and diffusers library
