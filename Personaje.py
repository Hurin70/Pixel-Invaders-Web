import pygame

class Nave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho_base = 50
        self.alto_base = 50
        self.velocidad_base = 10
        self.velocidad = self.velocidad_base
        self.color = (0, 0, 255)  # Azul
        self.rect = pygame.Rect(self.x, self.y, self.ancho_base, self.alto_base)
        self.sprite = None  # Añadido para evitar referencia a un atributo inexistente
        self.sprite_original = None

    def mover(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, self.color, self.rect)

    def crear_bala(self, x, y, dx, dy, sprite_bala):
        from Bala import Bala  # Importación local para evitar ciclos
        bala = Bala(x, y, dx, dy)
        bala.sprite = sprite_bala
        return bala

    def redimensionar(self, factor_escala, sprite_original=None):
        self.ancho = int(self.ancho_base * factor_escala)
        self.alto = int(self.alto_base * factor_escala)
        self.rect.width = self.ancho
        self.rect.height = self.alto
        if sprite_original:
            self.sprite_original = sprite_original
        if self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.ancho, self.alto))
        self.velocidad = max(1, int(self.velocidad_base * factor_escala))
        # Ajustar posición para que no salga de pantalla
        self.rect.x = min(self.rect.x, max(0, self.rect.x))
        self.rect.y = min(self.rect.y, max(0, self.rect.y))
