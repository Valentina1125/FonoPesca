import os
import json 
import cv2
import pygame

from emotrics.core.frame_analysis import FrameSymmetry
from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT



class CalibrationState:
    def __init__(self, display_surface, font_large=None, font_medium=None, font_small=None):
        self.display_surface = display_surface
        self.current_step = 0
        self.countdown_timer = None
        self.frame_analyzer = FrameSymmetry()
        self.metrics_results = {}
        self.font = font_large if font_large else pygame.font.SysFont("Arial", 36)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.retry_message = ""
        self.retry_timer = 0
        self.gesture = None  # Para almacenar el gesto actual
        self.review_gesture = None  # Nueva variable agregada aquí

        # Ruta para guardar la calibración
        self.calibration_file = os.path.join('game', 'data', 'calibration.json')
        
        # Crear directorio si no existe
        os.makedirs(os.path.join('game', 'data'), exist_ok=True)
        
        # Para el control de frames y visualización
        self.frame_count = 0
        self.last_landmarks_frame = None
        
        # Usar las fuentes proporcionadas o caer en fuentes por defecto
        self.font_large = font_large if font_large else pygame.font.SysFont("Arial", 36)
        self.font_medium = font_medium if font_medium else pygame.font.SysFont("Arial", 24)
        self.font_small = font_medium if font_small else pygame.font.SysFont("Arial", 12)
        
        
        # Remover la segunda asignación redundante de display_surface
        self.current_step = 0
        self.countdown_timer = None
        self.frame_analyzer = FrameSymmetry()
        self.metrics_results = {}
        # Remover las asignaciones redundantes de font y font_small que sobreescriben las personalizadas
        self.retry_message = ""
        self.retry_timer = 0
        self.gesture = None
        self.review_gesture = None
        
        # Estados posibles
        self.STATES = {
            'CALIBRATING': 'CALIBRATING',  # Esperando/procesando gestos
            'REVIEWING': 'REVIEWING'        # Mostrando resultados del intento
        }
        self.current_state = self.STATES['CALIBRATING']
        
        
        # Para el estado de revisión
        self.review_frame = None
        self.review_landmarks = None
        self.review_metrics = None
        self.button_continue = pygame.Rect(0, 0, 200, 50)
        self.button_retake = pygame.Rect(0, 0, 200, 50)
        
        # Calcular dimensiones correctas
        self.total_width = int(WINDOW_WIDTH * 1.5)
        self.half_width = self.total_width // 2
        self.camera_height = WINDOW_HEIGHT
        
        # Colores para los landmarks
        self.colors = {
            'face': (0, 255, 0),      # Verde para contorno facial
            'eyebrows': (0, 255, 255), # Cyan para cejas
            'nose': (255, 0, 0),       # Rojo para nariz
            'eyes': (255, 255, 0),     # Amarillo para ojos
            'lips': (0, 0, 255)        # Azul para labios
        }
        
        # Definir los pasos de calibración
        self.calibration_steps = [
            {
                'gesture': 'NEGATIVE',  # Añadimos el gesto de reposo primero
                'instruction': "Mantén una expresión neutral",
                'description': "Relaja tu rostro completamente"
            },
            {
                'gesture': 'NSM_SPREAD',
                'instruction': "¡Muéstrame tu mejor sonrisa!",
                'description': "Sonríe lo más amplio que puedas"
            },
            {
                'gesture': 'NSM_OPEN',
                'instruction': "¡Abre la boca lo más que puedas!",
                'description': "Como bostezando"
            },
            {
                'gesture': 'NSM_KISS',
                'instruction': "¡Haz un gesto de beso!",
                'description': "Como dando un beso"
            }
        ]

        # Agregar variables para el control de intentos
        self.attempts_per_gesture = 3
        self.current_attempt = 0
        self.current_metrics = []  # Lista para almacenar las métricas de cada intento
        
        # Modificar la estructura de metrics_results para almacenar múltiples intentos
        self.metrics_results = {
            'NEGATIVE': [],
            'NSM_SPREAD': [],
            'NSM_OPEN': [],
            'NSM_KISS': []
        }

    def save_calibration(self):
        """Guarda las métricas de calibración en un archivo JSON"""
        if not self.metrics_results:
            return False
            
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.metrics_results, f)
            return True
        except Exception as e:
            print(f"Error al guardar la calibración: {e}")
            return False

    @staticmethod
    def load_calibration():
        """Carga las métricas de calibración desde el archivo JSON"""
        calibration_file = os.path.join('game', 'data', 'calibration.json')
        try:
            if os.path.exists(calibration_file):
                with open(calibration_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error al cargar la calibración: {e}")
        return None


    def update(self, frame, current_gesture):
        """
        Optimización del método update para reducir procesamiento innecesario
        """
        # Si ya completamos todos los pasos, salimos inmediatamente
        if self.current_step >= len(self.calibration_steps):
            return True

        # Actualizamos el gesto actual solo si no estamos en revisión
        # No necesitamos procesar gestos durante la revisión
        if self.current_state != 'REVIEWING':
            self.gesture = current_gesture

        # Manejo de eventos en estado de revisión
        if self.current_state == 'REVIEWING':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    left_center_x = self.half_width // 2
                    self.button_continue = pygame.Rect(left_center_x - 100, WINDOW_HEIGHT - 200, 200, 50)
                    self.button_retake = pygame.Rect(left_center_x - 100, WINDOW_HEIGHT - 140, 200, 50)
                    
                    if self.button_continue.collidepoint(mouse_pos):
                        self.current_attempt += 1
                        if self.current_attempt >= self.attempts_per_gesture:
                            # Promediar las métricas solo cuando completamos todos los intentos
                            self._average_metrics()
                            self.current_step += 1
                            self.current_attempt = 0
                        self.current_state = 'CALIBRATING'
                        return False
                    elif self.button_retake.collidepoint(mouse_pos):
                        self.current_state = 'CALIBRATING'
                        self.countdown_timer = None
                        return False
            return False

        # Si hay un temporizador de reintento activo, solo decrementamos
        if self.retry_timer > 0:
            self.retry_timer -= 1
            return False

        # Procesamiento del gesto actual
        if self.countdown_timer is None:
            # Solo iniciamos el contador si el gesto coincide
            if current_gesture == self.calibration_steps[self.current_step]['gesture']:
                self.countdown_timer = 90  # 1.5 segundos a 60fps
                self.retry_message = ""
        else:
            self.countdown_timer -= 1
            # Solo procesamos el frame cuando el contador llegue a 0
            if self.countdown_timer == 0:
                # Convertimos y procesamos el frame solo cuando es necesario
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_analyzer.load_image(frame_rgb)
                metrics = self.frame_analyzer.calculate_metrics()
                
                if metrics is not None:
                    # Almacenar datos solo si la detección fue exitosa
                    self.review_frame = frame.copy()
                    self.review_landmarks = self.frame_analyzer.landmarks
                    self.review_metrics = metrics
                    self.review_gesture = current_gesture
                    current_gesture_type = self.calibration_steps[self.current_step]['gesture']
                    self.metrics_results[current_gesture_type].append(metrics)
                    self.current_state = 'REVIEWING'
                else:
                    self.retry_message = "No se detectó el gesto correctamente. Intentemos de nuevo."
                    self.retry_timer = 120
                
                self.countdown_timer = None
        
        return False

    def draw_landmarks(self, frame, landmarks):
        """
        Optimización del método draw_landmarks para evitar cálculos innecesarios
        """
        # Verificación rápida inicial
        if landmarks is None or landmarks._shape is None or frame is None:
            return frame

        # Crear una copia solo si vamos a modificar el frame
        frame_copy = frame.copy()
        shape = landmarks._shape

        # Dibujar solo los landmarks necesarios según el gesto actual
        current_gesture = self.calibration_steps[self.current_step]['gesture']
        
        # Siempre dibujamos el contorno facial (landmarks 0-16)
        for i in range(0, 16):
            pt1 = (int(shape[i][0]), int(shape[i][1]))
            pt2 = (int(shape[i+1][0]), int(shape[i+1][1]))
            cv2.line(frame_copy, pt1, pt2, self.colors['face'], 2)

        # Dibujar características específicas según el gesto
        if current_gesture in ['NSM_SPREAD', 'NSM_KISS']:
            # Dibujar labios para gestos que involucran la boca
            # Boca exterior (48-59)
            for i in range(48, 59):
                pt1 = (int(shape[i][0]), int(shape[i][1]))
                pt2 = (int(shape[i+1][0]), int(shape[i+1][1]))
                cv2.line(frame_copy, pt1, pt2, self.colors['lips'], 2)
            cv2.line(frame_copy, 
                    (int(shape[59][0]), int(shape[59][1])),
                    (int(shape[48][0]), int(shape[48][1])), 
                    self.colors['lips'], 2)

        if current_gesture == 'NSM_OPEN':
            # Dibujar boca interior para el gesto de apertura
            for i in range(60, 67):
                pt1 = (int(shape[i][0]), int(shape[i][1]))
                pt2 = (int(shape[i+1][0]), int(shape[i+1][1]))
                cv2.line(frame_copy, pt1, pt2, self.colors['lips'], 2)
            cv2.line(frame_copy, 
                    (int(shape[67][0]), int(shape[67][1])),
                    (int(shape[60][0]), int(shape[60][1])), 
                    self.colors['lips'], 2)

        return frame_copy

    def _average_metrics(self):
        """
        Promedia las métricas y normaliza los valores usando NEGATIVE como línea base
        """
        gesture_type = self.calibration_steps[self.current_step]['gesture']
        metrics_list = self.metrics_results[gesture_type]
        
        if not metrics_list:
            return
        
        # Crear un diccionario para almacenar las sumas
        avg_metrics = {}
        for key in metrics_list[0].keys():
            values = [m[key] for m in metrics_list if key in m]
            if values:
                avg_metrics[key] = sum(values) / len(values)
        
        # Si estamos procesando el gesto NEGATIVE, solo guardamos los promedios
        if gesture_type == 'NEGATIVE':
            self.metrics_results[gesture_type] = avg_metrics
            return
        
        # Para otros gestos, normalizamos usando NEGATIVE como base
        if 'NEGATIVE' in self.metrics_results and isinstance(self.metrics_results['NEGATIVE'], dict):
            base_metrics = self.metrics_results['NEGATIVE']
            normalized_metrics = {}
            
            # Normalizar las métricas relevantes según el tipo de gesto
            if gesture_type == 'NSM_SPREAD':
                # Normalizar métricas de sonrisa
                if 'CE_right' in avg_metrics and 'CE_right' in base_metrics:
                    normalized_metrics['smile_right'] = max(0, min(1, 
                        (avg_metrics['CE_right'] - base_metrics['CE_right']) / 
                        (base_metrics['CE_right'] * 2)))  # Factor 2 para dar más rango
                    
                if 'CE_left' in avg_metrics and 'CE_left' in base_metrics:
                    normalized_metrics['smile_left'] = max(0, min(1, 
                        (avg_metrics['CE_left'] - base_metrics['CE_left']) / 
                        (base_metrics['CE_left'] * 2)))
                    
                normalized_metrics['smile_symmetry'] = max(0, min(1, 
                    1 - abs(normalized_metrics.get('smile_right', 0) - 
                        normalized_metrics.get('smile_left', 0))))
                    
            elif gesture_type == 'NSM_OPEN':
                # Normalizar métricas de apertura
                if 'DS_right' in avg_metrics and 'DS_right' in base_metrics:
                    normalized_metrics['open_right'] = max(0, min(1, 
                        (avg_metrics['DS_right'] - base_metrics['DS_right']) / 
                        (base_metrics['DS_right'] * 3)))  # Factor 3 para apertura
                    
                if 'DS_left' in avg_metrics and 'DS_left' in base_metrics:
                    normalized_metrics['open_left'] = max(0, min(1, 
                        (avg_metrics['DS_left'] - base_metrics['DS_left']) / 
                        (base_metrics['DS_left'] * 3)))
                    
                normalized_metrics['open_symmetry'] = max(0, min(1, 
                    1 - abs(normalized_metrics.get('open_right', 0) - 
                        normalized_metrics.get('open_left', 0))))
                    
            elif gesture_type == 'NSM_KISS':
                # Normalizar métricas de protrusión
                if 'CE_right' in avg_metrics and 'CE_right' in base_metrics:
                    normalized_metrics['pucker_right'] = max(0, min(1, 
                        (avg_metrics['CE_right'] - base_metrics['CE_right']) / 
                        (base_metrics['CE_right'] * 1.5)))  # Factor 1.5 para protrusión
                    
                if 'CE_left' in avg_metrics and 'CE_left' in base_metrics:
                    normalized_metrics['pucker_left'] = max(0, min(1, 
                        (avg_metrics['CE_left'] - base_metrics['CE_left']) / 
                        (base_metrics['CE_left'] * 1.5)))
                    
                normalized_metrics['pucker_symmetry'] = max(0, min(1, 
                    1 - abs(normalized_metrics.get('pucker_right', 0) - 
                        normalized_metrics.get('pucker_left', 0))))
            
            # Guardar tanto las métricas originales como las normalizadas
            self.metrics_results[gesture_type] = {
                'original': avg_metrics,
                'normalized': normalized_metrics
            }
        else:
            # Si no tenemos métricas base, guardamos solo el promedio original
            self.metrics_results[gesture_type] = {
                'original': avg_metrics,
                'normalized': {}
            }
        # Guardar calibración después de promediar
        self.save_calibration()

    def get_normalized_metrics(self):
        """
        Retorna todas las métricas normalizadas para uso en el juego
        """
        normalized_results = {}
        for gesture_type in self.metrics_results:
            if gesture_type != 'NEGATIVE':
                if isinstance(self.metrics_results[gesture_type], dict) and 'normalized' in self.metrics_results[gesture_type]:
                    normalized_results[gesture_type] = self.metrics_results[gesture_type]['normalized']
        return normalized_results

        
    
    def draw(self, frame):
        if self.current_step >= len(self.calibration_steps):
            return
                
        current_step = self.calibration_steps[self.current_step]
        
        # Limpiar la pantalla primero
        self.display_surface.fill((0, 0, 0))

        if self.current_state == 'REVIEWING':
            # Mostrar frame con landmarks
            if self.review_frame is not None:
                frame_with_landmarks = self.draw_landmarks(self.review_frame, self.review_landmarks)
                frame_flipped = cv2.flip(frame_with_landmarks, 1)  
                frame_resized = cv2.resize(frame_flipped, (self.half_width, self.camera_height))
                frame_bgr = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(cv2.transpose(frame_bgr))
                self.display_surface.blit(frame_surface, (self.half_width, 0))

            # Dibujar panel de revisión
            overlay = pygame.Surface((self.half_width, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            self.display_surface.blit(overlay, (0, 0))

            # Mostrar métricas y botones según si el gesto es correcto
            left_center_x = self.half_width // 2
            
            # Título Principal
            title = self.font.render("Revisión de Gesto", True, (255, 255, 255))
            title_rect = title.get_rect(center=(left_center_x, 50))
            self.display_surface.blit(title, title_rect)

            # Información de intentos debajo del título
            attempts_text = f"Intento {self.current_attempt + 1} de {self.attempts_per_gesture}"
            attempts_surf = self.font_small.render(attempts_text, True, (200, 200, 200))
            attempts_rect = attempts_surf.get_rect(center=(left_center_x, 85))
            self.display_surface.blit(attempts_surf, attempts_rect)

            # Verificar si el gesto coincide
            if self.review_gesture == current_step['gesture']:
                # Mostrar métricas
                metrics_list = self.format_metrics(self.review_metrics, current_step['gesture'])
                
                # Mostrar el gesto detectado
                gesture_text = f"Gesto detectado: {self.review_gesture}"
                gesture_surf = self.font_small.render(gesture_text, True, (0, 255, 0))
                gesture_rect = gesture_surf.get_rect(center=(left_center_x, 120))
                self.display_surface.blit(gesture_surf, gesture_rect)

                # Métricas
                for i, metric in enumerate(metrics_list):
                    metric_surf = self.font_small.render(metric, True, (200, 200, 200))
                    metric_rect = metric_surf.get_rect(center=(left_center_x, 160 + i * 20))
                    self.display_surface.blit(metric_surf, metric_rect)

                # Mostrar ambos botones
                self.button_continue = pygame.Rect(left_center_x - 100, WINDOW_HEIGHT - 200, 200, 50)
                self.button_retake = pygame.Rect(left_center_x - 100, WINDOW_HEIGHT - 140, 200, 50)

                pygame.draw.rect(self.display_surface, (0, 200, 0), self.button_continue)
                pygame.draw.rect(self.display_surface, (200, 0, 0), self.button_retake)
                
                continue_text = self.font_small.render("Continuar", True, (255, 255, 255))
                retake_text = self.font_small.render("Repetir", True, (255, 255, 255))
                
                continue_rect = continue_text.get_rect(center=self.button_continue.center)
                retake_rect = retake_text.get_rect(center=self.button_retake.center)
                
                self.display_surface.blit(continue_text, continue_rect)
                self.display_surface.blit(retake_text, retake_rect)
            else:
                # Mostrar mensaje de error
                error_text = f"Se detectó {self.review_gesture} cuando debía ser {current_step['gesture']}"
                error_surf = self.font_small.render(error_text, True, (255, 100, 100))
                error_rect = error_surf.get_rect(center=(left_center_x, 150))
                self.display_surface.blit(error_surf, error_rect)

                # Solo mostrar botón de repetir
                self.button_retake = pygame.Rect(left_center_x - 100, WINDOW_HEIGHT - 140, 200, 50)
                pygame.draw.rect(self.display_surface, (200, 0, 0), self.button_retake)
                retake_text = self.font_small.render("Repetir", True, (255, 255, 255))
                retake_rect = retake_text.get_rect(center=self.button_retake.center)
                self.display_surface.blit(retake_text, retake_rect)

        else:
            # Mostrar el frame de la cámara en la mitad derecha
            if frame is not None:
                frame_flipped = cv2.flip(frame, 1)
                frame_resized = cv2.resize(frame_flipped, (self.half_width, self.camera_height))
                frame_bgr = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                frame_surface = pygame.surfarray.make_surface(cv2.transpose(frame_bgr))
                self.display_surface.blit(frame_surface, (self.half_width, 0))
            
            # Dibujar fondo semi-transparente en la mitad izquierda
            overlay = pygame.Surface((self.half_width, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.display_surface.blit(overlay, (0, 0))
            
            # Calcular posición central de la mitad izquierda
            left_center_x = self.half_width // 2
            
            # Mostrar gesto detectado actual
            if self.gesture:  # Suponiendo que self.gesture almacena el gesto actual
                gesto_texto = "Gesto detectado: "
                if self.gesture == current_step['gesture']:
                    gesto_texto += self.gesture
                    color_texto = (0, 255, 0)  # Verde si es el gesto correcto
                else:
                    gesto_texto += f"{self.gesture} - ¡Necesitas hacer {current_step['gesture']}!"
                    color_texto = (255, 100, 100)  # Rojo si es incorrecto
                    
                gesto_surf = self.font_small.render(gesto_texto, True, color_texto)
                gesto_rect = gesto_surf.get_rect(center=(left_center_x, WINDOW_HEIGHT//2 - 200))
                self.display_surface.blit(gesto_surf, gesto_rect)
            
            # Dibujar instrucciones
            instruction = self.font.render(current_step['instruction'], True, (255, 255, 255))
            description = self.font_small.render(current_step['description'], True, (200, 200, 200))
            
            # Centrar textos en la mitad izquierda
            instruction_rect = instruction.get_rect(center=(left_center_x, WINDOW_HEIGHT//2 - 50))
            description_rect = description.get_rect(center=(left_center_x, WINDOW_HEIGHT//2 + 10))
            
            self.display_surface.blit(instruction, instruction_rect)
            self.display_surface.blit(description, description_rect)
            
            # Si hay mensaje de reintento, mostrarlo
            if self.retry_message:
                retry_surf = self.font_small.render(self.retry_message, True, (255, 100, 100))
                retry_rect = retry_surf.get_rect(center=(left_center_x, WINDOW_HEIGHT//2 - 100))
                self.display_surface.blit(retry_surf, retry_rect)
            
            # Si el countdown está activo, mostrarlo
            if self.countdown_timer is not None:
                count = str(min(3, (self.countdown_timer // 30) + 1))
                count_surf = self.font.render(count, True, (255, 255, 255))
                count_rect = count_surf.get_rect(center=(left_center_x, WINDOW_HEIGHT//2 - 150))
                self.display_surface.blit(count_surf, count_rect)

            # Agregar un contenedor para la información de progreso en la parte inferior
            progress_container_height = 80  # Altura total para ambos textos
            base_y = WINDOW_HEIGHT - progress_container_height

            # Texto de paso actual
            step_text = f"Paso {self.current_step + 1} de {len(self.calibration_steps)}"
            step_surf = self.font_small.render(step_text, True, (255, 255, 255))
            step_rect = step_surf.get_rect(center=(left_center_x, base_y + 20))
            self.display_surface.blit(step_surf, step_rect)

            # Texto de intento actual
            attempt_text = f"Intento {self.current_attempt + 1} de {self.attempts_per_gesture}"
            attempt_surf = self.font_small.render(attempt_text, True, (200, 200, 200))
            attempt_rect = attempt_surf.get_rect(center=(left_center_x, base_y + 45))
            self.display_surface.blit(attempt_surf, attempt_rect)
            
    def format_metrics(self, metrics, gesture_type):
        """Formatea las métricas relevantes según el tipo de gesto"""
        if gesture_type == 'NEGATIVE':
            return [
                f"Línea base - Sonrisa derecha: {metrics['CE_right']:.2f}",
                f"Línea base - Sonrisa izquierda: {metrics['CE_left']:.2f}",
                f"Línea base - Apertura derecha: {metrics['DS_right']:.2f}",
                f"Línea base - Apertura izquierda: {metrics['DS_left']:.2f}",
                f"Línea base - Ángulo derecho: {metrics['SA_right']:.2f}°",
                f"Línea base - Ángulo izquierdo: {metrics['SA_left']:.2f}°",
                f"Línea base - Desviación comisura: {metrics['CH_dev']:.2f}",
                f"Línea base - Desviación labio sup.: {metrics['UVH_dev']:.2f}",
                f"Línea base - Desviación labio inf.: {metrics['LVH_dev']:.2f}"
            ]
        elif gesture_type == 'NSM_SPREAD':
            return [
                # Métricas básicas de sonrisa
                f"Sonrisa - Lado derecho: {metrics['CE_right']:.2f}",
                f"Sonrisa - Lado izquierdo: {metrics['CE_left']:.2f}",
                f"Ángulo derecho: {metrics['SA_right']:.2f}°",
                f"Ángulo izquierdo: {metrics['SA_left']:.2f}°",
                # Métricas de asimetría
                f"Desviación de altura comisura: {metrics['CH_dev']:.2f}",
                f"Desviación de excursión: {metrics['CE_dev']:.2f}",
                f"Desviación angular: {metrics['SA_dev']:.2f}°",
                # Métricas porcentuales
                f"Asimetría sonrisa: {metrics['CE_dev_p']:.1f}%",
                f"Asimetría angular: {metrics['SA_dev_p']:.1f}%"
            ]
        elif gesture_type == 'NSM_OPEN':
            return [
                # Métricas básicas de apertura
                f"Apertura derecha: {metrics['DS_right']:.2f}",
                f"Apertura izquierda: {metrics['DS_left']:.2f}",
                # Métricas de labios
                f"Altura labio superior: {metrics['UVH_dev']:.2f}",
                f"Altura labio inferior: {metrics['LVH_dev']:.2f}",
                # Métricas de asimetría
                f"Desviación apertura: {metrics['DS_dev']:.2f}",
                f"Desviación altura comisura: {metrics['CH_dev']:.2f}",
                # Métricas porcentuales
                f"Asimetría apertura: {metrics['DS_dev_p']:.1f}%",
                # Si existe openness en las métricas
                f"Apertura total: {metrics.get('openness', 0):.2f}"
            ]
        elif gesture_type == 'NSM_KISS':
            return [
                # Métricas básicas de protrusión
                f"Protrusión derecha: {metrics['CE_right']:.2f}",
                f"Protrusión izquierda: {metrics['CE_left']:.2f}",
                # Métricas de asimetría
                f"Desviación protrusión: {metrics['CE_dev']:.2f}",
                f"Desviación vertical: {metrics['CH_dev']:.2f}",
                # Métricas de labios
                f"Desvío labio superior: {metrics['UVH_dev']:.2f}",
                f"Desvío labio inferior: {metrics['LVH_dev']:.2f}",
                # Métricas porcentuales
                f"Asimetría protrusión: {metrics['CE_dev_p']:.1f}%"
            ]
        return []