import random
import pygame
from NaveVerde import NaveVerde

class NaveNaranja(NaveVerde):
    def __init__(self, x, y, ancho_pantalla, alto_pantalla):
        super().__init__(x, y) # Inicializa NaveVerde con x, y
        self.sprite = None  # Se asignará desde SpriteManager si existe
        self.color = (255, 140, 0)  # Naranja
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.vida = 3
        self.modificador_otorgado = False

    def otorgar_modificador(self, jugador, lista_modificadores, burbuja_escudo_img=None):
        if not self.modificador_otorgado:
            import Modificadores
            modificador_func = random.choice(Modificadores.MODIFICADORES_DISPONIBLES)
            mod = modificador_func(jugador, burbuja_escudo_img)
            lista_modificadores.append(mod)
            self.modificador_otorgado = True

    def redimensionar(self, factor_escala, sprite_original=None):
        # Tamaño base 50x50 para la nave naranja (llama)
        self.ancho = int(50 * factor_escala)
        self.alto = int(50 * factor_escala)
        self.rect.width = self.ancho
        self.rect.height = self.alto
        if sprite_original:
            self.sprite_original = sprite_original
        if hasattr(self, 'sprite_original') and self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.ancho, self.alto))
        # Ajustar posición para que no salga de pantalla
        self.rect.x = min(self.rect.x, max(0, self.ancho_pantalla - self.ancho))
        self.rect.y = min(self.rect.y, max(0, self.alto_pantalla - self.alto))
