import fitz  # PyMuPDF
import pytesseract
from pathlib import Path
from PIL import Image
import io
import base64

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []
    for page_no, page in enumerate(doc):
        text = page.get_text()
        chunks.append({
            "page": page_no + 1,
            "text": text,
            "image": None
        })
    return chunks

def extract_images_from_pdf(pdf_path, output_dir="images"):
    Path(output_dir).mkdir(exist_ok=True)
    doc = fitz.open(pdf_path)
    image_data = []
    
    for page_no, page in enumerate(doc):
        # Get page as image using PyMuPDF
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        
        # Save the page image
        image_path = f"{output_dir}/page_{page_no + 1}.png"
        with open(image_path, "wb") as f:
            f.write(img_data)
        
        # Extract text from image using OCR
        try:
            image = Image.open(io.BytesIO(img_data))
            ocr_text = pytesseract.image_to_string(image)
        except Exception as e:
            # OCR is optional - system works without it
            print(f"OCR not available for page {page_no + 1} (this is normal if Tesseract is not installed)")
            ocr_text = ""
        
        # Extract individual images from the page
        image_list = page.get_images()
        page_images = []
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Save individual image
            img_path = f"{output_dir}/page_{page_no + 1}_img_{img_index + 1}.png"
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            page_images.append(img_path)
        
        image_data.append({
            "page": page_no + 1,
            "image_path": image_path,
            "ocr_text": ocr_text,
            "extracted_images": page_images
        })
    
    doc.close()
    return image_data
