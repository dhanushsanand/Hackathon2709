#!/usr/bin/env python3
"""
Test Cloudinary configuration and upload functionality
"""
import asyncio
from utils.cloudinary import CloudinaryService
import io

async def test_cloudinary_config():
    """Test basic Cloudinary configuration"""
    try:
        service = CloudinaryService()
        print("✅ Cloudinary service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Cloudinary service: {e}")
        return False

async def test_cloudinary_upload():
    """Test uploading a small test file"""
    try:
        service = CloudinaryService()
        
        # Create a small test PDF-like content
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        result = await service.upload_pdf(
            file_bytes=test_content,
            filename="test.pdf",
            user_id="test_user_123"
        )
        
        print("✅ Test upload successful!")
        print(f"   Public ID: {result['public_id']}")
        print(f"   URL: {result['secure_url']}")
        print(f"   Size: {result['bytes']} bytes")
        
        # Clean up - delete the test file
        await service.delete_file(result['public_id'])
        print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test upload failed: {e}")
        return False

async def main():
    print("🧪 Testing Cloudinary Configuration...")
    print("=" * 50)
    
    tests = [
        ("Cloudinary Config", test_cloudinary_config),
        ("Cloudinary Upload", test_cloudinary_upload),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Summary: {passed}/{total} tests passed")

if __name__ == "__main__":
    asyncio.run(main())