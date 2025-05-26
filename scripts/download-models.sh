#!/bin/bash

# AI Models Download Script for VisaPics
set -e

echo "🤖 Downloading AI models..."

# Create model directories
mkdir -p gfpgan/weights
mkdir -p models

# Function to download with progress
download_with_progress() {
    local url=$1
    local output=$2
    local description=$3
    
    echo "📥 Downloading $description..."
    if command -v wget &> /dev/null; then
        wget --progress=bar:force:noscroll -O "$output" "$url"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$output" "$url"
    else
        echo "❌ Neither wget nor curl found. Please install one of them."
        exit 1
    fi
}

# Function to verify file size
verify_download() {
    local file=$1
    local min_size_mb=$2
    local description=$3
    
    if [ -f "$file" ]; then
        local size_mb=$(du -m "$file" | cut -f1)
        if [ "$size_mb" -ge "$min_size_mb" ]; then
            echo "✅ $description verified (${size_mb}MB)"
            return 0
        else
            echo "❌ $description appears corrupted (${size_mb}MB < ${min_size_mb}MB expected)"
            rm -f "$file"
            return 1
        fi
    else
        echo "❌ $description not found"
        return 1
    fi
}

# 1. GFPGAN Model
GFPGAN_PATH="gfpgan/weights/GFPGANv1.4.pth"
if [ ! -f "$GFPGAN_PATH" ] || ! verify_download "$GFPGAN_PATH" 300 "GFPGAN model"; then
    echo "🔄 Downloading GFPGAN model..."
    download_with_progress \
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth" \
        "$GFPGAN_PATH" \
        "GFPGAN face enhancement model"
    verify_download "$GFPGAN_PATH" 300 "GFPGAN model"
fi

# 2. Detection Model
DETECTION_PATH="gfpgan/weights/detection_Resnet50_Final.pth"
if [ ! -f "$DETECTION_PATH" ] || ! verify_download "$DETECTION_PATH" 100 "Detection model"; then
    echo "🔄 Downloading Detection model..."
    download_with_progress \
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth" \
        "$DETECTION_PATH" \
        "Face detection model"
    verify_download "$DETECTION_PATH" 100 "Detection model"
fi

# 3. Parsing Model
PARSING_PATH="gfpgan/weights/parsing_parsenet.pth"
if [ ! -f "$PARSING_PATH" ] || ! verify_download "$PARSING_PATH" 80 "Parsing model"; then
    echo "🔄 Downloading Parsing model..."
    download_with_progress \
        "https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth" \
        "$PARSING_PATH" \
        "Face parsing model"
    verify_download "$PARSING_PATH" 80 "Parsing model"
fi

# 4. BiRefNet Model (Background Removal)
BIREFNET_PATH="models/BiRefNet-portrait-epoch_150.onnx"
if [ ! -f "$BIREFNET_PATH" ] || ! verify_download "$BIREFNET_PATH" 900 "BiRefNet model"; then
    echo "🔄 Downloading BiRefNet model..."
    echo "⚠️  This is a large file (~930MB), it may take several minutes..."
    
    # Try multiple sources for BiRefNet
    BIREFNET_URLS=(
        "https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx"
        "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-portrait-epoch_150.onnx"
    )
    
    downloaded=false
    for url in "${BIREFNET_URLS[@]}"; do
        echo "🔄 Trying source: $url"
        if download_with_progress "$url" "$BIREFNET_PATH" "BiRefNet background removal model"; then
            if verify_download "$BIREFNET_PATH" 50 "BiRefNet model"; then
                downloaded=true
                break
            fi
        fi
    done
    
    if [ "$downloaded" = false ]; then
        echo "❌ Failed to download BiRefNet model from all sources"
        echo "📝 Manual download required:"
        echo "   1. Download BiRefNet model manually"
        echo "   2. Place it at: $BIREFNET_PATH"
        echo "   3. Re-run this script"
        
        # Create placeholder file
        touch "$BIREFNET_PATH"
        echo "⚠️  Created placeholder file. Please replace with actual model."
    fi
fi

# Set proper permissions
echo "🔒 Setting file permissions..."
find gfpgan/weights -name "*.pth" -exec chmod 644 {} \;
find models -name "*.onnx" -exec chmod 644 {} \;

# Summary
echo ""
echo "📊 Model Download Summary:"
echo "   GFPGAN (Face Enhancement): $([ -f "$GFPGAN_PATH" ] && echo "✅" || echo "❌")"
echo "   Detection (Face Detection): $([ -f "$DETECTION_PATH" ] && echo "✅" || echo "❌")"
echo "   Parsing (Face Parsing): $([ -f "$PARSING_PATH" ] && echo "✅" || echo "❌")"
echo "   BiRefNet (Background Removal): $([ -f "$BIREFNET_PATH" ] && du -h "$BIREFNET_PATH" | cut -f1 | grep -q "M\|G" && echo "✅" || echo "❌")"

# Calculate total size
total_size=$(du -sh gfpgan/weights models 2>/dev/null | awk '{sum += $1} END {print sum "MB"}' || echo "Unknown")
echo "   Total size: $total_size"

echo ""
echo "🤖 AI models setup completed!"

# Check if all critical models are present
if [ -f "$GFPGAN_PATH" ] && [ -f "$DETECTION_PATH" ] && [ -f "$PARSING_PATH" ]; then
    echo "✅ All critical models ready for deployment"
    exit 0
else
    echo "⚠️  Some models are missing. Application may have limited functionality."
    exit 1
fi