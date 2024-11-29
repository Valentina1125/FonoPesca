import pygame
from game.scripts.background import Background, MenuBackground

class CompletionWindow:
    def __init__(self, display_surface, gesto, font_large=None, font_medium=None):
        self.display_surface = display_surface
        self.background = MenuBackground()
        self.font_large = font_large or pygame.font.SysFont("Arial", 36)
        self.font_medium = font_medium or pygame.font.SysFont("Arial", 24)
        
        # Traduce el nombre del gesto para mostrar
        self.gesto_nombre = {
            'NSM_SPREAD': 'Sonrisa',
            'NSM_OPEN': 'Apertura de Boca',
            'NSM_KISS': 'Beso'
        }.get(gesto, gesto)
        
        # Dimensiones de la ventana
        self.width = 600
        self.height = 400
        self.x = (display_surface.get_width() - self.width) // 2
        self.y = (display_surface.get_height() - self.height) // 2

    def show(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                        return True

            # Dibujar el fondo
            self.background.draw(self.display_surface)
            
            # Overlay semi-transparente para toda la pantalla
            overlay = pygame.Surface(self.display_surface.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.display_surface.blit(overlay, (0, 0))
            
            # Panel central
            panel = pygame.Surface((self.width, self.height))
            panel.fill((30, 30, 30))
            panel_rect = panel.get_rect(center=(self.display_surface.get_width() // 2, 
                                              self.display_surface.get_height() // 2))
            
            # Borde dorado para el panel
            pygame.draw.rect(panel, (255, 215, 0), panel.get_rect(), 3)
            self.display_surface.blit(panel, panel_rect)

            # Título
            title = self.font_large.render("¡Sesión Completada!", True, (255, 215, 0))
            title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 40)
            self.display_surface.blit(title, title_rect)

            # Mensaje principal
            messages = [
                f"Has completado tu sesión de ejercicios",
                f"del gesto: {self.gesto_nombre}",
                "",
                "Recuerda mantener una práctica constante",
                "para obtener mejores resultados"
            ]

            y = title_rect.bottom + 40
            for message in messages:
                text = self.font_medium.render(message, True, (255, 255, 255))
                text_rect = text.get_rect(centerx=panel_rect.centerx, top=y)
                self.display_surface.blit(text, text_rect)
                y += 40

            # Instrucciones
            instructions = self.font_medium.render("Presiona ESPACIO o ENTER para continuar", True, (200, 200, 200))
            instructions_rect = instructions.get_rect(centerx=panel_rect.centerx, bottom=panel_rect.bottom - 30)
            self.display_surface.blit(instructions, instructions_rect)

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        return True