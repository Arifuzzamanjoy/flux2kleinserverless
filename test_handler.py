#!/usr/bin/env python3
"""
Local test script for FLUX.2 Klein RunPod serverless handler.
Tests the handler without needing to deploy to RunPod.
"""

import json
import base64
import requests
from PIL import Image
from io import BytesIO


def test_with_url():
    """Test the handler with an image URL."""
    print("\n" + "="*50)
    print("Testing FLUX.2 Handler with Image URL")
    print("="*50)
    
    test_payload = {
        "input": {
            "prompt": "Turn this cat into a dog",
            "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png",
            "num_inference_steps": 4,  # Reduced for testing
            "guidance_scale": 3.5,
            "strength": 0.8,
            "seed": 42
        }
    }
    
    print(f"Test payload: {json.dumps(test_payload, indent=2)}")
    return test_payload


def test_with_base64():
    """Test the handler with a base64 encoded image."""
    print("\n" + "="*50)
    print("Testing FLUX.2 Handler with Base64 Image")
    print("="*50)
    
    # Download a sample image and convert to base64
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png"
    response = requests.get(image_url)
    img_base64 = base64.b64encode(response.content).decode("utf-8")
    
    test_payload = {
        "input": {
            "prompt": "Turn this cat into a majestic lion",
            "image": img_base64,
            "num_inference_steps": 4,  # Reduced for testing
            "guidance_scale": 3.5,
            "strength": 0.75,
            "seed": 123
        }
    }
    
    print(f"Test payload created with base64 image ({len(img_base64)} chars)")
    return test_payload


def save_output_image(result, filename="output.png"):
    """Save the output image from the handler result."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    if "image" in result:
        img_data = base64.b64decode(result["image"])
        img = Image.open(BytesIO(img_data))
        img.save(filename)
        print(f"Output image saved to: {filename}")
        print(f"Seed used: {result.get('seed', 'N/A')}")
    else:
        print("No image in result")


def test_local_api(endpoint_url="http://localhost:8000/runsync"):
    """
    Test against local RunPod API server.
    
    Start the local server with:
        python handler.py --rp_serve_api
    """
    print("\n" + "="*50)
    print(f"Testing against local API: {endpoint_url}")
    print("="*50)
    
    payload = {
        "input": {
            "prompt": "Turn this cat into a dog",
            "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png",
            "num_inference_steps": 4,
            "seed": 42
        }
    }
    
    try:
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"Response: {json.dumps({k: v[:50] + '...' if isinstance(v, str) and len(v) > 50 else v for k, v in result.items()}, indent=2)}")
        save_output_image(result.get("output", result), "test_output.png")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to local API server.")
        print("Make sure to start it with: python handler.py --rp_serve_api")
    except Exception as e:
        print(f"Error: {e}")


def test_runpod_endpoint(endpoint_id, api_key):
    """
    Test against deployed RunPod endpoint.
    
    Args:
        endpoint_id: Your RunPod endpoint ID
        api_key: Your RunPod API key
    """
    print("\n" + "="*50)
    print(f"Testing against RunPod endpoint: {endpoint_id}")
    print("="*50)
    
    import runpod
    runpod.api_key = api_key
    
    endpoint = runpod.Endpoint(endpoint_id)
    
    run_request = endpoint.run_sync({
        "prompt": "Turn this cat into a dog",
        "image": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png",
        "num_inference_steps": 28,
        "seed": 42
    })
    
    print(f"Result: {run_request}")
    if isinstance(run_request, dict):
        save_output_image(run_request, "runpod_output.png")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FLUX.2 Klein RunPod Handler")
    parser.add_argument("--mode", choices=["url", "base64", "local", "runpod"], 
                        default="url", help="Test mode")
    parser.add_argument("--endpoint-id", help="RunPod endpoint ID (for runpod mode)")
    parser.add_argument("--api-key", help="RunPod API key (for runpod mode)")
    
    args = parser.parse_args()
    
    if args.mode == "url":
        payload = test_with_url()
        print("\nTo test locally, run: python handler.py")
        
    elif args.mode == "base64":
        payload = test_with_base64()
        print("\nTo test locally, run: python handler.py")
        
    elif args.mode == "local":
        test_local_api()
        
    elif args.mode == "runpod":
        if not args.endpoint_id or not args.api_key:
            print("ERROR: --endpoint-id and --api-key required for runpod mode")
        else:
            test_runpod_endpoint(args.endpoint_id, args.api_key)
