# main.py
import cv2
import pygame
import numpy as np
from game.scripts.game import Game
from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT, load_game_fonts
from game.scripts.start_menu import StartMenu
from game.scripts.calibration import CalibrationState
from game.scripts.face_gesture_classifier import FaceGestureClassifier
from game.scripts.metrics_viewer import MetricsViewer
from game.scripts.settings_window import SettingsWindow
from game.scripts.background import Background, MenuBackground # Añadir este import
class MainMenu:
    def __init__(self, display_surface, font_large=None, font_medium=None, font_huge=None):
        self.display_surface = display_surface
        self.font = font_large or pygame.font.SysFont("Arial", 36)
        self.font_small = font_medium or pygame.font.SysFont("Arial", 24)
        self.options = ["Jugar", "Ver Métricas", "Configuración", "Toma de Metricas"]
        self.selected_option = 0
        self.calibration_metrics = None
        self.warning_timer = 0
        self.classifier = FaceGestureClassifier()
        self.calibration_metrics = CalibrationState.load_calibration()
        self.title_font = font_huge or pygame.font.SysFont("Arial", 70)
        self.title_text = "FonoPesca"
        self.title_y = 50
        
        # Añadir el fondo
        self.background = MenuBackground()
        

        
        # Posiciones y dimensiones del menú
        self.menu_width = 400
        self.menu_start_y = self.title_y + 150
        self.option_height = 60
    def show(self):
        running = True
        while running:
            # Dibujar el fondo
            self.background.draw(self.display_surface)
            
            # Agregar overlay semi-transparente general
            overlay = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(100)
            self.display_surface.blit(overlay, (0, 0))
            
            # Dibujar título con efecto de sombra
            shadow_offset = 3
            title_shadow = self.title_font.render(self.title_text, True, (0, 0, 0))
            title_surface = self.title_font.render(self.title_text, True, (255, 215, 0))
            
            title_rect = title_surface.get_rect(centerx=self.display_surface.get_width() // 2, y=self.title_y)
            shadow_rect = title_rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            
            self.display_surface.blit(title_shadow, shadow_rect)
            self.display_surface.blit(title_surface, title_rect)
            
            # Crear panel semi-transparente para las opciones
            menu_height = len(self.options) * self.option_height
            menu_surface = pygame.Surface((self.menu_width, menu_height))
            menu_surface.fill((0, 0, 0))
            menu_surface.set_alpha(180)
            menu_rect = menu_surface.get_rect(centerx=self.display_surface.get_width() // 2, 
                                            top=self.menu_start_y)
            self.display_surface.blit(menu_surface, menu_rect)
            
            # Mostrar opciones del menú
            for i, option in enumerate(self.options):
                # Resaltar opción seleccionada con un rectángulo
                option_rect = pygame.Rect(
                    menu_rect.x,
                    menu_rect.y + i * self.option_height,
                    self.menu_width,
                    self.option_height
                )
                
                if i == self.selected_option:
                    highlight_surface = pygame.Surface((self.menu_width, self.option_height))
                    highlight_surface.fill((50, 50, 50))
                    highlight_surface.set_alpha(150)
                    self.display_surface.blit(highlight_surface, option_rect)
                
                color = (255, 215, 0) if i == self.selected_option else (255, 255, 255)
                text_surface = self.font.render(option, True, color)
                text_rect = text_surface.get_rect(
                    center=(self.display_surface.get_width() // 2,
                        self.menu_start_y + i * self.option_height + self.option_height // 2)
                )
                self.display_surface.blit(text_surface, text_rect)
            
            # Mostrar advertencia si es necesario
            if self.warning_timer > 0:
                warning_surface = pygame.Surface((400, 40))
                warning_surface.fill((0, 0, 0))
                warning_surface.set_alpha(200)
                warning_rect = warning_surface.get_rect(
                    centerx=self.display_surface.get_width() // 2,
                    bottom=self.display_surface.get_height() - 20
                )
                self.display_surface.blit(warning_surface, warning_rect)
                
                warning_text = self.font.render("¡Necesitas calibrar primero!", True, (255, 100, 100))
                warning_text_rect = warning_text.get_rect(center=warning_rect.center)
                self.display_surface.blit(warning_text, warning_text_rect)
                self.warning_timer -= 1
            
            # Instrucciones
            instructions = self.font_small.render(
                "↑↓: Seleccionar   ENTER: Confirmar   ESC: Salir",
                True, (200, 200, 200)
            )
            instructions_rect = instructions.get_rect(
                centerx=self.display_surface.get_width() // 2,
                bottom=self.display_surface.get_height() - 20
            )
            self.display_surface.blit(instructions, instructions_rect)
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0 and not self.calibration_metrics:
                            self.warning_timer = 120
                            continue
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

        return self.selected_option, self.calibration_metrics

class GestureSelectionMenu:
    def __init__(self, display_surface, font_large=None, font_medium=None):
        self.display_surface = display_surface
        self.font = font_medium or pygame.font.SysFont("Arial", 24)
        self.title_font = font_large or pygame.font.SysFont("Arial", 36)
        self.selected_option = 0
        self.background = MenuBackground()
        
        self.gestures = [
            {
                'name': "Sonrisa",
                'gesture': 'NSM_SPREAD',
                'description': "Ejercita los músculos de la sonrisa"
            },
            {
                'name': "Boca Abierta",
                'gesture': 'NSM_OPEN',
                'description': "Ejercita la apertura de la boca"
            },
            { 
                'name': "Beso",
                'gesture': 'NSM_KISS',
                'description': "Ejercita los músculos de los labios"
            }
        ]
        
        # Configuración del panel de gestos
        self.panel_width = 500
        self.panel_height = len(self.gestures) * 100 + 50
        self.panel_x = (self.display_surface.get_width() - self.panel_width) // 2
        self.panel_y = 100

    def draw(self):
        # Dibujar el fondo
        self.background.draw(self.display_surface)
        
        # Agregar overlay semi-transparente general
        overlay = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.display_surface.blit(overlay, (0, 0))
        
        # Dibujar panel principal
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill((20, 20, 20))
        panel_surface.set_alpha(200)
        self.display_surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # Título
        title = self.title_font.render("Selecciona el Gesto a Ejercitar", True, (255, 215, 0))
        title_rect = title.get_rect(centerx=self.display_surface.get_width() // 2, y=50)
        self.display_surface.blit(title, title_rect)

        # Dibujar opciones
        for i, gesture in enumerate(self.gestures):
            # Calcular posición del gesto
            y_pos = self.panel_y + 30 + i * 100
            
            # Resaltar opción seleccionada
            if i == self.selected_option:
                highlight_surface = pygame.Surface((self.panel_width - 20, 80))
                highlight_surface.fill((50, 50, 50))
                highlight_surface.set_alpha(150)
                self.display_surface.blit(highlight_surface, 
                    (self.panel_x + 10, y_pos - 10))
            
            # Nombre del gesto
            color = (255, 215, 0) if i == self.selected_option else (255, 255, 255)
            name_surf = self.font.render(gesture['name'], True, color)
            name_rect = name_surf.get_rect(
                x=self.panel_x + 30,
                centery=y_pos
            )
            self.display_surface.blit(name_surf, name_rect)
            
            # Descripción del gesto
            desc_surf = self.font.render(gesture['description'], True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(
                x=self.panel_x + 30,
                centery=y_pos + 30
            )
            self.display_surface.blit(desc_surf, desc_rect)

        # Instrucciones
        instructions = self.font.render(
            "↑↓: Seleccionar   ENTER: Confirmar   ESC: Volver",
            True, (200, 200, 200)
        )
        instructions_rect = instructions.get_rect(
            centerx=self.display_surface.get_width() // 2,
            bottom=self.display_surface.get_height() - 20
        )
        self.display_surface.blit(instructions, instructions_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.gestures)
                return None
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.gestures)
                return None
            elif event.key == pygame.K_RETURN:
                return self.gestures[self.selected_option]['gesture']
            elif event.key == pygame.K_ESCAPE:
                return "CANCEL"
        return None

    def show(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                result = self.handle_event(event)
                if result == "CANCEL":
                    return None
                elif result is not None:
                    return result
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)


def main():
    pygame.init()
    display_surface = pygame.display.set_mode((int(WINDOW_WIDTH * 1.5), WINDOW_HEIGHT))
    pygame.display.set_caption("MagicForest")

    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_HUGE = load_game_fonts()

    main_menu = MainMenu(display_surface, FONT_LARGE, FONT_MEDIUM, FONT_HUGE)
    

    while True:
        choice, calibration_metrics = main_menu.show()

        if choice == 3:  # Tomar medidas
            calibration = CalibrationState(display_surface, FONT_LARGE, FONT_MEDIUM, FONT_SMALL)
            cap = cv2.VideoCapture(0)
            classifier = FaceGestureClassifier()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    current_gesture = classifier.classify_face(frame_rgb)
                else:
                    current_gesture = None
                
                if calibration.update(frame, current_gesture):
                    calibration_metrics = calibration.metrics_results
                    if calibration_metrics:
                        main_menu.calibration_metrics = calibration_metrics
                        break
                
                calibration.draw(frame)
                pygame.display.update()
            cap.release()

        elif choice == 0:   # Jugar
            if not calibration_metrics:
                continue
                
            # Mostrar menú de selección de gestos
            # En la parte donde se crea el GestureSelectionMenu
            gesture_menu = GestureSelectionMenu(display_surface, FONT_LARGE, FONT_MEDIUM)
            selected_gesture = gesture_menu.show()
            
            # Iniciar juego con el gesto seleccionado
            game = Game(display_surface, calibration_metrics, selected_gesture, FONT_LARGE, FONT_MEDIUM)
            while game.is_game_running:
                frame = game.detect_gesture()
                if frame is not None:
                    game.update_interface(frame)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game.is_game_running = False
                        pygame.quit()
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game.is_game_running = False

            game.release_resources()
        
        elif choice == 1:  # Ver Métricas
            metrics_viewer = MetricsViewer(display_surface, FONT_LARGE, FONT_MEDIUM)
            if not metrics_viewer.show():
                break
        elif choice == 2:  # Configuración
            settings_window = SettingsWindow(display_surface, FONT_LARGE, FONT_MEDIUM)
            new_settings = settings_window.show()
            if new_settings is None:
                break
if __name__ == "__main__":
    main()