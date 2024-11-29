# game/scripts/fisherman.py
import pygame
from game.scripts.configu_ration import SPEED_FISHERMAN, ANIMSPEED_FISHERMAN
from game.scripts.sprite_sheet import SpriteSheet

class Fisherman():
    def __init__(self, position, moveRight):
        self.position = position
        self.movingRight = moveRight
        self.animationIndex = 0
        self.animationSpeed = ANIMSPEED_FISHERMAN
        self.animation_finished = False
        self.current_animation_type = None
        self.hold_timer = None
        
        # Diccionario para almacenar las diferentes animaciones
        self.animations = {}
        
        # Cargar animación inicial
        self.load_animation("cast", "game/assets/sprites/cast_bobbin_Sheet-short")

    def load_animation(self, animation_type, animation_path):
        """
        Carga una nueva animación
        animation_type: 'cast', 'catch'
        """
        sprite_sheet = SpriteSheet(animation_path)
        self.animations[animation_type] = sprite_sheet.getSprites()
        
        if self.current_animation_type is None:
            self.current_animation_type = animation_type
            self.currentAnimation = self.animations[animation_type]
            self.image = self.currentAnimation[0]
            self.rect = self.image.get_rect(bottomleft=self.position)

    def start_animation(self, animation_type, hold_time=None):
        """
        Inicia una animación específica
        hold_time: tiempo en frames para mantener el último frame
        """
        if animation_type in self.animations:
            self.current_animation_type = animation_type
            self.currentAnimation = self.animations[animation_type]
            self.animationIndex = 0
            self.animation_finished = False
            self.hold_timer = hold_time
            self.image = self.currentAnimation[0]
            self.rect = self.image.get_rect(bottomleft=self.position)

    def update(self):
        if not self.animation_finished and self.currentAnimation:
            self.animationIndex += self.animationSpeed
            if self.animationIndex >= len(self.currentAnimation):
                print(f"Índice de animación: {self.animationIndex}, Longitud de animación: {len(self.currentAnimation)}")  # Debug
                self.animationIndex = len(self.currentAnimation) - 1  # Mantener último frame
                if self.hold_timer is not None:
                    if self.hold_timer > 0:
                        self.hold_timer -= 1
                        print(f"Hold timer: {self.hold_timer}")  # Debug
                    else:
                        print("Animación terminada")  # Debug
                        self.animation_finished = True
                else:
                    print("Animación terminada (sin hold timer)")  # Debug
                    self.animation_finished = True
            
            self.image = self.currentAnimation[int(self.animationIndex)]
    def draw(self, displaySurface):
        displaySurface.blit(self.image, self.rect)