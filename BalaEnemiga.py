import pygame

class BalaEnemiga:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 5
        self.alto = 10
        self.color = (0, 0, 255)  # Azul para las balas del jefe
        self.velocidad_base = 5
        self.velocidad = self.velocidad_base
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.sprite = None  # Añadido para evitar referencia a un atributo inexistente
        self.sprite_original = None

    def mover(self):
        """Mueve la bala hacia abajo."""
        self.y += self.velocidad
        self.rect.y = self.y

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (0, 102, 255), self.rect)

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