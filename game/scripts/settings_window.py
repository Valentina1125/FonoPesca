# settings.py
import pygame
import json
import os
from game.scripts.background import Background, MenuBackground

class SettingsWindow:
   def __init__(self, display_surface, font_large=None, font_medium=None):
       self.display_surface = display_surface
       self.font_large = font_large or pygame.font.SysFont("Arial", 36)
       self.font_medium = font_medium or pygame.font.SysFont("Arial", 24)
       self.background = MenuBackground()
       
       # Cargar configuraciones existentes o usar valores por defecto
       self.settings = SettingsWindow.load_settings()
       
       # Control de selección y edición
       self.selected_option = 0
       self.editing = False
       self.current_value = ""
       
       # Definir opciones configurables
       self.options = [
           {"name": "Tiempo corto (segundos)", "key": "short_time", "value": self.settings['short_time'], "type": "number"},
           {"name": "Tiempo medio (segundos)", "key": "medium_time", "value": self.settings['medium_time'], "type": "number"},
           {"name": "Tiempo largo (segundos)", "key": "long_time", "value": self.settings['long_time'], "type": "number"},
           {"name": "Número de repeticiones", "key": "repetitions", "value": self.settings['repetitions'], "type": "number"},
           {"name": "Modo de juego", "key": "game_mode", "value": self.settings.get('game_mode', 'simple'), "type": "toggle", 
            "options": ['simple', 'avanzado']}
       ]

   @staticmethod
   def load_settings():
       """Método estático para cargar configuraciones"""
       try:
           settings_path = os.path.join('game', 'data', 'settings.json')
           if os.path.exists(settings_path):
               with open(settings_path, 'r') as f:
                   return json.load(f)
       except Exception as e:
           print(f"Error loading settings: {e}")
       
       # Valores por defecto
       return {
           'short_time': 2,
           'medium_time': 4,
           'long_time': 6,
           'repetitions': 10,
           'game_mode': 'simple'
       }

   def save_settings(self):
       try:
           settings_path = os.path.join('game', 'data', 'settings.json')
           os.makedirs(os.path.dirname(settings_path), exist_ok=True)
           with open(settings_path, 'w') as f:
               json.dump(self.settings, f, indent=2)
           print("Settings saved successfully")
       except Exception as e:
           print(f"Error saving settings: {e}")

   def handle_input(self, event):
       if self.editing:
           current_option = self.options[self.selected_option]
           if current_option["type"] == "number":
               if event.type == pygame.KEYDOWN:
                   if event.key == pygame.K_RETURN:
                       try:
                           value = int(self.current_value)
                           if value > 0:
                               current_option["value"] = value
                               self.settings[current_option["key"]] = value
                               self.save_settings()
                       except ValueError:
                           pass
                       self.editing = False
                       self.current_value = ""
                   elif event.key == pygame.K_BACKSPACE:
                       self.current_value = self.current_value[:-1]
                   elif event.key == pygame.K_ESCAPE:
                       self.editing = False
                       self.current_value = ""
                   elif event.unicode.isnumeric():
                       self.current_value += event.unicode
           elif current_option["type"] == "toggle":
               if event.type == pygame.KEYDOWN:
                   if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                       # Cambiar entre opciones
                       current_index = current_option["options"].index(current_option["value"])
                       next_index = (current_index + 1) % len(current_option["options"])
                       current_option["value"] = current_option["options"][next_index]
                       self.settings[current_option["key"]] = current_option["value"]
                       self.save_settings()
                       self.editing = False
                   elif event.key == pygame.K_ESCAPE:
                       self.editing = False
       else:
           if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_UP:
                   self.selected_option = (self.selected_option - 1) % len(self.options)
               elif event.key == pygame.K_DOWN:
                   self.selected_option = (self.selected_option + 1) % len(self.options)
               elif event.key == pygame.K_RETURN:
                   self.editing = True
                   if self.options[self.selected_option]["type"] == "number":
                       self.current_value = str(self.options[self.selected_option]["value"])
               elif event.key == pygame.K_ESCAPE:
                   return False
       return True

   def draw(self):
       # Dibujar el fondo
       self.background.draw(self.display_surface)
       
       # Agregar overlay semi-transparente para mejor legibilidad
       overlay = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
       overlay.fill((0, 0, 0))
       overlay.set_alpha(180)
       self.display_surface.blit(overlay, (0, 0))
       
       # Título
       title = self.font_large.render("Configuración", True, (255, 215, 0))
       title_rect = title.get_rect(centerx=self.display_surface.get_width()//2, y=20)
       self.display_surface.blit(title, title_rect)
       
       # Panel semi-transparente para las opciones
       options_surface = pygame.Surface((self.display_surface.get_width() - 100, len(self.options) * 60 + 40))
       options_surface.fill((20, 20, 20))
       options_surface.set_alpha(200)
       options_rect = options_surface.get_rect(centerx=self.display_surface.get_width()//2, top=100)
       self.display_surface.blit(options_surface, options_rect)
       
       # Opciones
       y = 100
       for i, option in enumerate(self.options):
           # Color según selección
           color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
           
           if option["type"] == "number":
               # Nombre de la opción numérica
               text = f"{option['name']}: "
               if self.editing and i == self.selected_option:
                   text += self.current_value + "_"
               else:
                   text += str(option['value'])
           else:  # toggle
               # Para opciones tipo toggle
               text = f"{option['name']}: < {option['value'].upper()} >"
           
           text_surface = self.font_medium.render(text, True, color)
           text_rect = text_surface.get_rect(x=50, y=y)
           self.display_surface.blit(text_surface, text_rect)
           
           y += 50

       # Instrucciones
       instructions = [
           "↑↓: Seleccionar   ENTER: Editar   ESC: Volver",
           "Durante edición: ENTER para guardar, ESC para cancelar"
       ]
       
       y = self.display_surface.get_height() - 60
       for instruction in instructions:
           text = self.font_medium.render(instruction, True, (200, 200, 200))
           text_rect = text.get_rect(centerx=self.display_surface.get_width()//2, y=y)
           self.display_surface.blit(text, text_rect)
           y += 30

   def show(self):
       running = True
       while running:
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   return None
               if not self.handle_input(event):
                   return self.settings

           self.draw()
           pygame.display.flip()
           pygame.time.Clock().tick(60)

       return self.settings