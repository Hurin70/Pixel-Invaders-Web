import pygame

class Bala:
    def __init__(self, x, y, dx=0, dy=-10):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.ancho = 5
        self.alto = 10
        self.color = (255, 0, 0)  # Rojo
        self.velocidad_base = 10
        self.velocidad = self.velocidad_base
        self.direccion = (0, -1)  # Por defecto, disparar hacia arriba
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.sprite = None  # Añadido para evitar referencia a un atributo inexistente
        self.sprite_original = None

    def mover(self):
        """Mueve la bala según su dirección."""
        self.rect.x += self.dx
        self.rect.y += self.dy

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (255, 51, 0), self.rect)

    def redimensionar(self, factor_escala, sprite_original=None):
        self.ancho = max(2, int(5 * factor_escala))
        self.alto = max(4, int(10 * factor_escala))
        self.rect.width = self.ancho
        self.rect.height = self.alto
        if sprite_original:
            self.sprite_original = sprite_original
        if self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.ancho, self.alto))
        self.velocidad = max(1, int(self.velocidad_base * factor_escala))
        # Ajustar dx, dy si es necesario
        self.dx = int(self.dx * factor_escala) if self.dx != 0 else 0
        self.dy = int(self.dy * factor_escala) if self.dy != 0 else 0