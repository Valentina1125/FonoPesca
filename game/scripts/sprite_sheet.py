import pygame
import os  # Importa el módulo os para trabajar con rutas de archivos
from game.scripts.configu_ration import *  # Importa configuraciones como las dimensiones de la ventana

# Clase que gestiona múltiples sprites a partir de una carpeta de imágenes
class SpriteSheet():

    def __init__(self, spritesFolderPath):
        # Inicializa la lista que almacenará los sprites
        self.sprites = []
        
        # Recorre todos los archivos en la carpeta especificada
        for spriteFile in sorted(os.listdir(spritesFolderPath)):  # Ordena los archivos para mantener el orden de los sprites
            spritePath = os.path.join(spritesFolderPath, spriteFile)  # Obtiene la ruta completa del archivo
            
            # Carga cada imagen individual del sprite
            sprite = pygame.image.load(spritePath).convert_alpha()  # Carga la imagen y la convierte con canal alfa
            
            # Agrega el sprite a la lista de sprites
            self.sprites.append(sprite)

    # Método para obtener los sprites
    def getSprites(self):
        return self.sprites  # Devuelve los sprites normales