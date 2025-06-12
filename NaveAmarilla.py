import random
import pygame
import math
from Enemigo import Enemigo
from BalaEnemiga import BalaEnemiga

class BalaEnemigaAmarilla(BalaEnemiga):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y)
        self.color = (255, 255, 0)  # Amarillo
        self.dx = dx
        self.dy = dy

    def mover(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, self.rect)

    def redimensionar(self, factor_escala, sprite_original=None):
        self.ancho = max(2, int(5 * factor_escala))
        self.alto = max(4, int(10 * factor_escala))
        self.rect.width = self.ancho
        self.rect.height = self.alto
        if sprite_original:
            self.sprite_original = sprite_original
        if hasattr(self, 'sprite_original') and self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.ancho, self.alto))
        self.dx = int(self.dx * factor_escala) if hasattr(self, 'dx') else 0
        self.dy = int(self.dy * factor_escala) if hasattr(self, 'dy') else 0

class NaveAmarilla(Enemigo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite = None
        self.velocidad_x = random.choice([-3, 3])
        self.velocidad_y = 2
        self.ultimo_disparo = pygame.time.get_ticks()
        self.tiempo_entre_disparos = 1200

    def movimiento(self):
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y
        if self.rect.left < 0 or self.rect.right > 900:
            self.velocidad_x *= -1

    def disparar(self, balas_enemigas, nave_principal):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.tiempo_entre_disparos:
            dx = nave_principal.rect.centerx - self.rect.centerx
            dy = nave_principal.rect.centery - self.rect.centery
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                distancia = 1
            velocidad = 6
            dx = int(velocidad * dx / distancia)
            dy = int(velocidad * dy / distancia)
            bala = BalaEnemigaAmarilla(self.rect.centerx, self.rect.centery, dx, dy)
            balas_enemigas.append(bala)
            self.ultimo_disparo = ahora

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (255, 255, 0), self.rect)

    def redimensionar(self, factor_escala, sprite_original=None):
        super().redimensionar(factor_escala, sprite_original)
        self.velocidad_x = int((self.velocidad_x/abs(self.velocidad_x)) * max(1, abs(self.velocidad_x) * factor_escala)) if self.velocidad_x != 0 else 0
        self.velocidad_y = max(1, int(2 * factor_escala))
        self.tiempo_entre_disparos = int(1200 / factor_escala)