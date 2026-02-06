# FLUX.2 Klein - RunPod Serverless Worker

A serverless worker for running [FLUX.2 Klein 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) text-to-image and image-to-image generation on RunPod.

[![Docker CD](https://github.com/<YOUR_USERNAME>/Flux2_serverless/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/<YOUR_USERNAME>/Flux2_serverless/actions/workflows/docker-build-push.yml)

## 🚀 Features

- **Text-to-image generation** using FLUX.2 Klein 4B
- **Image-to-image editing** with optional input images
- Fast inference with distilled model (4 steps default)
- Runs on consumer GPUs (~13GB VRAM)
- Configurable inference parameters
- Reproducible results with seed control
- **Automatic Docker builds via GitHub Actions**

## 🐳 Quick Start - Automated Deployment

### 1. Fork this repository
Click the "Fork" button at the top right of this page.

### 2. Set up Docker Hub token
1. Create a Docker Hub access token at https://hub.docker.com/settings/security
2. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
3. Create a new secret named `DOCKERHUB_TOKEN` with your token value

### 3. Push to trigger build
```bash
git clone https://github.com/<YOUR_USERNAME>/Flux2_serverless.git
cd Flux2_serverless
# Make any changes you want
git add .
git commit -m "Initial deployment"
git push origin main
```

The GitHub Actions workflow will automatically:
- ✅ Build your Docker image
- ✅ Push to Docker Hub as `s1710374103/flux2kleinserverless:tagname`
- ✅ Create a `:latest` tag for easy updates

### 4. Deploy to RunPod
Use the Docker image URL in RunPod:
```
docker.io/s1710374103/flux2kleinserverless:tagname
```

See [.github/workflows/README.md](.github/workflows/README.md) for detailed setup instructions.

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

### Option 1: Automated Build (Recommended)
**Use GitHub Actions** - See [Quick Start](#-quick-start---automated-deployment) above.

### Option 2: Manual Build
For advanced users who want to build locally:

```bash
# Build the image
docker build --platform linux/amd64 -t s1710374103/flux2kleinserverless:tagname .

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push s1710374103/flux2kleinserverless:tagname
```

Or use the provided build script:
```bash
chmod +x build.sh
./build.sh s1710374103 tagname
```

**Note:** Building locally requires a system with full Docker support and may take 10-15 minutes.

## 🚀 Deploying to RunPod

### Step 1: Get Your Docker Image URL
After GitHub Actions builds your image (or manual build), use:
```
docker.io/s1710374103/flux2kleinserverless:tagname
```

### Step 2: Create RunPod Serverless Endpoint

1. Go to [RunPod Serverless Console](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**
3. Choose **"Custom"** template
4. Enter your Docker image URL from Step 1
5. **Configure Endpoint:**
   - **Name:** `flux2-klein-worker`
   - **GPU Type:** Select GPU with at least 16GB VRAM (recommended: A5000, A6000, RTX 4090, or A100)
   - **Container Disk:** 20GB minimum
   - **Idle Timeout:** 5 seconds (to scale to zero quickly)
   - **Active Workers:** 0 (scale to zero)
   - **Max Workers:** Set based on your needs (e.g., 3)
   - **GPUs per Worker:** 1
6. Click **"Deploy"**

### Step 3: Test Your Endpoint

Once deployed, you'll get an **Endpoint ID** and **API Key**. Test it:

```bash
curl -X POST "https://api.runpod.ai/v2/<ENDPOINT_ID>/runsync" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "A cat holding a sign that says hello world",
      "width": 1024,
      "height": 1024,
      "num_inference_steps": 4
    }
  }'
```

### Alternative: Use RunPod GitHub Integration

1. **Push this repository to GitHub**
2. In RunPod Console, click **"New Endpoint"** → **"Import from GitHub"**
3. **Connect your GitHub account** and select this repository
4. RunPod will automatically build and deploy on every push

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
