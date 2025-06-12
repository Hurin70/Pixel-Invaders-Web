import pygame
import random
import os

class FondoAnimado:
    def __init__(self, ancho, alto, base_path):
        self.ancho = ancho
        self.alto = alto
        self.base_path = base_path
        self.fondo_actual = None
        self.mundo = 1
        # Cargar fondos
        self.fondos = [
            [self.cargar_fondo("fondos/fondo 1.png"), self.cargar_fondo("fondos/fondo 1.2.png")],
            [self.cargar_fondo("fondos/fondo 2.png")],
            [self.cargar_fondo("fondos/fondo 3.png"), self.cargar_fondo("fondos/fondo 3.2.png")],
            [self.cargar_fondo("fondos/fondo 4.png"), self.cargar_fondo("fondos/fondo 4.2.png")],
            [self.cargar_fondo("fondos/fondo 5.png")],
            [self.cargar_fondo("fondos/fondo 6.png"), self.cargar_fondo("fondos/fondo 6.2.png")]
        ]
        self.colores_estrellas = [
            (200, 120, 255),  # morado clarito
            (255, 255, 180),  # amarillo clarito
            (240, 240, 255),  # blanco clarito
            (180, 180, 180),  # gris
            (180, 255, 180)   # verde clarito
        ]
        # Estrellas: ahora cada estrella tiene su color fijo
        self.estrellas = [
            [random.randint(0, ancho), random.randint(0, alto), random.randint(1, 3), random.choice(self.colores_estrellas)]
            for _ in range(60)
        ]
        self.seleccionar_fondo(1)

    def cargar_fondo(self, ruta):
        base_path = os.path.dirname(os.path.abspath(__file__))
        fondo_path = os.path.join(base_path, ruta)
        if os.path.exists(fondo_path):
            return pygame.image.load(fondo_path).convert_alpha()
        return None

    def seleccionar_fondo(self, nombre_o_numero):
        import os
        if isinstance(nombre_o_numero, int):
            ruta = os.path.join(self.base_path, "fondos", f"fondo {nombre_o_numero}.png")
            self.fondo_actual = pygame.image.load(ruta).convert()
        elif isinstance(nombre_o_numero, str):
            ruta = os.path.join(self.base_path, "fondos", f"{nombre_o_numero}.png")
            self.fondo_actual = pygame.image.load(ruta).convert()

    def actualizar(self, velocidad_mundo=1):
        # Mover estrellas
        for estrella in self.estrellas:
            estrella[1] += estrella[2] * velocidad_mundo
            if estrella[1] > self.alto:
                estrella[0] = random.randint(0, self.ancho)
                estrella[1] = 0
                estrella[2] = random.randint(1, 3)

    def dibujar(self, ventana):
        if self.fondo_actual:
            fondo_escalado = pygame.transform.scale(self.fondo_actual, (self.ancho, self.alto))
            ventana.blit(fondo_escalado, (0, 0))
            # Oscurecer un 20%
            oscurecedor = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            oscurecedor.fill((0, 0, 0, int(255 * 0.7)))  # 0.2 = 20% opacidad
            ventana.blit(oscurecedor, (0, 0))
        else:
            ventana.fill((20, 0, 40))
        # Dibujar estrellas
        if self.mundo == 1:
            color = (255, 255, 255)
            for x, y, r, _ in self.estrellas:
                pygame.draw.circle(ventana, color, (x, y), r)
        else:
            for x, y, r, color in self.estrellas:
                pygame.draw.circle(ventana, color, (x, y), r)