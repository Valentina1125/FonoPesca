class RangeMotion:
    
    def __init__(self):
        self.max_spread_range_metrics = {
            'CE_right': 0,
            'CE_left': 0,
            'SA_right': 0,
            'SA_left': 0,
            'DS_right': 0,
            'DS_left': 0,
            'CH_dev': 0,    # Agregado
            'CE_dev': 0,    # Agregado
            'SA_dev': 0,    # Agregado
            'CE_dev_p': 0,  # Agregado
            'SA_dev_p': 0   # Agregado
        }

        self.max_open_range_metrics = {
            'DS_right': 0,
            'DS_left': 0,
            'UVH_dev': 0,
            'LVH_dev': 0,
            'CH_dev': 0,
            'DS_dev': 0,    # Agregado
            'DS_dev_p': 0,  # Agregado
            'openness': 0
        }

        self.max_kiss_range_metrics = {
            'CE_right': 0,
            'CE_left': 0,
            'CH_dev': 0,    # Agregado
            'CE_dev': 0,    # Agregado
            'UVH_dev': 0,   # Agregado
            'LVH_dev': 0,   # Agregado
            'CE_dev_p': 0   # Agregado
        }


    
    def calculate_brow_max(self, frame_metrics):
        for key, max_value in self.max_brow_range_metrics.items():
            new_value = frame_metrics[key]
            if new_value > max_value:
                self.max_brow_range_metrics[key] = new_value

    def calculate_spread_max(self, frame_metrics):
        """
        Actualiza las métricas máximas de sonrisa.
        """
        for key in ['CE_right', 'CE_left', 'SA_right', 'SA_left', 'DS_right', 'DS_left',
                    'CH_dev', 'CE_dev', 'SA_dev', 'CE_dev_p', 'SA_dev_p']:
            if key in frame_metrics:
                new_value = frame_metrics[key]
                if new_value > self.max_spread_range_metrics[key]:
                    self.max_spread_range_metrics[key] = new_value

    def calculate_open_max(self, frame_metrics):
        """
        Actualiza las métricas máximas de apertura bucal.
        """
        for key in ['DS_right', 'DS_left', 'UVH_dev', 'LVH_dev', 'CH_dev', 
                    'DS_dev', 'DS_dev_p']:
            if key in frame_metrics:
                new_value = frame_metrics[key]
                if new_value > self.max_open_range_metrics[key]:
                    self.max_open_range_metrics[key] = new_value

        # Calcular apertura total
        total_opening = (frame_metrics.get('UVH_dev', 0) + 
                        frame_metrics.get('LVH_dev', 0))
        
        if total_opening > self.max_open_range_metrics['openness']:
            self.max_open_range_metrics['openness'] = total_opening

    def calculate_kiss_min(self, frame_metrics):
        """
        Actualiza las métricas mínimas de protrusión labial.
        """
        for key in ['CE_right', 'CE_left', 'CH_dev', 'CE_dev', 
                    'UVH_dev', 'LVH_dev', 'CE_dev_p']:
            if key in frame_metrics:
                new_value = frame_metrics[key]
                if new_value < self.max_kiss_range_metrics[key]:
                    self.max_kiss_range_metrics[key] = new_value

    
        
    def calculate_bsmile_max(self, frame_metrics):
        for key, max_value in self.max_bsmile_range_metrics.items():
            new_value = frame_metrics[key]
            if new_value > max_value:
                self.max_bsmile_range_metrics[key] = new_value

    
    def get_normalized_metrics(self):
        """
        Retorna métricas normalizadas respecto a sus máximos.
        """
        normalized = {}
        for gesture_type, metrics in self.__dict__.items():
            if gesture_type.startswith('max_'):
                normalized[gesture_type] = {}
                max_val = max(metrics.values()) if metrics.values() else 1
                for key, value in metrics.items():
                    normalized[gesture_type][key] = value / max_val if max_val > 0 else 0
        return normalized