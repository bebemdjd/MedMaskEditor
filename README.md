# Mask Correction Tool

A Python-based GUI application for medical image mask correction and annotation. This tool allows users to load original images and their corresponding masks, and provides intuitive editing capabilities to refine mask boundaries for better accuracy in medical image analysis.


# MedMaskEditor - Medical Image Mask Correction Tool

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

<img width="2001" height="1063" alt="image" src="https://github.com/user-attachments/assets/343c3f9c-b03f-4808-af1e-bd0c07657588" />



> **A professional, intuitive GUI application designed for medical image segmentation mask refinement and annotation workflows.**

MedMaskEditor bridges the gap between automated segmentation algorithms and clinical precision requirements. Whether you're a researcher refining AI-generated masks, a clinician annotating medical images, or a data scientist preparing training datasets, this tool provides the precision and efficiency you need.

## 🎯 Why MedMaskEditor?

In medical image analysis, accurate segmentation masks are crucial for diagnosis, treatment planning, and research. However, automated segmentation often requires manual refinement to meet clinical standards. MedMaskEditor was specifically designed to make this process:

- **Efficient**: Navigate through hundreds of images with keyboard shortcuts and batch processing
- **Precise**: Pixel-perfect editing with adjustable brush sizes and real-time visual feedback
- **User-friendly**: Intuitive interface that doesn't require technical expertise
- **Reliable**: Handles large datasets with robust file management and auto-save functionality

## ✨ Key Highlights

🖼️ **Triple-Panel Visualization**: Simultaneous view of original image, editable mask, and overlay preview  
🎨 **Professional Editing Tools**: Variable brush sizes, add/erase modes, and one-click mask reset  
⚡ **Real-time Feedback**: Instant visual updates with colored overlays and contour highlighting  
📁 **Smart File Management**: Automatic image-mask pairing with support for various formats  
🌐 **Unicode Support**: Full compatibility with international file paths and names  
🔄 **Workflow Optimization**: Auto-save, batch navigation, and progress tracking  




## Features

- **Dual Image Display**: Side-by-side view of original images and masks
- **Interactive Mask Editing**: Draw and erase mask regions with adjustable brush sizes
- **Overlay Visualization**: Real-time overlay of masks on original images with adjustable transparency
- **Batch Processing**: Navigate through multiple images and masks efficiently
- **Auto-save Functionality**: Automatic saving of modifications during editing
- **Jump Navigation**: Quick access to any image in the dataset
- **File Format Support**: Supports common image formats (JPG, PNG, BMP, TIFF)
- **Chinese Path Support**: Handles file paths with Chinese characters
- **Real-time Logging**: System log display for operation tracking

## Screenshot

The application features a three-panel layout:
- **Left Panel**: Original medical image
- **Center Panel**: Editable mask (black/white)
- **Right Panel**: Overlay visualization with colored mask and contours
- **Right Sidebar**: System logs and operation feedback

## Requirements

- Python 3.6+
- Required packages:
  ```
  tkinter (usually included with Python)
  opencv-python
  pillow
  numpy
  ```

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install opencv-python pillow numpy
   ```
3. Run the application:
   ```bash
   python correct_mask_gui.py
   ```

## Usage

### Basic Workflow

1. **Load Images**: Click "选择图像文件夹" (Select Image Folder) to load original images
2. **Load Masks**: Click "选择Mask文件夹" (Select Mask Folder) to load corresponding masks
3. **Navigate**: Use "上一张"/"下一张" (Previous/Next) buttons or jump directly to specific images
4. **Edit Masks**: 
   - Select brush size using the slider
   - Choose "添加" (Add) or "擦除" (Erase) mode
   - Draw directly on the center mask panel
5. **Save**: Click "保存修改" (Save Changes) or enable "自动保存" (Auto-save)

### Advanced Features

- **Transparency Control**: Adjust overlay transparency to better visualize mask boundaries
- **Mask Reset**: Clear current mask with "重置Mask" (Reset Mask) button
- **Jump Navigation**: Enter image number in the jump field for quick access
- **Real-time Preview**: Overlay panel shows immediate feedback with colored masks and green contours

## File Organization

The application expects the following structure:
```
Project/
├── images/          # Original medical images
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
└── masks/           # Corresponding mask images
    ├── image1.png
    ├── image2.png
    └── ...
```

**Note**: Image and mask files should have matching names (excluding extensions).

## Building Executable

To create a standalone executable file:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --onefile --windowed --name=MaskCorrector correct_mask_gui.py
   ```

3. The executable will be created in the `dist/` folder

## Technical Details

### Key Components

- **Safe Image Reading**: Handles Chinese file paths using numpy buffer reading
- **Real-time Mask Editing**: Coordinate transformation for accurate pixel-level editing
- **Memory Efficient**: Only loads current image/mask pair
- **Cross-platform**: Works on Windows, macOS, and Linux

### Supported Formats

- **Input**: JPG, JPEG, PNG, BMP, TIFF
- **Output**: PNG (recommended for masks)

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source. Please check the license file for details.

## Use Cases

This tool is particularly useful for:
- Medical image annotation and correction
- Computer vision dataset preparation
- Manual refinement of automated segmentation results
- Quality control in medical imaging workflows
- Research in medical image analysis

## Support

For technical support or feature requests, please create an issue in the repository.

---

**Note**: This tool is designed for research and educational purposes. For clinical applications, please ensure proper validation and compliance with relevant medical standards.


