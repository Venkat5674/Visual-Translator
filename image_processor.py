import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

class ImageProcessor:
    """Advanced image processing capabilities for the Detector Bot"""
    
    def __init__(self):
        # Initialize MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range, 1 for full-range detection
            min_detection_confidence=0.5
        )
        
        # Initialize MediaPipe Pose Detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def detect_faces(self, image_path):
        """Detect faces in an image and return details"""
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Failed to load image"}
            
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image_rgb)
        
        faces = []
        if results.detections:
            height, width, _ = image.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                
                # Get coordinates
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)
                
                faces.append({
                    "confidence": detection.score[0],
                    "position": (x, y, w, h),
                    "landmark_nose": (
                        int(detection.location_data.relative_keypoints[0].x * width),
                        int(detection.location_data.relative_keypoints[0].y * height)
                    )
                })
                
                # Draw bounding box
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
        # Save annotated image
        annotated_path = "annotated_" + image_path.split("/")[-1]
        cv2.imwrite(annotated_path, image)
        
        return {
            "count": len(faces),
            "faces": faces,
            "annotated_image": annotated_path
        }
        
    def detect_pose(self, image_path):
        """Detect human pose in an image"""
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Failed to load image"}
            
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return {"pose_detected": False}
            
        # Draw pose landmarks on the image
        annotated_image = image.copy()
        self.mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS)
            
        # Save annotated image
        annotated_path = "pose_" + image_path.split("/")[-1]
        cv2.imwrite(annotated_path, annotated_image)
        
        # Extract key pose points
        landmarks = []
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks.append({
                "index": i,
                "x": landmark.x,
                "y": landmark.y,
                "visibility": landmark.visibility
            })
        
        return {
            "pose_detected": True,
            "landmarks_count": len(landmarks),
            "key_landmarks": landmarks[:5],  # Just return a few landmarks
            "annotated_image": annotated_path
        }
    
    def enhance_image(self, image_path, enhancement_type="sharpen"):
        """Apply various enhancements to an image"""
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Failed to load image"}
        
        enhanced_image = None
        
        if enhancement_type == "sharpen":
            # Sharpen the image
            kernel = np.array([[-1, -1, -1],
                              [-1, 9, -1],
                              [-1, -1, -1]])
            enhanced_image = cv2.filter2D(image, -1, kernel)
        
        elif enhancement_type == "brighten":
            # Increase brightness
            enhanced_image = cv2.convertScaleAbs(image, alpha=1.5, beta=30)
        
        elif enhancement_type == "grayscale":
            # Convert to grayscale
            enhanced_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Convert back to 3-channel for consistent saving
            enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2BGR)
        
        # Save enhanced image
        enhanced_path = f"{enhancement_type}_{image_path.split('/')[-1]}"
        cv2.imwrite(enhanced_path, enhanced_image)
        
        return {
            "enhancement": enhancement_type,
            "enhanced_image": enhanced_path
        }
