# -*- coding: utf-8 -*-
import pygame
import random
import os
import json
import time
import math
import asyncio
import sys

from FondoAnimado import FondoAnimado
from Personaje import Nave
from Enemigo import Enemigo
from NaveAmarilla import NaveAmarilla
from NaveRoja import NaveRoja
from NaveVerde import NaveVerde
from NaveNaranja import NaveNaranja
from Bala import Bala
from BalaEnemiga import BalaEnemiga
from Jefe import Jefe
from Modificadores import Escudo, DisparoTriple
from Explosion import Explosion
from SpriteManager import SpriteManager
from ManejadorMusica import ManejadorMusica


# ──────────────────────────────────────────────────────────────────────────────
# Rutas (solo constantes de string, sin tocar pygame aquí)
# ──────────────────────────────────────────────────────────────────────────────
BASE_PATH    = os.path.dirname(os.path.abspath(__file__))
IMG_PATH     = os.path.join(BASE_PATH, "img")
FUENTES_PATH = os.path.join(BASE_PATH, "FUENTES")

# Colores (no dependen de pygame.Surface, solo tuplas)
BLANCO = (255, 255, 255)
NEGRO  = (0, 0, 0)
ROJO   = (255, 0, 0)
VERDE  = (0, 255, 0)

# Constantes de resolución base
ANCHO_BASE    = 700
ALTO_BASE     = 800
FPS           = 60
ANCHO_NAVE_BASE = 75
ALTO_NAVE_BASE  = 75

# ──────────────────────────────────────────────────────────────────────────────
# Variables globales (se asignan en init_juego / reiniciar_juego)
# ──────────────────────────────────────────────────────────────────────────────
manejador_musica   = None
VENTANA            = None
surface_juego      = None
fondo_animado      = None
reloj              = None
FUENTE             = None
FUENTE_HUD         = None
sprite_manager     = None
sprite_nave        = None
sprite_nave_original = None
sprite_enemigo     = None
sprite_jefe        = None
sprite_bala        = None
sprite_bala_enemiga = None
sprite_explosion   = None
sprite_nave_verde  = None
sprite_nave_roja   = None
sprite_nave_amarilla = None
sprite_nave_naranja  = None
icono_escudo       = None
icono_triple       = None
burbuja_escudo_img = None
fondo_inicio_img   = None

ANCHO         = ANCHO_BASE
ALTO          = ALTO_BASE
FACTOR_ESCALA = 1.0

vida              = 5
puntos            = 0
enemigos_abatidos = 0
enemigos_por_jefe = 100
jefes_derrotados  = 0
enemigos_abatidos_ocultos = 0
tiempo_entre_enemigos     = 500
tiempo_entre_balas        = 100
ultima_bala               = 0
tiempo_ultimo_jefe        = 0
enemigos          = []
balas             = []
balas_enemigas    = []
jefe              = None
nave              = None
mundo             = 1
fondo_color       = NEGRO
musica_muted      = False
vida_base_jefe    = 10
escudo_mod        = None
disparo_triple    = None
mensaje_modificador       = None
mensaje_modificador_color = (255, 255, 0)
mensaje_modificador_tiempo = 0
MAX_PROB              = 10000
prob_nave_roja        = 1000
prob_nave_verde       = 1000
prob_nave_amarilla    = 1000
prob_nave_naranja     = 500
tiempo_disparo_nave_especial = 1200
modificadores_activos = []
contador_escudo       = 0
contador_disparo_triple = 0
tiempo_inicio_nivel   = 0
duracion_nivel        = 30
max_enemigos_en_pantalla = 6
explosiones       = []
jugando           = True
primera_partida   = True


# ──────────────────────────────────────────────────────────────────────────────
# Funciones auxiliares (no usan pygame en su definición, solo en su ejecución)
# ──────────────────────────────────────────────────────────────────────────────

def reproducir_musica(ruta, loop=True):
    try:
        if os.path.exists(ruta):
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1 if loop else 0)
            return True
        else:
            print(f"Archivo de música no encontrado: {ruta}")
            return False
    except pygame.error as e:
        print(f"Error de pygame al reproducir música: {e}")
        return False
    except Exception as e:
        print(f"Error general al reproducir música: {e}")
        return False


