# 📦 Quick Installation Guide - DINOv2 Dependencies

## Option 1: Install Everything (Recommended)

```bash
# Navigate to backend directory
cd e:\Smartgriv\smartgriev\backend

# Install PyTorch (CPU version - works on all systems)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Transformers and other dependencies
pip install transformers pillow opencv-python numpy

# Verify installation
python -c "import torch; import transformers; print('✅ All dependencies installed!')"
```

## Option 2: Install with GPU Support (Faster, if you have NVIDIA GPU)

```bash
# Check if you have CUDA
nvidia-smi

# Install PyTorch with CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# OR install with CUDA 12.1 (newer systems)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install transformers pillow opencv-python numpy

# Verify GPU is available
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

## Option 3: Skip DINOv2 (Use Fallback Mode)

```bash
# Don't install anything!
# System will use fallback mode automatically
# Still processes images, just with basic analysis instead of AI
```

---

## Testing Installation

### Test 1: Check PyTorch
```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
# Expected: PyTorch version: 2.x.x
```

### Test 2: Check Transformers
```bash
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
# Expected: Transformers version: 4.x.x
```

### Test 3: Test DINOv2 Module
```bash
cd e:\Smartgriv\smartgriev\backend\machine_learning
python dinov2_processor.py
```

Expected output:
```
============================================================
SmartGriev DINOv2 Image Processor - Testing Module
============================================================

DINOv2 System Info:
  available: True
  model_name: facebook/dinov2-base
  device: cuda  (or cpu)
  cuda_available: True  (or False)
  complaint_categories: ['infrastructure', 'sanitation', 'utilities', ...]
  version: 1.0

============================================================
```

---

## Troubleshooting

### Issue: "No module named 'torch'"
```bash
pip install torch torchvision
```

### Issue: "No module named 'transformers'"
```bash
pip install transformers
```

### Issue: "CUDA out of memory"
```python
# Edit dinov2_processor.py
# Change model to smaller version:
processor = DINOv2Processor(model_name="facebook/dinov2-small")
```

### Issue: Installation takes too long
```bash
# Use CPU version (faster download)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

## What Gets Installed?

### Package Sizes:
- **PyTorch**: ~800 MB (CPU) or ~2 GB (GPU)
- **Transformers**: ~400 MB
- **Pillow**: ~3 MB
- **OpenCV**: ~50 MB
- **NumPy**: ~20 MB

### Total: ~1.3 GB (CPU) or ~2.5 GB (GPU)

---

## After Installation

### Start using DINOv2:

1. **Restart Backend Server:**
```bash
cd e:\Smartgriv\smartgriev\backend
python manage.py runserver
```

2. **Submit Test Complaint:**
- Go to: http://localhost:3000/multimodal-submit
- Upload any image
- Submit complaint
- Check console logs for DINOv2 analysis

3. **Check Logs:**
```bash
# Look for:
"DINOv2 analysis completed: scene=outdoor, category=infrastructure"
```

---

## System Requirements

### Minimum (CPU Mode):
- RAM: 4 GB
- Disk: 2 GB free space
- Python: 3.8+
- OS: Windows, Linux, macOS

### Recommended (GPU Mode):
- RAM: 8 GB
- VRAM: 4 GB (NVIDIA GPU)
- Disk: 4 GB free space
- CUDA: 11.8 or 12.1
- Python: 3.9+

---

## Performance Expectations

### With Dependencies Installed:
- ✅ DINOv2 AI analysis active
- ✅ Advanced scene classification
- ✅ Detailed element detection
- ✅ High accuracy categorization
- ⏱️ Processing: 0.2-5 seconds per image

### Without Dependencies (Fallback):
- ⚠️ Basic image analysis
- ⚠️ Simple property detection
- ⚠️ Lower accuracy
- ⚠️ No AI features
- ⏱️ Processing: < 1 second

---

## Quick Commands Reference

```bash
# Install (CPU)
pip install torch torchvision transformers pillow opencv-python numpy

# Install (GPU - CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install transformers pillow opencv-python numpy

# Test
python backend/machine_learning/dinov2_processor.py

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Uninstall (if needed)
pip uninstall torch torchvision transformers

# Check versions
pip show torch transformers
```

---

## Installation Time Estimates

- **Fast Internet (50+ Mbps)**: 5-10 minutes
- **Medium Internet (10-50 Mbps)**: 15-30 minutes
- **Slow Internet (< 10 Mbps)**: 30-60 minutes

---

## Alternative: Docker Installation

```dockerfile
# Add to Dockerfile
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install transformers pillow opencv-python numpy
```

---

**Last Updated**: October 29, 2025  
**Status**: Ready for installation  
**Support**: Check DINOV2_INTEGRATION_GUIDE.md for details
