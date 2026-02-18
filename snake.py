import pygame
import random
import sys

pygame.init()

ANCHO = 600
ALTO = 460
TAMANO_CUADRO = 20
ALTO_INFO = 35
MODO_TACTIL = True
SWIPE_UMBRAL = 50

VERDE = (0, 255, 0)
VERDE_OSCURO = (0, 200, 0)
ROJO = (255, 0, 0)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
AMARILLO = (255, 255, 0)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('SnakeGame by jaimefg1888')
reloj = pygame.time.Clock()

import os
ruta_fuente = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DotGothic16-Regular.ttf')
if not os.path.exists(ruta_fuente):
    ruta_fuente = '/tmp/DotGothic16-Regular.ttf'

try:
    fuente = pygame.font.Font(ruta_fuente, 28)
    fuente_grande = pygame.font.Font(ruta_fuente, 48)
    fuente_pequena = pygame.font.Font(ruta_fuente, 20)
    fuente_titulo = pygame.font.Font(ruta_fuente, 64)
except Exception as e:
    fuente = pygame.font.Font(None, 28)
    fuente_grande = pygame.font.Font(None, 56)
    fuente_pequena = pygame.font.Font(None, 24)
    fuente_titulo = pygame.font.Font(None, 72)

class Boton:
    def __init__(self, x, y, texto, color=BLANCO, ancho=None, alto=40):
        self.texto = texto
        self.color = color
        self.texto_surface = fuente.render(texto, True, color)
        self.ancho = ancho if ancho else self.texto_surface.get_width() + 30
        self.alto = alto
        self.rect = pygame.Rect(x - self.ancho // 2, y - self.alto // 2, self.ancho, self.alto)
        self.seleccionado = False
        self.x = x
        self.y = y
    
    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        color_hover = tuple(min(c + 50, 255) for c in self.color)
        if self.rect.collidepoint(mouse_pos) or self.seleccionado:
            color_actual = color_hover
            pygame.draw.rect(superficie, AMARILLO, self.rect.inflate(6, 6), 2)
        else:
            color_actual = self.color
        
        pygame.draw.rect(superficie, color_actual, self.rect, 2)
        
        texto_surface = fuente.render(self.texto, True, color_actual)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        superficie.blit(texto_surface, texto_rect)
    
    def clickeado(self, pos):
        return self.rect.collidepoint(pos)

class SelectorVelocidad:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.valor = 5
        self.seleccionado = False
        self.cuadros = []
        ancho_total = 245
        inicio = x - ancho_total // 2
        for i in range(10):
            rect = pygame.Rect(inicio + i * 25, y - 10, 20, 20)
            self.cuadros.append(rect)
    
    def dibujar(self, superficie):
        if self.seleccionado:
            pygame.draw.rect(superficie, AMARILLO, [self.x - 130, self.y - 18, 260, 36], 3)
        
        for i, rect in enumerate(self.cuadros):
            color = VERDE if i + 1 == self.valor else GRIS
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                color = VERDE_OSCURO if i + 1 == self.valor else (150, 150, 150)
            pygame.draw.rect(superficie, color, rect)
    
    def clickeado(self, pos):
        for i, rect in enumerate(self.cuadros):
            if rect.collidepoint(pos):
                self.valor = i + 1
                return True
        return False
    
    def cambiar(self, delta):
        self.valor = max(1, min(10, self.valor + delta))

class SelectorBordes:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.valor = True
        self.seleccionado = False
        self.rect_si = pygame.Rect(x - 55, y - 18, 50, 36)
        self.rect_no = pygame.Rect(x + 5, y - 18, 50, 36)
    
    def dibujar(self, superficie):
        if self.seleccionado:
            pygame.draw.rect(superficie, AMARILLO, [self.x - 62, self.y - 22, 124, 44], 2)
        
        mouse_pos = pygame.mouse.get_pos()
        
        color_si = VERDE if self.valor else GRIS
        if self.rect_si.collidepoint(mouse_pos):
            color_si = VERDE_OSCURO if self.valor else (150, 150, 150)
        pygame.draw.rect(superficie, color_si, self.rect_si)
        texto_si = fuente.render('SI', True, NEGRO)
        superficie.blit(texto_si, [self.rect_si.centerx - texto_si.get_width() // 2, self.rect_si.centery - texto_si.get_height() // 2])
        
        color_no = VERDE if not self.valor else GRIS
        if self.rect_no.collidepoint(mouse_pos):
            color_no = VERDE_OSCURO if not self.valor else (150, 150, 150)
        pygame.draw.rect(superficie, color_no, self.rect_no)
        texto_no = fuente.render('NO', True, NEGRO)
        superficie.blit(texto_no, [self.rect_no.centerx - texto_no.get_width() // 2, self.rect_no.centery - texto_no.get_height() // 2])
    
    def clickeado(self, pos):
        if self.rect_si.collidepoint(pos):
            self.valor = True
            return True
        elif self.rect_no.collidepoint(pos):
            self.valor = False
            return True
        return False
    
    def toggle(self):
        self.valor = not self.valor

class GestosTactiles:
    def __init__(self):
        self.touch_inicio = None
        self.umbral = SWIPE_UMBRAL
    
    def inicio_touch(self, pos):
        self.touch_inicio = pos
    
    def detectar_swipe(self, pos):
        if self.touch_inicio is None:
            return None
        
        dx = pos[0] - self.touch_inicio[0]
        dy = pos[1] - self.touch_inicio[1]
        
        if abs(dx) < self.umbral and abs(dy) < self.umbral:
            return None
        
        self.touch_inicio = None
        
        if abs(dx) > abs(dy):
            return 'derecha' if dx > 0 else 'izquierda'
        else:
            return 'abajo' if dy > 0 else 'arriba'

def menu_principal():
    selector_vel = SelectorVelocidad(ANCHO // 2, 170)
    selector_bordes = SelectorBordes(ANCHO // 2, 250)
    boton_iniciar = Boton(ANCHO // 2, 330, 'COMENZAR', VERDE, 180)
    boton_salir = Boton(ANCHO // 2, 385, 'SALIR', ROJO, 160)
    
    indice_actual = 2
    
    while True:
        pantalla.fill(NEGRO)
        
        titulo = fuente_titulo.render('SNAKE', True, VERDE)
        pantalla.blit(titulo, [ANCHO // 2 - titulo.get_width() // 2, 20])
        
        vel_texto = fuente.render('Velocidad:', True, BLANCO)
        pantalla.blit(vel_texto, [ANCHO // 2 - vel_texto.get_width() // 2, 125])
        
        selector_vel.seleccionado = (indice_actual == 0)
        selector_vel.dibujar(pantalla)
        
        bordes_texto = fuente.render('Bordes:', True, BLANCO)
        pantalla.blit(bordes_texto, [ANCHO // 2 - bordes_texto.get_width() // 2, 205])
        
        selector_bordes.seleccionado = (indice_actual == 1)
        selector_bordes.dibujar(pantalla)
        
        boton_iniciar.seleccionado = (indice_actual == 2)
        boton_salir.seleccionado = (indice_actual == 3)
        
        boton_iniciar.dibujar(pantalla)
        boton_salir.dibujar(pantalla)
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                selector_vel.clickeado(pos)
                selector_bordes.clickeado(pos)
                if boton_iniciar.clickeado(pos):
                    return selector_vel.valor, selector_bordes.valor, 'comenzar'
                elif boton_salir.clickeado(pos):
                    return selector_vel.valor, selector_bordes.valor, 'salir'
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    if indice_actual == 3:
                        indice_actual = 2
                    elif indice_actual == 2:
                        indice_actual = 1
                    elif indice_actual == 1:
                        indice_actual = 0
                elif evento.key == pygame.K_DOWN:
                    if indice_actual == 0:
                        indice_actual = 1
                    elif indice_actual == 1:
                        indice_actual = 2
                    elif indice_actual == 2:
                        indice_actual = 3
                elif evento.key == pygame.K_LEFT:
                    if indice_actual == 0:
                        selector_vel.cambiar(-1)
                    elif indice_actual == 1:
                        selector_bordes.toggle()
                elif evento.key == pygame.K_RIGHT:
                    if indice_actual == 0:
                        selector_vel.cambiar(1)
                    elif indice_actual == 1:
                        selector_bordes.toggle()
                elif evento.key == pygame.K_RETURN:
                    if indice_actual == 2:
                        return selector_vel.valor, selector_bordes.valor, 'comenzar'
                    elif indice_actual == 3:
                        return selector_vel.valor, selector_bordes.valor, 'salir'
                elif evento.key == pygame.K_ESCAPE:
                    return selector_vel.valor, selector_bordes.valor, 'salir'

def menu_pausa(puntos, tiempo):
    boton_continuar = Boton(ANCHO // 2, 220, 'CONTINUAR', VERDE, 160)
    boton_reiniciar = Boton(ANCHO // 2, 280, 'REINICIAR', BLANCO, 160)
    boton_menu = Boton(ANCHO // 2, 340, 'MENU PRINCIPAL', ROJO, 180)
    
    botones = [boton_continuar, boton_reiniciar, boton_menu]
    indice_actual = 0
    
    while True:
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        pantalla.blit(overlay, (0, 0))
        
        pausa_texto = fuente_grande.render('PAUSA', True, AMARILLO)
        pantalla.blit(pausa_texto, [ANCHO // 2 - pausa_texto.get_width() // 2, 60])
        
        puntos_texto = fuente.render(f'Puntuacion: {puntos}', True, BLANCO)
        pantalla.blit(puntos_texto, [ANCHO // 2 - puntos_texto.get_width() // 2, 130])
        
        tiempo_texto = fuente.render(f'Tiempo: {formatear_tiempo(tiempo)}', True, BLANCO)
        pantalla.blit(tiempo_texto, [ANCHO // 2 - tiempo_texto.get_width() // 2, 165])
        
        for i, boton in enumerate(botones):
            boton.seleccionado = (i == indice_actual)
            boton.dibujar(pantalla)
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if boton_continuar.clickeado(pos):
                    return 'continuar'
                elif boton_reiniciar.clickeado(pos):
                    return 'reiniciar'
                elif boton_menu.clickeado(pos):
                    return 'menu'
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    indice_actual = (indice_actual - 1) % 3
                elif evento.key == pygame.K_DOWN:
                    indice_actual = (indice_actual + 1) % 3
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if indice_actual == 0:
                        return 'continuar'
                    elif indice_actual == 1:
                        return 'reiniciar'
                    elif indice_actual == 2:
                        return 'menu'
                elif evento.key == pygame.K_ESCAPE:
                    return 'continuar'

def formatear_tiempo(segundos):
    mins = int(segundos // 60)
    segs = int(segundos % 60)
    return f'{mins:02d}:{segs:02d}'

def dibujar_serpiente(serpiente, offset_y_juego):
    for i, segmento in enumerate(serpiente):
        color = VERDE_OSCURO if i == 0 else VERDE
        pygame.draw.rect(pantalla, color, [segmento[0] + 1, segmento[1] + offset_y_juego + 1, TAMANO_CUADRO - 2, TAMANO_CUADRO - 2])

def generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto):
    while True:
        x = juego_x + random.randint(0, (juego_ancho // TAMANO_CUADRO) - 1) * TAMANO_CUADRO
        y = juego_y + random.randint(0, (juego_alto // TAMANO_CUADRO) - 1) * TAMANO_CUADRO
        if [x, y] not in serpiente:
            return [x, y]

def dibujar_barra_info(puntos, tiempo, boton_pausa=None):
    pygame.draw.rect(pantalla, (30, 30, 30), [0, 0, ANCHO, ALTO_INFO])
    pygame.draw.line(pantalla, BLANCO, (0, ALTO_INFO), (ANCHO, ALTO_INFO), 2)
    
    puntos_texto = fuente_pequena.render(f'PUNTOS: {puntos}', True, BLANCO)
    pantalla.blit(puntos_texto, [20, 8])
    
    tiempo_str = formatear_tiempo(tiempo)
    tiempo_texto = fuente_pequena.render(f'TIEMPO: {tiempo_str}', True, BLANCO)
    pantalla.blit(tiempo_texto, [ANCHO - tiempo_texto.get_width() - 20, 8])
    
    if boton_pausa:
        boton_pausa.dibujar(pantalla)

class BotonPausa:
    def __init__(self, x, y, ancho=50, alto=28):
        self.rect = pygame.Rect(x - ancho // 2, y - alto // 2, ancho, alto)
        self.x = x
        self.y = y
    
    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        color = AMARILLO if self.rect.collidepoint(mouse_pos) else BLANCO
        pygame.draw.rect(superficie, color, self.rect, 2, border_radius=5)
        
        cx, cy = self.rect.center
        barra_ancho = 6
        barra_alto = 14
        espacio = 4
        
        pygame.draw.rect(superficie, color, [cx - espacio - barra_ancho, cy - barra_alto // 2, barra_ancho, barra_alto])
        pygame.draw.rect(superficie, color, [cx + espacio, cy - barra_alto // 2, barra_ancho, barra_alto])
    
    def clickeado(self, pos):
        return self.rect.collidepoint(pos)

def juego(velocidad, con_bordes):
    fps = 5 + velocidad * 1.5
    
    offset_y_juego = ALTO_INFO
    area_ancho = ANCHO
    area_alto = ALTO - ALTO_INFO
    
    if con_bordes:
        juego_x = TAMANO_CUADRO
        juego_y = TAMANO_CUADRO
        juego_ancho = area_ancho - 2 * TAMANO_CUADRO
        juego_alto = area_alto - 2 * TAMANO_CUADRO
    else:
        juego_x = 0
        juego_y = 0
        juego_ancho = area_ancho
        juego_alto = area_alto
    
    inicio_x = juego_x + (juego_ancho // 2 // TAMANO_CUADRO) * TAMANO_CUADRO
    inicio_y = juego_y + (juego_alto // 2 // TAMANO_CUADRO) * TAMANO_CUADRO
    
    serpiente = [[inicio_x, inicio_y]]
    direccion = [TAMANO_CUADRO, 0]
    comida = generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto)
    puntos = 0
    tiempo_inicio = pygame.time.get_ticks()
    
    gestos = GestosTactiles() if MODO_TACTIL else None
    boton_pausa = BotonPausa(ANCHO // 2, ALTO_INFO // 2)
    
    while True:
        tiempo_transcurrido = (pygame.time.get_ticks() - tiempo_inicio) / 1000
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_pausa.clickeado(evento.pos):
                    resultado = menu_pausa(puntos, tiempo_transcurrido)
                    if resultado == 'continuar':
                        tiempo_inicio = pygame.time.get_ticks() - int(tiempo_transcurrido * 1000)
                        continue
                    elif resultado == 'reiniciar':
                        return 'reiniciar', puntos, tiempo_transcurrido
                    elif resultado == 'menu':
                        return 'menu', puntos, tiempo_transcurrido
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    resultado = menu_pausa(puntos, tiempo_transcurrido)
                    if resultado == 'continuar':
                        tiempo_inicio = pygame.time.get_ticks() - int(tiempo_transcurrido * 1000)
                        continue
                    elif resultado == 'reiniciar':
                        return 'reiniciar', puntos, tiempo_transcurrido
                    elif resultado == 'menu':
                        return 'menu', puntos, tiempo_transcurrido
                elif evento.key == pygame.K_UP and direccion != [0, TAMANO_CUADRO]:
                    direccion = [0, -TAMANO_CUADRO]
                elif evento.key == pygame.K_DOWN and direccion != [0, -TAMANO_CUADRO]:
                    direccion = [0, TAMANO_CUADRO]
                elif evento.key == pygame.K_LEFT and direccion != [TAMANO_CUADRO, 0]:
                    direccion = [-TAMANO_CUADRO, 0]
                elif evento.key == pygame.K_RIGHT and direccion != [-TAMANO_CUADRO, 0]:
                    direccion = [TAMANO_CUADRO, 0]
            elif MODO_TACTIL and gestos:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    gestos.inicio_touch(evento.pos)
                elif evento.type == pygame.MOUSEBUTTONUP:
                    swipe = gestos.detectar_swipe(evento.pos)
                    if swipe == 'arriba' and direccion != [0, TAMANO_CUADRO]:
                        direccion = [0, -TAMANO_CUADRO]
                    elif swipe == 'abajo' and direccion != [0, -TAMANO_CUADRO]:
                        direccion = [0, TAMANO_CUADRO]
                    elif swipe == 'izquierda' and direccion != [TAMANO_CUADRO, 0]:
                        direccion = [-TAMANO_CUADRO, 0]
                    elif swipe == 'derecha' and direccion != [-TAMANO_CUADRO, 0]:
                        direccion = [TAMANO_CUADRO, 0]
                elif evento.type == pygame.FINGERDOWN:
                    gestos.inicio_touch((int(evento.x * ANCHO), int(evento.y * ALTO)))
                elif evento.type == pygame.FINGERUP:
                    swipe = gestos.detectar_swipe((int(evento.x * ANCHO), int(evento.y * ALTO)))
                    if swipe == 'arriba' and direccion != [0, TAMANO_CUADRO]:
                        direccion = [0, -TAMANO_CUADRO]
                    elif swipe == 'abajo' and direccion != [0, -TAMANO_CUADRO]:
                        direccion = [0, TAMANO_CUADRO]
                    elif swipe == 'izquierda' and direccion != [TAMANO_CUADRO, 0]:
                        direccion = [-TAMANO_CUADRO, 0]
                    elif swipe == 'derecha' and direccion != [-TAMANO_CUADRO, 0]:
                        direccion = [TAMANO_CUADRO, 0]
        
        cabeza = [serpiente[0][0] + direccion[0], serpiente[0][1] + direccion[1]]
        
        if con_bordes:
            limite_der = juego_x + juego_ancho - TAMANO_CUADRO
            limite_aba = juego_y + juego_alto - TAMANO_CUADRO
            
            if (cabeza[0] < juego_x or cabeza[0] > limite_der or
                cabeza[1] < juego_y or cabeza[1] > limite_aba or
                cabeza in serpiente):
                return 'gameover', puntos, tiempo_transcurrido
        else:
            if cabeza[0] < 0:
                cabeza[0] = juego_ancho - TAMANO_CUADRO
            elif cabeza[0] >= juego_ancho:
                cabeza[0] = 0
            if cabeza[1] < 0:
                cabeza[1] = juego_alto - TAMANO_CUADRO
            elif cabeza[1] >= juego_alto:
                cabeza[1] = 0
            
            if cabeza in serpiente:
                return 'gameover', puntos, tiempo_transcurrido
        
        serpiente.insert(0, cabeza)
        
        if cabeza == comida:
            puntos += 1
            comida = generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto)
        else:
            serpiente.pop()
        
        pantalla.fill(NEGRO)
        
        if con_bordes:
            pygame.draw.rect(pantalla, (20, 20, 20), [juego_x, juego_y + offset_y_juego, juego_ancho, juego_alto])
            pygame.draw.rect(pantalla, BLANCO, [juego_x, juego_y + offset_y_juego, juego_ancho, juego_alto], 3)
        
        dibujar_serpiente(serpiente, offset_y_juego)
        pygame.draw.rect(pantalla, ROJO, [comida[0] + 2, comida[1] + offset_y_juego + 2, TAMANO_CUADRO - 4, TAMANO_CUADRO - 4])
        
        dibujar_barra_info(puntos, tiempo_transcurrido, boton_pausa)
        pygame.display.flip()
        reloj.tick(fps)

def game_over(puntos, tiempo):
    boton_reiniciar = Boton(ANCHO // 2, 240, 'REINICIAR', VERDE, 160)
    boton_menu = Boton(ANCHO // 2, 310, 'MENU PRINCIPAL', ROJO, 180)
    
    botones = [boton_reiniciar, boton_menu]
    indice_actual = 0
    
    while True:
        pantalla.fill(NEGRO)
        
        fin_texto = fuente_grande.render('GAME OVER', True, ROJO)
        pantalla.blit(fin_texto, [ANCHO // 2 - fin_texto.get_width() // 2, 80])
        
        puntos_texto = fuente.render(f'Puntuacion: {puntos}', True, BLANCO)
        pantalla.blit(puntos_texto, [ANCHO // 2 - puntos_texto.get_width() // 2, 150])
        
        tiempo_texto = fuente.render(f'Tiempo: {formatear_tiempo(tiempo)}', True, BLANCO)
        pantalla.blit(tiempo_texto, [ANCHO // 2 - tiempo_texto.get_width() // 2, 185])
        
        for i, boton in enumerate(botones):
            boton.seleccionado = (i == indice_actual)
            boton.dibujar(pantalla)
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if boton_reiniciar.clickeado(pos):
                    return 'reiniciar'
                elif boton_menu.clickeado(pos):
                    return 'menu'
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP or evento.key == pygame.K_DOWN:
                    indice_actual = (indice_actual + 1) % 2
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if indice_actual == 0:
                        return 'reiniciar'
                    elif indice_actual == 1:
                        return 'menu'

def main():
    while True:
        velocidad, con_bordes, accion = menu_principal()
        
        if accion == 'salir':
            pygame.quit()
            sys.exit()
        
        while True:
            resultado, puntos, tiempo = juego(velocidad, con_bordes)
            
            if resultado == 'menu':
                break
            
            accion = game_over(puntos, tiempo)
            
            if accion == 'menu':
                break

if __name__ == '__main__':
    main()
