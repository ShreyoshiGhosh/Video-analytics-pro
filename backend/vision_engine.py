import cv2
import torch
import numpy as np
import sys #we are importing sys becuase we are imporing a ton shit of libraries and python modules from python
#also we needs expand our sys search area cuz python is dumb and doesnt know when we are importing something
#from YOLO and DeepSort which are local files and not installed libraries
import time
import psutil
from pathlib import Path
from .shared_state import SmokeStatus
from .dcp import apply_dcp_stream

# 1. Define where we are
FILE = Path(__file__).resolve() #resolve absolute path because python is dumb and cant figire out relative paths
ROOT = FILE.parents[1]  # The project root (Video-Analytics-Pro)
BACKEND_ROOT = FILE.parents[0] # The backend folder

if str(ROOT) not in sys.path: #since yolo is a local folder not an installed lbrary everytime we try  to import functioanlities from it we fai
    sys.path.append(str(ROOT))#hence we need to append this folders into pythons search reas so then when python
if str(BACKEND_ROOT) not in sys.path: #searched for libraries and imports it also looks into these folders
    sys.path.append(str(BACKEND_ROOT))
if str(BACKEND_ROOT / 'yolov5') not in sys.path:
    sys.path.append(str(BACKEND_ROOT / 'yolov5'))

# --- PYTORCH 2.6+ FIX ---
import functools
_old_load = torch.load    ##k so this is used to store the model in cpu kinda givinf it a headstart and why do we do this becase yolo is heavy instead of calling functions and weights and othehr stuff every time we need to do something why not have the thinfs handy in cpu registers , basically pickle on steroids
@functools.wraps(_old_load) ## cascading file calls doesnt work here because A) can you image 7 million littele imports being called everytime a neuron is fired yall would eed a supercomputer for that shit and B) even if yall did it would cause infinite recursion and C) even if it ddidnt python would die of memory leaks and D) IT'S JUST FUCKING INEFFICIENT BRO
def _new_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _old_load(*args, **kwargs)
torch.load = _new_load
# ------------------------

# YOLOv5 Imports (assuming yolov5 folder is in sys.path)
from models.common import DetectMultiBackend
from utils.general import check_img_size, non_max_suppression, scale_coords #non_max_supression is an important module because it selects the best bounding boxes from all the predicted bounding boxes , scale cords again is used to scale the bounding boxes to the original image size
from utils.torch_utils import select_device ##use cuda if available protip you gotta install a special version of pytorch if you have gpu in your system or it installs the cpu version only and btw cuda only works with nvidia gpus
from utils.augmentations import letterbox #we are feeding small images into yolo but in dashboard the iages get stretched out this moule helps maintain that aspect ratio

# DeepSORT Imports
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort
from graphs import bbox_rel, draw_boxes

