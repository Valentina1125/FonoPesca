# game.py
import cv2
import pygame
import random
import json

from datetime import datetime
from emotrics.core.frame_analysis import FrameSymmetry
from game.scripts.face_gesture_classifier import FaceGestureClassifier
from game.scripts.configu_ration import *
from game.scripts.game_state import GameState
from game.scripts.fisherman import Fisherman
from game.scripts.sprite_sheet import SpriteSheet
from game.scripts.fish_system import FishDatabase, FishInfoWindow
from game.scripts.settings_window import SettingsWindow
from game.scripts.completion_window import CompletionWindow

class Game:
    def __init__(self, displaySurface, calibration_metrics, selected_gesture, font_large=None, font_medium=None):
        self.key_pressed = False  # Control de tecla presionada
        # Configuración básica
        self.display_surface = displaySurface
        self.clock = pygame.time.Clock()
        self.classifier = FaceGestureClassifier()
        self.is_game_running = True
        self.frame_count = 0
        self.gesture = "No gesture"
        self.cap = cv2.VideoCapture(0)
        self.all_metrics = []  # Nueva variable para almacenar todas las repeticiones
        # Configuración de visualización
        WINDOW_WIDTH_REDUCED = int(WINDOW_WIDTH * 1.5)
        self.camera_width = int(WINDOW_WIDTH_REDUCED / 2)
        self.camera_height = WINDOW_HEIGHT
        

        self.high_score = self.load_high_score()
        # Estados del juego
        self.cast_state = {
            'WAITING': 'waiting',      
            'HOLDING': 'holding',    
            'ANIMATING': 'animating',
            'CATCHING': 'catching'     
            # 'FISHING': 'fishing',  # Comentado por ahora
        }
        self.current_cast_state = self.cast_state['WAITING']
        
        # Variables para el control del tiempo
        self.hold_timer = 0
        self.last_gesture = None
        
        # Cargar configuraciones
        settings = SettingsWindow.load_settings()  # Ahora funcionará correctamente
        self.total_fish_needed = settings['repetitions']
        
        # Umbrales de tiempo en frames (60 fps)
        self.time_thresholds = {
            'short': settings['short_time'] * 60,  # Convertir segundos a frames
            'medium': settings['medium_time'] * 60,
            'max': settings['long_time'] * 60
        }
        
        # Métricas de calibración y gesto seleccionado
        self.calibration_metrics = calibration_metrics
        self.selected_gesture = selected_gesture
        

        # Fuentes
        self.font = font_large or pygame.font.SysFont("Arial", 36)
        self.font_medium = font_medium or pygame.font.SysFont("Arial", 24)
        
        # Cargar las imágenes estáticas de líneas
        self.fishing_sprites = {
            'short': {
                'tensed': pygame.image.load('game/assets/sprites/line_tensed_short.png').convert_alpha(),
                'broken': pygame.image.load('game/assets/sprites/line_broken_short.png').convert_alpha()
            },
            'medium': {
                'tensed': pygame.image.load('game/assets/sprites/line_tensed_medium.png').convert_alpha(),
                'broken': pygame.image.load('game/assets/sprites/line_broken_medium.png').convert_alpha()
            },
            'long': {
                'tensed': pygame.image.load('game/assets/sprites/line_tensed_long.png').convert_alpha(),
                'broken': pygame.image.load('game/assets/sprites/line_broken_long.png').convert_alpha()
            }
        }

        # Variable para mantener el tipo de lanzamiento actual
        self.current_cast_length = 'short'
        
        # Estado del juego y pescador
        self.fisherman = Fisherman((WINDOW_WIDTH / 3, WINDOW_HEIGHT / 1.5), moveRight=True)
        # Precargar todas las animaciones del pescador
        for length in ['short', 'medium', 'long']:
            # Cargar animaciones de lanzamiento
            self.fisherman.load_animation(
                f"cast_{length}", 
                f"game/assets/sprites/cast_bobbin_Sheet-{length}"
            )
            # Cargar animaciones de captura
            self.fisherman.load_animation(
                f"catch_{length}", 
                f"game/assets/sprites/catch_red_fish-Sheet-{length}"
            )
        
        self.game_state = GameState(displaySurface, self.calibration_metrics)
        self.game_state.set_fisherman(self.fisherman)
        
        # Dimensiones de la barra de progreso
        self.progress_bar = {
            'x': self.camera_width // 4,
            'y': 50,
            'width': self.camera_width // 2,
            'height': 30
        }
        
        # Texto de instrucción inicial
        self.instruction_text = "Presiona ESPACIO para preparar el lanzamiento"

        self.fish_db = FishDatabase()
        self.fish_window = None
        
        # Agregar estado SHOWING_FISH
        self.cast_state['SHOWING_FISH'] = 'showing_fish'

        # Sistema de puntuación y capturas
        self.score = 0
        self.score_position = (20, 20)
        #self.high_score = self.load_high_score()
        self.catches = []  # Lista para almacenar los peces capturados
        self.max_display_catches = 12  # Número máximo de capturas a mostrar


                # Control de peces pescados - asegurarnos que sean enteros
        self.fish_caught = 0
      
        self.key_pressed = False
        
        # Registro de tipos de lanzamiento
        self.cast_records = {
            'short': 0,
            'medium': 0,
            'long': 0
        }
        
        # Almacenamiento de métricas
        self.session_metrics = []  # Lista para todas las métricas
        self.last_gesture_frame = None  # Para guardar el último frame con gesto
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Variables para el control de frames del gesto
        self.gesture_frames = []
        self.gesture_frames_count = 0
        self.middle_frame = None

    
    def detect_gesture(self):
        """
        Detecta gestos faciales en el frame de la cámara.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_count += 1

        # Detectar gesto cada 12 frames para optimizar rendimiento
        if self.frame_count % 12 == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.gesture = self.classifier.classify_face(frame_rgb)

        return frame
    def analyze_frame(self, frame):
        """Analiza el frame y obtiene las métricas según el gesto"""
        print("Analizando frame...")
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_analyzer = FrameSymmetry()
        frame_analyzer.load_image(frame_rgb)
        metrics = frame_analyzer.calculate_metrics()
        
        if metrics:
            print("Métricas obtenidas exitosamente")
            # Guardar toda la información del frame analizado
            frame_data = {
                'pez_numero': self.fish_caught + 1,
                'tipo_lanzamiento': self.current_cast_length,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'gesto': self.selected_gesture,
                'metricas_completas': {  # Guardar todas las métricas del frame
                    key: round(value, 2) for key, value in metrics.items()
                }
            }
            
            # Agregar también las métricas específicas para mantener compatibilidad
            if self.selected_gesture == 'NSM_SPREAD':
                frame_data.update({
                    'CE_right': round(metrics['CE_right'], 2),
                    'CE_left': round(metrics['CE_left'], 2),
                    'SA_right': round(metrics['SA_right'], 2),
                    'SA_left': round(metrics['SA_left'], 2)
                })
            elif self.selected_gesture == 'NSM_OPEN':
                frame_data.update({
                    'DS_right': round(metrics['DS_right'], 2),
                    'DS_left': round(metrics['DS_left'], 2)
                })
            elif self.selected_gesture == 'NSM_KISS':
                frame_data.update({
                    'CE_dev': round(metrics['CE_dev'], 2),
                    'UVH_dev': round(metrics['UVH_dev'], 2),
                    'LVH_dev': round(metrics['LVH_dev'], 2)
                })
            
            self.session_metrics.append(frame_data)
            self.save_session_metrics()
    def save_session_metrics(self):
        try:
            metrics_dir = os.path.join(os.getcwd(), 'game', 'data', 'metrics')
            os.makedirs(metrics_dir, exist_ok=True)

            # Preparar los datos de los intentos según el gesto
            intentos = []
            if self.selected_gesture == 'NSM_SPREAD':
                for metric in self.session_metrics:
                    intentos.append({
                        'intento': metric['pez_numero'],
                        'CE_right': metric['CE_right'],
                        'CE_left': metric['CE_left'],
                        'SA_right': metric['SA_right'],
                        'SA_left': metric['SA_left'],
                        'tipo_lanzamiento': metric['tipo_lanzamiento']
                    })
                
                # Calcular promedios y máximos
                promedios = {
                    'CE_right': round(sum(m['CE_right'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'CE_left': round(sum(m['CE_left'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'SA_right': round(sum(m['SA_right'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'SA_left': round(sum(m['SA_left'] for m in self.session_metrics) / len(self.session_metrics), 2)
                }
                
                maximos = {
                    'CE_right': round(max(m['CE_right'] for m in self.session_metrics), 2),
                    'CE_left': round(max(m['CE_left'] for m in self.session_metrics), 2),
                    'SA_right': round(max(m['SA_right'] for m in self.session_metrics), 2),
                    'SA_left': round(max(m['SA_left'] for m in self.session_metrics), 2)
                }
                
            elif self.selected_gesture == 'NSM_OPEN':
                for metric in self.session_metrics:
                    intentos.append({
                        'intento': metric['pez_numero'],
                        'DS_right': metric['DS_right'],
                        'DS_left': metric['DS_left'],
                        'UVH_right': metric['metricas_completas']['UVH_dev'],
                        'UVH_left': metric['metricas_completas']['UVH_dev'],
                        'LVH_right': metric['metricas_completas']['LVH_dev'],
                        'LVH_left': metric['metricas_completas']['LVH_dev'],
                        'tipo_lanzamiento': metric['tipo_lanzamiento']
                    })
                
                promedios = {
                    'DS_right': round(sum(m['DS_right'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'DS_left': round(sum(m['DS_left'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'UVH_dev': round(sum(m['metricas_completas']['UVH_dev'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'LVH_dev': round(sum(m['metricas_completas']['LVH_dev'] for m in self.session_metrics) / len(self.session_metrics), 2)
                }
                
                maximos = {
                    'DS_right': round(max(m['DS_right'] for m in self.session_metrics), 2),
                    'DS_left': round(max(m['DS_left'] for m in self.session_metrics), 2),
                    'UVH_dev': round(max(m['metricas_completas']['UVH_dev'] for m in self.session_metrics), 2),
                    'LVH_dev': round(max(m['metricas_completas']['LVH_dev'] for m in self.session_metrics), 2)
                }
                
            elif self.selected_gesture == 'NSM_KISS':
                for metric in self.session_metrics:
                    intentos.append({
                        'intento': metric['pez_numero'],
                        'CH': metric['metricas_completas']['CH_dev'],
                        'CE': metric['CE_dev'],
                        'tipo_lanzamiento': metric['tipo_lanzamiento']
                    })
                
                promedios = {
                    'CH': round(sum(m['metricas_completas']['CH_dev'] for m in self.session_metrics) / len(self.session_metrics), 2),
                    'CE': round(sum(m['CE_dev'] for m in self.session_metrics) / len(self.session_metrics), 2)
                }
                
                maximos = {
                    'CH': round(max(m['metricas_completas']['CH_dev'] for m in self.session_metrics), 2),
                    'CE': round(max(m['CE_dev'] for m in self.session_metrics), 2)
                }

            session_data = {
                'session_id': self.session_id,
                'gesto': self.selected_gesture,
                'intentos': intentos,
                'resumen': {
                    'promedios': promedios,
                    'maximos': maximos
                },
                'distribucion_lanzamientos': {
                    'corto': self.cast_records['short'],
                    'medio': self.cast_records['medium'],
                    'largo': self.cast_records['long'],
                    'total': len(self.session_metrics) 
                }
            }
            
            filename = f"metrics_{self.session_id}_{self.selected_gesture}.json"
            filepath = os.path.join(metrics_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            print(f"¡Métricas guardadas exitosamente en {filepath}!")
        except Exception as e:
            print(f"Error al guardar métricas: {str(e)}")


    def load_high_score(self):
        """Carga el high score desde un archivo"""
        try:
            score_path = os.path.join('game', 'data', 'score.json')
            if os.path.exists(score_path):
                with open(score_path, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except Exception as e:
            print(f"Error loading high score: {e}")
        return 0

    def save_high_score(self):
        """Guarda el high score en un archivo"""
        try:
            score_path = os.path.join('game', 'data', 'score.json')
            os.makedirs(os.path.dirname(score_path), exist_ok=True)
            with open(score_path, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except Exception as e:
            print(f"Error saving high score: {e}")

    def update_score(self, fish_info):
        """Actualiza el puntaje y el historial de capturas"""
        points = int(fish_info['valor'])
        self.score += points
        
        # Agregar la captura al historial
        self.catches.append({
            'name': fish_info['nombre_pez'],
            'points': points,
            'type': fish_info['tipo_de_pez']
        })
        
        # Mantener solo las últimas X capturas
        if len(self.catches) > self.max_display_catches:
            self.catches = self.catches[-self.max_display_catches:]
        
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        return points
    def draw_score_and_catches(self):
        """Dibuja el puntaje y el historial de capturas"""
        # Dibujar puntuación total - mantenemos esta posición
        score_text = self.font_medium.render(f"Total: {self.score}", True, (255, 255, 255))
        self.display_surface.blit(score_text, self.score_position)
        
        # Ajustar la posición inicial Y para la lista de capturas
        # La barra está en y=50, así que empezamos después de ella
        start_y = 150  # Cambiado de 60 a 150 para evitar la barra
        for i, catch in enumerate(self.catches):
            color = {
                'Común': (150, 150, 150),
                'Raro': (100, 200, 255),
                'Exótico': (255, 150, 50),
                'Legendario': (255, 215, 0)
            }.get(catch['type'], (255, 255, 255))
            
            catch_text = self.font_medium.render(
                f"{catch['name']}: +{catch['points']}", 
                True, 
                color
            )
            catch_pos = (self.score_position[0], start_y + (i * 25))
            self.display_surface.blit(catch_text, catch_pos)


            


    

    def draw_score(self):
        """Dibuja el puntaje en la pantalla"""
        # Puntuación actual
        score_text = self.font_medium.render(f"Puntos: {self.score}", True, (255, 255, 255))
        self.display_surface.blit(score_text, self.score_position)
        
        # High score
        high_score_text = self.font_medium.render(f"Récord: {self.high_score}", True, (255, 215, 0))
        high_score_pos = (self.score_position[0], self.score_position[1] + 30)
        self.display_surface.blit(high_score_text, high_score_pos)




    def determine_cast_type(self):
        """Determina el tipo de lanzamiento basado en el tiempo mantenido"""
        hold_time = self.hold_timer
        
        if hold_time >= self.time_thresholds['medium']:
            self.current_cast_length = 'long'
            return 'long'
        elif hold_time >= self.time_thresholds['short']:
            self.current_cast_length = 'medium'
            return 'medium'
        else:
            self.current_cast_length = 'short'
            return 'short'

    def start_cast_animation(self, cast_type):
        """Inicia la animación de lanzamiento según el tipo"""
        hold_time = 1  # 1 segundo (60 frames a 60 fps)
        self.fisherman.start_animation(f"cast_{cast_type}", hold_time)
        self.current_cast_length = cast_type


    def start_catch_animation(self, cast_type):
        """Inicia la animación de captura según el tipo"""
        print(f"Iniciando animación catch_{cast_type}")  # Debug
        self.fisherman.start_animation(f"catch_{cast_type}", None)  # No necesitamos hold timer aquí

    def draw_progress_bar(self):
        # Dibujar el fondo de la barra
        bar_bg = pygame.Rect(
            self.progress_bar['x'], 
            self.progress_bar['y'], 
            self.progress_bar['width'], 
            self.progress_bar['height']
        )
        pygame.draw.rect(self.display_surface, (50, 50, 50), bar_bg)

        # Calcular el progreso actual
        progress = min(self.hold_timer / self.time_thresholds['max'], 1.0)
        progress_width = int(self.progress_bar['width'] * progress)

        # Obtener color basado en el progreso
        if self.hold_timer <= self.time_thresholds['short']:
            # Transición más suave de rojo a amarillo
            progress_to_yellow = self.hold_timer / self.time_thresholds['short']
            green = int(220 * progress_to_yellow)  # Aumenta más gradualmente
            color = (255, green, 50)
        elif self.hold_timer <= self.time_thresholds['medium']:
            # Transición de amarillo a verde
            progress_in_medium = (self.hold_timer - self.time_thresholds['short']) / (self.time_thresholds['medium'] - self.time_thresholds['short'])
            color = (255 * (1 - progress_in_medium), 220, 50)
        else:
            color = (50, 220, 50)  # Verde

        # Dibujar la barra de progreso
        if progress_width > 0:
            progress_rect = pygame.Rect(
                self.progress_bar['x'],
                self.progress_bar['y'],
                progress_width,
                self.progress_bar['height']
            )
            pygame.draw.rect(self.display_surface, color, progress_rect)

        # Dibujar las líneas de umbral
        for threshold_name in ['short', 'medium']:
            threshold_x = self.progress_bar['x'] + (self.progress_bar['width'] * 
                         (self.time_thresholds[threshold_name] / self.time_thresholds['max']))
            
            pygame.draw.line(
                self.display_surface,
                (255, 255, 255),
                (threshold_x, self.progress_bar['y']),
                (threshold_x, self.progress_bar['y'] + self.progress_bar['height']),
                2
            )

        # Dibujar texto de zonas
        texts = ['Corto', 'Medio', 'Largo']
        zone_widths = [
            self.time_thresholds['short'],
            self.time_thresholds['medium'] - self.time_thresholds['short'],
            self.time_thresholds['max'] - self.time_thresholds['medium']
        ]
        
        accumulated_width = 0
        for i, text in enumerate(texts):
            # Calcular el centro de cada zona
            zone_center = self.progress_bar['x'] + (accumulated_width + zone_widths[i]/2) * (self.progress_bar['width'] / self.time_thresholds['max'])
            
            text_surface = self.font_medium.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(zone_center, self.progress_bar['y'] - 15))
            self.display_surface.blit(text_surface, text_rect)
            
            accumulated_width += zone_widths[i]

    def draw_fishing_state(self):
        """Dibuja el estado actual de pesca"""
        current_sprite = self.fishing_sprites[self.current_cast_length]['tensed']
        # Usar exactamente la misma posición que tiene el pescador actualmente
        sprite_rect = current_sprite.get_rect(bottomleft=self.fisherman.rect.bottomleft)
        self.display_surface.blit(current_sprite, sprite_rect)
    
    def update_interface(self, frame):
        if frame is None:
            return

        # Procesar frame para visualización
        frame_flipped = cv2.flip(frame, 1)
        frame_resized = cv2.resize(frame_flipped, (self.camera_width, self.camera_height))
        frame_bgr = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR)
        frame_surface = pygame.surfarray.make_surface(cv2.transpose(frame_bgr))

        # Limpiar pantalla
        self.display_surface.fill((0, 0, 0))

        # Actualizar y detectar gesto si es necesario
        if self.frame_count % 12 == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.gesture = self.classifier.classify_face(frame_rgb)

        # Dibujar el fondo siempre antes de cualquier estado
        self.game_state.background.draw(self.display_surface)

        # Manejar estados de lanzamiento y actualizar pescador
        if self.current_cast_state == self.cast_state['WAITING']:
            # Dibujar el estado del juego normalmente
            self.game_state.run(True)
            
            text_surface = self.font_medium.render(self.instruction_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.camera_width//2, 100))
            self.display_surface.blit(text_surface, text_rect)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.current_cast_state = self.cast_state['HOLDING']
                self.hold_timer = 0
                self.last_gesture = None
        elif self.current_cast_state == self.cast_state['HOLDING']:
            self.game_state.run(True)  
            self.draw_progress_bar()

            if self.gesture == self.selected_gesture:
                # Si es el primer frame del gesto
                if self.last_gesture != self.selected_gesture:
                    self.gesture_frames_count = 1
                    self.gesture_frames = [frame.copy()]
                    print(f"Inicio del gesto: Frame 1")
                else:
                    self.gesture_frames_count += 1
                    self.gesture_frames.append(frame.copy())
                    middle_index = (self.gesture_frames_count - 1) // 2
                    self.middle_frame = self.gesture_frames[middle_index]

                self.hold_timer += 1

            else:
                if self.last_gesture == self.selected_gesture:
                    # Analizar el frame del medio cuando se suelta el gesto
                    if hasattr(self, 'middle_frame'):
                        self.analyze_frame(self.middle_frame)

                    
                    cast_type = self.determine_cast_type()
                    self.cast_records[cast_type] += 1
                    self.start_cast_animation(cast_type)
                    self.current_cast_state = self.cast_state['ANIMATING']
                    
                    # Limpiar las variables de frames
                    self.gesture_frames = []
                    self.gesture_frames_count = 0
                else:
                    # Reiniciar el timer y contadores si se suelta el gesto sin completar
                    self.hold_timer = 0
                    self.gesture_frames = []
                    self.gesture_frames_count = 0
            
            self.last_gesture = self.gesture

        elif self.current_cast_state == self.cast_state['ANIMATING']:
            self.game_state.background.draw(self.display_surface)
            self.fisherman.update()
            self.fisherman.draw(self.display_surface)
            
            if self.fisherman.animation_finished:
                self.start_catch_animation(self.current_cast_length)
                self.current_cast_state = self.cast_state['CATCHING']

        elif self.current_cast_state == self.cast_state['CATCHING']:
            self.game_state.background.draw(self.display_surface)
            self.fisherman.update()
            self.fisherman.draw(self.display_surface)
            
            if self.fisherman.animation_finished:
                caught_fish = self.fish_db.get_random_fish(self.current_cast_length)
                points_earned = self.update_score(caught_fish)
                self.fish_window = FishInfoWindow(self.display_surface, caught_fish, 
                                                self.camera_width, self.font, 
                                                self.font_medium, points_earned)
                self.current_cast_state = self.cast_state['SHOWING_FISH']

        elif self.current_cast_state == self.cast_state['SHOWING_FISH']:
            # Dibujar el fondo antes de la ventana del pez
            self.game_state.background.draw(self.display_surface)
            self.fish_window.draw()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.key_pressed:
                self.key_pressed = True
                
                # Solo incrementar el contador de peces
                self.fish_caught += 1
                
                print(f"Pez #{self.fish_caught} pescado - Tipo: {self.current_cast_length}")
                print(f"Total de peces pescados: {self.fish_caught} de {self.total_fish_needed}")  # Debug adicional

                if self.fish_caught >= self.total_fish_needed:
                    print(f"¡Juego completado!")
                    print(f"Peces por tipo: Corto: {self.cast_records['short']}, "
                        f"Medio: {self.cast_records['medium']}, "
                        f"Largo: {self.cast_records['long']}")
                    
                    # Mostrar ventana de finalización
                    completion_window = CompletionWindow(self.display_surface, 
                                                    self.selected_gesture,
                                                    self.font,
                                                    self.font_medium)
                    completion_window.show()
                    
                    self.is_game_running = False
                    return
                                                
                # Si no hemos llegado al límite, preparar siguiente pesca
                self.current_cast_state = self.cast_state['WAITING']
                self.fish_window = None
                
            elif not keys[pygame.K_SPACE]:
                self.key_pressed = False  # Resetear cuando se suelta la tecla

        if self.current_cast_state != self.cast_state['SHOWING_FISH']:
            self.draw_score_and_catches()

        # Dibujar frame de la cámara después de todo lo demás
        self.display_surface.blit(frame_surface, (self.camera_width, 0))

        # Dibujar contador de peces
        counter_text = self.font_medium.render(f"Peces: {self.fish_caught}/{self.total_fish_needed}", True, (255, 255, 255))
        counter_rect = counter_text.get_rect(bottom=WINDOW_HEIGHT - 20, left=20)
        self.display_surface.blit(counter_text, counter_rect)
        
        # Actualizar pantalla
        pygame.display.flip()
        self.clock.tick(60)
                 
    def release_resources(self):
        """Libera recursos del juego."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()