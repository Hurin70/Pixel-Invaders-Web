import random
import pygame
from Enemigo import Enemigo
from BalaEnemiga import BalaEnemiga

class BalaEnemigaRoja(BalaEnemiga):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 0, 0)

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

class NaveRoja(Enemigo):
    def __init__(self, ancho_pantalla, alto_pantalla):
        esquina = random.choice(['izquierda', 'derecha'])
        if esquina == 'izquierda':
            x = 0
        else:
            x = ancho_pantalla - 75
        y = alto_pantalla - 75
        super().__init__(x, y)
        self.sprite = None
        self.vida = 5
        self.en_superior = False
        self.velocidad_y = -4
        self.velocidad_x = 3 if esquina == 'izquierda' else -3
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.ultimo_disparo = pygame.time.get_ticks()
        self.tiempo_entre_disparos = random.randint(900, 1500)

    def movimiento(self):
        if not self.en_superior:
            self.rect.y += self.velocidad_y
            if self.rect.y <= 10:
                self.rect.y = 10
                self.en_superior = True
        else:
            self.rect.x += self.velocidad_x
            if self.rect.left <= 0 or self.rect.right >= self.ancho_pantalla:
                self.velocidad_x *= -1

    def disparar(self, balas_enemigas):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.tiempo_entre_disparos:
            bala = BalaEnemigaRoja(self.rect.centerx, self.rect.bottom)
            balas_enemigas.append(bala)
            self.ultimo_disparo = ahora
            self.tiempo_entre_disparos = random.randint(900, 1500)

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (255, 0, 0), self.rect)

    def redimensionar(self, factor_escala, sprite_original=None):
        super().redimensionar(factor_escala, sprite_original)
        self.velocidad_x = int((self.velocidad_x/abs(self.velocidad_x)) * max(1, abs(self.velocidad_x) * factor_escala)) if self.velocidad_x != 0 else 0
        self.velocidad_y = int(-4 * factor_escala)
        self.tiempo_entre_disparos = int(self.tiempo_entre_disparos / factor_escala) if hasattr(self, 'tiempo_entre_disparos') else 1000