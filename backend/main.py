from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

print("[SYSTEM] Main.py is being loaded by Uvicorn...")
from .sensor_manager import start_sensor_thread
from .shared_state import SmokeStatus
from .vision_engine import VisionEngine

UPLOAD_DIR = "backend/uploads"#creates a folder uploads in the backend folder so that if there isa video uploaded it gets stored here temporarily
os.makedirs(UPLOAD_DIR, exist_ok=True)#ensures the folder exists before the app starts otherwise it throws an error

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WE LOAD THE ENGINE HERE
engine = None

@app.on_event("startup") #listen to the shared state "startup " and when the set of of yolo is inititalized tthis function satarts as well
async def startup_event(): #
    global engine#gets the global state of yolov5
    print("[SERVER] Starting Up...")#
    WEIGHTS_PATH = os.path.join(os.getcwd(), 'backend', 'yolov5', 'yolov5s.pt')#gets the weights manually from the path yolo is being loaded
    engine = VisionEngine(weights=WEIGHTS_PATH)#loads the backend engine and passes them weights
    start_sensor_thread()#starts the daemon thread
    print("[SERVER] System Ready.")

@app.get("/status")
async def get_status():
    return {
        "is_smoke_detected": SmokeStatus.is_smoke_detected,
        "smoke_level": round(SmokeStatus.smoke_level, 1),
        "human_count": SmokeStatus.human_count,
        "total_detections": SmokeStatus.total_detections,
        "fps": SmokeStatus.fps,
        "min_fps": round(SmokeStatus.min_fps, 1) if SmokeStatus.min_fps < 900 else 0,
        "max_fps": round(SmokeStatus.max_fps, 1),
        "cpu_usage": SmokeStatus.cpu_usage,
        "memory_usage": SmokeStatus.memory_usage,
        "emergency_mode": SmokeStatus.smoke_level > 90
    }

@app.post("/configure")
async def configure_system(data: dict):
    if 'source' in data:
        SmokeStatus.current_source = data['source']
    if 'conf_thres' in data:
        SmokeStatus.conf_thres = data['conf_thres']
    if 'is_tracking' in data:
        SmokeStatus.is_tracking = data['is_tracking']
    return {"status": "System Reconfigured"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    SmokeStatus.current_source = file_path
    return {"message": "Processing uploaded video", "filename": file.filename}

@app.get("/video_feed")
def video_feed():
    if engine is None:
        return {"error": "Engine not initialized"}
    return StreamingResponse(
        engine.get_video_stream(source=SmokeStatus.current_source), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
