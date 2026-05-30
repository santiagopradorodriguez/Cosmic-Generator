import ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Union
import json
import re

app = FastAPI(title="Director IA - Audio Visualizer")

# Modelo de datos para la entrada
class PromptRequest(BaseModel):
    prompt: str
    current_lyrics: str = ""

class ConfigResponse(BaseModel):
    engines: List[str]
    render_modes: List[str] = []
    objects: List[str] = []
    explanation: str
    colors: Union[str, List[str]]

class LyricsRequest(BaseModel):
    text: str

# Definición de los motores disponibles para que la IA sepa qué elegir
AVAILABLE_ENGINES = {
    "GS": "Patrones biológicos, manchas, Turing, reacción-difusión, orgánico.",
    "KS": "Caos, fuego, llamas, turbulencia, inestable.",
    "GPE": "Cuántica, condensados, superfluido, místico, etéreo, gas.",
    "WAVE": "Agua, ondas, gotas, lluvia, acústica, vibración.",
    "CH": "Aceite y agua, separación de fases, burbujas, celular.",
    "PARTICLES": "Flujo, viento, estrellas, polvo, arena.",
    "LORENZ": "Atractores extraños, mariposas, matemáticas, líneas vectoriales.",
    "GEOMETRY": "Geometría sagrada, mandalas, estructura rígida.",
    "KDV": "Solitones, ondas solitarias, pulsos."
}

AVAILABLE_MODES = {
    "God Mode": "Estándar, equilibrado, mezcla todo, cinematográfico.",
    "Neural": "IA, abstracto, onírico, mapeo directo audio-física.",
    "Clásico": "Estable, simulación pura, ambient.",
    "Lenia": "Vida artificial, células, biológico, microscópico.",
    "Fluidos": "Humo, tinta, realismo físico (LBM).",
    "Caos": "Atractores 3D, matemáticas, líneas, orbital.",
    "Fractales": "Helechos, Sierpinski, geometría recursiva.",
    "Legacy": "Estilo retro, crudo, glitch."
}

AVAILABLE_OBJECTS = {
    "Spirits": "Entidades que bailan, fantasmas.",
    "Kaleido": "Simetría radial, mandalas.",
    "Flash": "Destellos con el beat, intensidad.",
    "Chroma": "Color cambia con la nota musical."
}

@app.post("/analyze_scene", response_model=ConfigResponse)
async def analyze_scene(request: PromptRequest):
    """
    Analiza una descripción en lenguaje natural y decide qué motores activar.
    """
    system_prompt = f"""
    Eres un Director de Visuales (VJ) experto en física simulada.
    Tu trabajo es traducir la intención artística del usuario a una configuración técnica.
    
    MODOS DE RENDER (Scripts):
    {json.dumps(AVAILABLE_MODES, indent=2)}

    OBJETOS Y ESTILOS:
    {json.dumps(AVAILABLE_OBJECTS, indent=2)}

    MOTORES FÍSICOS (Solo para God Mode):
    {json.dumps(AVAILABLE_ENGINES, indent=2)}
    
    INSTRUCCIONES:
    1. Selecciona 1 o más MODOS DE RENDER (ej. 'God Mode', 'Fractales').
    2. Selecciona OBJETOS/ESTILOS (ej. 'Spirits', 'Kaleido').
    3. Selecciona MOTORES FÍSICOS (ej. 'GS', 'WAVE') si usas God Mode.
    4. Sugiere una paleta de colores (ej. 'magma', 'viridis', 'inferno', 'ocean').
    5. Responde SOLAMENTE en formato JSON válido.
    
    Ejemplo de salida JSON:
    {{
        "render_modes": ["God Mode", "Fractales"],
        "objects": ["Spirits", "Chroma"],
        "engines": ["GS", "PARTICLES"],
        "explanation": "Seleccioné Gray-Scott para la textura orgánica y Partículas para el flujo etéreo.",
        "colors": "twilight"
    }}
    """

    try:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"El usuario quiere este estilo visual: '{request.prompt}'"}
        ])
        
        content = response['message']['content']
        print("\n" + "="*40)
        print(f"🤖 PENSAMIENTO IA (RAW):\n{content}") 
        print("="*40 + "\n")
        
        # Limpieza robusta usando Regex para encontrar el primer objeto JSON válido
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            
            # FIX: Si la IA devuelve una lista de colores, tomamos el primero para evitar error de validación
            if "colors" in data and isinstance(data["colors"], list):
                data["colors"] = data["colors"][0] if data["colors"] else "viridis"

            return ConfigResponse(**data)
        else:
            raise ValueError("No se encontró JSON válido en la respuesta de la IA")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO IA: {e}")
        print("👉 Sugerencia: Asegúrate de tener Ollama corriendo y el modelo 'llama3.2' instalado.")
        # Fallback por defecto
        return ConfigResponse(engines=["GS", "WAVE"], render_modes=["God Mode"], objects=["Spirits"], explanation=f"ERROR REAL: {str(e)}", colors="viridis")

@app.post("/beautify_lyrics")
async def beautify_lyrics(request: LyricsRequest):
    """
    Toma la letra cruda y la formatea estéticamente (Streaming).
    """
    system_prompt = """
    Eres un corrector ortográfico profesional. Tu única tarea es corregir errores tipográficos, de puntuación y gramática en esta transcripción de una canción. MANTÉN la estructura exacta, los saltos de línea y el estilo poético o coloquial original. NO agregues palabras tuyas ni comentarios, devuelve únicamente la letra corregida.
    """
    
    def generate():
        try:
            stream = ollama.chat(model='llama3.2', messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': request.text}
            ], stream=True, options={'temperature': 0.1}) # Temperatura baja = Cero creatividad/alucinaciones
            
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            yield f"❌ ERROR CRÍTICO: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    print("🧠 Iniciando Cerebro IA en puerto 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)