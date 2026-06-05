import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import librosa
import imageio_ffmpeg
import subprocess
import re

def corregir_ortografia_whisper(texto):
    """
    (C) Rebeldía Cósmica
    Limpia los artefactos y alucinaciones comunes de Whisper en español.
    """
    # Fallos comunes de caracteres raros
    texto = texto.replace("s??", "sé")
    texto = texto.replace("q??", "qué")
    texto = texto.replace("a??", "ahí")
    # Limpiar exceso de signos de interrogación aislados
    texto = re.sub(r'\?+', '?', texto)
    texto = re.sub(r' +', ' ', texto)
    return texto.strip()

def transcribir_audio_para_edicion(audio_path, model_size="medium", max_duration=0):
    """
    Extrae la letra usando Whisper y la pasa por el corrector ortográfico.
    Devuelve el texto puro para que el usuario lo edite en la UI.
    """
    import torch
    try:
        try:
            import stable_whisper
        except ImportError:
            print("Instalando stable-ts automáticamente en este entorno...")
            import subprocess
            import sys
            import importlib
            import site
            subprocess.check_call([sys.executable, "-m", "pip", "install", "stable-ts"])
            # Limpiar caché de Python para que detecte la nueva instalación
            importlib.invalidate_caches()
            if hasattr(site, 'main'): site.main()
            import stable_whisper
            
        # --- PARCHE FFMPEG (Seguridad) ---
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir
            
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dur = max_duration if max_duration > 0 else None
        audio_array, _ = librosa.load(audio_path, sr=16000, mono=True, duration=dur)
        model = stable_whisper.load_model(model_size, device=device)
        result = model.transcribe(audio_array, language='es', vad=False)
        
        # Guardar JSON preliminar
        json_path = os.path.splitext(audio_path)[0] + ".json"
        result.save_as_json(json_path)
        
        # Extraer texto y corregir ortografía
        texto_crudo = result.text if hasattr(result, 'text') else ""
        texto_limpio = corregir_ortografia_whisper(texto_crudo)
        return texto_limpio
    except Exception as e:
        print(f"Error extrayendo letra para edición: {e}")
        import traceback
        traceback.print_exc()
        return f"Error al transcribir el audio. Detalles técnicos: {e}"

