import pygame
import json
import os
from datetime import datetime
from game.scripts.background import Background, MenuBackground

class MetricsViewer:
    def __init__(self, display_surface, font_large=None, font_medium=None):
        self.display_surface = display_surface
        self.font_large = font_large or pygame.font.SysFont("Arial", 36)
        self.font_medium = font_medium or pygame.font.SysFont("Arial", 24)
        self.background = MenuBackground()
        
        self.selected_session = None
        self.showing_details = False
        
        self.buttons = []
        self.load_metrics()

    def load_metrics(self):
        """Carga todas las métricas disponibles"""
        self.metrics_data = []
        metrics_dir = os.path.join('game', 'data', 'metrics')
        
        if os.path.exists(metrics_dir):
            for filename in os.listdir(metrics_dir):
                if filename.startswith('metrics_') and filename.endswith('.json'):
                    try:
                        with open(os.path.join(metrics_dir, filename), 'r') as f:
                            data = json.load(f)
                            self.metrics_data.append(data)
                    except Exception as e:
                        print(f"Error loading metrics file {filename}: {e}")
        
        # Ordenar por fecha más reciente
        self.metrics_data.sort(key=lambda x: x['session_id'], reverse=True)

    def create_session_buttons(self):
        """Crea botones para cada sesión"""
        self.buttons = []
        y = 100
        for session in self.metrics_data:
            date = datetime.strptime(session['session_id'], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M')
            gesto_nombre = {
                'NSM_SPREAD': 'Sonrisa',
                'NSM_OPEN': 'Apertura',
                'NSM_KISS': 'Beso'
            }.get(session['gesto'], session['gesto'])
            
            total_intentos = len(session.get('intentos', []))
            
            text = f"{date} - {gesto_nombre} - Total intentos: {total_intentos}"
            button = {
                'rect': pygame.Rect(50, y, self.display_surface.get_width() - 100, 40),
                'text': text,
                'session': session
            }
            self.buttons.append(button)
            y += 50

    def draw_session_list(self):
        """Dibuja la lista de sesiones como botones"""
        # Dibujar el fondo
        self.background.draw(self.display_surface)
        
        # Agregar overlay semi-transparente para mejor legibilidad
        overlay = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.display_surface.blit(overlay, (0, 0))
        
        # Título
        title = self.font_large.render("Sesiones de Ejercicio", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.display_surface.get_width()//2, y=20)
        self.display_surface.blit(title, title_rect)
        
        # Dibujar botones de sesiones
        for button in self.buttons:
            # Dibujar fondo del botón
            button_surface = pygame.Surface((button['rect'].width, button['rect'].height))
            color = (100, 100, 100) if button['session'] != self.selected_session else (50, 150, 50)
            button_surface.fill(color)
            button_surface.set_alpha(200)
            self.display_surface.blit(button_surface, button['rect'])
            pygame.draw.rect(self.display_surface, (200, 200, 200), button['rect'], 2)
            
            # Dibujar texto del botón
            text_surf = self.font_medium.render(button['text'], True, (255, 255, 255))
            text_rect = text_surf.get_rect(midleft=(button['rect'].left + 10, button['rect'].centery))
            self.display_surface.blit(text_surf, text_rect)

        # Instrucciones
        instructions = self.font_medium.render("↑↓: Seleccionar   ENTER: Ver detalles   ESC: Volver", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(centerx=self.display_surface.get_width()//2, bottom=self.display_surface.get_height()-20)
        self.display_surface.blit(instructions, instructions_rect)

    def draw_session_details(self):
        """Dibuja los detalles de la sesión seleccionada"""
        # Dibujar el fondo
        self.background.draw(self.display_surface)
        
        # Agregar overlay semi-transparente para mejor legibilidad
        overlay = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.display_surface.blit(overlay, (0, 0))
        
        session = self.selected_session
        y = 20

        # Título con fecha y gesto
        date = datetime.strptime(session['session_id'], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M')
        gesto_nombre = {
            'NSM_SPREAD': 'Sonrisa',
            'NSM_OPEN': 'Apertura',
            'NSM_KISS': 'Beso'
        }.get(session['gesto'], session['gesto'])
        
        title = self.font_large.render(f"Sesión: {date} - {gesto_nombre}", True, (255, 215, 0))
        self.display_surface.blit(title, (20, y))
        y += 60

        # Distribución de lanzamientos
        intentos = session.get('intentos', [])
        cortos = sum(1 for i in intentos if i['tipo_lanzamiento'] == 'short')
        medios = sum(1 for i in intentos if i['tipo_lanzamiento'] == 'medium')
        largos = sum(1 for i in intentos if i['tipo_lanzamiento'] == 'long')
        dist_text = f"Distribución - Corto: {cortos}, Medio: {medios}, Largo: {largos}"
        dist_surf = self.font_medium.render(dist_text, True, (255, 255, 255))
        self.display_surface.blit(dist_surf, (20, y))
        y += 40

        # Detalles de los intentos
        if 'intentos' in session:
            intentos_title = self.font_medium.render("Intentos:", True, (255, 215, 0))
            self.display_surface.blit(intentos_title, (20, y))
            y += 30
            
            # Headers
            headers = []
            if session['gesto'] == 'NSM_SPREAD':
                headers = ['Intento', 'CE Der', 'CE Izq', 'SA Der', 'SA Izq', 'Tipo']
            elif session['gesto'] == 'NSM_OPEN':
                headers = ['Intento', 'DS Der', 'DS Izq', 'UVH Der', 'UVH Izq', 'LVH Der', 'LVH Izq', 'Tipo']
            elif session['gesto'] == 'NSM_KISS':
                headers = ['Intento', 'CH', 'CE', 'Tipo']

            # Dibujar headers
            x = 20
            for header in headers:
                text = self.font_medium.render(header, True, (200, 200, 200))
                self.display_surface.blit(text, (x, y))
                x += 100 if session['gesto'] != 'NSM_OPEN' else 80  # Ajuste para NSM_OPEN
            y += 30

            # Dibujar datos de intentos
            for intento in session['intentos']:
                x = 20
                values = []
                if session['gesto'] == 'NSM_SPREAD':
                    values = [str(intento['intento']), f"{intento['CE_right']:.1f}", f"{intento['CE_left']:.1f}",
                            f"{intento['SA_right']:.1f}", f"{intento['SA_left']:.1f}", intento['tipo_lanzamiento']]
                elif session['gesto'] == 'NSM_OPEN':
                    values = [str(intento['intento']), f"{intento['DS_right']:.1f}", f"{intento['DS_left']:.1f}",
                            f"{intento['UVH_right']:.1f}", f"{intento['UVH_left']:.1f}",
                            f"{intento['LVH_right']:.1f}", f"{intento['LVH_left']:.1f}", intento['tipo_lanzamiento']]
                elif session['gesto'] == 'NSM_KISS':
                    values = [str(intento['intento']), f"{intento['CH']:.1f}", f"{intento['CE']:.1f}",
                            intento['tipo_lanzamiento']]

                for value in values:
                    text = self.font_medium.render(value, True, (255, 255, 255))
                    self.display_surface.blit(text, (x, y))
                    x += 100 if session['gesto'] != 'NSM_OPEN' else 80  # Ajuste para NSM_OPEN
                y += 25

        # Agregar línea separadora
        y += 20
        pygame.draw.line(self.display_surface, (200, 200, 200), 
                        (20, y), (self.display_surface.get_width() - 20, y), 2)
        y += 20

        # Mostrar promedios y máximos
        if 'resumen' in session:
            resumen_title = self.font_medium.render("Resumen:", True, (255, 215, 0))
            self.display_surface.blit(resumen_title, (20, y))
            y += 30

            promedios = session['resumen']['promedios']
            maximos = session['resumen']['maximos']
            
            # Headers
            prom_text = self.font_medium.render("Promedios:", True, (200, 200, 200))
            max_text = self.font_medium.render("Máximos:", True, (200, 200, 200))
            self.display_surface.blit(prom_text, (40, y))
            self.display_surface.blit(max_text, (400, y))
            y += 30

            # Mostrar valores según el gesto
            if session['gesto'] == 'NSM_SPREAD':
                metrics = [
                    ('CE derecho', 'CE_right'),
                    ('CE izquierdo', 'CE_left'),
                    ('SA derecho', 'SA_right'),
                    ('SA izquierdo', 'SA_left')
                ]
            elif session['gesto'] == 'NSM_OPEN':
                metrics = [
                    ('DS derecho', 'DS_right'),
                    ('DS izquierdo', 'DS_left'),
                    ('UVH dev', 'UVH_dev'),
                    ('LVH dev', 'LVH_dev')
                ]
            elif session['gesto'] == 'NSM_KISS':
                metrics = [
                    ('CH', 'CH'),
                    ('CE', 'CE')
                ]

            for label, key in metrics:
                if key in promedios:
                    prom = f"{label}: {promedios[key]:.2f}"
                    max_val = f"{label}: {maximos[key]:.2f}"
                    prom_surf = self.font_medium.render(prom, True, (255, 255, 255))
                    max_surf = self.font_medium.render(max_val, True, (255, 255, 255))
                    self.display_surface.blit(prom_surf, (40, y))
                    self.display_surface.blit(max_surf, (400, y))
                    y += 25

        # Instrucciones
        instructions = self.font_medium.render("ESC: Volver a la lista", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(centerx=self.display_surface.get_width()//2, 
                                                bottom=self.display_surface.get_height()-20)
        self.display_surface.blit(instructions, instructions_rect)

    def show(self):
        self.create_session_buttons()
        running = True
        selected_index = 0 if self.buttons else -1

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if self.showing_details:
                        if event.key == pygame.K_ESCAPE:
                            self.showing_details = False
                    else:
                        if event.key == pygame.K_UP and selected_index > 0:
                            selected_index -= 1
                        elif event.key == pygame.K_DOWN and selected_index < len(self.buttons) - 1:
                            selected_index += 1
                        elif event.key == pygame.K_RETURN and selected_index >= 0:
                            self.selected_session = self.buttons[selected_index]['session']
                            self.showing_details = True
                        elif event.key == pygame.K_ESCAPE:
                            return True

            if selected_index >= 0:
                self.selected_session = self.buttons[selected_index]['session']

            if self.showing_details:
                self.draw_session_details()
            else:
                self.draw_session_list()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        return True