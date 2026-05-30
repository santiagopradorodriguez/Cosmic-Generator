import sys
import os
import random
import numpy as np
import librosa
import cv2
import torch
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Importar Motor de Lyrics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio.motor_lyrics import LyricsEngine

# Compatibilidad MoviePy 1.0 y 2.0
try:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx, ImageClip, CompositeVideoClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx, ImageClip, CompositeVideoClip

def safe_subclip(clip, start, end):
    """Wrapper seguro para subclip/subclipped"""
    if hasattr(clip, 'subclipped'):
        return clip.subclipped(start, end)
    return clip.subclip(start, end)

def get_visual_energy(video_path):
    """
    Usa PyTorch para calcular la 'Energía Visual' del video.
    Retorna un valor entre 0.0 (Calma) y 1.0 (Caos total).
    """
    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames < 10: return 0.5
        
        # Muestrear 5 frames distribuidos a lo largo del video
        indices = np.linspace(0, total_frames-2, 5).astype(int)
        frames = []
        
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Reducir tamaño para procesar rápido (64x64 es suficiente para ver energía)
                frame = cv2.resize(frame, (64, 64))
                frames.append(frame)
        cap.release()
        
        if len(frames) < 2: return 0.5
        
        # Convertir a Tensor PyTorch (N, H, W, C)
        tensors = torch.tensor(np.array(frames), dtype=torch.float32) / 255.0
        
        # 1. Energía de Movimiento (Diferencia entre frames)
        diffs = tensors[1:] - tensors[:-1]
        motion_score = torch.mean(torch.abs(diffs)).item()
        
        # 2. Energía de Contraste (Desviación estándar de brillo)
        contrast_score = torch.std(tensors).item()
        
        # Fórmula: El movimiento pesa más que el contraste
        return (motion_score * 0.7) + (contrast_score * 0.3)
    except Exception as e:
        print(f"⚠️ No se pudo analizar {os.path.basename(video_path)}: {e}")
        return 0.5