def mostrar_overlay_pausa():
    fuente_pausa = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 60)
    overlay = pygame.Surface((ANCHO_BASE, ALTO_BASE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    texto = fuente_pausa.render("PAUSE", True, BLANCO)
    overlay.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, ALTO_BASE // 2 - texto.get_height() // 2))
    surface_juego.blit(overlay, (0, 0))
    blit_centrado_letterbox()


def actualizar_ventana_y_escala(nuevo_ancho, nuevo_alto):
    global ANCHO, ALTO, VENTANA, FACTOR_ESCALA, FUENTE, FUENTE_HUD
    global icono_escudo, icono_triple, burbuja_escudo_img
    ANCHO = nuevo_ancho
    ALTO  = nuevo_alto
    VENTANA = pygame.display.set_mode([ANCHO, ALTO], pygame.RESIZABLE)
    FACTOR_ESCALA = min(ANCHO / ANCHO_BASE, ALTO / ALTO_BASE)
    nuevo_ancho_nave = max(1, int(ANCHO_NAVE_BASE * FACTOR_ESCALA))
    nuevo_alto_nave  = max(1, int(ALTO_NAVE_BASE  * FACTOR_ESCALA))
    if nave:
        nave.redimensionar(FACTOR_ESCALA, sprite_nave_original)
    fondo_animado.ancho = ANCHO
    fondo_animado.alto  = ALTO
    for enemigo in enemigos:
        if hasattr(enemigo, 'sprite_original'):
            if isinstance(enemigo, NaveRoja):
                enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_roja)
            elif isinstance(enemigo, NaveVerde):
                enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_verde)
            elif isinstance(enemigo, NaveAmarilla):
                enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_amarilla)
            elif isinstance(enemigo, NaveNaranja):
                enemigo.redimensionar(FACTOR_ESCALA, sprite_nave_naranja)
            else:
                enemigo.redimensionar(FACTOR_ESCALA, sprite_enemigo)
        else:
            enemigo.redimensionar(FACTOR_ESCALA)
    for bala in balas:
        if hasattr(bala, 'sprite_original'):
            bala.redimensionar(FACTOR_ESCALA, sprite_bala)
        else:
            bala.redimensionar(FACTOR_ESCALA)
    for be in balas_enemigas:
        if hasattr(be, 'sprite_original'):
            be.redimensionar(FACTOR_ESCALA, sprite_bala_enemiga)
        else:
            be.redimensionar(FACTOR_ESCALA)
    if jefe:
        if hasattr(jefe, 'sprite_original'):
            jefe.redimensionar(FACTOR_ESCALA, sprite_jefe)
        else:
            jefe.redimensionar(FACTOR_ESCALA)
        if hasattr(jefe, 'escudo') and jefe.escudo:
            jefe.escudo.redimensionar(FACTOR_ESCALA, burbuja_escudo_img)
    for explosion in explosiones:
        if hasattr(explosion, 'sprite_original'):
            explosion.redimensionar(FACTOR_ESCALA, sprite_explosion)
        else:
            explosion.redimensionar(FACTOR_ESCALA)
    for mod in modificadores_activos:
        if hasattr(mod, 'redimensionar'):
            if isinstance(mod, Escudo):
                mod.redimensionar(FACTOR_ESCALA, burbuja_escudo_img)
            else:
                mod.redimensionar(FACTOR_ESCALA)
    icono_escudo = pygame.transform.smoothscale(
        pygame.image.load(os.path.join(IMG_PATH, "icono_escudo.png")).convert_alpha(),
        (int(32 * FACTOR_ESCALA), int(32 * FACTOR_ESCALA)))
    icono_triple = pygame.transform.smoothscale(
        pygame.image.load(os.path.join(IMG_PATH, "icono_triple.png")).convert_alpha(),
        (int(32 * FACTOR_ESCALA), int(32 * FACTOR_ESCALA)))
    burbuja_escudo_img = pygame.transform.smoothscale(
        pygame.image.load(os.path.join(IMG_PATH, "burbuja_escudo.png")).convert_alpha(),
        (int(nuevo_ancho_nave * 1.3), int(nuevo_alto_nave * 1.3)))
    FUENTE     = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(40 * FACTOR_ESCALA), 12))
    FUENTE_HUD = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(20 * FACTOR_ESCALA), 10))


def fuente_ajustada(texto, fuente_path, ancho_max, alto_max=None, tamaño_inicial=60):
    tamaño = tamaño_inicial
    while tamaño > 10:
        fuente = pygame.font.Font(fuente_path, tamaño)
        superficie = fuente.render(texto, True, (255, 255, 255))
        if superficie.get_width() <= ancho_max and (alto_max is None or superficie.get_height() <= alto_max):
            return fuente
        tamaño -= 2
    return pygame.font.Font(fuente_path, 10)


def blit_centrado_letterbox():
    ventana_real = pygame.display.get_surface()
    ancho_ventana, alto_ventana = ventana_real.get_size()
    escala = min(ancho_ventana / ANCHO_BASE, alto_ventana / ALTO_BASE)
    ancho_escalado = int(ANCHO_BASE * escala)
    alto_escalado  = int(ALTO_BASE  * escala)
    x_offset = (ancho_ventana - ancho_escalado) // 2
    y_offset  = (alto_ventana  - alto_escalado)  // 2
    ventana_real.fill((0, 0, 0))
    surface_escalada = pygame.transform.smoothscale(surface_juego, (ancho_escalado, alto_escalado))
    ventana_real.blit(surface_escalada, (x_offset, y_offset))
    pygame.display.update()


def dibujar_fondo_inicio(ventana, fondo_img, ancho, alto, opacidad=255, oscurecer=80):
    fondo_escalado = pygame.transform.smoothscale(fondo_img, (ancho, alto))
    ventana.blit(fondo_escalado, (0, 0))
    oscurecedor = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    oscurecedor.fill((0, 0, 0, oscurecer))
    ventana.blit(oscurecedor, (0, 0))


def render_texto_dorado(texto, fuente, ancho, alto, destello_x):
    texto_img = fuente.render(texto, True, (255, 255, 255))
    degradado = pygame.Surface(texto_img.get_size()).convert_alpha()
    for y in range(texto_img.get_height()):
        color = (
            255,
            int(180 + 75 * y / texto_img.get_height()),
            int(40  + 100 * y / texto_img.get_height())
        )
        pygame.draw.line(degradado, color, (0, y), (texto_img.get_width(), y))
    texto_dorado = texto_img.copy()
    texto_dorado.blit(degradado, (0, 0), special_flags=pygame.BLEND_MULT)
    destello = pygame.Surface((40, texto_img.get_height()), pygame.SRCALPHA)
    pygame.draw.rect(destello, (255, 255, 255, 120), (0, 0, 40, texto_img.get_height()))
    texto_dorado.blit(destello, (destello_x % texto_img.get_width(), 0), special_flags=pygame.BLEND_ADD)
    return texto_dorado


def crear_explosion(x, y, tamaño=100):
    explosion = Explosion(x, y, tamaño)
    explosion.asignar_sprite(sprite_explosion)
    explosiones.append(explosion)


def mostrar_mensaje_modificador(texto, color=(255, 255, 0), duracion=1000):
    global mensaje_modificador, mensaje_modificador_color, mensaje_modificador_tiempo
    mensaje_modificador       = texto
    mensaje_modificador_color = color
    mensaje_modificador_tiempo = pygame.time.get_ticks() + duracion


