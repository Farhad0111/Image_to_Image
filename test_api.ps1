# Image-to-Image API Testing Examples (PowerShell)
# Make sure the server is running: python main.py
# API Key: 310e237f-636e-43bc-a59f-1a1c7580965b
# 
# Note: This API has been simplified to only require an image and prompt.
# Default settings: 2K size, URL response format, watermark enabled.

Write-Host "🚀 Image-to-Image API Testing Examples (Simplified)" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "API Key: 310e237f-636e-43bc-a59f-1a1c7580965b" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "🏥 Test 1: Health Check" -ForegroundColor Yellow
Write-Host "----------------------" -ForegroundColor Yellow

try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/image-to-image/health" -Method Get
    Write-Host "✅ Health Check Response:" -ForegroundColor Green
    $healthResponse | ConvertTo-Json -Depth 3
    
    if ($healthResponse.status -eq "healthy") {
        Write-Host "✅ Service is healthy and ready" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Service health issue detected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Make sure the server is running with: python main.py" -ForegroundColor Cyan
}

Write-Host ""

# Test 2: Service Info
Write-Host "ℹ️  Test 2: Service Information" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow

try {
    $infoResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/image-to-image/info" -Method Get
    Write-Host "✅ Service Info Response:" -ForegroundColor Green
    $infoResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Service info failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Create a test image if needed
Write-Host "📁 Test 3: Test Image Preparation" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow

$testImagePath = "test_image.jpg"

if (-not (Test-Path $testImagePath)) {
    Write-Host "📝 Creating a test image..." -ForegroundColor Cyan
    
    # PowerShell script to create a simple test image using .NET
    Add-Type -AssemblyName System.Drawing
    
    $bitmap = New-Object System.Drawing.Bitmap(256, 256)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([System.Drawing.Color]::LightBlue)
    
    # Draw a simple pattern
    $whitePen = New-Object System.Drawing.Pen([System.Drawing.Color]::Blue, 3)
    $graphics.DrawRectangle($whitePen, 50, 50, 156, 156)
    
    $yellowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Yellow)
    $graphics.FillEllipse($yellowBrush, 100, 100, 56, 56)
    
    $font = New-Object System.Drawing.Font("Arial", 12)
    $blackBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
    $graphics.DrawString("TEST", $font, $blackBrush, 110, 120)
    
    $bitmap.Save($testImagePath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
    
    $graphics.Dispose()
    $bitmap.Dispose()
    $whitePen.Dispose()
    $yellowBrush.Dispose()
    $blackBrush.Dispose()
    $font.Dispose()
    
    Write-Host "✅ Test image created: $testImagePath" -ForegroundColor Green
} else {
    Write-Host "✅ Test image found: $testImagePath" -ForegroundColor Green
}

Write-Host ""

# Test 4: Example curl commands
Write-Host "🖼️  Test 4: Image Generation Examples" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

Write-Host "💡 Example curl commands for testing:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ Basic image transformation (simplified API):" -ForegroundColor White
Write-Host 'curl -X POST "http://localhost:8000/api/v1/image-to-image" \' -ForegroundColor Gray
Write-Host '  -H "Content-Type: multipart/form-data" \' -ForegroundColor Gray
Write-Host "  -F `"image=@$testImagePath`" \" -ForegroundColor Gray
Write-Host '  -F "prompt=Transform this into a beautiful cartoon style image"' -ForegroundColor Gray

Write-Host ""

Write-Host "2️⃣ Watercolor style:" -ForegroundColor White
Write-Host 'curl -X POST "http://localhost:8000/api/v1/image-to-image" \' -ForegroundColor Gray
Write-Host '  -H "Content-Type: multipart/form-data" \' -ForegroundColor Gray
Write-Host "  -F `"image=@$testImagePath`" \" -ForegroundColor Gray
Write-Host '  -F "prompt=Make this look like a watercolor painting"' -ForegroundColor Gray

Write-Host ""

Write-Host "3️⃣ Cyberpunk style:" -ForegroundColor White
Write-Host 'curl -X POST "http://localhost:8000/api/v1/image-to-image" \' -ForegroundColor Gray
Write-Host '  -H "Content-Type: multipart/form-data" \' -ForegroundColor Gray
Write-Host "  -F `"image=@$testImagePath`" \" -ForegroundColor Gray
Write-Host '  -F "prompt=Convert to cyberpunk style with neon colors"' -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Make sure your server is running: python main.py" -ForegroundColor White
Write-Host "   2. Verify the .env file contains: ARK_API_KEY=310e237f-636e-43bc-a59f-1a1c7580965b" -ForegroundColor White
Write-Host "   3. Test with the Python script: python test_image_to_image.py" -ForegroundColor White
Write-Host "   4. Or use the curl commands above" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "   - Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - ReDoc: http://localhost:8000/redoc" -ForegroundColor White