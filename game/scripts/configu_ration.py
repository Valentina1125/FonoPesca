# game/scripts/config.py
import os
import pygame

# Rutas base
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Rutas de assets
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'game', 'assets')
SPRITE_PATH = os.path.join(ASSETS_PATH, 'sprites')
FONTS_PATH = os.path.join(ASSETS_PATH, 'fonts')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'emotrics', 'assets', 'models', 'best_model.pth')

# Ruta específica de la fuente
FONT_FILE = os.path.join(FONTS_PATH, 'Pixelify_Sans\PixelifySans-VariableFont_wght.ttf')

# Configuraciones de ventana
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Configuraciones de jugador
SPEED_FISHERMAN = 2
ANIMSPEED_FISHERMAN = 0.2

# Configuraciones de fuentes
def load_game_fonts():
    """
    Carga las fuentes del juego y maneja los errores apropiadamente.
    Retorna una tupla de (FONT_LARGE, FONT_MEDIUM, FONT_SMALL)
    """
    try:
        # Verifica si el archivo existe
        if not os.path.exists(FONT_FILE):
            print(f"Archivo de fuente no encontrado en: {FONT_FILE}")
            raise FileNotFoundError
        
        # Intenta cargar la fuente personalizada
        FONT_HUGE = pygame.font.Font(FONT_FILE, 70)
        FONT_LARGE = pygame.font.Font(FONT_FILE, 36)
        FONT_MEDIUM = pygame.font.Font(FONT_FILE, 24)
        FONT_SMALL = pygame.font.Font(FONT_FILE, 12)
        print("Fuente personalizada cargada exitosamente")
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"Error al cargar la fuente personalizada: {str(e)}")
        print("Usando fuente por defecto")
        FONT_HUGE = pygame.font.SysFont("Arial", 70)
        FONT_LARGE = pygame.font.SysFont("Arial", 36)
        FONT_MEDIUM = pygame.font.SysFont("Arial", 24)
        FONT_SMALL = pygame.font.SysFont("Arial", 18)
    
    return FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_HUGE