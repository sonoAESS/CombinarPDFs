# llm_translator.py
import os
import textwrap
from typing import List, Optional
import re

from llama_cpp import Llama      # pip install llama-cpp-python
from pypdf import PdfReader      # pip install pypdf

# Configuración del modelo (ajusta la ruta al tuyo)
MODEL_PATH = r"D:\Coding\reporteEXE\llama.cpp\qwen.gguf"
N_THREADS = 4
N_CTX = 4096
MODEL_TEMPERATURE = 0.2
MAX_TOKENS_OUT = 800
CHARS_PER_BLOCK = 2000

# Instancia global (lazy load)
_llm_instance: Optional[Llama] = None


def get_llm() -> Llama:
    """
    Devuelve una instancia de Llama cargada.
    Carga el modelo solo la primera vez que se llama.
    """
    global _llm_instance
    if _llm_instance is None:
        print("Cargando modelo LLM local...")
        _llm_instance = Llama(
            model_path=MODEL_PATH,
            n_threads=N_THREADS,
            n_ctx=N_CTX,
            logits_all=False,
            verbose=False,
        )
        print("Modelo LLM cargado.")
    return _llm_instance


def extraer_texto_pdf(ruta_pdf: str) -> str:
    """Extrae texto de todas las páginas de un PDF."""
    reader = PdfReader(ruta_pdf)
    textos = []
    for page in reader.pages:
        try:
            txt = page.extract_text()
        except Exception:
            txt = ""
        if txt:
            textos.append(txt)
    return "\n\n".join(textos)


def partir_en_bloques(texto: str, max_chars: int) -> List[str]:
    """Parte el texto en bloques de longitud máxima max_chars respetando párrafos."""
    parrafos = texto.split("\n\n")
    bloques = []
    bloque_actual = ""

    for p in parrafos:
        p = p.strip()
        if not p:
            continue
        if len(bloque_actual) + len(p) + 2 <= max_chars:
            if bloque_actual:
                bloque_actual += "\n\n" + p
            else:
                bloque_actual = p
        else:
            if bloque_actual:
                bloques.append(bloque_actual)
            if len(p) > max_chars:
                for chunk in textwrap.wrap(p, max_chars):
                    bloques.append(chunk)
                bloque_actual = ""
            else:
                bloque_actual = p

    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


def traducir_bloque_a_markdown(texto_en: str) -> str:
    """
    Traduce un bloque de texto en inglés a español, dando una salida tipo Markdown sencillo.
    """
    llm = get_llm()

    prompt = (
        "Eres un traductor experto en textos científicos.\n"
        "Traduce el siguiente texto académico del inglés al español, "
        "manteniendo terminología técnica y estructura.\n"
        "Usa un formato sencillo de Markdown (títulos con #, párrafos, listas cuando existan), "
        "pero no inventes secciones.\n\n"
        "Texto en inglés:\n"
        f"{texto_en}\n\n"
        "Traducción al español en Markdown:"
    )

    resp = llm(
        prompt,
        temperature=MODEL_TEMPERATURE,
        max_tokens=MAX_TOKENS_OUT,
        stop=["Texto en inglés:", "Traducción al español en Markdown:"],
    )

    texto_out = ""
    if "choices" in resp and len(resp["choices"]) > 0:
        texto_out = resp["choices"][0].get("text", "")
    return texto_out.strip()


def traducir_pdf_a_markdown(ruta_pdf: str) -> str:
    """
    Traduce un PDF inglés→español y devuelve un string en Markdown sencillo.
    """
    if not os.path.isfile(ruta_pdf):
        raise FileNotFoundError(f"No existe el archivo PDF: {ruta_pdf}")

    print(f"Extrayendo texto de: {ruta_pdf}")
    texto = extraer_texto_pdf(ruta_pdf)
    texto = cortar_referencias(texto)

    print("Partiendo en bloques...")
    bloques = partir_en_bloques(texto, CHARS_PER_BLOCK)
    print(f"Número de bloques: {len(bloques)}")

    traducciones = []
    for i, bloque in enumerate(bloques, start=1):
        print(f"Traduciendo bloque {i}/{len(bloques)}...")
        try:
            md = traducir_bloque_a_markdown(bloque)
        except Exception as e:
            print(f"  ERROR en bloque {i}: {e}")
            md = f"\n\n<!-- ERROR en bloque {i}: {e} -->\n"
        traducciones.append(md)

    markdown_final = "\n\n".join(traducciones)
    return markdown_final

def cortar_referencias(texto: str) -> str:
    """
    Devuelve el texto hasta antes de la sección de referencias/bibliografía.
    Busca encabezados típicos como 'References', 'Bibliography', 'Referencias'.
    """
    # patrones típicos de encabezado (al inicio de línea, opcional numeración)
    patrones = [
        r"^\s*references\s*$",
        r"^\s*bibliography\s*$",
        r"^\s*referencias\s*$",
        r"^\s*lista de referencias\s*$",
    ]

    lines = texto.splitlines()
    indices_corte = []

    for i, line in enumerate(lines):
        lower = line.strip().lower()
        for pat in patrones:
            if re.match(pat, lower, flags=re.IGNORECASE):
                indices_corte.append(i)
                break

    if not indices_corte:
        # no se encontró sección de referencias
        return texto

    idx = min(indices_corte)  # primer match
    # devolvemos todo lo anterior a ese encabezado
    return "\n".join(lines[:idx]).strip()