import imageio_ffmpeg
import os
try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip

def unir_video_con_musica(video_path, audio_path, output_path, duracion=None):
    print(f"--- 3. Renderizando Audio Final ---")
    
    if not os.path.exists(video_path):
        print(f"❌ Error: El archivo de video '{video_path}' no existe.")
        return
    if os.path.getsize(video_path) == 0:
        print(f"❌ Error: El archivo de video '{video_path}' está vacío (0 bytes).")
        return

    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # Lógica de seguridad: Si el video es más corto que el audio (Modo Prueba),
        # cortamos el audio a la duración exacta del video.
        if video.duration < audio.duration:
            print(f"✂️ Ajustando audio ({audio.duration:.2f}s) al video ({video.duration:.2f}s)...")
            if hasattr(audio, 'subclipped'):
                audio = audio.subclipped(0, video.duration)
            else:
                audio = audio.subclip(0, video.duration)
        elif duracion:
            # Si se especificó duración manual
            if hasattr(audio, 'subclipped'):
                audio = audio.subclipped(0, duracion)
                video = video.subclipped(0, duracion)
            else:
                audio = audio.subclip(0, duracion)
                video = video.subclip(0, duracion)
    
        if hasattr(video, 'with_audio'):
            final = video.with_audio(audio)
        else:
            final = video.set_audio(audio)
        
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)
    except Exception as e:
        print(f"Error uniendo audio: {e}")