def gestionar_teclas(teclas):
    global ultima_bala
    dx = dy = 0
    if (teclas[pygame.K_w] or teclas[pygame.K_UP])    and nave.rect.top    > 0:    dy = -nave.velocidad
    if (teclas[pygame.K_s] or teclas[pygame.K_DOWN])  and nave.rect.bottom < ALTO: dy =  nave.velocidad
    if (teclas[pygame.K_a] or teclas[pygame.K_LEFT])  and nave.rect.left   > 0:    dx = -nave.velocidad
    if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) and nave.rect.right  < ANCHO: dx =  nave.velocidad
    if dx != 0 or dy != 0:
        nave.mover(dx, dy)
    ahora = pygame.time.get_ticks()
    if teclas[pygame.K_SPACE] and ahora - ultima_bala > tiempo_entre_balas:
        for mod in modificadores_activos:
            if isinstance(mod, DisparoTriple) and mod.activo:
                mod.disparar(balas, sprite_bala)
                ultima_bala = ahora
                break
        else:
            bala = nave.crear_bala(nave.rect.centerx - 5, nave.rect.top, 0, -10, sprite_bala)
            balas.append(bala)
            ultima_bala = ahora


def cambiar_mundo():
    global vida_base_jefe, mundo, enemigos_abatidos_ocultos
    global prob_nave_roja, prob_nave_verde, prob_nave_amarilla, prob_nave_naranja
    global tiempo_disparo_nave_especial, tiempo_entre_enemigos, max_enemigos_en_pantalla
    global enemigos_por_jefe, enemigos_abatidos, tiempo_inicio_nivel, duracion_nivel

    enemigos_abatidos_ocultos = 0
    enemigos_por_jefe *= 2
    enemigos_abatidos  = 0

    Enemigo.velocidad = int(Enemigo.velocidad * 1.5)
    if Enemigo.velocidad >= 50:
        Enemigo.velocidad = 50

    if mundo == 1:
        vida_base_jefe = 10
    else:
        vida_base_jefe = int(vida_base_jefe * 1.5)

    if Jefe.velocidad >= 50:
        Jefe.velocidad = 50

    Jefe.tiempo_entre_disparos = int(Jefe.tiempo_entre_disparos / 1.5)
    if Jefe.tiempo_entre_disparos <= 300:
        Jefe.tiempo_entre_disparos = 300

    prob_nave_roja    = min(100 + mundo * 50, 800)
    prob_nave_verde   = min(100 + mundo * 50, 800)
    prob_nave_amarilla = min(100 + mundo * 50, 800)
    prob_nave_naranja = min(500, 500)
    tiempo_disparo_nave_especial = max(1200 - (mundo - 1) * 150, 400)
    tiempo_entre_enemigos = max(100, 500 - (mundo - 1) * 40)
    max_enemigos_en_pantalla = min(6 + mundo * 2, 40)
    duracion_nivel = 90 + (mundo - 1) * 15

    if mundo >= 6:
        fondos_dir = os.path.join(BASE_PATH, "fondos")
        fondos_disponibles = [f for f in os.listdir(fondos_dir) if f.endswith(".png")]
        fondo_aleatorio = random.choice(fondos_disponibles)
        nombre_fondo = os.path.splitext(fondo_aleatorio)[0]
        fondo_animado.seleccionar_fondo(nombre_fondo)
    else:
        fondo_animado.seleccionar_fondo(mundo)
    tiempo_inicio_nivel = pygame.time.get_ticks()


