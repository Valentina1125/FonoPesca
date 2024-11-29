# background.py
import pygame
import os
from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT

class Background:
    def __init__(self, image_filename="background_extended.png"):
        # Ruta de la imagen de fondo (puedes pasar un archivo diferente según la pantalla)
        background_path = os.path.join('game', 'assets', image_filename)
        self.skyImage = pygame.image.load(background_path).convert()
        
        # Escala la imagen para que coincida con el tamaño de la ventana
        self.skyImage = pygame.transform.scale(self.skyImage, (WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw(self, display_surface):
        # Dibuja la imagen de fondo en la superficie proporcionada
        display_surface.blit(self.skyImage, (0, 0))

class MenuBackground:
    _instance = None
    _background_cache = {}
    
    def __init__(self, image_filename="background_extendedall.png", alpha=255):
        """
        Inicializa un fondo de menú con la imagen especificada y nivel de transparencia.
        """
        if image_filename in MenuBackground._background_cache:
            self.background = MenuBackground._background_cache[image_filename]
        else:
            background_path = os.path.join('game', 'assets', image_filename)
            try:
                # Cargar la imagen original
                original_image = pygame.image.load(background_path).convert()
                
                # Calcular proporciones
                target_width = int(WINDOW_WIDTH * 1.5)  # Ancho de la ventana del juego
                target_height = WINDOW_HEIGHT
                target_ratio = target_width / target_height
                image_ratio = original_image.get_width() / original_image.get_height()
                
                if image_ratio > target_ratio:
                    # La imagen es más ancha proporcionalmente
                    new_height = target_height
                    new_width = int(target_height * image_ratio)
                else:
                    # La imagen es más alta proporcionalmente
                    new_width = target_width
                    new_height = int(target_width / image_ratio)
                
                # Escalar la imagen manteniendo proporción
                scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
                
                # Crear superficie del tamaño objetivo
                self.background = pygame.Surface((target_width, target_height))
                
                # Calcular posición para centrar
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2
                
                # Colocar imagen escalada en el centro
                self.background.blit(scaled_image, (x_offset, y_offset))
                
                # Guardar en caché
                MenuBackground._background_cache[image_filename] = self.background
                
            except pygame.error as e:
                print(f"Error loading background {image_filename}: {e}")
                self.background = pygame.Surface((target_width, target_height))
                self.background.fill((0, 0, 0))
        
        # Crear una copia para manejar la transparencia
        self.background_alpha = self.background.copy()
        self.set_alpha(alpha)

    def set_alpha(self, alpha):
        """Establece el nivel de transparencia del fondo."""
        self.background_alpha = self.background.copy()
        self.background_alpha.set_alpha(alpha)

    def draw(self, display_surface, x=0, y=0):
        """Dibuja el fondo en la superficie especificada."""
        display_surface.blit(self.background_alpha, (x, y))