import pygame

# Clase para manejar las explosiones
class Explosion:
    def __init__(self, x, y, tamaño=100):
        self.x = x
        self.y = y
        self.tamaño_base = tamaño
        self.tamaño = tamaño
        self.frame = 0
        self.max_frames = 10
        self.rect = pygame.Rect(self.x - tamaño//2, self.y - tamaño//2, tamaño, tamaño)
        self.sprite = None
        self.sprite_original = None
    
    def asignar_sprite(self, sprite):
        """Asigna un sprite a la explosión."""
        self.sprite_original = sprite
        self.sprite = pygame.transform.scale(sprite, (self.tamaño, self.tamaño))
    
    def redimensionar(self, factor_escala, sprite_original=None):
        self.tamaño = int(self.tamaño_base * factor_escala)
        self.rect.width = self.tamaño
        self.rect.height = self.tamaño
        self.rect.x = self.x - self.tamaño // 2
        self.rect.y = self.y - self.tamaño // 2
        if sprite_original:
            self.sprite_original = sprite_original
        if self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.tamaño, self.tamaño))
    
    def actualizar(self):
        self.frame += 1
        return self.frame > self.max_frames
    
    def dibujar(self, ventana):
        if self.sprite:
            # Escalar el sprite según el progreso de la animación
            escala = 1 + (self.frame / self.max_frames) * 0.5
            tamaño_actual = int(self.tamaño * escala)
            sprite_escalado = pygame.transform.scale(self.sprite, (tamaño_actual, tamaño_actual))
            
            # Calcular la posición centralizada
            x = self.x - tamaño_actual // 2
            y = self.y - tamaño_actual // 2
            
            # Ajustar la transparencia
            alpha = 255 * (1 - (self.frame / self.max_frames))
            sprite_escalado.set_alpha(alpha)
            
            ventana.blit(sprite_escalado, (x, y))
        else:
            # Fallback si no hay sprite
            radio = int(self.tamaño/2 * (1 - self.frame/self.max_frames))
            alpha = 255 * (1 - (self.frame / self.max_frames))
            color = (255, 200, 0, alpha)
            
            superficie_temp = pygame.Surface((2*radio, 2*radio), pygame.SRCALPHA)
            pygame.draw.circle(superficie_temp, color, (radio, radio), radio)
            ventana.blit(superficie_temp, (self.x - radio, self.y - radio))