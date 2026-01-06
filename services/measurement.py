import cv2
import numpy as np

def calculate_foot_length(paper_contour, foot_contour):
    """
    Calculates foot length in cm using A4 paper as a reference.
    A4 Paper: 21.0 x 29.7 cm
    We use the longer side (29.7 cm) for ratio calculation if paper is portrait, 
    but usually we just need the pixels-to-cm ratio.
    """
    
    # Get the bounding box of the paper to find its longest side in pixels
    rect = cv2.minAreaRect(paper_contour)
    (x, y), (w, h), angle = rect
    
    # A4 is 29.7cm (long) x 21.0cm (short)
    pixel_long_side = max(w, h)
    cm_long_side = 29.7
    
    pixels_per_cm = pixel_long_side / cm_long_side
    
    # Get the foot's length in pixels (the longest dimension of the foot contour)
    foot_rect = cv2.minAreaRect(foot_contour)
    (fx, fy), (fw, fh), fangle = foot_rect
    foot_pixel_length = max(fw, fh)
    
    foot_cm = foot_pixel_length / pixels_per_cm
    
    return round(foot_cm, 1)
