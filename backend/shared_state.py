import psutil

class SmokeStatus:
    is_smoke_detected = False
    smoke_level = 0.0
    
    # NEW METRICS
    human_count = 0
    total_detections = 0
    fps = 0.0
    min_fps = 999.0
    max_fps = 0.0
    
    cpu_usage = 0.0
    memory_usage = 0.0
    gpu_memory_usage = 0.0
    
    # CONFIGURATION
    conf_thres = 0.25
    is_tracking = False
    
    # DYNAMIC SOURCE
    current_source = 0 # This will be the "Live" source