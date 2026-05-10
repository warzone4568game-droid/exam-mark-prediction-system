import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import os

class OCRHandler:
    def __init__(self):
        """Initialize OCR Handler"""
        # Configure Tesseract path for Windows
        if os.name == 'nt':
            # Common installation paths for Tesseract on Windows
            username = os.environ.get('USERNAME') or os.environ.get('USER') or 'User'
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tesseract-OCR', 'tesseract.exe'),
                r'C:\Users\\' + username + r'\AppData\Local\Tesseract-OCR\tesseract.exe',
                r'tesseract.exe' # If in PATH
            ]
            
            found = False
            for path in tesseract_paths:
                if path and os.path.exists(path):
                    pytesseract.pytesseract.pytesseract_cmd = path
                    print(f"Tesseract found at: {path}")
                    found = True
                    break
            
            if not found:
                print("WARNING: Tesseract OCR not found in common locations. OCR features may not work.")
                print("Please install Tesseract OCR or add it to your PATH.")

    
    def extract_text(self, image_path):
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Extracted text string
        """
        try:
            # Read image
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text
            extracted_text = pytesseract.image_to_string(image)
            
            return extracted_text
        
        except Exception as e:
            print(f"Error in OCR extraction: {str(e)}")
            return ""
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
        
        Returns:
            Preprocessed PIL Image object
        """
        try:
            # Convert PIL image to RGB if it's not (important for grayscale/alpha images)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Convert to numpy array for OpenCV processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Resize image for better OCR
            scale = 3
            width = int(denoised.shape[1] * scale)
            height = int(denoised.shape[0] * scale)
            resized = cv2.resize(denoised, (width, height), interpolation=cv2.INTER_CUBIC)
            
            # Convert back to PIL Image
            result = Image.fromarray(resized)
            
            return result
        
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return image
    
    def parse_marks(self, extracted_text):
        """
        Parse CGPA/marks from extracted text using regex
        
        Args:
            extracted_text: Text extracted from image
        
        Returns:
            Dictionary with parsed results
        """
        parsed_marks = {
            'total_marks': 10,  # Default CGPA scale
            'obtained_marks': None,
            'percentage': None,
            'grade': None,
            'raw_text': extracted_text[:200]
        }
        
        try:
            # Search for patterns like "CGPA: 8.5", "GPA 9.0/10", etc.
            cgpa_pattern = r'(?:CGPA|GPA)\s*:?\s*(\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?'
            cgpa_match = re.search(cgpa_pattern, extracted_text, re.IGNORECASE)
            
            if cgpa_match:
                parsed_marks['obtained_marks'] = float(cgpa_match.group(1))
                if cgpa_match.group(2):
                    parsed_marks['total_marks'] = float(cgpa_match.group(2))
                
                # Assign grade based on 10-point scale
                if parsed_marks['obtained_marks'] >= 9.0: parsed_marks['grade'] = 'A+'
                elif parsed_marks['obtained_marks'] >= 8.0: parsed_marks['grade'] = 'A'
                elif parsed_marks['obtained_marks'] >= 7.0: parsed_marks['grade'] = 'B'
                elif parsed_marks['obtained_marks'] >= 6.0: parsed_marks['grade'] = 'C'
                elif parsed_marks['obtained_marks'] >= 5.0: parsed_marks['grade'] = 'D'
                else: parsed_marks['grade'] = 'F'
            
            # Fallback to standard marks pattern if no CGPA found
            if not parsed_marks['obtained_marks']:
                obtained_pattern = r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+)'
                obtained_match = re.search(obtained_pattern, extracted_text)
                
                if obtained_match:
                    val = float(obtained_match.group(1))
                    total = float(obtained_match.group(2))
                    
                    # If total is 100, convert to 10
                    if total == 100:
                        parsed_marks['obtained_marks'] = val / 10
                        parsed_marks['total_marks'] = 10
                    else:
                        parsed_marks['obtained_marks'] = val
                        parsed_marks['total_marks'] = total
            
        except Exception as e:
            print(f"Error in parsing marks: {str(e)}")
        
        return parsed_marks
    
    def _get_grade(self, percentage):
        """
        Get letter grade based on percentage
        
        Args:
            percentage: Percentage score
        
        Returns:
            Letter grade
        """
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
