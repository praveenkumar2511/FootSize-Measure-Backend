import cv2
import numpy as np

def process_image(image_bytes):
    """
    Processes the image to find the A4 paper and foot contours.
    Uses HSV color filtering and convex hull for high robustness.
    Returns: (ref_paper_contour, foot_contour, error_message)
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return None, None, "Invalid image format"

    # 1. Detect WHITE Paper using HSV (White is low saturation, high value)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # White paper in typical indoor lighting
    lower_white = np.array([0, 0, 180]) 
    upper_white = np.array([180, 50, 255])
    paper_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Morphological cleaning to fill holes and remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    paper_mask = cv2.morphologyEx(paper_mask, cv2.MORPH_CLOSE, kernel)
    paper_mask = cv2.morphologyEx(paper_mask, cv2.MORPH_OPEN, kernel)

    # Find Paper Contour
    contours, _ = cv2.findContours(paper_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    paper_contour = None
    if contours:
        # Take the largest contour by area
        paper_contour = max(contours, key=cv2.contourArea)
        
    # Check if paper area is significant (at least 10% of image)
    if paper_contour is None or cv2.contourArea(paper_contour) < (image.shape[0] * image.shape[1] * 0.1):
        # Fallback to Brightness thresholding if HSV fails
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            paper_contour = max(contours, key=cv2.contourArea)

    if paper_contour is None or cv2.contourArea(paper_contour) < (image.shape[0] * image.shape[1] * 0.1):
        return None, None, "A4 Paper not detected. Ensure it's fully visible and well-lit."

    # Use Convex Hull for the paper to ignore the "dent" made by the leg/foot intrusion at the edge
    paper_contour = cv2.convexHull(paper_contour)

    # 2. Find Foot Contour
    # The foot is the largest thing INSIDE the paper that is NOT white
    # Create a mask of the paper area
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [paper_contour], -1, 255, -1)
    
    # Foot potential is what is INSIDE the paper area but NOT in the white paper_mask
    foot_potential_mask = cv2.bitwise_and(mask, cv2.bitwise_not(paper_mask))
    
    # Clean up foot mask (remove thin lines/noise)
    foot_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    foot_potential_mask = cv2.morphologyEx(foot_potential_mask, cv2.MORPH_OPEN, foot_kernel)
    
    foot_contours, _ = cv2.findContours(foot_potential_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    foot_contour = None
    if foot_contours:
        # Take the largest contour inside the paper
        foot_contour = max(foot_contours, key=cv2.contourArea)

    if foot_contour is None or cv2.contourArea(foot_contour) < 2000:
        return None, None, "Foot not detected on the paper. Place your foot clearly in the center."

    # 3. Finalize Paper corners for measurement
    # Use minAreaRect to get 4 precise corners for pixel-to-cm ratio
    rect = cv2.minAreaRect(paper_contour)
    box = cv2.boxPoints(rect)
    approx_paper = box.astype(np.int32) # Standard integer type for OpenCV points

    return approx_paper, foot_contour, None
