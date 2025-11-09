# Test Fixtures

This directory contains sample files for testing multimodal complaint submission.

## Files Needed

- **sample-image.jpg**: Sample image for testing image upload
- **sample-audio.mp3**: Sample audio for testing voice complaints  
- **sample-video.mp4**: Sample video for testing video complaints

## Creating Test Files

You can use any sample files, but here are recommended specifications:

### Sample Image
- Format: JPG/PNG
- Size: 1-5 MB
- Resolution: 1920x1080 or lower
- Content: Street, pothole, garbage, or any civic issue

### Sample Audio
- Format: MP3/WAV
- Duration: 5-30 seconds
- Sample rate: 16kHz or higher
- Content: Voice describing a civic complaint

### Sample Video
- Format: MP4/WebM
- Duration: 10-60 seconds
- Resolution: 1280x720 or lower
- Size: < 50 MB
- Content: Recording of a civic issue

## Quick Setup

You can download free sample files or create your own:

```bash
# Download sample image (placeholder)
# Add your own test files here

# Or create a simple test image using ImageMagick:
convert -size 800x600 xc:blue sample-image.jpg

# Create a test audio file (requires ffmpeg):
ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" sample-audio.mp3

# Create a test video (requires ffmpeg):
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 sample-video.mp4
```

## Using in Tests

```typescript
// Upload image
await page.setInputFiles('input[type="file"]', 'fixtures/sample-image.jpg');

// Upload audio
await page.setInputFiles('input[type="file"]', 'fixtures/sample-audio.mp3');

// Upload video
await page.setInputFiles('input[type="file"]', 'fixtures/sample-video.mp4');
```
