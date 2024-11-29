import pygame
from game.scripts.configu_ration import WINDOW_WIDTH, WINDOW_HEIGHT
from game.scripts.fisherman import Fisherman
from game.scripts.background import Background


class GameState():
    def __init__(self, displaySurface, baseline_metrics=None, font_large=None, font_medium=None):
        self.displaySurface = displaySurface
        self.font = font_large or pygame.font.SysFont("Arial", 36)
        self.font_small = font_medium or pygame.font.SysFont("Arial", 24)
        # Usar el fondo específico del juego
        self.background = Background("background_extended.png")
        self.fisherman = None
        self.baseline_metrics = baseline_metrics
        
        if baseline_metrics:
            self.fishing_zones = self._create_fishing_zones()
        else:
            self.fishing_zones = self._create_default_fishing_zones()

    def set_fisherman(self, fisherman):
        """Método para establecer la referencia al pescador"""
        self.fisherman = fisherman

    def update(self, animate):
        if animate and self.fisherman:
            self.fisherman.update()

    def draw(self):
        self.background.draw(self.displaySurface)
        if self.fisherman:
            self.fisherman.draw(self.displaySurface)


    def _create_fishing_zones(self):
        """Crea zonas de pesca basadas en las métricas base del jugador"""
        zones = []
        
        # Usar las métricas de sonrisa (SPREAD) para determinar las zonas
        if 'NSM_SPREAD' in self.baseline_metrics:
            metrics = self.baseline_metrics['NSM_SPREAD']['original']  # Añadimos ['original']
            if 'CE_right' in metrics:
                max_spread = metrics['CE_right']  
                
                # Zona cercana - 30% del máximo
                zones.append({
                    'distance': 'NEAR',
                    'threshold': max_spread * 0.3,
                    'fish_types': ['small_fish'],
                    'points': 10
                })
                
                # Zona media - 60% del máximo
                zones.append({
                    'distance': 'MEDIUM',
                    'threshold': max_spread * 0.6,
                    'fish_types': ['medium_fish'],
                    'points': 20
                })
                
                # Zona lejana - 90% del máximo
                zones.append({
                    'distance': 'FAR',
                    'threshold': max_spread * 0.9,
                    'fish_types': ['rare_fish'],
                    'points': 50
                })
        
        # Si no se pudieron crear las zonas, usar valores por defecto
        if not zones:
            return self._create_default_fishing_zones()
                
        return zones

    def _create_default_fishing_zones(self):
        """Crea zonas de pesca con valores predeterminados"""
        return [
            {'distance': 'NEAR', 'threshold': 10, 'fish_types': ['small_fish'], 'points': 10},
            {'distance': 'MEDIUM', 'threshold': 20, 'fish_types': ['medium_fish'], 'points': 20},
            {'distance': 'FAR', 'threshold': 30, 'fish_types': ['rare_fish'], 'points': 50}
        ]



    def run(self, animate):
        self.update(animate)
        self.draw()

    def _draw_fishing_zones(self):
        """Dibuja las zonas de pesca (para debugging)"""
        font = pygame.font.SysFont("Arial", 16)
        y_pos = 50
        
        for zone in self.fishing_zones:
            text = font.render(
                f"Zona {zone['distance']}: {zone['threshold']:.2f}", 
                True, (255, 255, 255)
            )
            self.displaySurface.blit(text, (10, y_pos))
            y_pos += 20
