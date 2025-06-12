import pygame
import os
import random


# Clase para manejar los sprites SVG
class SpriteManager:
    def __init__(self):
        self.sprites = {}
    
    def cargar_svg(self, nombre, svg_string):
        """Carga un SVG desde un string y lo convierte en una superficie de Pygame."""
        # Guardamos el SVG como un archivo temporal
        temp_path = f"{nombre}.svg"
        with open(temp_path, 'w') as f:
            f.write(svg_string)
        
        try:
            # Cargar el SVG como una superficie de Pygame
            # Nota: Pygame solo puede cargar SVG directamente si está compilado con soporte SVG
            # o si se usa una biblioteca como cairosvg o rasterio
            superficie = pygame.image.load(temp_path)
            self.sprites[nombre] = superficie
        except Exception as e:
            print(f"Error al cargar SVG {nombre}: {e}")
            # Crear una superficie de respaldo en caso de error
            if nombre == 'nave':
                superficie = self._crear_sprite_nave()
            elif nombre == 'enemigo':
                superficie = self._crear_sprite_enemigo()
            elif nombre == 'nave_roja':
                superficie = self._crear_sprite_nave_roja()
            elif nombre == 'nave_amarilla':
                superficie = self._crear_sprite_nave_amarilla()
            elif nombre == 'nave_verde':
                superficie = self._crear_sprite_nave_verde()
            elif nombre == 'nave_naranja':
                superficie = self._crear_sprite_nave_naranja()
            elif nombre == 'jefe':
                superficie = self._crear_sprite_jefe()
            elif nombre == 'bala':
                superficie = self._crear_sprite_bala()
            elif nombre == 'bala_enemiga':
                superficie = self._crear_sprite_bala_enemiga()
            elif nombre == 'explosion':
                superficie = self._crear_sprite_explosion()
            else:
                # Superficie por defecto
                superficie = pygame.Surface((50, 50), pygame.SRCALPHA)
                superficie.fill((255, 0, 0, 128))
            
            self.sprites[nombre] = superficie
        finally:
            # Eliminar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return self.sprites[nombre]
    
    def _crear_sprite_nave(self):
        superficie = pygame.Surface((50, 50), pygame.SRCALPHA)
        color = (0, 102, 204)  # Azul
        pygame.draw.polygon(superficie, color, [(25, 5), (40, 40), (25, 35), (10, 40)])
        pygame.draw.circle(superficie, (102, 204, 255), (25, 20), 5)
        return superficie
    
    def _crear_sprite_enemigo(self):
        superficie = pygame.Surface((75, 75), pygame.SRCALPHA)
        color = (153, 0, 204)  # Morado
        pygame.draw.polygon(superficie, color, [(37, 10), (55, 30), (60, 50), (37, 65), (15, 50), (20, 30)])
        pygame.draw.circle(superficie, (255, 0, 0), (30, 30), 5)
        pygame.draw.circle(superficie, (255, 0, 0), (45, 30), 5)
        return superficie
    
    def _crear_sprite_jefe(self):
        superficie = pygame.Surface((150, 100), pygame.SRCALPHA)
        color = (255, 0, 0)  # Rojo
        pygame.draw.polygon(superficie, color, [(75, 10), (130, 30), (140, 60), (75, 90), (10, 60), (20, 30)])
        pygame.draw.polygon(superficie, (255, 204, 0), [(45, 25), (75, 15), (105, 25), (105, 50), (75, 65), (45, 50)])
        pygame.draw.circle(superficie, (0, 255, 255), (55, 35), 8)
        pygame.draw.circle(superficie, (0, 255, 255), (95, 35), 8)
        return superficie
    
    def _crear_sprite_bala(self):
        superficie = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(superficie, (255, 51, 0), (0, 0, 5, 10))
        return superficie
    
    def _crear_sprite_bala_enemiga(self):
        superficie = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(superficie, (0, 102, 255), (0, 0, 5, 10))
        return superficie
    
    def _crear_sprite_explosion(self):
        superficie = pygame.Surface((100, 100), pygame.SRCALPHA)
        for r in [45, 35, 25, 15]:
            color_temp = (255, min(255, 153 + (45-r)*5), min(255, 51 + (45-r)*5))
            pygame.draw.circle(superficie, color_temp, (50, 50), r)
        return superficie
    
    def obtener_sprite(self, nombre):
        """Devuelve un sprite previamente cargado."""
        return self.sprites.get(nombre)
    
    def _crear_sprite_nave_verde(self):
        superficie = pygame.Surface((75, 75), pygame.SRCALPHA)
        color = (0, 200, 0)  # Verde
        pygame.draw.polygon(superficie, color, [(37, 10), (55, 30), (60, 50), (37, 65), (15, 50), (20, 30)])
        pygame.draw.circle(superficie, (255, 255, 255), (30, 30), 5)
        pygame.draw.circle(superficie, (255, 255, 255), (45, 30), 5)
        return superficie
    
    def _crear_sprite_nave_roja(self):
        superficie = pygame.Surface((75, 75), pygame.SRCALPHA)
        color = (255, 0, 0)
        pygame.draw.polygon(superficie, color, [(37, 10), (55, 30), (60, 50), (37, 65), (15, 50), (20, 30)])
        pygame.draw.circle(superficie, (255, 255, 255), (37, 50), 8)
        return superficie
    
    def _crear_sprite_nave_amarilla(self):
        superficie = pygame.Surface((75, 75), pygame.SRCALPHA)
        # Cuerpo principal
        pygame.draw.polygon(superficie, (255, 224, 102), [(37, 10), (60, 40), (55, 65), (19, 65), (14, 40)])
        # Cabina elíptica
        pygame.draw.ellipse(superficie, (255, 249, 179), (27, 50, 20, 13))
        # Escudos laterales
        pygame.draw.rect(superficie, (255, 215, 0), (5, 35, 10, 25), border_radius=4)
        pygame.draw.rect(superficie, (255, 215, 0), (60, 35, 10, 25), border_radius=4)
        # Detalles centrales
        pygame.draw.rect(superficie, (191, 166, 0), (33, 20, 8, 20))
        pygame.draw.rect(superficie, (255, 224, 102), (31, 25, 12, 3))
        pygame.draw.rect(superficie, (255, 224, 102), (31, 32, 12, 3))
        # Propulsores laterales
        pygame.draw.polygon(superficie, (255, 153, 0), [(17, 65), (12, 72), (25, 72)])
        pygame.draw.polygon(superficie, (255, 153, 0), [(57, 65), (50, 72), (63, 72)])
        # Propulsor central
        pygame.draw.polygon(superficie, (255, 102, 0), [(35, 65), (37, 75), (39, 65)])
        return superficie
    
    def _crear_sprite_nave_naranja(self):
        superficie = pygame.Surface((75, 75), pygame.SRCALPHA)
        # Cuerpo principal naranja
        pygame.draw.polygon(superficie, (255, 140, 0), [(37, 10), (60, 40), (55, 65), (19, 65), (14, 40)])
        # Cabina
        pygame.draw.ellipse(superficie, (255, 200, 100), (27, 50, 20, 13))
        # Detalles centrales
        pygame.draw.rect(superficie, (255, 180, 60), (33, 20, 8, 20))
        pygame.draw.rect(superficie, (255, 200, 100), (31, 25, 12, 3))
        pygame.draw.rect(superficie, (255, 200, 100), (31, 32, 12, 3))
        # Propulsores laterales
        pygame.draw.polygon(superficie, (255, 180, 0), [(17, 65), (12, 72), (25, 72)])
        pygame.draw.polygon(superficie, (255, 180, 0), [(57, 65), (50, 72), (63, 72)])
        # Propulsor central
        pygame.draw.polygon(superficie, (255, 120, 0), [(35, 65), (37, 75), (39, 65)])
        return superficie