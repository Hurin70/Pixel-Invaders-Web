import pygame
import random
from BalaEnemiga import BalaEnemiga

class Jefe:
    """Clase que representa al jefe del juego, que se mueve de forma horizontal y dispara balas hacia abajo."""
    def __init__(self, x, y, ancho, vida, velocidad=3, tiempo_entre_disparos=300):
        self.x = x
        self.y = y
        self.ancho = 150
        self.alto = 100
        self.vida = vida
        self.colores_posibles = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        self.color_index = 0  # Inicializamos en 0 para empezar con el primer color
        self.color = self.colores_posibles[self.color_index]  # Primer color inicial
        self.rect = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
        self.ultimo_disparo = 0
        self.ancho_pantalla = ancho
        self.enemigos_pausados = False
        self.sprite = None
        self.sprite_original = None
        self.velocidad_base = velocidad
        self.velocidad = velocidad
        self.tiempo_entre_disparos_base = tiempo_entre_disparos
        self.tiempo_entre_disparos = tiempo_entre_disparos

    def generar_color_secuencial(self):
        # Devolver el color actual y luego avanzar al siguiente color
        color_actual = self.colores_posibles[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.colores_posibles)  # Avanzar al siguiente color
        return color_actual

    def dibujar(self, ventana):
        if self.sprite:
            ventana.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(ventana, self.color, self.rect)  # Usar el color actual del jefe

    def movimiento(self):
        # Cambiar el color en cada movimiento
        self.color = self.generar_color_secuencial()

        # Movimiento aleatorio dentro del margen superior
        if random.randint(0, 100) < 20:  # 20% de probabilidad de cambiar de dirección
            self.x += random.choice([-self.velocidad, self.velocidad])
        
        # Mantener al jefe dentro de los límites de la pantalla
        self.x = max(0, min(self.x, self.ancho_pantalla - self.ancho))
        self.rect.x = self.x  # Actualizar la posición del rectángulo

    def disparar(self, balas):
        if pygame.time.get_ticks() - self.ultimo_disparo > self.tiempo_entre_disparos:
            # Crear una bala que se mueve hacia abajo
            bala = BalaEnemiga(self.x + self.ancho // 2, self.y + self.alto)
            balas.append(bala)
            self.ultimo_disparo = pygame.time.get_ticks()

    def pausar_enemigos(self, enemigos):
        if not self.enemigos_pausados:
            for enemigo in enemigos:
                enemigo.pausado = True
            self.enemigos_pausados = True

    def reanudar_enemigos(self, enemigos):
        if self.enemigos_pausados:
            for enemigo in enemigos:
                enemigo.pausado = False
            self.enemigos_pausados = False

    def redimensionar(self, factor_escala, sprite_original=None):
        self.ancho = int(150 * factor_escala)
        self.alto = int(100 * factor_escala)
        self.rect.width = self.ancho
        self.rect.height = self.alto
        if sprite_original:
            self.sprite_original = sprite_original
        if self.sprite_original:
            self.sprite = pygame.transform.smoothscale(self.sprite_original, (self.ancho, self.alto))
        self.velocidad = max(1, int(self.velocidad_base * factor_escala))
        self.tiempo_entre_disparos = int(self.tiempo_entre_disparos_base / factor_escala)
        # Ajustar posición para que no salga de pantalla
        self.rect.x = min(self.rect.x, max(0, self.rect.x))
        self.rect.y = min(self.rect.y, max(0, self.rect.y))