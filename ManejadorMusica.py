import os
import random
import pygame

class ManejadorMusica:
    def __init__(self, base_path):
        self.base_path = base_path
        self.phase_songs = [
            os.path.join(base_path, "songs", f"phase {i}.ogg") for i in range(1, 6)
        ]
        self.cancion_actual = None

    def reproducir_para_mundo(self, mundo):
        if mundo <= 5:
            ruta = self.phase_songs[mundo - 1]
        else:
            ruta = random.choice(self.phase_songs)
        self.reproducir(ruta)

    def reproducir(self, ruta, loop=True):
        if ruta != self.cancion_actual:
            try:
                if os.path.exists(ruta):
                    pygame.mixer.music.load(ruta)
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1 if loop else 0)
                    self.cancion_actual = ruta
                else:
                    print(f"[Música] Archivo no encontrado: {ruta}")
            except Exception as e:
                print(f"[Música] Error al reproducir {ruta}: {e}")

    def parar(self):
        pygame.mixer.music.stop()
        self.cancion_actual = None
    
    def reproducir_loose(self):
        ruta = os.path.join(self.base_path, "songs", "loose.ogg")
        self.reproducir(ruta, loop=True)