class LyricsEngine:
    def __init__(self, audio_path, max_duration=None, position="Abajo", progress_callback=None):
        """
        Inicializa el motor de lyrics.
        :param audio_path: Ruta al archivo de audio.
        :param max_duration: Si se especifica, solo procesa esta cantidad de segundos.
        :param position: "Abajo" o "Centro".
        :param progress_callback: Función f(current, total) para reportar progreso a la UI.
        """
        self.audio_path = os.path.abspath(audio_path)
        self.max_duration = max_duration
        self.position = position
        self.progress_callback = progress_callback
        # El archivo JSON se guardará en la misma carpeta que el audio con el mismo nombre base
        self.json_path = os.path.splitext(audio_path)[0] + ".json"
        self.data = {} # Inicializar vacío para evitar NoneType error
        self.words = []
        
        # 1. Gestión Inteligente de Transcripción (Caché vs Edición Manual)
        txt_path = os.path.splitext(self.audio_path)[0] + ".txt"
        should_transcribe = True
        
        if os.path.exists(self.json_path):
            # Si existe JSON, verificamos si el TXT es más nuevo (usuario lo editó)
            if os.path.exists(txt_path):
                json_mtime = os.path.getmtime(self.json_path)
                txt_mtime = os.path.getmtime(txt_path)
                if txt_mtime > json_mtime:
                    print("📝 [LyricsEngine] Se detectaron cambios en el archivo .txt. Re-alineando...")
                    should_transcribe = True
                else:
                    should_transcribe = False
            else:
                should_transcribe = False
        
        if not should_transcribe:
             self.load_transcription()
        else:
            self.transcribe_audio()
            
        # Pre-procesar para búsqueda rápida
        self._flatten_words()
        
        # RE-SEGMENTACIÓN DINÁMICA (Intervalos cortos para video)
        self._resegment_dynamic(max_words=4, max_duration=2.0)
        
        # Imprimir resultados en consola (Requerimiento usuario)
        self.print_lyrics()

    def _get_external_lyrics(self):
        """
        Intenta obtener la letra original desde:
        1. Un archivo .txt con el mismo nombre.
        2. Los metadatos del archivo de audio (FFmpeg).
        Retorna el texto (str) o None.
        """
        # 1. Buscar archivo .txt (Prioridad Alta - Fácil de editar para el usuario)
        txt_path = os.path.splitext(self.audio_path)[0] + ".txt"
        if os.path.exists(txt_path):
            try:
                print(f"   📄 Archivo de letra encontrado: {txt_path}")
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    print(f"   📝 Preview del texto: '{text[:60]}...'")
                    return text
            except Exception as e:
                print(f"   ⚠️ Error leyendo .txt: {e}")

        # 2. Buscar en Metadatos (FFmpeg)
        # DESACTIVADO: Para evitar que lea letras incrustadas incorrectas y fuerce alineación.
        # Si el usuario quiere usar letra externa, debe crear un archivo .txt explícitamente.
            
        return None

    def transcribe_audio(self):
        """
        Ejecuta stable-ts para obtener timestamps a nivel de palabra.
        """
        print(f"🎤 [LyricsEngine] Iniciando transcripción con Stable Whisper (Modelo 'base')...")
        print(f"   Audio: {self.audio_path}")
        
        try:
            try:
                import stable_whisper
            except ImportError:
                print("Instalando stable-ts automáticamente...")
                import subprocess
                import sys
                import importlib
                import site
                subprocess.check_call([sys.executable, "-m", "pip", "install", "stable-ts"])
                importlib.invalidate_caches()
                if hasattr(site, 'main'): site.main()
                import stable_whisper
        except Exception as e:
            print(f"❌ Error Crítico: No se pudo cargar o instalar 'stable-ts': {e}")
            return

        # --- PARCHE FFMPEG (Seguridad) ---
        # Aseguramos que stable-ts tenga acceso a ffmpeg por si acaso
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + ffmpeg_dir

        # Detectar GPU para acelerar Whisper
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   🚀 Dispositivo de inferencia: {device}")

        try:
            # Cargar modelo y transcribir
            # CARGA DE AUDIO CON LIBROSA (Más robusto que FFmpeg CLI)
            print(f"   🔊 Cargando audio con Librosa (16kHz)...")
            audio_array, _ = librosa.load(self.audio_path, sr=16000, mono=True, duration=self.max_duration)

            # CAMBIO: Usamos 'medium' en lugar de 'large-v2' para evitar que se congele en CPU
            print("   🧠 Cargando modelo Whisper 'medium' (Balance velocidad/precisión)...")
            try:
                model = stable_whisper.load_model('medium', device=device)
            except Exception as e:
                print(f"❌ Error crítico en PyTorch/Whisper al cargar modelo: {e}")
                print("⚠️ Fallback: Ejecución sin letras.")
                return
            
            # --- ALINEACIÓN FORZADA VS TRANSCRIPCIÓN ---
            external_text = self._get_external_lyrics()
            
            if external_text:
                print("   🎯 MODO ALINEACIÓN: Usando letra original para sincronizar...")
                # align() fuerza al modelo a usar este texto y solo buscar los tiempos
                result = model.align(
                    audio_array, 
                    external_text, 
                    language='es',
                    progress_callback=self.progress_callback
                )
            else:
                print("   ✍️  MODO TRANSCRIPCIÓN: La IA adivinará la letra...")
                # verbose=True mostrará el progreso frase por frase
                result = model.transcribe(
                    audio_array, 
                    language='es', 
                    vad=False, 
                    verbose=True,
                    progress_callback=self.progress_callback
                )
            
            # Guardar en JSON para futuras ejecuciones
            result.save_as_json(self.json_path)
            self.data = result.to_dict()
            
            # --- FIX: Guardar TXT con la nueva detección ---
            if not external_text:
                try:
                    # Obtener texto completo detectado
                    full_text = ""
                    if hasattr(result, 'text'):
                        full_text = result.text
                    else:
                        full_text = "\n".join([s.get('text', '').strip() for s in self.data.get('segments', [])])
                    
                    txt_path = os.path.splitext(self.audio_path)[0] + ".txt"
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(full_text.strip())
                    print(f"   📄 Texto detectado guardado en: {txt_path}")
                except Exception as e:
                    print(f"   ⚠️ No se pudo guardar TXT: {e}")

            print(f"✅ Transcripción completada y guardada en: {self.json_path}")
            
        except Exception as e:
            print(f"❌ Error durante la transcripción: {e}")
            import traceback
            traceback.print_exc()

    def load_transcription(self):
        """Carga el JSON de caché si ya existe."""
        print(f"📂 [LyricsEngine] Cargando lyrics desde caché: {self.json_path}")
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"❌ Error cargando JSON: {e}")
            self.data = {}

    def _flatten_words(self):
        """
        Aplana la estructura jerárquica (Segmentos -> Palabras) a una lista simple
        para facilitar la búsqueda por tiempo.
        """
        self.words = []
        if not self.data:
            return

        # --- FILTRO ANTI-ALUCINACIONES (Whisper) ---
        # Palabras o frases que indican que el modelo está leyendo metadatos o inventando
        BLACKLIST = [
            "https:", "http:", "www.", ".com", ".net", ".org", 
            "bandcamp", "instagram", "facebook", "twitter", 
            "subscribe", "visit", "thanks for watching", "gracias por ver",
            "subtitles by", "captioned by", "sync by", "provided by"
        ]

        # La estructura de stable-ts suele ser: {'segments': [{'words': [...]}, ...]}
        segments = self.data.get('segments', [])
        
        for seg in segments:
            # 1. Filtro rápido por texto del segmento
            seg_text = seg.get('text', '').lower()
            if any(bad in seg_text for bad in BLACKLIST):
                print(f"   🗑️ Filtrando alucinación detectada: '{seg.get('text')}'")
                continue

            # Verificar si existen timestamps por palabra (word_timestamps)
            if 'words' in seg and seg['words']:
                for w in seg['words']:
                    text = w.get('word', w.get('text', '')).strip()
                    # 2. Filtro por palabra individual
                    if any(bad in text.lower() for bad in BLACKLIST):
                        continue
                        
                    if text:
                        self.words.append({
                            'text': text,
                            'start': w['start'],
                            'end': w['end']
                        })
            else:
                # Fallback: Usar el segmento completo si no hay detalle de palabras
                text = seg.get('text', '').strip()
                if text:
                    self.words.append({
                        'text': text,
                        'start': seg['start'],
                        'end': seg['end']
                    })
        
        print(f"📝 [LyricsEngine] Se cargaron {len(self.words)} palabras/segmentos.")

    def _resegment_dynamic(self, max_words=4, max_duration=2.5):
        """
        Reconstruye self.data['segments'] agrupando palabras en intervalos cortos.
        Esto crea subtítulos estilo 'TikTok' o 'Lyric Video' dinámico.
        """
        if not self.words: return

        new_segments = []
        current_segment = []
        current_start = self.words[0]['start']
        
        for i, word in enumerate(self.words):
            current_segment.append(word)
            
            # Calcular duración actual del grupo
            duration = word['end'] - current_start
            
            # Condiciones de corte:
            # 1. Máximo de palabras alcanzado
            # 2. Duración máxima excedida
            # 3. Pausa grande con la siguiente palabra (si existe)
            
            force_break = False
            if i < len(self.words) - 1:
                gap = self.words[i+1]['start'] - word['end']
                if gap > 0.5: # Si hay silencio de 0.5s, cortar
                    force_break = True
            
            if len(current_segment) >= max_words or duration > max_duration or force_break:
                # Crear segmento
                seg_text = " ".join([w['text'] for w in current_segment])
                new_segments.append({
                    'start': current_start,
                    'end': word['end'],
                    'text': seg_text,
                    'words': current_segment
                })
                # Reset
                current_segment = []
                if i < len(self.words) - 1:
                    current_start = self.words[i+1]['start']

        # Añadir lo que sobre
        if current_segment:
            seg_text = " ".join([w['text'] for w in current_segment])
            new_segments.append({
                'start': current_start,
                'end': current_segment[-1]['end'],
                'text': seg_text,
                'words': current_segment
            })
            
        # Sobrescribir los segmentos originales con los optimizados
        self.data['segments'] = new_segments
        
        # --- GUARDAR JSON LIMPIO Y SEGMENTADO ---
        # Esto asegura que si el usuario abre el editor, vea la versión limpia y cortada
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ No se pudo guardar el JSON actualizado: {e}")
            
        print(f"✂️ [LyricsEngine] Re-segmentado en {len(new_segments)} frases cortas (Max {max_words} palabras).")

    def print_lyrics(self):
        """Imprime la letra extraída y sus tiempos en la consola."""
        segments = self.data.get('segments', [])
        print(f"\n📜 --- LETRA RE-SEGMENTADA ({len(segments)} bloques) ---")
        for s in segments:
            print(f"   [{s['start']:.2f}s - {s['end']:.2f}s] {s['text']}")
        print("----------------------------------------------------------\n")

    def get_current_word_data(self, time):
        """
        Busca la palabra activa en el tiempo t.
        Retorna el diccionario de la palabra {'text': str, 'start': float, 'end': float} o None.
        """
        # Búsqueda lineal (Suficiente para < 5000 palabras en una canción típica)
        for w in self.words:
            if w['start'] <= time <= w['end']:
                return w
        return None

    def get_current_word(self, time):
        """Wrapper de compatibilidad."""
        w = self.get_current_word_data(time)
        return w['text'] if w else None

    def get_text_mask(self, time, resolution_xy):
        """
        Genera una máscara NumPy con la palabra actual rasterizada.
        
        :param time: Tiempo actual en segundos.
        :param resolution_xy: Tupla (width, height) del grid de destino.
        :return: Array NumPy (height, width) float32, valores 0.0 a 1.0.
        """
        w, h = resolution_xy
        word = self.get_current_word(time)
        
        # Si no hay palabra activa, retornar máscara vacía (negra)
        if not word:
            return np.zeros((h, w), dtype=np.float32)
            
        # 1. Crear imagen PIL (Modo 'L' = Escala de grises 8-bit)
        img = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(img)
        
        # 2. Configurar Fuente (Dinámica según altura del grid)
        font_size = int(h * 0.5) # La letra ocupa el 50% de la altura
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default() # Fallback
        
        # 3. Calcular posición para centrar el texto
        try:
            # Pillow >= 9.2.0
            left, top, right, bottom = draw.textbbox((0, 0), word, font=font)
            text_w, text_h = right - left, bottom - top
        except AttributeError:
            # Pillow antiguo
            text_w, text_h = draw.textsize(word, font=font)
            
        x = (w - text_w) // 2
        y = (h - text_h) // 2
        
        # 4. Dibujar texto en blanco (255)
        draw.text((x, y), word, font=font, fill=255)
        
        # 5. Convertir a NumPy y Normalizar (0.0 - 1.0)
        # Esto permite usarlo directamente como multiplicador en las ecuaciones físicas
        mask = np.array(img, dtype=np.float32) / 255.0
        
        return mask

    def draw(self, frame, time, kick=0.0, snare=0.0, energy=0.0):
        """
        Dibuja la palabra actual en el frame usando OpenCV/Pillow con estética Cyberpunk Neón y Cromestesia.
        Incluye posicionamiento y animaciones suaves (Fade-in).
        """
        w_data = self.get_current_word_data(time)
        if not w_data:
            return frame
            
        word = w_data['text']
        start_t = w_data['start']
        end_t = w_data['end']
            
        h, w = frame.shape[:2]
        
        # Animación de Fade-in (Pro Lyrics)
        duracion_palabra = end_t - start_t
        progreso = min(max((time - start_t) / (duracion_palabra * 0.3 + 0.001), 0.0), 1.0)
        alpha_fade = int(255 * progreso)
        
        # Suavizado del kick y energy para evitar saltos violentos
        if not hasattr(self, 'smoothed_kick'):
            self.smoothed_kick = 0.0
            self.smoothed_energy = 0.0
            
        self.smoothed_kick = self.smoothed_kick * 0.7 + kick * 0.3
        self.smoothed_energy = self.smoothed_energy * 0.8 + energy * 0.2
        
        # Crear imagen con canal Alfa transparente para superposición suave
        img_pil = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_pil)
        
        # Tamaño dinámico reactivo al kick (latido del texto)
        base_size = int(h * 0.08)
        kick_bump = int((h * 0.04) * self.smoothed_kick)
        font_size = base_size + kick_bump
        
        try:
            font = ImageFont.truetype("impact.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("ariblk.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
        try:
            left, top, right, bottom = draw.textbbox((0, 0), word, font=font)
            text_w, text_h = right - left, bottom - top
        except AttributeError:
            text_w, text_h = draw.textsize(word, font=font)
        
        # Posicionamiento (Abajo vs Centro)
        x = (w - text_w) // 2
        if self.position == "Centro":
            y = (h - text_h) // 2
        else:
            y = int(h * 0.80) - (text_h // 2)
        
        # --- CROMESTESIA Y ESTÉTICA CYBERPUNK ---
        # Aberración Cromática ligada a la energía del audio
        glitch_offset = int((w * 0.01) * self.smoothed_energy) + 2
        
        # Colores reactivos: Cyan y Magenta base
        cyan_color = (0, 255, int(200 + 55 * self.smoothed_kick), alpha_fade)
        magenta_color = (int(200 + 55 * self.smoothed_kick), 0, 255, alpha_fade)
        blanco_core = (255, 255, 255, alpha_fade)
        
        # Sombra paralela / Glow difuso
        shadow_offset = max(2, font_size // 12)
        glow_intensity = int((100 + 155 * self.smoothed_energy) * progreso)
        cyan_glow = (cyan_color[0], cyan_color[1], cyan_color[2], glow_intensity)
        magenta_glow = (magenta_color[0], magenta_color[1], magenta_color[2], glow_intensity)
        
        # Dibujar Aberración Cromática (Glow expansivo)
        for ox in range(-shadow_offset, shadow_offset + 1, 2):
            for oy in range(-shadow_offset, shadow_offset + 1, 2):
                if ox != 0 or oy != 0:
                    draw.text((x + ox - glitch_offset, y + oy), word, font=font, fill=cyan_glow)
                    draw.text((x + ox + glitch_offset, y + oy), word, font=font, fill=magenta_glow)
        
        # Glitch Offset (Rojo y Azul duros)
        draw.text((x - glitch_offset, y), word, font=font, fill=cyan_color)
        draw.text((x + glitch_offset, y), word, font=font, fill=magenta_color)
        
        # Core text
        draw.text((x, y), word, font=font, fill=blanco_core)
        
        # Convertir a numpy RGBA
        img_np = np.array(img_pil)
        
        # --- ONDAS LÍQUIDAS Y DISTORSIÓN (EFECTO PSICODÉLICO) ---
        if self.smoothed_energy > 0.1:
            Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
            # Oscilación ondulante dependiente de la energía (kick) y el tiempo
            map_x = X + np.sin(Y * 0.05 + time * 4.0) * (2.0 + self.smoothed_kick * 10.0)
            map_y = Y + np.cos(X * 0.03 + time * 3.0) * (1.0 + self.smoothed_kick * 5.0)
            img_np = cv2.remap(img_np, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        
        # Mezclar (Alpha Compositing)
        alpha = img_np[:, :, 3] / 255.0
        for c in range(3):
            frame[:, :, c] = frame[:, :, c] * (1.0 - alpha) + img_np[:, :, c] * alpha
            
        return frame