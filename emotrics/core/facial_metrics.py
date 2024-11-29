import cv2
import numpy as np
from emotrics.core.frame_analysis import FrameSymmetry
from emotrics.core.video_range_of_motion import RangeMotion

class FacialMetricsAnalyzer:
    def __init__(self):
        self.symmetry_analyzer = FrameSymmetry()
        self.motion_analyzer = RangeMotion()
        
    def get_symmetry_metrics(self, image):
        """
        Analiza una imagen y devuelve las métricas de simetría facial.
        
        Args:
            image: Imagen en formato OpenCV/numpy array
            
        Returns:
            dict: Diccionario con todas las métricas de simetría
            None: Si no se detectaron landmarks
        """
        try:
            self.symmetry_analyzer.load_image(image)
            metrics = self.symmetry_analyzer.calculate_metrics()
            return metrics
        except Exception as e:
            print(f"Error al analizar simetría: {str(e)}")
            return None

    def get_motion_metrics(self, image, gesture_type):
        """
        Analiza una imagen y actualiza las métricas de rango de movimiento para un gesto específico.
        
        Args:
            image: Imagen en formato OpenCV/numpy array
            gesture_type: str - Tipo de gesto ('spread', 'brow', 'open', 'bsmile', 'kiss')
            
        Returns:
            dict: Métricas actualizadas para el gesto específico
            None: Si no se detectaron landmarks o el gesto no es válido
        """
        try:
            # Validar tipo de gesto
            valid_gestures = ['spread', 'brow', 'open', 'bsmile', 'kiss']
            if gesture_type not in valid_gestures:
                raise ValueError(f"Gesto no válido. Debe ser uno de: {valid_gestures}")

            # Obtener métricas de simetría del frame
            frame_metrics = self.get_symmetry_metrics(image)
            if frame_metrics is None:
                return None

            # Actualizar y obtener métricas específicas del gesto
            gesture_metrics = self._update_gesture_metrics(frame_metrics, gesture_type)
            return gesture_metrics
        except Exception as e:
            print(f"Error al analizar movimiento: {str(e)}")
            return None

    def _update_gesture_metrics(self, frame_metrics, gesture_type):
        """
        Actualiza y devuelve las métricas específicas para cada tipo de gesto.
        """
        gesture_methods = {
            'spread': self.motion_analyzer.calculate_spread_max,
            'brow': self.motion_analyzer.calculate_brow_max,
            'open': self.motion_analyzer.calculate_open_max,
            'bsmile': self.motion_analyzer.calculate_bsmile_max,
            'kiss': self.motion_analyzer.calculate_kiss_min
        }
        
        gesture_metrics = {
            'spread': self.motion_analyzer.max_spread_range_metrics,
            'brow': self.motion_analyzer.max_brow_range_metrics,
            'open': self.motion_analyzer.max_open_range_metrics,
            'bsmile': self.motion_analyzer.max_bsmile_range_metrics,
            'kiss': self.motion_analyzer.max_kiss_range_metrics
        }

        # Actualizar métricas para el gesto específico
        gesture_methods[gesture_type](frame_metrics)
        
        # Devolver métricas actualizadas
        return gesture_metrics[gesture_type]

    def reset_motion_metrics(self):
        """
        Reinicia todas las métricas de rango de movimiento.
        """
        self.motion_analyzer = RangeMotion()