def reiniciar_juego():
    global nave, modificadores_activos, vida, puntos, enemigos_abatidos, enemigos_por_jefe
    global jefes_derrotados, enemigos_abatidos_ocultos, tiempo_entre_enemigos, tiempo_entre_balas
    global ultima_bala, tiempo_ultimo_jefe, enemigos, balas, balas_enemigas
    global jefe, mundo, fondo_color, explosiones, contador_escudo, contador_disparo_triple
    global tiempo_inicio_nivel, duracion_nivel

    nave = Nave(ANCHO // 2 - 25, ALTO - 60)
    nave.sprite = sprite_nave
    modificadores_activos = []
    Enemigo.velocidad = 5
    Jefe.velocidad = 5
    Jefe.tiempo_entre_disparos = 1000
    vida = 5
    puntos = 0
    enemigos_abatidos = 0
    enemigos_por_jefe = 100
    jefes_derrotados  = 0
    enemigos_abatidos_ocultos = 0
    tiempo_entre_enemigos = 500
    tiempo_entre_balas    = 100
    ultima_bala           = 0
    tiempo_ultimo_jefe    = pygame.time.get_ticks()
    enemigos       = []
    balas          = []
    balas_enemigas = []
    jefe           = None
    mundo          = 1
    fondo_color    = NEGRO
    explosiones    = []
    contador_escudo        = 0
    contador_disparo_triple = 0
    tiempo_inicio_nivel = pygame.time.get_ticks()
    duracion_nivel      = 30
    fondo_animado.seleccionar_fondo(mundo)


# ──────────────────────────────────────────────────────────────────────────────
# Pantallas async
# ──────────────────────────────────────────────────────────────────────────────

async def mostrar_pantalla_inicio():
    font_title        = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), int(60 * FACTOR_ESCALA))
    font_instructions = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), int(14 * FACTOR_ESCALA))
    destello_x = 0
    clock      = pygame.time.Clock()
    esperando  = True
    offset_y   = int(ALTO * 0.2)
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False
                    pygame.mixer.music.stop()
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        dibujar_fondo_inicio(surface_juego, fondo_inicio_img, ANCHO_BASE, ALTO_BASE, 128)
        titulo_pixel    = render_texto_dorado("PIXEL",    font_title, ANCHO_BASE, ALTO_BASE, destello_x)
        titulo_invaders = render_texto_dorado("INVADERS", font_title, ANCHO_BASE, ALTO_BASE, destello_x + int(80 * FACTOR_ESCALA))
        y_titulo = int(ALTO_BASE // 6 + offset_y)
        surface_juego.blit(titulo_pixel,    (ANCHO_BASE // 2 - titulo_pixel.get_width()    // 2, y_titulo))
        surface_juego.blit(titulo_invaders, (ANCHO_BASE // 2 - titulo_invaders.get_width() // 2, y_titulo + titulo_pixel.get_height() + int(10 * FACTOR_ESCALA)))
        instrucciones = [
            "Controles:",
            "W, A, S, D para mover la nave",
            "ESPACIO para disparar",
            "ESC para salir",
            "P pausa M mute",
            "",
        ]
        for i, linea in enumerate(instrucciones):
            texto = font_instructions.render(linea, True, BLANCO)
            surface_juego.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, int(ALTO_BASE // 3 + offset_y + i * 30 * FACTOR_ESCALA)))
        alpha = int(128 + 127 * (1 + math.sin(pygame.time.get_ticks() / 500)) / 2)
        font_intro  = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), max(int(18 * FACTOR_ESCALA), 12))
        texto_intro = font_intro.render("Presiona ENTER para comenzar", True, BLANCO)
        texto_intro.set_alpha(alpha)
        superficie_intro = pygame.Surface(texto_intro.get_size(), pygame.SRCALPHA)
        superficie_intro.blit(texto_intro, (0, 0))
        y_intro = int(ALTO_BASE // 2 + offset_y + len(instrucciones) * 35 * FACTOR_ESCALA + 30 * FACTOR_ESCALA)
        if y_intro + texto_intro.get_height() > ALTO_BASE:
            y_intro = ALTO_BASE - texto_intro.get_height() - int(20 * FACTOR_ESCALA)
        surface_juego.blit(superficie_intro, (ANCHO_BASE // 2 - texto_intro.get_width() // 2, y_intro))
        blit_centrado_letterbox()
        destello_x += int(8 * FACTOR_ESCALA)
        reloj.tick(60)
        await asyncio.sleep(0)


async def mostrar_mensaje_malo_y_cambiar():
    fuente_path = os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf")
    font       = fuente_ajustada("ERES MUY MALO", fuente_path, int(ANCHO_BASE * 0.9), int(80 * FACTOR_ESCALA), tamaño_inicial=int(60 * FACTOR_ESCALA))
    font_small = fuente_ajustada("Pulsa ENTER para continuar", fuente_path, int(ANCHO_BASE * 0.8), int(40 * FACTOR_ESCALA), tamaño_inicial=int(28 * FACTOR_ESCALA))
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    esperando = False
        surface_juego.fill(NEGRO)
        texto1 = font.render("ERES MUY MALO", True, ROJO)
        texto2 = font_small.render("Vuelve a la version demo", True, BLANCO)
        texto3 = font_small.render("Pulsa ENTER para continuar", True, BLANCO)
        surface_juego.blit(texto1, (ANCHO_BASE // 2 - texto1.get_width() // 2, int(ALTO_BASE * 0.3)))
        surface_juego.blit(texto2, (ANCHO_BASE // 2 - texto2.get_width() // 2, int(ALTO_BASE * 0.45)))
        surface_juego.blit(texto3, (ANCHO_BASE // 2 - texto3.get_width() // 2, int(ALTO_BASE * 0.55)))
        blit_centrado_letterbox()
        await asyncio.sleep(0)


async def mostrar_game_over_y_guardar(puntos):
    fuente_path = os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf")
    font       = fuente_ajustada("GAME OVER", fuente_path, int(ANCHO_BASE * 0.9), int(100 * FACTOR_ESCALA), tamaño_inicial=int(60 * FACTOR_ESCALA))
    font_small = fuente_ajustada("Introduce tus iniciales:", fuente_path, int(ANCHO_BASE * 0.8), int(40 * FACTOR_ESCALA), tamaño_inicial=int(32 * FACTOR_ESCALA))
    iniciales    = ""
    tiempo_limite = 20
    start_time   = time.time()
    terminado    = False
    while not terminado:
        tiempo_restante = max(0, int(tiempo_limite - (time.time() - start_time)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if len(iniciales) < 3 and event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    iniciales += event.unicode.upper()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and iniciales:
                    iniciales = iniciales[:-1]
                if event.key == pygame.K_RETURN and len(iniciales) == 3:
                    terminado = True
        if tiempo_restante == 0 and len(iniciales) < 3:
            terminado = True
        surface_juego.fill(NEGRO)
        texto       = font.render("GAME OVER", True, ROJO)
        texto_puntos = font_small.render(f"Puntos: {puntos}", True, BLANCO)
        texto_intro = font_small.render("Introduce tus iniciales:", True, BLANCO)
        font_iniciales  = fuente_ajustada("AAA", fuente_path, int(ANCHO_BASE * 0.7), int(80 * FACTOR_ESCALA), tamaño_inicial=int(60 * FACTOR_ESCALA))
        texto_iniciales = font_iniciales.render(iniciales + "_" * (3 - len(iniciales)), True, VERDE)
        texto_timer     = font_small.render(f"Tiempo: {tiempo_restante}", True, ROJO)
        surface_juego.blit(texto,          (ANCHO_BASE // 2 - texto.get_width()          // 2, int(ALTO_BASE * 0.13)))
        surface_juego.blit(texto_puntos,   (ANCHO_BASE // 2 - texto_puntos.get_width()   // 2, int(ALTO_BASE * 0.28)))
        surface_juego.blit(texto_intro,    (ANCHO_BASE // 2 - texto_intro.get_width()    // 2, int(ALTO_BASE * 0.39)))
        surface_juego.blit(texto_iniciales,(ANCHO_BASE // 2 - texto_iniciales.get_width()// 2, int(ALTO_BASE * 0.48)))
        surface_juego.blit(texto_timer,    (ANCHO_BASE // 2 - texto_timer.get_width()    // 2, int(ALTO_BASE * 0.62)))
        blit_centrado_letterbox()
        await asyncio.sleep(0)
    if iniciales:
        ruta_json = os.path.join(BASE_PATH, "puntuaciones.json")
        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                puntuaciones = json.load(f)
        except Exception:
            puntuaciones = []
        puntuaciones.append({"iniciales": iniciales, "puntos": puntos})
        puntuaciones = sorted(puntuaciones, key=lambda x: x["puntos"], reverse=True)[:10]
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(puntuaciones, f, indent=2)
    await mostrar_pantalla_puntuaciones()


async def mostrar_pantalla_puntuaciones():
    fuente_path         = os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf")
    font                = fuente_ajustada("PUNTUACIONES", fuente_path, int(ANCHO_BASE * 0.9), int(100 * FACTOR_ESCALA), tamaño_inicial=int(60 * FACTOR_ESCALA))
    font_small          = fuente_ajustada("AAA   999999", fuente_path, int(ANCHO_BASE * 0.7), int(40 * FACTOR_ESCALA), tamaño_inicial=int(32 * FACTOR_ESCALA))
    instrucciones_texto = "ESC: Salir   ENTER: Reiniciar"
    font_instrucciones  = fuente_ajustada(instrucciones_texto, fuente_path, int(ANCHO_BASE * 0.95), int(40 * FACTOR_ESCALA), tamaño_inicial=int(28 * FACTOR_ESCALA))
    ruta_json = os.path.join(BASE_PATH, "puntuaciones.json")
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            puntuaciones = json.load(f)
    except Exception:
        puntuaciones = []
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    esperando = False
        surface_juego.fill(NEGRO)
        texto = font.render("PUNTUACIONES", True, BLANCO)
        surface_juego.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, int(ALTO_BASE * 0.08)))
        for i, entry in enumerate(puntuaciones):
            linea = f"{entry['iniciales']}   {entry['puntos']}"
            color = VERDE if i == 0 else BLANCO
            t     = font_small.render(linea, True, color)
            y_linea = int(ALTO_BASE * 0.22) + i * int(44 * FACTOR_ESCALA)
            surface_juego.blit(t, (ANCHO_BASE // 2 - t.get_width() // 2, y_linea))
        instrucciones = font_instrucciones.render(instrucciones_texto, True, ROJO)
        surface_juego.blit(instrucciones, (ANCHO_BASE // 2 - instrucciones.get_width() // 2, int(ALTO_BASE * 0.88)))
        blit_centrado_letterbox()
        await asyncio.sleep(0)


async def mostrar_pantalla_pausa(mensaje):
    global mundo
    fuente_path    = os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf")
    font           = fuente_ajustada(mensaje, fuente_path, ANCHO_BASE - 40)
    fuente_opciones = fuente_ajustada("Presiona Y o ENTER para continuar, N para salir", fuente_path, ANCHO_BASE - 40, tamaño_inicial=32)
    surface_juego.fill(NEGRO)
    texto = font.render(mensaje, True, BLANCO)
    surface_juego.blit(texto, (ANCHO_BASE // 2 - texto.get_width() // 2, ALTO_BASE // 2 - texto.get_height() // 2))
    texto_opciones = fuente_opciones.render("Presiona Y o ENTER para continuar, N para salir", True, BLANCO)
    surface_juego.blit(texto_opciones, (ANCHO_BASE // 2 - texto_opciones.get_width() // 2, ALTO_BASE // 2 + 50))
    blit_centrado_letterbox()
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_y or evento.key == pygame.K_RETURN:
                    esperando = False
                    mundo += 1
                    manejador_musica.reproducir_para_mundo(mundo)
                    cambiar_mundo()
                elif evento.key == pygame.K_n:
                    return False
        await asyncio.sleep(0)
    return True


# ──────────────────────────────────────────────────────────────────────────────
# INIT — toda la inicialización de pygame ocurre aquí, ya dentro del event loop
# ──────────────────────────────────────────────────────────────────────────────

async def init_juego():
    global manejador_musica, VENTANA, surface_juego, fondo_animado, reloj
    global FUENTE, FUENTE_HUD, sprite_manager
    global sprite_nave, sprite_nave_original, sprite_enemigo, sprite_jefe
    global sprite_bala, sprite_bala_enemiga, sprite_explosion
    global sprite_nave_verde, sprite_nave_roja, sprite_nave_amarilla, sprite_nave_naranja
    global icono_escudo, icono_triple, burbuja_escudo_img, fondo_inicio_img
    global nave, tiempo_ultimo_jefe, tiempo_inicio_nivel, ANCHO, ALTO

    pygame.init()
    pygame.mixer.init()
    await asyncio.sleep(0)

    manejador_musica = ManejadorMusica(BASE_PATH)

    pygame.display.set_caption("Pixel Invaders")
    VENTANA       = pygame.display.set_mode([ANCHO_BASE, ALTO_BASE], pygame.RESIZABLE)
    surface_juego = pygame.Surface((ANCHO_BASE, ALTO_BASE))
    reloj         = pygame.time.Clock()
    await asyncio.sleep(0)

    try:
        FUENTE     = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 40)
        FUENTE_HUD = pygame.font.Font(os.path.join(FUENTES_PATH, "PressStart2P-Regular.ttf"), 20)
    except Exception as e:
        print(f"Error al cargar la fuente retro: {e}")
        FUENTE     = pygame.font.SysFont("Consolas", 40)
        FUENTE_HUD = pygame.font.SysFont("Consolas", 20)
    await asyncio.sleep(0)

    icono_escudo   = pygame.image.load(os.path.join(IMG_PATH, "icono_escudo.png")).convert_alpha()
    icono_triple   = pygame.image.load(os.path.join(IMG_PATH, "icono_triple.png")).convert_alpha()
    burbuja_escudo_img = pygame.image.load(os.path.join(IMG_PATH, "burbuja_escudo.png")).convert_alpha()
    await asyncio.sleep(0)

    fondo_animado = FondoAnimado(ANCHO_BASE, ALTO_BASE, BASE_PATH)
    await asyncio.sleep(0)

    sprite_manager = SpriteManager()
    try:
        svg_nave         = open(os.path.join(IMG_PATH, 'nave-sprite.svg'), 'r').read()
        sprite_nave      = sprite_manager.cargar_svg('nave', svg_nave)
        sprite_nave_original = sprite_nave

        svg_enemigo      = open(os.path.join(IMG_PATH, 'enemigo-sprite.svg'), 'r').read()
        sprite_enemigo   = sprite_manager.cargar_svg('enemigo', svg_enemigo)

        svg_jefe         = open(os.path.join(IMG_PATH, 'jefe-sprite.svg'), 'r').read()
        sprite_jefe      = sprite_manager.cargar_svg('jefe', svg_jefe)

        svg_bala         = open(os.path.join(IMG_PATH, 'bala-sprite.svg'), 'r').read()
        sprite_bala      = sprite_manager.cargar_svg('bala', svg_bala)

        svg_bala_enemiga = open(os.path.join(IMG_PATH, 'bala-enemiga-sprite.svg'), 'r').read()
        sprite_bala_enemiga = sprite_manager.cargar_svg('bala_enemiga', svg_bala_enemiga)

        svg_explosion    = open(os.path.join(IMG_PATH, 'efectos-explosiones.svg'), 'r').read()
        sprite_explosion = sprite_manager.cargar_svg('explosion', svg_explosion)

        svg_nave_verde   = open(os.path.join(IMG_PATH, 'naveVerde-sprite.svg'), 'r').read()
        sprite_nave_verde = sprite_manager.cargar_svg('nave_verde', svg_nave_verde)

        svg_nave_roja    = open(os.path.join(IMG_PATH, 'naveRoja-sprite.svg'), 'r').read()
        sprite_nave_roja = sprite_manager.cargar_svg('nave_roja', svg_nave_roja)

        svg_nave_amarilla = open(os.path.join(IMG_PATH, 'naveAmarilla-sprite.svg'), 'r').read()
        sprite_nave_amarilla = sprite_manager.cargar_svg('nave_amarilla', svg_nave_amarilla)

        svg_nave_naranja = open(os.path.join(IMG_PATH, 'naveNaranja-sprite.svg'), 'r').read()
        sprite_nave_naranja = sprite_manager.cargar_svg('nave_naranja', svg_nave_naranja)

    except Exception as e:
        print(f"Error al cargar SVG: {e}")
        sprite_nave           = sprite_manager._crear_sprite_nave();          sprite_manager.sprites['nave']          = sprite_nave
        sprite_nave_original  = sprite_nave
        sprite_enemigo        = sprite_manager._crear_sprite_enemigo();       sprite_manager.sprites['enemigo']       = sprite_enemigo
        sprite_jefe           = sprite_manager._crear_sprite_jefe();          sprite_manager.sprites['jefe']          = sprite_jefe
        sprite_bala           = sprite_manager._crear_sprite_bala();          sprite_manager.sprites['bala']          = sprite_bala
        sprite_bala_enemiga   = sprite_manager._crear_sprite_bala_enemiga();  sprite_manager.sprites['bala_enemiga']  = sprite_bala_enemiga
        sprite_explosion      = sprite_manager._crear_sprite_explosion();     sprite_manager.sprites['explosion']     = sprite_explosion
        sprite_nave_verde     = sprite_manager._crear_sprite_nave_verde();    sprite_manager.sprites['nave_verde']    = sprite_nave_verde
        sprite_nave_roja      = sprite_manager._crear_sprite_nave_roja();     sprite_manager.sprites['nave_roja']     = sprite_nave_roja
        sprite_nave_amarilla  = sprite_manager._crear_sprite_nave_amarilla(); sprite_manager.sprites['nave_amarilla'] = sprite_nave_amarilla
        sprite_nave_naranja   = sprite_manager._crear_sprite_nave_naranja();  sprite_manager.sprites['nave_naranja']  = sprite_nave_naranja
    await asyncio.sleep(0)

    fondo_inicio_path = os.path.join(BASE_PATH, "main", "fondo inicio.png")
    fondo_inicio_img  = pygame.image.load(fondo_inicio_path).convert()
    await asyncio.sleep(0)

    nave = Nave(ANCHO_BASE // 2 - 25, ALTO_BASE - 60)
    nave.sprite = sprite_nave
    tiempo_ultimo_jefe  = pygame.time.get_ticks()
    tiempo_inicio_nivel = pygame.time.get_ticks()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

async def main():
    global primera_partida, jefe, jefes_derrotados, enemigos_abatidos_ocultos
    global tiempo_inicio_nivel, duracion_nivel, vida, puntos
    global enemigos, balas, balas_enemigas, modificadores_activos
    global mensaje_modificador, musica_muted, jugando
    global contador_escudo, contador_disparo_triple, mundo
    global prob_nave_roja, prob_nave_verde, prob_nave_amarilla, prob_nave_naranja
    global tiempo_disparo_nave_especial, max_enemigos_en_pantalla, tiempo_entre_enemigos

    # ── Inicializar todo dentro del event loop ──
    await init_juego()

    while True:
        manejador_musica.reproducir(os.path.join(BASE_PATH, "songs", "main.ogg"))
        reiniciar_juego()
        jefe                     = None
        jefes_derrotados         = 0
        enemigos_abatidos_ocultos = 0
        tiempo_inicio_nivel      = pygame.time.get_ticks()
        duracion_nivel           = 30
        actualizar_ventana_y_escala(ANCHO, ALTO)
        await mostrar_pantalla_inicio()
        manejador_musica.reproducir_para_mundo(1)

        tiempo_pasado     = 0
        juego_en_progreso = True
        en_pausa          = False

        while juego_en_progreso and vida > 0:
            tiempo_pasado += reloj.tick(FPS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    jugando = False
                    juego_en_progreso = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        jugando = False
                        juego_en_progreso = False
                    if evento.key == pygame.K_p:
                        en_pausa = True
                        mostrar_overlay_pausa()
                        while en_pausa:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    juego_en_progreso = False
                                    en_pausa = False
                                if ev.type == pygame.KEYDOWN:
                                    if ev.key == pygame.K_p:
                                        en_pausa = False
                                    if ev.key == pygame.K_ESCAPE:
                                        juego_en_progreso = False
                                        en_pausa = False
                            await asyncio.sleep(0)
                    if evento.key == pygame.K_m:
                        musica_muted = not musica_muted
                        pygame.mixer.music.set_volume(0 if musica_muted else 0.7)
                if evento.type == pygame.VIDEORESIZE:
                    actualizar_ventana_y_escala(evento.w, evento.h)

            teclas = pygame.key.get_pressed()
            gestionar_teclas(teclas)

            # Generación de enemigos
            if tiempo_pasado > tiempo_entre_enemigos and len(enemigos) < max_enemigos_en_pantalla:
                r = random.uniform(0, MAX_PROB)
                if r < prob_nave_roja:
                    ne = NaveRoja(ANCHO_BASE, ALTO_BASE)
                    ne.sprite = sprite_nave_roja
                    ne.tiempo_entre_disparos = tiempo_disparo_nave_especial
                    enemigos.append(ne)
                elif r < prob_nave_roja + prob_nave_verde:
                    ne = NaveVerde(random.randint(0, ANCHO_BASE - 75), 0)
                    ne.sprite = sprite_nave_verde
                    ne.tiempo_entre_disparos = tiempo_disparo_nave_especial
                    enemigos.append(ne)
                elif r < prob_nave_roja + prob_nave_verde + prob_nave_amarilla:
                    y_i = 0
                    x_i = random.randint(100, ANCHO_BASE - 250)
                    for i in range(6):
                        na = NaveAmarilla(x_i + i * 75, y_i)
                        na.sprite = sprite_nave_amarilla
                        na.tiempo_entre_disparos = tiempo_disparo_nave_especial
                        enemigos.append(na)
                elif r < prob_nave_roja + prob_nave_verde + prob_nave_amarilla + prob_nave_naranja:
                    nn = NaveNaranja(random.randint(0, ANCHO_BASE - 75), -100, ANCHO_BASE, ALTO_BASE)
                    nn.sprite = sprite_nave_naranja
                    nn.redimensionar(FACTOR_ESCALA, sprite_nave_naranja)
                    enemigos.append(nn)
                else:
                    en = Enemigo(random.randint(0, ANCHO_BASE - 75), -100)
                    en.sprite = sprite_enemigo
                    enemigos.append(en)
                tiempo_pasado = 0

            # Aparición del jefe
            velocidad_jefe           = min(3 + (mundo - 1), 20)
            tiempo_entre_disparos_jefe = max(1200 - (mundo - 1) * 150, 300)
            if enemigos_abatidos >= enemigos_por_jefe and not jefe:
                jefe = Jefe(ANCHO_BASE // 2, 50, ANCHO_BASE, vida_base_jefe,
                            velocidad=velocidad_jefe, tiempo_entre_disparos=tiempo_entre_disparos_jefe)
                jefe.sprite = sprite_jefe
                jefe.escudo = Escudo(jefe, burbuja_escudo_img, duracion=20) if mundo >= 3 else None
                for en in enemigos:
                    en.pausado = True
                enemigos = []

            # Render
            surface_juego.fill(fondo_color)
            fondo_animado.actualizar(velocidad_mundo=mundo)
            fondo_animado.dibujar(surface_juego)

            if jefe:
                jefe.movimiento()
                jefe.disparar(balas_enemigas)
                for be in balas_enemigas:
                    if not hasattr(be, 'sprite') or be.sprite is None:
                        be.sprite = sprite_bala_enemiga
                jefe.dibujar(surface_juego)
                if hasattr(jefe, 'escudo') and jefe.escudo and jefe.escudo.activo:
                    jefe.escudo.dibujar(surface_juego)

            enemigos_a_eliminar = []
            for enemigo in enemigos:
                if not enemigo.pausado:
                    enemigo.movimiento()
                    if isinstance(enemigo, NaveVerde):   enemigo.disparar(balas_enemigas)
                    if isinstance(enemigo, NaveRoja):    enemigo.disparar(balas_enemigas)
                    if isinstance(enemigo, NaveAmarilla): enemigo.disparar(balas_enemigas, nave)
                    if enemigo.rect.top > ALTO:
                        puntos -= 50
                        enemigos_a_eliminar.append(enemigo)
                        continue
                enemigo.dibujar(surface_juego)
                if nave.rect.colliderect(enemigo.rect):
                    escudo_activo = False
                    for mod in modificadores_activos:
                        if isinstance(mod, Escudo) and mod.activo:
                            mod.recibir_golpe()
                            escudo_activo = True
                            break
                    if not escudo_activo:
                        vida -= 1
                        modificadores_activos = [m for m in modificadores_activos if not (isinstance(m, DisparoTriple) and m.activo)]
                    enemigos_a_eliminar.append(enemigo)
                    enemigos_abatidos += 1
                    enemigos_abatidos_ocultos += 1
                    crear_explosion(nave.rect.centerx, nave.rect.centery)

            for enemigo in enemigos_a_eliminar:
                if enemigo in enemigos:
                    if isinstance(enemigo, NaveRoja):
                        contador_disparo_triple += 1
                        if contador_disparo_triple >= 30:
                            modificadores_activos.append(DisparoTriple(nave))
                            contador_disparo_triple = 0
                    elif isinstance(enemigo, NaveVerde):
                        contador_escudo += 1
                        if contador_escudo >= 30:
                            modificadores_activos.append(Escudo(nave, burbuja_escudo_img))
                            contador_escudo = 0
                    elif isinstance(enemigo, NaveNaranja):
                        enemigo.otorgar_modificador(nave, modificadores_activos, burbuja_escudo_img)
                        if modificadores_activos:
                            mod = modificadores_activos[-1]
                            if isinstance(mod, Escudo):         mostrar_mensaje_modificador("¡Escudo obtenido!", (100, 200, 255))
                            elif isinstance(mod, DisparoTriple): mostrar_mensaje_modificador("¡Disparo triple!", (255, 200, 0))
                    enemigos.remove(enemigo)
                    puntos -= 50

            balas_a_eliminar = []
            for bala in balas[:]:
                bala.mover()
                if bala.rect.bottom < 0:
                    balas_a_eliminar.append(bala)
                    continue
                bala.dibujar(surface_juego)
                for enemigo in enemigos:
                    if bala.rect.colliderect(enemigo.rect):
                        if isinstance(enemigo, NaveNaranja):
                            enemigo.otorgar_modificador(nave, modificadores_activos, burbuja_escudo_img)
                            if modificadores_activos:
                                mod = modificadores_activos[-1]
                                if isinstance(mod, Escudo):          mostrar_mensaje_modificador("¡Escudo obtenido!", (100, 200, 255))
                                elif isinstance(mod, DisparoTriple):  mostrar_mensaje_modificador("¡Disparo triple!", (255, 200, 0))
                        puntos += 100
                        enemigos.remove(enemigo)
                        enemigos_abatidos += 1
                        enemigos_abatidos_ocultos += 1
                        crear_explosion(enemigo.rect.centerx, enemigo.rect.centery)
                        if bala not in balas_a_eliminar:
                            balas_a_eliminar.append(bala)
                        break
                if jefe and bala.rect.colliderect(jefe.rect):
                    if hasattr(jefe, 'escudo') and jefe.escudo and jefe.escudo.activo:
                        jefe.escudo.recibir_golpe()
                    else:
                        jefe.vida -= 1
                    if jefe.vida <= 0:
                        puntos += 100000
                        enemigos_abatidos += 10
                        jefes_derrotados  += 1
                        crear_explosion(jefe.rect.centerx, jefe.rect.centery, 200)
                        jefe = None
                        balas_enemigas.clear()
                        await mostrar_pantalla_pausa("YOU WIN!")
                        break
                    if bala in balas:
                        balas.remove(bala)
                    break

            for bala in balas_a_eliminar:
                if bala in balas:
                    balas.remove(bala)

            balas_enemigas_a_eliminar = []
            for be in balas_enemigas:
                be.mover()
                if be.rect.top > ALTO:
                    balas_enemigas_a_eliminar.append(be)
                    continue
                be.dibujar(surface_juego)
                if be.rect.colliderect(nave.rect):
                    escudo_activo = False
                    for mod in modificadores_activos:
                        if isinstance(mod, Escudo) and mod.activo:
                            mod.recibir_golpe()
                            escudo_activo = True
                            break
                    if not escudo_activo:
                        vida -= 1
                    crear_explosion(nave.rect.centerx, nave.rect.centery)
                    balas_enemigas_a_eliminar.append(be)
                    continue

            for bala in balas[:]:
                for be in balas_enemigas[:]:
                    if bala.rect.colliderect(be.rect):
                        if bala in balas:          balas.remove(bala)
                        if be   in balas_enemigas: balas_enemigas.remove(be)
                        crear_explosion(be.rect.centerx, be.rect.centery, 50)
                        break

            for be in balas_enemigas_a_eliminar:
                if be in balas_enemigas:
                    balas_enemigas.remove(be)

            explosiones_a_eliminar = []
            for explosion in explosiones:
                if explosion.actualizar():
                    explosiones_a_eliminar.append(explosion)
                else:
                    explosion.dibujar(surface_juego)
            for explosion in explosiones_a_eliminar:
                if explosion in explosiones:
                    explosiones.remove(explosion)

            for mod in modificadores_activos:
                if isinstance(mod, Escudo) and mod.activo:
                    mod.dibujar(surface_juego)
            nave.dibujar(surface_juego)

            x_icon = 20
            y_icon = 120
            if any(isinstance(m, Escudo)        and m.activo for m in modificadores_activos):
                surface_juego.blit(icono_escudo, (x_icon, y_icon)); y_icon += 36
            if any(isinstance(m, DisparoTriple) and m.activo for m in modificadores_activos):
                surface_juego.blit(icono_triple, (x_icon, y_icon)); y_icon += 36

            texto_vida     = FUENTE_HUD.render(f"Vida: {vida}",                   True, VERDE)
            texto_puntos   = FUENTE_HUD.render(f"Puntos: {puntos}",               True, ROJO)
            texto_enemigos = FUENTE_HUD.render(f"Enemigos: {enemigos_abatidos}",  True, BLANCO)
            texto_mundo_t  = FUENTE_HUD.render(f"Mundo: {mundo}",                 True, BLANCO)

            escudo_vidas = sum(m.duracion for m in modificadores_activos if isinstance(m, Escudo) and m.activo)
            if escudo_vidas > 0:
                texto_escudo = FUENTE_HUD.render(f"Escudo: {escudo_vidas}", True, (100, 200, 255))
                surface_juego.blit(texto_escudo, (20, 90))

            surface_juego.blit(texto_vida,     (20, 60))
            surface_juego.blit(texto_puntos,   (20, 20))
            surface_juego.blit(texto_enemigos, (ANCHO_BASE - texto_enemigos.get_width() - 20, 20))
            surface_juego.blit(texto_mundo_t,  (ANCHO_BASE - texto_mundo_t.get_width()  - 20, 60))

            modificadores_activos = [m for m in modificadores_activos if getattr(m, 'activo', True)]

            if mensaje_modificador and pygame.time.get_ticks() < mensaje_modificador_tiempo:
                sup = FUENTE_HUD.render(mensaje_modificador, True, mensaje_modificador_color)
                surface_juego.blit(sup, (ANCHO_BASE // 2 - sup.get_width() // 2, ALTO_BASE // 2 - 100))
            else:
                mensaje_modificador = None

            tiempo_transcurrido = int((pygame.time.get_ticks() - tiempo_inicio_nivel) / 1000)
            texto_tiempo = FUENTE_HUD.render(f" {tiempo_transcurrido}s", True, BLANCO)
            surface_juego.blit(texto_tiempo, (ANCHO_BASE // 2 - texto_tiempo.get_width() // 2, 20))

            blit_centrado_letterbox()
            await asyncio.sleep(0)

        # Fin de partida
        if vida <= 0:
            if primera_partida and puntos < 0:
                await mostrar_mensaje_malo_y_cambiar()
            else:
                manejador_musica.reproducir_loose()
                await mostrar_game_over_y_guardar(puntos)

        primera_partida = False