class VisionEngine:
    def __init__(self, weights='yolov5s.pt'): #this funciton is basically torch in action its loading all teh models to the cpu
        # Fix for PyTorch 2.6+ "weights_only" security error
        try:
            import numpy as np
            torch.serialization.add_safe_globals([np.core.multiarray._reconstruct, np.ndarray, np.dtype, np.core.multiarray.scalar])
        except Exception as e:
            print(f"[DEBUG] Torch safety config skipped: {e}")

        print(f"[DEBUG] Initializing VisionEngine with weights: {weights}")
        self.source = 0
        self.device = select_device('cuda') if torch.cuda.is_available() else select_device('cpu')
        
        # Load YOLO model
        print("[DEBUG] Loading YOLOv5 Model...")
        self.model = DetectMultiBackend(weights, device=self.device)
        self.imgsz = check_img_size((640, 640), s=self.model.stride)
        self.half = self.device.type != 'cpu'
        if self.half:
            self.model.model.half()
        print("[DEBUG] YOLOv5 Loaded Successfully.")

        # Load DeepSORT
        print("[DEBUG] Loading DeepSORT...")
        cfg = get_config()
        cfg_path = BACKEND_ROOT / "deep_sort_pytorch/configs/deep_sort.yaml"
        cfg.merge_from_file(str(cfg_path))
        
        self.deepsort = DeepSort(
            str(BACKEND_ROOT / cfg.DEEPSORT.REID_CKPT),
            max_dist=cfg.DEEPSORT.MAX_DIST,
            min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
            nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP,
            max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
            max_age=cfg.DEEPSORT.MAX_AGE,
            n_init=cfg.DEEPSORT.N_INIT,
            nn_budget=cfg.DEEPSORT.NN_BUDGET,
            use_cuda=torch.cuda.is_available()
        )
        print("[DEBUG] DeepSORT Loaded Successfully.")

    def get_video_stream(self, source=0):#this is the main loop that keeps running and keeps the backend alive as long as this runs the app runs
        print(f"[DEBUG] Starting Video Stream with source: {source}")#source is by default 0 that points to webcam unless specified byuer
        SmokeStatus.current_source = source #shared state so that the frontend can update it basically reaact can change states
        self.source = source #assign the source to self source
        cap = cv2.VideoCapture(self.source)#a smartthings capable of handling itself through source it adapts
        
        if not cap.isOpened():
            print(f"[ERROR] Could not open video source: {self.source}")
        
        while True: #this loop runs infinite times unless we break it  basically
            # HOT SWAP- if in between the inference we change the source we need to update that shit in the backend heres how it works
            if str(self.source) != str(SmokeStatus.current_source): #this keeps checking periodically if the self source and the currenct_source are same if not we set the self source to this new current souce
                print(f"[DEBUG] Source change detected: {self.source} -> {SmokeStatus.current_source}")
                self.source = SmokeStatus.current_source
                cap.release() #cap object from opencv is currently assigned with the old sorce if we gotta update it bitch needs to let the old shit go.
                cap = cv2.VideoCapture(self.source)#new source assigned
                if not cap.isOpened(): #checks if the object is even running open cv is written in C++ who knew sike!
                    print(f"[ERROR] Failed to switch to source: {self.source}")

            t_start = time.perf_counter()
            success, frame = cap.read()# if cap.read returns an image then success is set as true and frame gets the pixels elsesuccess if false frame gets no pixels
            
            if not success: # this is specifically for the local video,,,, when the local video ends the system stops to prevent that we restart with the video, 
                if isinstance(self.source, str): #this checks if the source is a string(local video) or not  if self.source is 0 it returns false
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                time.sleep(0.1) # Prevent CPU pegging if source fails
                continue

            # ADAPTIVE DCP
            is_file = isinstance(self.source, str)
            if is_file or SmokeStatus.is_smoke_detected:#dcp only applied conditionally in webcam that is when smoke is detected otherwise in case of localvide and rstp dcp runs by default>
                frame = apply_dcp_stream(frame)

            # AI TRACKING
            if SmokeStatus.is_tracking:
                img = letterbox(frame, self.imgsz, stride=self.model.stride, auto=True)[0] #its important to resize images in the size yolo preefers thats 640x640 in our case for yolo5s hence letterbox maintains that ratio by ading grey pading to top and bottom
                img = img.transpose((2, 0, 1))[::-1] #images comming from open cv are in format height x width x color but yolo accepts color X height X width so we transpose it
                img = np.ascontiguousarray(img)
                img = torch.from_numpy(img).to(self.device) #converting numpy array to a pytorch tensor, shit tensor is 4d
                img = img.half() if self.half else img.float()
                img /= 255.0 #scale pixels in range 0 to 1
                if len(img.shape) == 3: img = img[None]
                
                pred = self.model(img, augment=False, visualize=False)
                pred = non_max_suppression(pred, conf_thres=SmokeStatus.conf_thres, iou_thres=0.45) #this removes unwanted bounding boxes also its taking smokestatus.con_thres as input because we set out custom confidence scores in the frontend which is that shared globally

                current_humans = 0 #set the human count 0 for every frame
                for i, det in enumerate(pred): #any detections are stored in det so we iterate through it and extract the cooordinates and confidences and class 
                    if len(det):#if len det is 0 there is no detection , if its not zero however we extract coordinates and confidences and class
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round() #again yolo peformed detectin in that 640*640 tiny image we have to scale it up to fit the origina dimensions
                        bbox_xywh = []
                        confs = [] #deepsort is a weird program that accepts only these parameters in the form of configs which is generally array of shape(1,1,4) 
                        for *xyxy, conf, cls in det: #here xyxy is actually the coordinates of the best bounding box that  yolo predicts for out confidence score
                            if int(cls) == 0: current_humans += 1 #in yolo class 0 is human so if we find class 0 in yolo we call current_human as the number of humans and add one to it
                            x_c, y_c, bbox_w, bbox_h = bbox_rel(*xyxy) #config stuff needed for deepsort to work
                            bbox_xywh.append([x_c, y_c, bbox_w, bbox_h]) #we append the coordiate dimensions in forrm of array of size 4
                            confs.append([conf.item()]) # the we append these coordinates and confidenses in deepsorts configs format and we are readyto pass it on as deepsorts argumane
                        
                        outputs = self.deepsort.update(torch.Tensor(bbox_xywh), torch.Tensor(confs), frame)
                        if len(outputs) > 0:
                            draw_boxes(frame, outputs[:, :4], outputs[:, -1])
                    else:
                        self.deepsort.increment_ages() #runs if yolo found nothing in the image
                
                SmokeStatus.human_count = current_humans #updates the global state when the number of humans change 

            # SYSTEM STATS
            t_end = time.perf_counter()
            duration = t_end - t_start
            SmokeStatus.fps = round(1.0 / duration, 1) if duration > 0 else 0
            SmokeStatus.cpu_usage = psutil.cpu_percent()
            SmokeStatus.memory_usage = psutil.virtual_memory().percent

            # ENCODE & YIELD
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