def generar_montaje_ia(audio_path, duration_arg=None, clips_dir_arg=None, output_filename="Director_AI_Final.mp4", progress_callback=None):
    if progress_callback: progress_callback(5, "Iniciando Director IA (Buscando clips)...")

    # 1. Buscar videos generados
    candidates = []
    
    if clips_dir_arg and os.path.exists(clips_dir_arg):
        # Si se especifica carpeta, SOLO buscar ahí para evitar mezclar sesiones
        search_dirs = [clips_dir_arg]
        print(f"📂 Modo Sesión: Buscando clips ÚNICAMENTE en {clips_dir_arg}")
    else:
        # Modo fallback: buscar en todos lados
        search_dirs = [".", "RENDERS", "src"]
        print("🔍 Modo General: Buscando clips en carpetas cercanas...")
    
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".mp4") and "Director" not in f:
                    full_path = os.path.join(d, f)
                    candidates.append(full_path)
    
    if not candidates:
        if progress_callback: progress_callback(0, "Error: No hay clips en la carpeta.")
        return None

    if progress_callback: progress_callback(10, f"Analizando {len(candidates)} clips...")

    # 1.5 Analizar Energía Visual de los Clips (PyTorch)
    print("🧠 Director Neural: Analizando energía visual de los clips...")
    clip_data = []
    for path in candidates:
        score = get_visual_energy(path)
        clip_data.append({'path': path, 'score': score})
        print(f"   👁️ {os.path.basename(path)[:20]}... -> Energía: {score:.3f}")
    
    # Normalizar scores visuales (0.0 a 1.0) para comparar con audio
    scores = [x['score'] for x in clip_data]
    if scores:
        min_s, max_s = min(scores), max(scores)
        if max_s > min_s:
            for x in clip_data:
                x['score'] = (x['score'] - min_s) / (max_s - min_s)

    # 2. Analizar Audio
    if progress_callback: progress_callback(30, "Analizando beats y frecuencias de audio...")
    print(f"🎵 Analizando audio: {os.path.basename(audio_path)}")
    try:
        y, sr = librosa.load(audio_path, duration=duration_arg)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        duration_audio = librosa.get_duration(y=y, sr=sr)
    except Exception as e:
        print(f"❌ Error analizando audio: {e}")
        return

    # 3. Crear Edición
    if progress_callback: progress_callback(50, "Calculando cortes y emparejando clips...")
    print("✂️ Calculando cortes basados en el ritmo...")
    final_clips = []
    
    # Estrategia: Cambiar de clip cada 4 beats (aprox 1 compás)
    beats_per_cut = 4
    if len(beat_times) > 0:
        cut_points = list(beat_times[::beats_per_cut])
        if cut_points[-1] < duration_audio:
            cut_points.append(duration_audio)
    else:
        cut_points = np.arange(0, duration_audio, 2.0)

    last_t = 0
    for t in cut_points:
        if t <= last_t: continue
        seg_len = t - last_t
        
        # --- SELECCIÓN INTELIGENTE ---
        # 1. Calcular energía del audio en este segmento
        start_sample = int(last_t * sr)
        end_sample = int(t * sr)
        if end_sample > start_sample:
            segment = y[start_sample:end_sample]
            rms = np.mean(librosa.feature.rms(y=segment))
            # Normalizar RMS (asumiendo un max típico de 0.3-0.5)
            audio_energy = np.clip(rms * 4.0, 0.0, 1.0)
        else:
            audio_energy = 0.5
            
        # 2. Buscar el video que tenga una energía visual similar
        # Ordenamos los clips por qué tan cerca está su energía de la del audio
        clip_data.sort(key=lambda x: abs(x['score'] - audio_energy))
        
        # Elegimos uno de los 3 mejores (para mantener variedad y no repetir siempre el mismo)
        best_candidates = clip_data[:3]
        chosen_data = random.choice(best_candidates)
        
        try:
            clip = VideoFileClip(chosen_data['path'])
        except:
            continue
        
        # Tomar un fragmento aleatorio del clip
        if clip.duration > seg_len:
            start = random.uniform(0, clip.duration - seg_len)
            sub = safe_subclip(clip, start, start + seg_len)
        else:
            sub = safe_subclip(clip, 0, clip.duration)
            
        final_clips.append(sub)
        last_t = t

    # 4. Renderizar
    if progress_callback: progress_callback(70, "Montando video final...")
    print("🎞️ Renderizando video final...")
    final_video = concatenate_videoclips(final_clips, method="compose")
    
    # --- 5. AÑADIR SUBTÍTULOS (LYRICS) ---
    if progress_callback: progress_callback(85, "Procesando e incrustando subtítulos (Lyrics)...")
    print("📝 Procesando subtítulos...")
    try:
        lyrics_engine = LyricsEngine(audio_path)
        # Usamos 'segments' (frases) en lugar de palabras sueltas para subtítulos más legibles
        segments = lyrics_engine.data.get('segments', [])
        
        if segments:
            subtitle_clips = [final_video] # La base es el video montado
            W, H = final_video.size
            
            # Función auxiliar para crear imagen de texto ÉPICO
            def create_epic_text_image(text, w, h):
                # Lienzo transparente
                img = Image.new('RGBA', (w, h), (0,0,0,0))
                
                # 1. Configurar fuente (Más pequeña para que quepa: 5% altura)
                fontsize = int(h * 0.05) 
                try:
                    font = ImageFont.truetype("arialbd.ttf", fontsize)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", fontsize)
                    except:
                        font = ImageFont.load_default()
                
                # 2. Ajuste de línea (Word Wrap)
                # Calculamos cuántos caracteres caben aprox (ancho / tamaño fuente * factor ajuste)
                avg_char_width = fontsize * 0.6
                chars_per_line = int((w * 0.8) / avg_char_width)
                lines = textwrap.wrap(text, width=chars_per_line)
                
                # Calcular altura total del bloque de texto
                line_height = fontsize * 1.2
                total_text_h = len(lines) * line_height
                start_y = (h - total_text_h) // 2 # Centrado verticalmente
                
                draw = ImageDraw.Draw(img)
                
                # 3. Dibujar cada línea
                for i, line in enumerate(lines):
                    # Calcular ancho de esta línea para centrarla
                    bbox = draw.textbbox((0,0), line, font=font)
                    line_w = bbox[2] - bbox[0]
                    line_x = (w - line_w) // 2
                    line_y = start_y + i * line_height
                    
                    # --- EFECTO GLOW (Resplandor) ---
                    # Dibujamos varias veces con offset y transparencia para simular brillo
                    glow_range = 4
                    for ox in range(-glow_range, glow_range+1, 2):
                        for oy in range(-glow_range, glow_range+1, 2):
                            draw.text((line_x+ox, line_y+oy), line, font=font, fill=(0, 255, 255, 50)) # Cyan transparente

                    # --- BORDE NEGRO (Outline) ---
                    stroke_w = 4
                    draw.text((line_x, line_y), line, font=font, fill='white', stroke_width=stroke_w, stroke_fill='black')
                    
                    # --- TEXTO PRINCIPAL ---
                    draw.text((line_x, line_y), line, font=font, fill='white')
                
                # Aplicar un ligero desenfoque al canal alpha para suavizar bordes si se desea (opcional)
                # img = img.filter(ImageFilter.SMOOTH)
                
                return np.array(img)

            print(f"   Incrustando {len(segments)} líneas de subtítulos ÉPICOS...")
            for seg in segments:
                text = seg.get('text', '').strip()
                if not text: continue
                
                # FIX: Ignorar subtítulos que empiezan después del tiempo de corte
                if duration_arg and seg['start'] > duration_arg:
                    continue
                
                img_np = create_epic_text_image(text, W, H)
                txt_clip = ImageClip(img_np)
                
                # Compatibilidad MoviePy v2.0 (with_*) vs v1.0 (set_*)
                if hasattr(txt_clip, 'with_start'):
                    txt_clip = txt_clip.with_start(seg['start'])
                    txt_clip = txt_clip.with_duration(seg['end'] - seg['start'])
                else:
                    txt_clip = txt_clip.set_start(seg['start'])
                    txt_clip = txt_clip.set_duration(seg['end'] - seg['start'])
                
                # Aplicar Fade In/Out para aparición suave (Épico)
                try:
                    if hasattr(txt_clip, 'crossfadein'):
                        txt_clip = txt_clip.crossfadein(0.2).crossfadeout(0.2)
                    elif hasattr(vfx, 'CrossFadeIn'):
                        txt_clip = txt_clip.with_effects([vfx.CrossFadeIn(0.2), vfx.CrossFadeOut(0.2)])
                except: pass
                
                subtitle_clips.append(txt_clip)
            
            final_video = CompositeVideoClip(subtitle_clips)
            
            # FIX: Recortar composición final para evitar colas de subtítulos
            if duration_arg:
                final_video = safe_subclip(final_video, 0, duration_arg)
    except Exception as e:
        print(f"⚠️ No se pudieron añadir subtítulos: {e}")

    audio = AudioFileClip(audio_path)
    if duration_arg: audio = safe_subclip(audio, 0, duration_arg)
    if hasattr(final_video, 'with_audio'):
        final_video = final_video.with_audio(audio)
    else:
        final_video = final_video.set_audio(audio)
    
    final_video.write_videofile(output_filename, codec='libx264', audio_codec='aac', fps=24)
    if progress_callback: progress_callback(100, "¡Video completado y guardado!")
    return output_filename

def main():
    print("🎬 INICIANDO DIRECTOR IA (Edición Automática) DESDE CONSOLA...")
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar un archivo de audio.")
        return
    audio = sys.argv[1]
    dur = None
    if "--duration" in sys.argv: dur = float(sys.argv[sys.argv.index("--duration")+1])
    cdir = None
    if "--clips_dir" in sys.argv: cdir = sys.argv[sys.argv.index("--clips_dir")+1]
    
    out = "Director_AI_Final.mp4"
    if cdir: out = os.path.join(cdir, out)
    
    generar_montaje_ia(audio, dur, cdir, out)

if __name__ == "__main__":
    main()