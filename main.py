from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.image_processing import process_image
from services.measurement import calculate_foot_length
from services.size_converter import cm_to_shoe_size

app = FastAPI(title="Foot Size Measurement API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/measure-foot")
async def measure_foot(file: UploadFile = File(...)):
    # 1. Validate image format
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are supported.")

    try:
        image_bytes = await file.read()
        
        # 2. Image Processing
        paper_cnt, foot_cnt, error = process_image(image_bytes)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
            
        # 3. Measurement
        foot_length_cm = calculate_foot_length(paper_cnt, foot_cnt)
        
        # 4. Size Conversion
        shoe_sizes = cm_to_shoe_size(foot_length_cm)
        
        return {
            "foot_length_cm": foot_length_cm,
            "shoe_sizes": shoe_sizes
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during image processing.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
