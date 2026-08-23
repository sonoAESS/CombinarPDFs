"""
Genera el icono de la aplicación (assets/icon.png y assets/icon.ico).

Diseño: dos hojas de documento superpuestas que se fusionan, con una
insignia circular "+" en la esquina inferior derecha, sobre un fondo
oscuro redondeado con degradado (paleta estilo Sun Valley).

Uso:
    python tools/make_icon.py
"""

import os

from PIL import Image, ImageDraw

S = 512  # lienzo base
RADIO = 110  # radio de las esquinas del fondo

COLOR_FONDO_TOP = (31, 39, 51)      # #1f2733
COLOR_FONDO_BOTTOM = (16, 22, 30)   # #101616e -> #101620 aprox
COLOR_HOJA = (245, 247, 250)
COLOR_HOJA_TRASERA = (196, 208, 222)
COLOR_DOBLEZ = (168, 182, 198)
COLOR_ACENTO = (0, 120, 212)        # #0078d4
COLOR_ACENTO_CLARO = (96, 205, 255) # #60cdff

DESTINO = os.path.join(os.path.dirname(__file__), "..", "assets")
TAMANOS_ICO = [(16, 16), (24, 24), (32, 32), (48, 48),
               (64, 64), (128, 128), (256, 256)]


def fondo_redondeado():
    """Cuadrado redondeado con degradado vertical."""
    gradiente = Image.new("RGBA", (S, S))
    px = gradiente.load()
    for y in range(S):
        t = y / (S - 1)
        color = tuple(
            int(COLOR_FONDO_TOP[i] + (COLOR_FONDO_BOTTOM[i] - COLOR_FONDO_TOP[i]) * t)
            for i in range(3)
        ) + (255,)
        for x in range(S):
            px[x, y] = color
    mascara = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [8, 8, S - 8, S - 8], radius=RADIO, fill=255
    )
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.paste(gradiente, (0, 0), mascara)
    return img


def hoja(img, d, caja, relleno, doblez_color):
    """Dibuja una página con esquina superior derecha doblada."""
    x0, y0, x1, y1 = caja
    f = int((x1 - x0) * 0.22)
    cuerpo = [
        (x0, y0),
        (x1 - f, y0),
        (x1, y0 + f),
        (x1, y1),
        (x0, y1),
    ]
    d.polygon(cuerpo, fill=relleno)
    d.polygon([(x1 - f, y0), (x1 - f, y0 + f), (x1, y0 + f)], fill=doblez_color)
    # líneas de "texto"
    margen = int((x1 - x0) * 0.14)
    ancho_linea = max(6, int((x1 - x0) * 0.055))
    paso = int((y1 - y0) * 0.17)
    for i in range(1, 4):
        y = y0 + margen + i * paso
        if y < y1 - margen // 2:
            d.rounded_rectangle(
                [x0 + margen, y, x1 - margen, y + ancho_linea],
                radius=ancho_linea // 2,
                fill=(203, 213, 225),
            )


def insignia(img):
    """Círculo azul con '+' blanco en la esquina inferior derecha."""
    d = ImageDraw.Draw(img)
    cx, cy, r = int(S * 0.70), int(S * 0.72), int(S * 0.155)
    d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10],
              fill=COLOR_FONDO_BOTTOM)
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=COLOR_ACENTO,
              outline=COLOR_ACENTO_CLARO, width=max(4, S // 170))
    grosor = max(10, int(r * 0.28))
    brazo = int(r * 0.62)
    d.rounded_rectangle([cx - brazo, cy - grosor // 2, cx + brazo, cy + grosor // 2],
                        radius=grosor // 2, fill=(255, 255, 255))
    d.rounded_rectangle([cx - grosor // 2, cy - brazo, cx + grosor // 2, cy + brazo],
                        radius=grosor // 2, fill=(255, 255, 255))


def generar():
    os.makedirs(DESTINO, exist_ok=True)

    img = fondo_redondeado()
    d = ImageDraw.Draw(img)

    # Hoja trasera (desplazada arriba-izquierda) y hoja frontal
    hoja(img, d, (int(S*0.20), int(S*0.14), int(S*0.58), int(S*0.66)),
         COLOR_HOJA_TRASERA, COLOR_DOBLEZ)
    hoja(img, d, (int(S*0.34), int(S*0.26), int(S*0.76), int(S*0.82)),
         COLOR_HOJA, COLOR_DOBLEZ)

    insignia(img)

    png_path = os.path.join(DESTINO, "icon.png")
    ico_path = os.path.join(DESTINO, "icon.ico")

    img.save(png_path)
    img.save(ico_path, sizes=TAMANOS_ICO)

    print(f"Generados:\n  {os.path.abspath(png_path)}\n  {os.path.abspath(ico_path)}")


if __name__ == "__main__":
    generar()
