import cv2
import pygame

from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT
from game.scripts.face_gesture_classifier import FaceGestureClassifier
from game.scripts.game_state import GameState


import pygame
from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT
from game.scripts.background import Background  # Importa la clase Background

class StartMenu:
    def __init__(self, display_surface, font_large=None, font_medium=None, font_small=None):
        self.display_surface = display_surface
        self.font = font_large or pygame.font.SysFont("Arial", 36)
        self.font_medium = font_medium or pygame.font.SysFont("Arial", 24)
        self.font_small = font_medium or pygame.font.SysFont("Arial", 24)
        
        # Cargar el fondo específico del menú de inicio
        self.background = Background("background_start_menu.jpg")  # Usa la imagen del menú de inicio
        
        # Textos del menú
        self.menu_active = True
        self.title = "Welcome to MagicForest"
        self.subtitle = "A Facial Exercise Game"
        self.start_text = "Press any key to start"
        
        # Posiciones de los textos (centrados)
        self.title_pos = (WINDOW_WIDTH // 2, 100)
        self.subtitle_pos = (WINDOW_WIDTH // 2, 150)
        self.start_text_pos = (WINDOW_WIDTH // 2, 250)

    def draw_text_centered(self, text, position, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.display_surface.blit(text_surface, text_rect)

    def draw(self):
        # Dibuja el fondo del menú de inicio
        self.background.draw(self.display_surface)
        
        # Agrega los textos del menú sobre el fondo
        self.draw_text_centered(self.title, self.title_pos)
        self.draw_text_centered(self.subtitle, self.subtitle_pos, color=(200, 200, 200))
        self.draw_text_centered(self.start_text, self.start_text_pos, color=(255, 255, 255))
    def show(self):
        while self.menu_active:
            # Manejo de eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    self.menu_active = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu_active = False

            # Limpiar pantalla
            self.display_surface.fill(self.background_color)

            # Dibujar textos
            self.draw_text_centered(self.title, self.title_pos)
            self.draw_text_centered(self.subtitle, self.subtitle_pos)
            self.draw_text_centered(self.start_text, self.start_text_pos)
            
            # Instrucciones adicionales
            instructions = [
                "Use your facial expressions to play:",
                "SMILE - Cast your line",
                "OPEN - Attract fish",
                "KISS - Reel in fish"
            ]
            
            # Dibujar instrucciones
            for i, instruction in enumerate(instructions):
                pos = (WINDOW_WIDTH // 2, 300 + i * 30)
                self.draw_text_centered(instruction, pos)

            # Actualizar pantalla
            pygame.display.flip()

            # Control de FPS
            pygame.time.Clock().tick(60)