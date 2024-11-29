# fish_system.py
import csv
import random
import os
import pygame



class FishDatabase:
    def __init__(self):
        self.fish_data = {}
        # Separar los peces por zonas según su valor
        self.fish_by_zone = {
            'short': [],   # Peces de valor bajo (0-40)
            'medium': [],  # Peces de valor medio (41-70)
            'long': []     # Peces de valor alto (71-100)
        }
        self.load_fish_data()

    def load_fish_data(self):
        csv_path = os.path.join('game', 'assets', 'fish', 'fish_info.csv')
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.fish_data[row['nombre_imagen']] = row
                
                # Clasificar peces por su valor
                valor = int(row['valor'])
                if valor <= 40:
                    self.fish_by_zone['short'].append(row['nombre_imagen'])
                elif valor <= 70:
                    self.fish_by_zone['medium'].append(row['nombre_imagen'])
                else:
                    self.fish_by_zone['long'].append(row['nombre_imagen'])

    def get_random_fish(self, cast_type):
        """Obtiene un pez aleatorio de la zona correspondiente al tipo de lanzamiento"""
        # Seleccionar un pez aleatorio de la zona correspondiente
        fish_image = random.choice(self.fish_by_zone[cast_type])
        return self.fish_data[fish_image]

class FishInfoWindow:
    def __init__(self, display_surface, fish_info, game_width, font_large=None, font_medium=None, points_earned=None):
     
        self.points_earned = points_earned
        self.display_surface = display_surface
        self.fish_info = fish_info
        
        # Cargar imagen del pez
        image_path = os.path.join('game', 'assets', 'fish', 'fish_image', fish_info['nombre_imagen'])
        self.fish_image = pygame.image.load(image_path).convert_alpha()
        
        # Dimensiones de la ventana
        self.width = 600
        self.height = 400
        self.x = (game_width - self.width) // 2
        self.y = (display_surface.get_height() - self.height) // 2
        
        # Usar las fuentes del juego
        self.title_font = font_large or pygame.font.SysFont("Arial", 36)
        self.text_font = font_medium or pygame.font.SysFont("Arial", 24)
        
        # Colores según tipo de pez
        self.type_colors = {
            'Común': (150, 150, 150),
            'Raro': (100, 200, 255),
            'Exótico': (255, 150, 50),
            'Legendario': (255, 215, 0)
        }
        
    def draw(self):
        # Fondo semi-transparente
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(230)
        s.fill((50, 50, 50))
        self.display_surface.blit(s, (self.x, self.y))
        
        # Borde de la ventana
        window_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.display_surface, self.type_colors[self.fish_info['tipo_de_pez']], window_rect, 3)
        
        # Imagen del pez (reducida a 150x150)
        scaled_image = pygame.transform.scale(self.fish_image, (150, 150))
        image_rect = scaled_image.get_rect(topleft=(self.x + 20, self.y + 20))
        self.display_surface.blit(scaled_image, image_rect)
        
        # Información del pez con posiciones ajustadas
        title = self.title_font.render(self.fish_info['nombre_pez'], True, 
                                     self.type_colors[self.fish_info['tipo_de_pez']])
        title_rect = title.get_rect(topleft=(self.x + 190, self.y + 20))
        self.display_surface.blit(title, title_rect)
        
        info_texts = [
                    f"Tipo: {self.fish_info['tipo_de_pez']}",
                    f"Ecosistema: {self.fish_info['Ecosistema']}",
                    f"Valor: {self.fish_info['valor']} puntos",  # Modificado para mostrar 'puntos'
                    f"Características: {self.fish_info['descripcion']}"
                ]
        
        for i, text in enumerate(info_texts):
            text_surface = self.text_font.render(text, True, (255, 255, 255))
            # Asegurar que el texto no se salga usando word wrap si es necesario
            if text.startswith("Características:"):
                # Separar las características en múltiples líneas si es necesario
                desc = self.fish_info['descripcion']
                text_surface = self.text_font.render(f"Características:", True, (255, 255, 255))
                desc_surface = self.text_font.render(desc, True, (255, 255, 255))
                self.display_surface.blit(text_surface, (self.x + 190, self.y + 80 + i * 35))
                self.display_surface.blit(desc_surface, (self.x + 190, self.y + 80 + (i + 1) * 35))
            else:
                self.display_surface.blit(text_surface, (self.x + 190, self.y + 80 + i * 35))
        
        
        # Instrucción para continuar en la parte inferior de la ventana
        continue_text = self.text_font.render("Presiona ESPACIO para continuar", True, (200, 200, 200))
        text_rect = continue_text.get_rect(centerx=self.x + self.width//2, 
                                         bottom=self.y + self.height - 20)
        self.display_surface.blit(continue_text, text_rect)

        # Mostrar puntos ganados si están disponibles
        if self.points_earned is not None:
            points_text = self.title_font.render(f"+{self.points_earned}", True, (50, 255, 50))
            points_rect = points_text.get_rect(topright=(self.x + self.width - 20, self.y + 20))
            self.display_surface.blit(points_text, points_rect)