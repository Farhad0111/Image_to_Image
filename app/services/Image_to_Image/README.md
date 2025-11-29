# Image-to-Image Generation Service

This service provides an API endpoint for generating new images based on input images and text prompts using the BytePlus Ark API with the `seedream-4-0-250828` model.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- BytePlus Ark API Key: `310e237f-636e-43bc-a59f-1a1c7580965b`

### Setup
1. **Environment Configuration**:
   ```bash
   # Add to .env file
   ARK_API_KEY=310e237f-636e-43bc-a59f-1a1c7580965b
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**:
   ```bash
   python main.py
   ```

4. **Access the API**:
   - Server: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`

## 🛠️ API Endpoints

### 1. Generate Image-to-Image
```
POST /api/v1/image-to-image
```

Transform an input image using a text prompt.

**Parameters (multipart/form-data):**
- `image` (file, required): Input image file (JPEG, PNG, etc.) - max 10MB
- `prompt` (string, required): Text describing desired transformation (1-1000 chars)
- `size` (string, optional): Output size - "1K", "2K" (default), or "4K"
- `response_format` (string, optional): "url" (default) or "b64_json"
- `watermark` (boolean, optional): Add watermark - true (default) or false

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/image-to-image" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@your_image.jpg" \
  -F "prompt=Transform this into a cartoon style image" \
  -F "size=2K" \
  -F "response_format=url" \
  -F "watermark=true"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Image generated successfully",
  "image_url": "https://generated-image-url.com/image.jpg",
  "image_data": null,
  "prompt_used": "Transform this into a cartoon style image",
  "size": "2K",
  "model_used": "seedream-4-0-250828",
  "generation_time": 3.45
}
```

### 2. Health Check
```
GET /api/v1/image-to-image/health
```

Check service health and configuration.

### 3. Service Information
```
GET /api/v1/image-to-image/info
```

Get service capabilities and supported formats.

## 🧪 Testing

### Option 1: Python Test Script
```bash
python test_image_to_image.py
```

### Option 2: PowerShell Test Script
```powershell
.\test_api.ps1
```

### Option 3: Manual curl Testing
```bash
# Health check
curl -X GET "http://localhost:8000/api/v1/image-to-image/health"

# Service info
curl -X GET "http://localhost:8000/api/v1/image-to-image/info"

# Image generation
curl -X POST "http://localhost:8000/api/v1/image-to-image" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_image.jpg" \
  -F "prompt=Make this look like a watercolor painting" \
  -F "size=2K" \
  -F "response_format=url"
```

## 📋 Features

- ✅ **BytePlus Ark Integration**: Uses the official BytePlus API
- ✅ **Multiple Image Sizes**: 1K, 2K, and 4K output options
- ✅ **Flexible Response Formats**: URL or base64 data
- ✅ **Image Validation**: Smart validation and error handling
- ✅ **Performance Monitoring**: Generation time tracking
- ✅ **Health Monitoring**: Service health endpoints
- ✅ **Comprehensive Error Handling**: Detailed error responses

## 🖼️ Supported Image Formats

**Input Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png) 
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

**Output Formats:**
- JPEG (via URL or base64)
- PNG (via URL or base64)

## ⚙️ Configuration

### Environment Variables
```bash
# Required
ARK_API_KEY=310e237f-636e-43bc-a59f-1a1c7580965b

# Optional (with defaults)
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

### Image Limits
- **File Size**: Maximum 10MB
- **Dimensions**: 32x32 to 4096x4096 pixels
- **Prompt Length**: 1-1000 characters

## 🏗️ Architecture

```
app/services/Image_to_Image/
├── Image_to_Image.py          # Core service logic
├── Image_to_Image_Route.py    # FastAPI endpoints  
├── Image_to_Image_Schema.py   # Pydantic models
└── README.md                  # This documentation
```

### Key Components:

1. **ImageToImageService**: Core service class handling BytePlus API integration
2. **Pydantic Schemas**: Request/response validation and serialization
3. **FastAPI Routes**: HTTP endpoint definitions and error handling
4. **Image Processing**: PIL-based image validation and processing

## 🔧 API Integration

This service integrates with BytePlus Ark API:

- **Base URL**: `https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`
- **Model**: `seedream-4-0-250828`  
- **Authentication**: Bearer token
- **API Key**: `310e237f-636e-43bc-a59f-1a1c7580965b`

## 🚨 Error Handling

The service includes comprehensive error handling for:

- ❌ Invalid image formats or corrupted files
- ❌ File size violations (>10MB)
- ❌ Invalid image dimensions
- ❌ API authentication failures
- ❌ Network timeouts and connectivity issues
- ❌ Invalid prompts or parameters
- ❌ BytePlus API errors and rate limits

## 📊 Example Use Cases

1. **Style Transfer**: "Convert this photo to an oil painting style"
2. **Color Enhancement**: "Make the colors more vibrant and saturated"
3. **Artistic Filters**: "Apply a vintage sepia tone effect"
4. **Object Modification**: "Add flowers to this landscape image"
5. **Mood Changes**: "Make this image look more dramatic and moody"

## 🔒 Security Notes

- API keys should be stored securely in environment variables
- File uploads are validated for type and size
- Input sanitization prevents malicious file uploads
- Rate limiting should be implemented for production use

## 🐛 Troubleshooting

### Common Issues:

1. **"ARK_API_KEY not found"**
   - Ensure `.env` file contains: `ARK_API_KEY=310e237f-636e-43bc-a59f-1a1c7580965b`

2. **"Connection error"**
   - Check internet connectivity
   - Verify BytePlus API endpoint availability

3. **"Invalid image file"**
   - Ensure image is in supported format (JPEG, PNG, etc.)
   - Check file size is under 10MB

4. **"Request timeout"**
   - Large images or complex prompts may take longer
   - Consider using smaller image sizes

### Debug Mode:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 📈 Performance Tips

- Use appropriate image sizes (2K is usually optimal)
- Keep prompts clear and specific
- Optimize input images before upload
- Consider caching for repeated requests