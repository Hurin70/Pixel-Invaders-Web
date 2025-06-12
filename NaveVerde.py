import random
import pygame
import math
from Enemigo import Enemigo
from BalaEnemiga import BalaEnemiga 

class NaveVerde(Enemigo):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite = None
        self.amplitud = random.randint(80, 200) # Amplitud aleatoria
        self.velocidad_pendulo = random.uniform(0.005, 0.012) # Velocidad de oscilación aleatoria
        self.fase = random.uniform(0, 2 * math.pi) # Fase aleatoria de la oscilación
        self.x_inicial = x
        self.tiempo_inicio = pygame.time.get_ticks() # Tiempo de inicio de la oscilación
        self.velocidad_caida = random.randint(2, 4) # Velocidad de caída aleatoria
        self.ultimo_disparo = pygame.time.get_ticks() 
        self.tiempo_entre_disparos = random.randint(1200, 2200)  # ms

    def movimiento(self):
        tiempo = (pygame.time.get_ticks() - self.tiempo_inicio)
        self.rect.x = int(
            max(0, min(900 - self.rect.width,
                self.x_inicial + self.amplitud * math.sin(self.velocidad_pendulo * tiempo + self.fase)
            ))
        )
        self.rect.y += self.velocidad_caida

    def disparar(self, balas_enemigas):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.tiempo_entre_disparos:
            bala = BalaEnemigaVerde(self.rect.centerx, self.rect.bottom)
            balas_enemigas.append(bala)
            self.ultimo_disparo = ahora
            self.tiempo_entre_disparos = random.randint(1200, 2200)

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, (0, 255, 0), self.rect)

    def redimensionar(self, factor_escala, sprite_original=None):
        super().redimensionar(factor_escala, sprite_original)
        self.amplitud = int(self.amplitud * factor_escala)
        self.velocidad_pendulo = self.velocidad_pendulo * factor_escala
        self.velocidad_caida = max(1, int(self.velocidad_caida * factor_escala))
        self.tiempo_entre_disparos = int(self.tiempo_entre_disparos / factor_escala) if hasattr(self, 'tiempo_entre_disparos') else 1500
    
class BalaEnemigaVerde(BalaEnemiga):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 255, 0)  # Verde

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