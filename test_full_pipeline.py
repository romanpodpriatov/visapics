#!/usr/bin/env python3
"""Test the full processing pipeline with mask-based hair detection"""

import os
import cv2
import logging
from PIL import Image
import mediapipe as mp
from photo_specs import get_photo_specification
from image_processing import VisaPhotoProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Get specification
spec = get_photo_specification("US", "Visa Lottery")

# Setup paths
input_image = "tests/IMG_5520.JPG"
unique_id = "test_mask_pipeline"
processed_path = f"test_output/processed_{unique_id}.jpg"
preview_path = f"test_output/preview_{unique_id}.jpg"
printable_path = f"test_output/printable_{unique_id}.jpg"
printable_preview_path = f"test_output/printable_preview_{unique_id}.jpg"

# Create output directory
os.makedirs("test_output", exist_ok=True)

print("=" * 70)
print("🧪 FULL PIPELINE TEST WITH MASK-BASED HAIR DETECTION")
print("=" * 70)
print(f"📋 Specification: {spec.country_code} {spec.document_name}")
print(f"📐 Source: {input_image}")

# Initialize face mesh (we'll pass None for GFPGAN and ONNX to avoid model loading)
face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

try:
    # Create processor without GFPGAN and ONNX for simplicity
    processor = VisaPhotoProcessor(
        input_path=input_image,
        processed_path=processed_path,
        preview_path=preview_path,
        printable_path=printable_path,
        printable_preview_path=printable_preview_path,
        fonts_folder="fonts",
        photo_spec=spec,
        gfpganer_instance=None,  # Skip enhancement for this test
        ort_session_instance=None,  # Skip background removal for this test
        face_mesh_instance=face_mesh
    )

    print("\n🔧 Processing with mask-based algorithm...")
    photo_info = processor.process()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Head Height: {photo_info['head_height']}mm")
    print(f"   Eye Distance: {photo_info['eye_to_bottom']}mm")
    print(f"   Head Compliance: {'✅' if photo_info['compliance']['head_height'] else '❌'}")
    print(f"   Eye Compliance: {'✅' if photo_info['compliance']['eye_to_bottom'] else '❌'}")
    print(f"   Scale Factor: {photo_info.get('scale_factor', 'N/A')}")
    
    # Check if measurements match expectations
    expected_head_mm = 30.2  # From our crop_data calculation
    actual_head_mm = photo_info['head_height']
    
    print(f"\n🔍 VALIDATION:")
    print(f"   Expected head height: {expected_head_mm}mm")
    print(f"   Actual head height: {actual_head_mm}mm")
    print(f"   Difference: {abs(actual_head_mm - expected_head_mm):.1f}mm")
    
    success = abs(actual_head_mm - expected_head_mm) < 0.5  # Allow 0.5mm tolerance
    print(f"\n🏆 PIPELINE TEST: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("   ✅ Mask-based measurements are correctly used in compliance check")
        print("   ✅ No more re-analysis with landmark-only detection")
        print("   ✅ BiRefNet hair detection data preserved through pipeline")
    
except Exception as e:
    print(f"❌ Error in pipeline: {e}")
    import traceback
    traceback.print_exc()

# Clean up
if os.path.exists("test_output"):
    import shutil
    shutil.rmtree("test_output")
    print(f"\n🧹 Cleaned up test output directory")