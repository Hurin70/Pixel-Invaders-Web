import pygame

class Enemigo:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 75
        self.alto = 75
        
        self.color = (128, 0, 128)  # Morado
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.vida = 5
        self.pausado = False
        self.sprite = None  # Añadido para evitar referencia a un atributo inexistente
        self.sprite_original = None  # Para escalado
        self.velocidad_base = 5
        self.velocidad = self.velocidad_base

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (153, 0, 204), self.rect)

    def movimiento(self):
        if not self.pausado:  # Solo moverse si no está pausado
            self.y += self.velocidad
            self.rect.y = self.y  # Actualiza la posición del rectángulo con la nueva posición

    def redimensionar(self, factor_escala, sprite_original=None):
        self.ancho = int(75 * factor_escala)
        self.alto = int(75 * factor_escala)
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