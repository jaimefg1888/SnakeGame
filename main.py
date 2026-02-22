import sys
import random

import pygame

# --- Inicialización ---
pygame.init()

# Dimensiones de pantalla y cuadrícula
ANCHO = 600
ALTO = 460
TAMANO_CUADRO = 20
ALTO_INFO = 35

# Modo táctil: detecta swipes además de teclado
MODO_TACTIL = True
SWIPE_UMBRAL = 50

# Colores
VERDE       = (0, 255, 0)
VERDE_OSCURO = (0, 200, 0)
ROJO        = (255, 0, 0)
NEGRO       = (0, 0, 0)
BLANCO      = (255, 255, 255)
GRIS        = (100, 100, 100)
AMARILLO    = (255, 255, 0)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('SnakeGame by jaimefg1888')
reloj = pygame.time.Clock()

# Fuente del sistema (None = fuente por defecto de pygame)
# Para usar una fuente personalizada: pygame.font.Font('DotGothic16-Regular.ttf', tamaño)
fuente         = pygame.font.Font(None, 28)
fuente_grande  = pygame.font.Font(None, 56)
fuente_pequena = pygame.font.Font(None, 24)
fuente_titulo  = pygame.font.Font(None, 72)


# --- Clases de UI ---

class Boton:
    def __init__(self, x, y, texto, color=BLANCO, ancho=None, alto=40):
        self.texto = texto
        self.color = color
        self.seleccionado = False
        texto_surface = fuente.render(texto, True, color)
        self.ancho = ancho if ancho else texto_surface.get_width() + 30
        self.alto = alto
        self.rect = pygame.Rect(x - self.ancho // 2, y - self.alto // 2, self.ancho, self.alto)

    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse_pos) or self.seleccionado
        color_actual = tuple(min(c + 50, 255) for c in self.color) if hover else self.color

        if hover:
            pygame.draw.rect(superficie, AMARILLO, self.rect.inflate(6, 6), 2)
        pygame.draw.rect(superficie, color_actual, self.rect, 2)

        texto_surface = fuente.render(self.texto, True, color_actual)
        superficie.blit(texto_surface, texto_surface.get_rect(center=self.rect.center))

    def clickeado(self, pos):
        return self.rect.collidepoint(pos)


