import pygame
import math

class Escudo:
    """Escudo que protege la nave durante 5 impactos."""
    def __init__(self, nave, burbuja_img, duracion=5):
        self.nave = nave
        self.duracion = duracion
        self.activo = True
        self.burbuja_img = burbuja_img

    def recibir_golpe(self):
        if self.activo:
            self.duracion -= 1
            if self.duracion <= 0:
                self.activo = False

    def dibujar(self, ventana):
        if self.activo:
            # Centrar la burbuja sobre la nave
            burbuja_rect = self.burbuja_img.get_rect(center=self.nave.rect.center)
            ventana.blit(self.burbuja_img, burbuja_rect)

    def redimensionar(self, factor_escala, burbuja_img_original=None):
        if burbuja_img_original:
            self.burbuja_img = pygame.transform.smoothscale(burbuja_img_original, (int(self.nave.rect.width * 1.3), int(self.nave.rect.height * 1.3)))

class DisparoTriple:
    def __init__(self, nave):
        self.nave = nave
        self.activo = True

    def disparar(self, balas, sprite_bala):
        balas.append(self.nave.crear_bala(self.nave.rect.centerx - 5, self.nave.rect.top, 0, -10, sprite_bala))
        balas.append(self.nave.crear_bala(self.nave.rect.centerx - 5, self.nave.rect.top, -3, -10, sprite_bala))
        balas.append(self.nave.crear_bala(self.nave.rect.centerx - 5, self.nave.rect.top, 3, -10, sprite_bala))

    def redimensionar(self, factor_escala):
        pass  # No requiere escalado visual

# Lista de modificadores disponibles para la nave naranja
# Solo Escudo y DisparoTriple
MODIFICADORES_DISPONIBLES = [
    lambda jugador, burbuja_escudo_img=None: Escudo(jugador, burbuja_escudo_img) if burbuja_escudo_img else DisparoTriple(jugador),
    lambda jugador, burbuja_escudo_img=None: DisparoTriple(jugador)
]