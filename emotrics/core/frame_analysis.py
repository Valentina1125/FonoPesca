import cv2
import numpy as np
from emotrics.core.landmarks import GetLandmarks
from emotrics.core.measurements import get_measurements_from_data


class FrameSymmetry:
    def __init__(self):
        self._file_name = None
        self._opencvimage = None
        self.landmarks = None
        self._ModelName = 'MEE'
        self._CalibrationType = 'Iris'
        self._CalibrationValue = 11.77

    def load_image(self, image):
        """Carga una imagen para análisis."""
        self._opencvimage = image
        self.getShapefromImage()

    def getShapefromImage(self):
        """Procesa la imagen para obtener los landmarks faciales."""
        h, w, d = self._opencvimage.shape

        # Escala la imagen si es demasiado grande
        self._Scale = 1
        if h > 1500 or w > 1500:
            if h >= w:
                h_n = 1500
                self._Scale = h/h_n
                w_n = int(np.round(w/self._Scale, 0))
                temp_image = cv2.resize(self._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
            else:
                w_n = 1500
                self._Scale = w/w_n
                h_n = int(np.round(h/self._Scale, 0))
                temp_image = cv2.resize(self._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
        else:
            temp_image = self._opencvimage.copy()

        # Obtiene los landmarks usando el modelo especificado
        self.landmarks = GetLandmarks(temp_image, self._ModelName)
        self.landmarks.getlandmarks()

    def calculate_metrics(self):
        """Calcula las métricas faciales si se detectaron landmarks."""
        if self.landmarks._shape is not None:
            MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual = get_measurements_from_data(
                self.landmarks._shape,
                self.landmarks._lefteye,
                self.landmarks._righteye,
                self._CalibrationType,
                self._CalibrationValue
            )
            return self.parse_frame_metrics(
                MeasurementsLeft,
                MeasurementsRight,
                MeasurementsDeviation,
                MeasurementsPercentual
            )
        return None

    def parse_frame_metrics(self, MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual):
        """Convierte las mediciones en un diccionario de métricas."""
        frame_metrics = {}

        # Medidas del lado derecho
        frame_metrics.update({
            'CE_right': MeasurementsRight.CommissureExcursion,
            'SA_right': MeasurementsRight.SmileAngle,
            'DS_right': MeasurementsRight.DentalShow,
            'MRD1_right': MeasurementsRight.MarginalReflexDistance1,
            'MRD2_right': MeasurementsRight.MarginalReflexDistance2,
            'BH_right': MeasurementsRight.BrowHeight,
            'PFH_right': MeasurementsRight.PalpebralFissureHeight
        })

        # Medidas del lado izquierdo
        frame_metrics.update({
            'CE_left': MeasurementsLeft.CommissureExcursion,
            'SA_left': MeasurementsLeft.SmileAngle,
            'DS_left': MeasurementsLeft.DentalShow,
            'MRD1_left': MeasurementsLeft.MarginalReflexDistance1,
            'MRD2_left': MeasurementsLeft.MarginalReflexDistance2,
            'BH_left': MeasurementsLeft.BrowHeight,
            'PFH_left': MeasurementsLeft.PalpebralFissureHeight
        })

        # Medidas de desviación
        frame_metrics.update({
            'CE_dev': MeasurementsDeviation.CommissureExcursion,
            'SA_dev': MeasurementsDeviation.SmileAngle,
            'MRD1_dev': MeasurementsDeviation.MarginalReflexDistance1,
            'MRD2_dev': MeasurementsDeviation.MarginalReflexDistance2,
            'BH_dev': MeasurementsDeviation.BrowHeight,
            'DS_dev': MeasurementsDeviation.DentalShow,
            'CH_dev': MeasurementsDeviation.CommisureHeightDeviation,
            'UVH_dev': MeasurementsDeviation.UpperLipHeightDeviation,
            'LVH_dev': MeasurementsDeviation.LowerLipHeightDeviation,
            'PFH_dev': MeasurementsDeviation.PalpebralFissureHeight
        })

        # Medidas porcentuales de desviación
        frame_metrics.update({
            'CE_dev_p': MeasurementsPercentual.CommissureExcursion,
            'SA_dev_p': MeasurementsPercentual.SmileAngle,
            'MRD1_dev_p': MeasurementsPercentual.MarginalReflexDistance1,
            'MRD2_dev_p': MeasurementsPercentual.MarginalReflexDistance2,
            'BH_dev_p': MeasurementsPercentual.BrowHeight,
            'DS_dev_p': MeasurementsPercentual.DentalShow,
            'PFH_dev_p': MeasurementsPercentual.PalpebralFissureHeight
        })

        return frame_metrics

    def clear(self):
        """Limpia los datos almacenados."""
        self._file_name = None
        self._opencvimage = None
        self.landmarks = None