class BotonPausa:
    """Botón con icono de pausa (dos barras verticales)."""
    def __init__(self, x, y, ancho=50, alto=28):
        self.rect = pygame.Rect(x - ancho // 2, y - alto // 2, ancho, alto)

    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        color = AMARILLO if self.rect.collidepoint(mouse_pos) else BLANCO
        pygame.draw.rect(superficie, color, self.rect, 2, border_radius=5)

        cx, cy = self.rect.center
        barra_ancho, barra_alto, espacio = 6, 14, 4
        pygame.draw.rect(superficie, color, [cx - espacio - barra_ancho, cy - barra_alto // 2, barra_ancho, barra_alto])
        pygame.draw.rect(superficie, color, [cx + espacio, cy - barra_alto // 2, barra_ancho, barra_alto])

    def clickeado(self, pos):
        return self.rect.collidepoint(pos)


class SelectorVelocidad:
    """10 cuadros que representan los niveles de velocidad (1-10)."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.valor = 5
        self.seleccionado = False
        inicio = x - 245 // 2
        self.cuadros = [pygame.Rect(inicio + i * 25, y - 10, 20, 20) for i in range(10)]

    def dibujar(self, superficie):
        if self.seleccionado:
            pygame.draw.rect(superficie, AMARILLO, [self.x - 130, self.y - 18, 260, 36], 3)

        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.cuadros):
            activo = (i + 1 == self.valor)
            if rect.collidepoint(mouse_pos):
                color = VERDE_OSCURO if activo else (150, 150, 150)
            else:
                color = VERDE if activo else GRIS
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
    """Botones SI/NO para activar o desactivar los bordes."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.valor = True
        self.seleccionado = False
        self.rect_si = pygame.Rect(x - 55, y - 18, 50, 36)
        self.rect_no = pygame.Rect(x + 5,  y - 18, 50, 36)

    def _dibujar_opcion(self, superficie, rect, etiqueta, activo):
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            color = VERDE_OSCURO if activo else (150, 150, 150)
        else:
            color = VERDE if activo else GRIS
        pygame.draw.rect(superficie, color, rect)
        texto = fuente.render(etiqueta, True, NEGRO)
        superficie.blit(texto, [rect.centerx - texto.get_width() // 2,
                                 rect.centery - texto.get_height() // 2])

    def dibujar(self, superficie):
        if self.seleccionado:
            pygame.draw.rect(superficie, AMARILLO, [self.x - 62, self.y - 22, 124, 44], 2)
        self._dibujar_opcion(superficie, self.rect_si, 'SI', self.valor)
        self._dibujar_opcion(superficie, self.rect_no, 'NO', not self.valor)

    def clickeado(self, pos):
        if self.rect_si.collidepoint(pos):
            self.valor = True
            return True
        if self.rect_no.collidepoint(pos):
            self.valor = False
            return True
        return False

    def toggle(self):
        self.valor = not self.valor


class GestosTactiles:
    """Detecta swipes por distancia y dirección entre inicio y fin del toque."""
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
        self.touch_inicio = None

        if abs(dx) < self.umbral and abs(dy) < self.umbral:
            return None
        if abs(dx) > abs(dy):
            return 'derecha' if dx > 0 else 'izquierda'
        return 'abajo' if dy > 0 else 'arriba'


# --- Funciones auxiliares ---

def formatear_tiempo(segundos):
    mins = int(segundos // 60)
    segs = int(segundos % 60)
    return f'{mins:02d}:{segs:02d}'


def generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto):
    """Genera comida en una celda libre aleatoria."""
    while True:
        x = juego_x + random.randint(0, juego_ancho // TAMANO_CUADRO - 1) * TAMANO_CUADRO
        y = juego_y + random.randint(0, juego_alto // TAMANO_CUADRO - 1) * TAMANO_CUADRO
        if [x, y] not in serpiente:
            return [x, y]


def dibujar_serpiente(serpiente, offset_y):
    for i, segmento in enumerate(serpiente):
        color = VERDE_OSCURO if i == 0 else VERDE
        pygame.draw.rect(pantalla, color,
                         [segmento[0] + 1, segmento[1] + offset_y + 1,
                          TAMANO_CUADRO - 2, TAMANO_CUADRO - 2])


def dibujar_barra_info(puntos, tiempo, boton_pausa=None):
    pygame.draw.rect(pantalla, (30, 30, 30), [0, 0, ANCHO, ALTO_INFO])
    pygame.draw.line(pantalla, BLANCO, (0, ALTO_INFO), (ANCHO, ALTO_INFO), 2)

    txt_puntos = fuente_pequena.render(f'PUNTOS: {puntos}', True, BLANCO)
    pantalla.blit(txt_puntos, [20, 8])

    txt_tiempo = fuente_pequena.render(f'TIEMPO: {formatear_tiempo(tiempo)}', True, BLANCO)
    pantalla.blit(txt_tiempo, [ANCHO - txt_tiempo.get_width() - 20, 8])

    if boton_pausa:
        boton_pausa.dibujar(pantalla)


def aplicar_swipe(swipe, direccion):
    """Cambia la dirección según el swipe, sin permitir giros de 180°."""
    mapa = {
        'arriba':    ([0, -TAMANO_CUADRO], [0,  TAMANO_CUADRO]),
        'abajo':     ([0,  TAMANO_CUADRO], [0, -TAMANO_CUADRO]),
        'izquierda': ([-TAMANO_CUADRO, 0], [ TAMANO_CUADRO, 0]),
        'derecha':   ([ TAMANO_CUADRO, 0], [-TAMANO_CUADRO, 0]),
    }
    if swipe in mapa:
        nueva, opuesta = mapa[swipe]
        if direccion != opuesta:
            return nueva
    return direccion


# --- Pantallas ---

def menu_principal():
    selector_vel    = SelectorVelocidad(ANCHO // 2, 170)
    selector_bordes = SelectorBordes(ANCHO // 2, 250)
    boton_iniciar   = Boton(ANCHO // 2, 330, 'COMENZAR', VERDE, 180)
    boton_salir     = Boton(ANCHO // 2, 385, 'SALIR', ROJO, 160)

    # Orden de foco: 0=velocidad, 1=bordes, 2=comenzar, 3=salir
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
        boton_salir.seleccionado   = (indice_actual == 3)
        boton_iniciar.dibujar(pantalla)
        boton_salir.dibujar(pantalla)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                selector_vel.clickeado(pos)
                selector_bordes.clickeado(pos)
                if boton_iniciar.clickeado(pos):
                    return selector_vel.valor, selector_bordes.valor, 'comenzar'
                if boton_salir.clickeado(pos):
                    return selector_vel.valor, selector_bordes.valor, 'salir'

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_UP, pygame.K_DOWN):
                    delta = -1 if evento.key == pygame.K_UP else 1
                    indice_actual = (indice_actual + delta) % 4
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
    boton_menu      = Boton(ANCHO // 2, 340, 'MENU PRINCIPAL', ROJO, 180)
    botones = [boton_continuar, boton_reiniciar, boton_menu]
    resultados = ['continuar', 'reiniciar', 'menu']
    indice_actual = 0

    while True:
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        pantalla.blit(overlay, (0, 0))

        pausa_txt = fuente_grande.render('PAUSA', True, AMARILLO)
        pantalla.blit(pausa_txt, [ANCHO // 2 - pausa_txt.get_width() // 2, 60])

        puntos_txt = fuente.render(f'Puntuacion: {puntos}', True, BLANCO)
        pantalla.blit(puntos_txt, [ANCHO // 2 - puntos_txt.get_width() // 2, 130])

        tiempo_txt = fuente.render(f'Tiempo: {formatear_tiempo(tiempo)}', True, BLANCO)
        pantalla.blit(tiempo_txt, [ANCHO // 2 - tiempo_txt.get_width() // 2, 165])

        for i, boton in enumerate(botones):
            boton.seleccionado = (i == indice_actual)
            boton.dibujar(pantalla)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                for i, boton in enumerate(botones):
                    if boton.clickeado(pos):
                        return resultados[i]

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    indice_actual = (indice_actual - 1) % 3
                elif evento.key == pygame.K_DOWN:
                    indice_actual = (indice_actual + 1) % 3
                elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return resultados[indice_actual]
                elif evento.key == pygame.K_ESCAPE:
                    return 'continuar'


def juego(velocidad, con_bordes):
    fps = 5 + velocidad * 1.5

    offset_y = ALTO_INFO
    area_ancho = ANCHO
    area_alto  = ALTO - ALTO_INFO

    # Con bordes: área de juego reducida dejando margen; sin bordes: área completa con wrap-around
    if con_bordes:
        juego_x     = TAMANO_CUADRO
        juego_y     = TAMANO_CUADRO
        juego_ancho = area_ancho - 2 * TAMANO_CUADRO
        juego_alto  = area_alto  - 2 * TAMANO_CUADRO
    else:
        juego_x, juego_y = 0, 0
        juego_ancho = area_ancho
        juego_alto  = area_alto

    inicio_x = juego_x + (juego_ancho // 2 // TAMANO_CUADRO) * TAMANO_CUADRO
    inicio_y = juego_y + (juego_alto  // 2 // TAMANO_CUADRO) * TAMANO_CUADRO

    serpiente    = [[inicio_x, inicio_y]]
    direccion    = [TAMANO_CUADRO, 0]
    comida       = generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto)
    puntos       = 0
    tiempo_inicio = pygame.time.get_ticks()

    gestos      = GestosTactiles() if MODO_TACTIL else None
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
                    else:
                        return resultado, puntos, tiempo_transcurrido

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    resultado = menu_pausa(puntos, tiempo_transcurrido)
                    if resultado == 'continuar':
                        tiempo_inicio = pygame.time.get_ticks() - int(tiempo_transcurrido * 1000)
                    else:
                        return resultado, puntos, tiempo_transcurrido
                elif evento.key == pygame.K_UP:
                    direccion = aplicar_swipe('arriba', direccion)
                elif evento.key == pygame.K_DOWN:
                    direccion = aplicar_swipe('abajo', direccion)
                elif evento.key == pygame.K_LEFT:
                    direccion = aplicar_swipe('izquierda', direccion)
                elif evento.key == pygame.K_RIGHT:
                    direccion = aplicar_swipe('derecha', direccion)

            elif MODO_TACTIL and gestos:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    gestos.inicio_touch(evento.pos)
                elif evento.type == pygame.MOUSEBUTTONUP:
                    swipe = gestos.detectar_swipe(evento.pos)
                    direccion = aplicar_swipe(swipe, direccion)
                elif evento.type == pygame.FINGERDOWN:
                    gestos.inicio_touch((int(evento.x * ANCHO), int(evento.y * ALTO)))
                elif evento.type == pygame.FINGERUP:
                    swipe = gestos.detectar_swipe((int(evento.x * ANCHO), int(evento.y * ALTO)))
                    direccion = aplicar_swipe(swipe, direccion)

        # Mover cabeza
        cabeza = [serpiente[0][0] + direccion[0], serpiente[0][1] + direccion[1]]

        if con_bordes:
            limite_der = juego_x + juego_ancho - TAMANO_CUADRO
            limite_aba = juego_y + juego_alto  - TAMANO_CUADRO
            if (cabeza[0] < juego_x or cabeza[0] > limite_der or
                    cabeza[1] < juego_y or cabeza[1] > limite_aba or
                    cabeza in serpiente):
                return 'gameover', puntos, tiempo_transcurrido
        else:
            # Wrap-around
            cabeza[0] = cabeza[0] % juego_ancho
            cabeza[1] = cabeza[1] % juego_alto
            if cabeza in serpiente:
                return 'gameover', puntos, tiempo_transcurrido

        serpiente.insert(0, cabeza)
        if cabeza == comida:
            puntos += 1
            comida = generar_comida(serpiente, juego_x, juego_y, juego_ancho, juego_alto)
        else:
            serpiente.pop()

        # Dibujo
        pantalla.fill(NEGRO)
        if con_bordes:
            pygame.draw.rect(pantalla, (20, 20, 20),
                             [juego_x, juego_y + offset_y, juego_ancho, juego_alto])
            pygame.draw.rect(pantalla, BLANCO,
                             [juego_x, juego_y + offset_y, juego_ancho, juego_alto], 3)

        dibujar_serpiente(serpiente, offset_y)
        pygame.draw.rect(pantalla, ROJO,
                         [comida[0] + 2, comida[1] + offset_y + 2,
                          TAMANO_CUADRO - 4, TAMANO_CUADRO - 4])
        dibujar_barra_info(puntos, tiempo_transcurrido, boton_pausa)
        pygame.display.flip()
        reloj.tick(fps)


def game_over(puntos, tiempo):
    boton_reiniciar = Boton(ANCHO // 2, 240, 'REINICIAR', VERDE, 160)
    boton_menu      = Boton(ANCHO // 2, 310, 'MENU PRINCIPAL', ROJO, 180)
    botones    = [boton_reiniciar, boton_menu]
    resultados = ['reiniciar', 'menu']
    indice_actual = 0

    while True:
        pantalla.fill(NEGRO)

        fin_txt = fuente_grande.render('GAME OVER', True, ROJO)
        pantalla.blit(fin_txt, [ANCHO // 2 - fin_txt.get_width() // 2, 80])

        puntos_txt = fuente.render(f'Puntuacion: {puntos}', True, BLANCO)
        pantalla.blit(puntos_txt, [ANCHO // 2 - puntos_txt.get_width() // 2, 150])

        tiempo_txt = fuente.render(f'Tiempo: {formatear_tiempo(tiempo)}', True, BLANCO)
        pantalla.blit(tiempo_txt, [ANCHO // 2 - tiempo_txt.get_width() // 2, 185])

        for i, boton in enumerate(botones):
            boton.seleccionado = (i == indice_actual)
            boton.dibujar(pantalla)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                for i, boton in enumerate(botones):
                    if boton.clickeado(evento.pos):
                        return resultados[i]

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_UP, pygame.K_DOWN):
                    indice_actual = (indice_actual + 1) % 2
                elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return resultados[indice_actual]


# --- Bucle principal ---

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
