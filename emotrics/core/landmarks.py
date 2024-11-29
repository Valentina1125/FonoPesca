"""
This module is a modified version of Emotrics
Original Emotrics repository: https://github.com/dguari1/Emotrics
Authors of original code: Diego L.Guarin -- diego_guarin at meei.harvard.edu

Modified for FacialTherapyGame to provide metrics to the game
"""

from dlib import get_frontal_face_detector, shape_predictor, rectangle
import cv2
import os
import numpy as np

class GetLandmarks:
    def __init__(self, image, ModelName):
        self._image = image
        self._ModelName = ModelName
        self._shape = np.zeros((68,2), dtype=int)
        self._lefteye = [-1,-1,-1]
        self._righteye = [-1,-1,-1]
        self._boundingbox = [-1,-1,-1,-1]

    def getlandmarks(self):
        detector = get_frontal_face_detector()
        
        # Asume que el modelo está en una ubicación específica
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'assets', 'models', 
                                'shape_predictor_68_face_landmarks.dat')
        
        predictor = shape_predictor(model_path)
        
        image = self._image.copy()
        height, width, d = image.shape
        
        if d > 1:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
        newWidth = 200
        ScalingFactor = width/newWidth
        newHeight = int(height/ScalingFactor)
        smallImage = cv2.resize(gray, (newWidth, newHeight), interpolation=cv2.INTER_AREA)

        rects = detector(smallImage, 1)
        
        if len(rects) == 0:
            rects = detector(gray, 1)
            
        if len(rects) == 1:
            for (i, rect) in enumerate(rects):
                mod_rect = rectangle(
                    left=int(rect.left() * ScalingFactor),
                    top=int(rect.top() * ScalingFactor),
                    right=int(rect.right() * ScalingFactor),
                    bottom=int(rect.bottom() * ScalingFactor))
                
                shape_dlib = predictor(image, mod_rect)
                
                for k in range(0,68):
                    self._shape[k] = (shape_dlib.part(k).x, shape_dlib.part(k).y)
                    if self._shape[k,0] <= 0: self._shape[k,0] = 1
                    if self._shape[k,1] <= 0: self._shape[k,1] = 1
                    
                self._boundingbox = [
                    int(rect.left() * ScalingFactor),
                    int(rect.top() * ScalingFactor),
                    int(rect.right() * ScalingFactor) - int(rect.left() * ScalingFactor),
                    int(rect.bottom() * ScalingFactor) - int(rect.top() * ScalingFactor)
                ]
                
            self.get_iris()

    def get_iris(self):
        # Procesamiento del ojo izquierdo
        x_left = self._shape[42,0]
        w_left = (self._shape[45,0]-x_left)
        y_left = min(self._shape[43,1],self._shape[44,1])
        h_left = (max(self._shape[46,1],self._shape[47,1])-y_left)
        Eye = self._image.copy()
        Eye = Eye[(y_left-5):(y_left+h_left+5),(x_left-5):(x_left+w_left+5)]
        
        selected_circle_left = self.process_eye(Eye)
        selected_circle_left[0] = int(selected_circle_left[0])+x_left-5
        selected_circle_left[1] = int(selected_circle_left[1])+y_left-5
        selected_circle_left[2] = int(selected_circle_left[2])
        
        self._lefteye = selected_circle_left
        
        # Procesamiento del ojo derecho
        x_right = self._shape[36,0]
        w_right = (self._shape[39,0]-x_right)
        y_right = min(self._shape[37,1],self._shape[38,1])
        h_right = (max(self._shape[41,1],self._shape[40,1])-y_right)
        Eye = self._image.copy()
        Eye = Eye[(y_right-5):(y_right+h_right+5),(x_right-5):(x_right+w_right+5)]
        
        selected_circle_right = self.process_eye(Eye)
        selected_circle_right[0] = int(selected_circle_right[0])+x_right-5
        selected_circle_right[1] = int(selected_circle_right[1])+y_right-5
        selected_circle_right[2] = int(selected_circle_right[2])
        
        self._righteye = selected_circle_right

    def process_eye(self, InputImage):
        h_eye, w_eye, d_eye = InputImage.shape
        
        if d_eye < 3:
            return [-1,-1,-1]
            
        if w_eye/h_eye > 3.2:
            return [int(w_eye/2), int(h_eye/2), int(w_eye/4)]
        
        InputImage = np.array(InputImage*0.75+0, dtype=InputImage.dtype)
        b,g,r = cv2.split(InputImage)
        bg = cv2.add(b,g)
        bg = cv2.GaussianBlur(bg,(3,3),0)
        
        Rmin = int(w_eye/5.5)
        Rmax = int(w_eye/3.5)
        radius = range(Rmin,Rmax+1)
        
        result_value = np.zeros(bg.shape, dtype=float)
        result_index_ratio = np.zeros(bg.shape, dtype=bg.dtype)
        mask = np.zeros(bg.shape, dtype=bg.dtype)
        
        possible_x = range(Rmin,w_eye-Rmin)
        possible_y = range(0,h_eye)
        
        for x in possible_x:
            for y in possible_y:
                intensity = []
                for r in radius:
                    if y >= int(h_eye/2):
                        temp_mask = mask.copy()
                        cv2.ellipse(temp_mask, (x,y), (r,r), 0, -35, 0, (255,255,255),1)
                        cv2.ellipse(temp_mask, (x,y), (r,r), 0, 180, 215, (255,255,255),1)
                        processed = cv2.bitwise_and(bg,temp_mask)
                        intensity.append(cv2.sumElems(processed)[0]/(2*3.141516*r))
                    else:
                        temp_mask = mask.copy()
                        cv2.ellipse(temp_mask, (x,y), (r,r), 0, 0, 35, (255,255,255),1)
                        cv2.ellipse(temp_mask, (x,y), (r,r), 0, 145, 180, (255,255,255),1)
                        processed = cv2.bitwise_and(bg,temp_mask)
                        intensity.append(cv2.sumElems(processed)[0]/(2*3.141516*r))
                
                diff_vector = np.diff(intensity)
                max_value = max(diff_vector)
                max_index = [i for i, j in enumerate(diff_vector) if j == max_value]
                result_value[y,x] = max_value
                result_index_ratio[y,x] = max_index[0]
        
        result_value = cv2.GaussianBlur(result_value,(7,7),0)
        matrix = result_value
        needle = np.max(matrix)
        matrix_dim = w_eye
        item_index = 0
        
        for row in matrix:
            for i in row:
                if i == needle:
                    break
                item_index += 1
            if i == needle:
                break
        
        c_y_det = int(item_index / matrix_dim)
        c_x_det = item_index % matrix_dim
        r_det = radius[result_index_ratio[c_y_det,c_x_det]]
        
        return [c_x_det,c_y_det,r_det]
