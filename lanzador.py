import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
from tkinter import simpledialog
import threading
import sys
import shutil
import re
import json
import requests
import time

class VisualizerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Motor de Visualización Física")
        self.root.geometry("420x900") # Aumentado para evitar cortes
        self.root.configure(bg="#1e1e1e")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=5, font=('Helvetica', 9, 'bold'), background="#333", foreground="white")
        style.map("TButton", background=[('active', '#555')])
        
        # Directorio base absoluto (Para evitar errores de "Archivo no encontrado")
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ai_palette = "magma" # Paleta por defecto
        self.ai_render_modes = [] # Modos sugeridos por la IA

        # Variable para controlar el proceso de IA
        self.ai_process = None

        # Iniciar Servidor IA en segundo plano
        self.start_ai_server()

        # Título
        lbl_title = tk.Label(root, text="MOTOR DE RENDER", font=('Helvetica', 14, 'bold'), bg="#1e1e1e", fg="#00ffcc")
        lbl_title.pack(pady=10)
        
        # Variable para la canción
        self.audio_file = ""

        # --- FRAME DIRECTOR IA (NUEVO) ---
        self.ai_frame = tk.LabelFrame(root, text="🧠 Director IA (Voz/Texto)", bg="#1e1e1e", fg="#ff00ff")
        self.ai_frame.pack(fill='x', padx=10, pady=5)
        
        # Input Prompt
        frame_input_ai = tk.Frame(self.ai_frame, bg="#1e1e1e")
        frame_input_ai.pack(fill='x', padx=5, pady=5)
        
        self.entry_prompt = tk.Entry(frame_input_ai, bg="#333", fg="white", insertbackground="white")
        self.entry_prompt.pack(side='left', fill='x', expand=True, padx=2)
        self.entry_prompt.insert(0, "Ej: Sueño cyberpunk con agua...")
        self.entry_prompt.bind("<FocusIn>", lambda args: self.entry_prompt.delete(0, 'end') if "Ej:" in self.entry_prompt.get() else None)

        # Botón Micrófono
        btn_mic = ttk.Button(frame_input_ai, text="🎤", width=3, command=self.listen_voice)
        btn_mic.pack(side='left', padx=2)

        # Botones Acción IA
        frame_btns_ai = tk.Frame(self.ai_frame, bg="#1e1e1e")
        frame_btns_ai.pack(fill='x', padx=5, pady=2)
        
        btn_apply_ai = ttk.Button(frame_btns_ai, text="✨ APLICAR ESTILO", command=self.apply_ai_config)
        btn_apply_ai.pack(side='left', fill='x', expand=True, padx=2)
        
        btn_fix_lyrics = ttk.Button(frame_btns_ai, text="💅 LINDA LETRA", command=self.beautify_lyrics_ai)
        btn_fix_lyrics.pack(side='left', fill='x', expand=True, padx=2)

        # --- CHAT LOG (NUEVO) ---
        self.chat_log = tk.Text(self.ai_frame, height=5, bg="#252526", fg="#00ffcc", font=("Consolas", 8), state='disabled', wrap='word')
        self.chat_log.pack(fill='x', padx=5, pady=5)

        # --- FRAME DE CONFIGURACIÓN ---
        self.config_frame = tk.LabelFrame(root, text="⚙️ Configuración", bg="#1e1e1e", fg="#00ffcc")
        self.config_frame.pack(fill='x', padx=10, pady=2)
        
        # Input Duración
        tk.Label(self.config_frame, text="Duración (s):", bg="#1e1e1e", fg="white").pack(side='left', padx=5)
        self.entry_duration = tk.Entry(self.config_frame, width=6)
        self.entry_duration.pack(side='left', padx=5)
        tk.Label(self.config_frame, text="(Vacío=Todo)", bg="#1e1e1e", fg="#888", font=("Arial", 8)).pack(side='left')

        # Combobox Resolución
        tk.Label(self.config_frame, text="Res:", bg="#1e1e1e", fg="white").pack(side='left', padx=5)
        self.combo_res = ttk.Combobox(self.config_frame, values=["1280x720", "1920x1080", "640x360"], width=10)
        self.combo_res.set("1280x720")
        self.combo_res.pack(side='left', padx=5)
        self.combo_res.bind("<<ComboboxSelected>>", self.update_config_file)

        # --- FRAME DE MOTORES FÍSICOS & SEED ---
        self.physics_frame = tk.LabelFrame(root, text="⚛️ Motores Físicos & Semilla", bg="#1e1e1e", fg="#00ffcc")
        self.physics_frame.pack(fill='x', padx=10, pady=2)

        self.vars_engines = {}
        engines = ["GS", "KS", "GPE", "WAVE", "CH", "PARTICLES", "LORENZ", "GEOMETRY", "KDV"]
        frame_checks = tk.Frame(self.physics_frame, bg="#1e1e1e")
        frame_checks.pack(fill='x', padx=5, pady=2)

        for i, eng in enumerate(engines):
            var = tk.BooleanVar(value=True)
            self.vars_engines[eng] = var
            chk = tk.Checkbutton(frame_checks, text=eng, variable=var, bg="#1e1e1e", fg="white", selectcolor="#333", activebackground="#1e1e1e", activeforeground="white")
            chk.grid(row=i//4, column=i%4, sticky='w')

        frame_seed = tk.Frame(self.physics_frame, bg="#1e1e1e")
        frame_seed.pack(fill='x', padx=5, pady=2)
        tk.Label(frame_seed, text="Seed:", bg="#1e1e1e", fg="white").pack(side='left')
        self.entry_seed = tk.Entry(frame_seed, width=10)
        self.entry_seed.pack(side='left', padx=5)
        btn_rnd_seed = ttk.Button(frame_seed, text="🎲 Random", width=10, command=self.generate_seed)
        btn_rnd_seed.pack(side='left', padx=5)
        
        # Frame para Opciones Extra (Espíritus, Caleido, Flash)
        frame_opts = tk.Frame(self.physics_frame, bg="#1e1e1e")
        frame_opts.pack(fill='x', padx=5, pady=2)

        # Checkbox Espíritus
        self.var_spirits = tk.BooleanVar(value=True)
        chk_spirits = tk.Checkbutton(frame_opts, text="👻 Espíritus", variable=self.var_spirits, bg="#1e1e1e", fg="#00ffcc", selectcolor="#333", activebackground="#1e1e1e", activeforeground="#00ffcc")
        chk_spirits.pack(side='left', padx=2)

        # Checkbox Caleidoscopio
        self.var_kaleido = tk.BooleanVar(value=True)
        chk_kaleido = tk.Checkbutton(frame_opts, text="🔮 Caleido", variable=self.var_kaleido, bg="#1e1e1e", fg="#00ffcc", selectcolor="#333", activebackground="#1e1e1e", activeforeground="#00ffcc")
        chk_kaleido.pack(side='left', padx=2)

        # Checkbox Epilepsia (Flash)
        self.var_flash = tk.BooleanVar(value=True)
        chk_flash = tk.Checkbutton(frame_opts, text="⚡ Flash", variable=self.var_flash, bg="#1e1e1e", fg="#ff5555", selectcolor="#333", activebackground="#1e1e1e", activeforeground="#ff5555")
        chk_flash.pack(side='left', padx=2)

        # Checkbox Chroma (Nota Dominante) - NUEVO
        self.var_chroma = tk.BooleanVar(value=False)
        chk_chroma = tk.Checkbutton(frame_opts, text="🎨 Nota", variable=self.var_chroma, bg="#1e1e1e", fg="#ffff00", selectcolor="#333", activebackground="#1e1e1e", activeforeground="#ffff00")
        chk_chroma.pack(side='left', padx=2)

        # Frame para botones
        self.frame = tk.Frame(root, bg="#1e1e1e")
        self.frame.pack(expand=True, fill='both', padx=10)

        # --- FILA 1: ARCHIVOS ---
        frame_files = tk.Frame(self.frame, bg="#1e1e1e")
        frame_files.pack(fill='x', pady=2)
        
        btn_select = ttk.Button(frame_files, text="📂 SELECCIONAR", command=self.select_file)
        btn_select.pack(side='left', fill='x', expand=True, padx=2)
        
        btn_move = ttk.Button(frame_files, text="📦 MOVER VIDEOS", command=self.move_videos)
        btn_move.pack(side='left', fill='x', expand=True, padx=2)
        
        self.lbl_file = tk.Label(self.frame, text="Ningún archivo seleccionado", bg="#1e1e1e", fg="#ff5555")
        self.lbl_file.pack(pady=2)

        # --- FILA 2: LETRAS ---
        frame_lyrics = tk.Frame(self.frame, bg="#1e1e1e")
        frame_lyrics.pack(fill='x', pady=2)
        
        btn_extract = ttk.Button(frame_lyrics, text="🧠 EXTRAER LETRA", command=self.extract_lyrics)
        btn_extract.pack(side='left', fill='x', expand=True, padx=2)
        
        btn_edit_lyrics = ttk.Button(frame_lyrics, text="📝 EDITAR LETRA", command=self.edit_lyrics)
        btn_edit_lyrics.pack(side='left', fill='x', expand=True, padx=2)

        # Lista de Scripts
        self.scripts = [
            ("🚀 God Mode (Estándar)", os.path.join(self.base_dir, "src", "render_standard.py")),
            ("🧠 Neural (IA)", os.path.join(self.base_dir, "src", "render_main_autoencoders.py")),
            ("🏛️ Clásico (Main)", os.path.join(self.base_dir, "src", "render_main clasico.py")),
            ("🧬 Lenia (Vida)", os.path.join(self.base_dir, "src", "render_lenia.py")),
            ("🌊 Fluidos (LBM)", os.path.join(self.base_dir, "src", "render_lbm.py")),
            ("🌀 Caos (3D)", os.path.join(self.base_dir, "src", "render_chaos.py")),
            ("🌿 Fractales (IFS)", os.path.join(self.base_dir, "src", "render_ifs.py")),
            ("🧪 Experimental", os.path.join(self.base_dir, "src", "render_experimental.py")),
            ("📜 Legacy (V1.0)", os.path.join(self.base_dir, "src", "render_main_legacy.py")),
        ]

        # Frame contenedor para grid de scripts (2 columnas)
        frame_scripts = tk.Frame(self.frame, bg="#1e1e1e")
        frame_scripts.pack(fill='x', pady=2)
        frame_scripts.columnconfigure(0, weight=1)
        frame_scripts.columnconfigure(1, weight=1)

        for i, (name, script) in enumerate(self.scripts):
            btn = ttk.Button(frame_scripts, text=name, command=lambda s=script: self.run_script(s))
            btn.grid(row=i//2, column=i%2, sticky='ew', padx=2, pady=2)

        # Separador y Botón de Diagnóstico
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=5)
        
        # --- FILA 3: ACCIONES SECUNDARIAS ---
        frame_actions = tk.Frame(self.frame, bg="#1e1e1e")
        frame_actions.pack(fill='x', pady=2)

        btn_test_all = ttk.Button(frame_actions, text="🧪 DIAGNÓSTICO", command=self.run_all_scripts)
        btn_test_all.pack(side='left', fill='x', expand=True, padx=2)

        btn_director = ttk.Button(frame_actions, text="🎬 DIRECTOR IA", command=self.run_director)
        btn_director.pack(side='left', fill='x', expand=True, padx=2)

        # Botón Ejecutar Todos + Fusión (Grande)
        btn_process = ttk.Button(self.frame, text="🚀 PROCESAR CANCIÓN", command=self.process_song_workflow)
        btn_process.pack(fill='x', pady=5)

        # Consola de estado
        self.status_label = tk.Label(root, text="Listo para iniciar...", bg="#1e1e1e", fg="#888")
        self.status_label.pack(pady=10)
        
        # Protocolo de cierre para matar procesos hijos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_ai_server(self):
        """Inicia el servidor FastAPI en un hilo separado si no está corriendo."""
        def run_server():
            api_path = os.path.join(self.base_dir, "src", "api_ai.py")
            if os.path.exists(api_path):
                # Verificar si ya está corriendo (simple check de puerto)
                try:
                    requests.get("http://127.0.0.1:8000/docs", timeout=2)
                    print("✅ Servidor IA ya está activo.")
                except:
                    print("🚀 Iniciando servidor IA...")
                    # CAMBIO: Usamos CREATE_NEW_CONSOLE para que veas la ventana negra con los logs
                    creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                    self.ai_process = subprocess.Popen([sys.executable, api_path], creationflags=creation_flags)
        
        t = threading.Thread(target=run_server)
        t.daemon = True
        t.start()

    def listen_voice(self):
        """Escucha el micrófono y transcribe a texto."""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.status_label.config(text="🎤 Escuchando...", fg="#ff00ff")
                self.root.update()
                audio = r.listen(source, timeout=5)
                
            text = r.recognize_google(audio, language="es-ES")
            self.entry_prompt.delete(0, tk.END)
            self.entry_prompt.insert(0, text)
            self.status_label.config(text=f"🗣️ Entendido: {text}", fg="#00ffcc")
            # Auto-aplicar si se detectó voz
            self.apply_ai_config()
            
        except ImportError:
            messagebox.showerror("Error", "Instala SpeechRecognition y PyAudio:\npip install SpeechRecognition pyaudio")
        except Exception as e:
            self.status_label.config(text="❌ No te escuché bien.", fg="red")
            print(e)

    def log_to_chat(self, sender, message):
        """Escribe un mensaje en la ventana de chat."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"[{sender}]: {message}\n\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state='disabled')

    def log_stream_start(self, sender):
        """Inicia una línea de chat para streaming."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, f"[{sender}]: ")
        self.chat_log.see(tk.END)
        self.chat_log.config(state='disabled')

    def log_stream_chunk(self, text):
        """Añade un fragmento de texto al chat actual."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, text)
        self.chat_log.see(tk.END)
        self.chat_log.config(state='disabled')
        
    def log_stream_end(self):
        """Finaliza la línea de chat."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, "\n\n")
        self.chat_log.see(tk.END)
        self.chat_log.config(state='disabled')

    def apply_ai_config(self, prompt_override=None, callback=None):
        """Envía el prompt a la IA y configura los checkboxes."""
        if prompt_override:
            prompt = prompt_override
        else:
            prompt = self.entry_prompt.get()
            if not prompt or "Ej:" in prompt: return

        self.log_to_chat("YO", prompt)
        self.status_label.config(text="🤖 IA Pensando...", fg="#ff00ff")
        self.root.update()

        def thread_request():
            try:
                res = requests.post("http://127.0.0.1:8000/analyze_scene", json={"prompt": prompt})
                if res.status_code == 200:
                    data = res.json()
                    engines = data.get("engines", [])
                    explanation = data.get("explanation", "")
                    colors = data.get("colors", "magma")
                    render_modes = data.get("render_modes", [])
                    objects = data.get("objects", [])
                    
                    # Actualizar GUI en el hilo principal
                    self.root.after(0, lambda: self._update_gui_from_ai(engines, explanation, colors, render_modes, objects))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error IA", "El servidor IA no respondió correctamente."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error Conexión", f"¿Está corriendo Ollama?\n{e}"))
            finally:
                if callback:
                    self.root.after(0, callback)

        threading.Thread(target=thread_request).start()

    def _update_gui_from_ai(self, engines, explanation, colors=None, render_modes=None, objects=None):
        if colors:
            self.ai_palette = colors
            if isinstance(self.ai_palette, list):
                 self.ai_palette = self.ai_palette[0]

        # 1. Resetear todos
        for var in self.vars_engines.values():
            var.set(False)
        
        # 2. Activar seleccionados
        count = 0
        for eng in engines:
            eng_upper = eng.upper()
            if eng_upper in self.vars_engines:
                self.vars_engines[eng_upper].set(True)
                count += 1

        # 3. Configurar Objetos (Spirits, Kaleido, etc.)
        if objects is not None:
            self.var_spirits.set("Spirits" in objects)
            self.var_kaleido.set("Kaleido" in objects)
            self.var_flash.set("Flash" in objects)
            self.var_chroma.set("Chroma" in objects)

        # 4. Guardar Modos de Render sugeridos
        if render_modes:
            self.ai_render_modes = render_modes
        else:
            self.ai_render_modes = []
        
        self.status_label.config(text="✅ Configuración aplicada.", fg="#00ffcc")
        self.log_to_chat("IA", f"Modos: {render_modes}\nObjetos: {objects}\nEngines: {engines}\n🎨 Color: {self.ai_palette}\nRAZÓN: {explanation}")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.flac")])
        if file_path:
            self.audio_file = file_path
            self.lbl_file.config(text=os.path.basename(file_path), fg="#00ffcc")

    def extract_lyrics(self, callback=None, confirm=True):
        """Fuerza la extracción de letra usando Whisper (abre consola nueva)."""
        if not self.audio_file:
            messagebox.showwarning("Atención", "Selecciona una canción primero.")
            return
        
        if confirm:
            if not messagebox.askyesno("Confirmar Extracción", "Esto usará IA (Whisper) para transcribir la canción.\n\nSe abrirá una consola negra con el progreso.\nPuede tardar unos minutos.\n\n¿Continuar?"):
                return

        self.status_label.config(text="⏳ Iniciando extracción de letra...", fg="yellow")
        
        def _run():
            try:
                # Borrar JSON previo para forzar extracción limpia
                json_path = os.path.splitext(self.audio_file)[0] + ".json"
                if os.path.exists(json_path):
                    try: os.remove(json_path)
                    except: pass
                
                # --- FIX: Ocultar TXT antiguo para forzar a la IA a escuchar de nuevo ---
                txt_path = os.path.splitext(self.audio_file)[0] + ".txt"
                if os.path.exists(txt_path):
                    try:
                        bak_path = txt_path + ".bak"
                        if os.path.exists(bak_path): os.remove(bak_path)
                        os.rename(txt_path, bak_path)
                    except: pass

                # Ejecutar motor_lyrics como script inline para aislar procesos
                cmd = [
                    sys.executable, 
                    "-c", 
                    "import sys; sys.path.append('src'); from motor_lyrics import LyricsEngine; LyricsEngine(sys.argv[1])", 
                    self.audio_file
                ]
                
                # CREATE_NEW_CONSOLE para ver progreso (Windows)
                creation_flags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                
                process = subprocess.Popen(cmd, creationflags=creation_flags)
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: messagebox.showinfo("Éxito", "✅ Letra extraída y segmentada correctamente."))
                    self.root.after(0, lambda: self.status_label.config(text="✅ Letra lista.", fg="#00ff00"))
                    if callback: self.root.after(0, callback)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Hubo un error en la extracción.\nRevisa la consola."))
                    self.root.after(0, lambda: self.status_label.config(text="❌ Error en extracción.", fg="red"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Fallo al lanzar proceso: {e}"))

        threading.Thread(target=_run).start()

    def edit_lyrics(self, wait=False):
        """Abre una ventana interna para editar la letra y tiempos (.json)."""
        if not self.audio_file:
            messagebox.showwarning("Atención", "Selecciona una canción primero.")
            return

        json_path = os.path.splitext(self.audio_file)[0] + ".json"
        
        # Estructura de datos para el editor
        segments = []
        
        # 1. Cargar JSON existente
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                segments = data.get('segments', [])
            except Exception as e:
                messagebox.showerror("Error", f"Error leyendo JSON: {e}")
                return
        else:
            messagebox.showinfo("Información", "No se encontraron datos de tiempos (JSON).\nEjecuta un render primero para generar la transcripción automática.")
            return

        # 2. Formatear contenido para el editor
        content_to_show = ""
        for s in segments:
            start = s.get('start', 0.0)
            end = s.get('end', 0.0)
            text = s.get('text', '').strip()
            content_to_show += f"[{start:.2f} - {end:.2f}] {text}\n"
        
        # 3. Crear Ventana de Edición
        editor = tk.Toplevel(self.root)
        editor.title("📝 Editor de Letras y Tiempos")
        editor.geometry("600x700")
        editor.configure(bg="#1e1e1e")
        
        lbl_info = tk.Label(editor, text="Formato: [Inicio - Fin] Texto\nEdita los tiempos y la letra. Al guardar, se actualizará el archivo JSON.", 
                           bg="#1e1e1e", fg="#aaaaaa", justify="left")
        lbl_info.pack(pady=5)

        frame_text = tk.Frame(editor, bg="#1e1e1e")
        frame_text.pack(expand=True, fill='both', padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(frame_text)
        scrollbar.pack(side='right', fill='y')
        
        txt_editor = tk.Text(frame_text, wrap='word', bg="#252526", fg="white", 
                            insertbackground="white", font=("Consolas", 11),
                            yscrollcommand=scrollbar.set)
        txt_editor.pack(expand=True, fill='both')
        scrollbar.config(command=txt_editor.yview)
        
        txt_editor.insert('1.0', content_to_show)

        # Botones
        frame_btns = tk.Frame(editor, bg="#1e1e1e")
        frame_btns.pack(fill='x', padx=10, pady=10)

        def save_changes():
            raw_text = txt_editor.get("1.0", tk.END).strip()
            new_segments = []
            
            # Regex para parsear: [0.00 - 1.00] Texto
            pattern = re.compile(r'\[\s*([\d\.]+)\s*-\s*([\d\.]+)\s*\](.*)')
            
            lines = raw_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                
                match = pattern.match(line)
                if match:
                    try:
                        s_time = float(match.group(1))
                        e_time = float(match.group(2))
                        text_content = match.group(3).strip()
                        
                        new_segments.append({
                            'start': s_time,
                            'end': e_time,
                            'text': text_content,
                            'words': [] 
                        })
                    except ValueError:
                        pass
            
            if not new_segments:
                if not messagebox.askyesno("Advertencia", "No se detectaron segmentos válidos con formato [0.00 - 0.00].\n¿Guardar archivo vacío?"):
                    return

            # Guardar JSON
            new_data = {'segments': new_segments, 'text': " ".join([s['text'] for s in new_segments])}
            
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)
                
                # Actualizar TXT plano para referencia
                txt_path = os.path.splitext(self.audio_file)[0] + ".txt"
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(new_data['text'])
                    
                messagebox.showinfo("Guardado", "✅ Tiempos y Letra actualizados en JSON.")
                editor.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        btn_save = ttk.Button(frame_btns, text="💾 GUARDAR JSON", command=save_changes)
        btn_save.pack(side='right', padx=5)
        
        btn_close = ttk.Button(frame_btns, text="Cancelar", command=editor.destroy)
        btn_close.pack(side='right', padx=5)
        
        if wait:
            self.root.wait_window(editor)

    def beautify_lyrics_ai(self, callback=None):
        """Lee el JSON actual, manda el texto a la IA y lo actualiza."""
        if not self.audio_file: 
            if callback: callback()
            return
        json_path = os.path.splitext(self.audio_file)[0] + ".json"
        if not os.path.exists(json_path):
            messagebox.showwarning("Error", "No hay archivo de letra (.json). Renderiza primero.")
            if callback: callback()
            return

        self.log_to_chat("YO", "Mejora la letra y segmentala para video.")
        self.status_label.config(text="💅 Segmentando letra con IA...", fg="#ff00ff")
        
        def process():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraer texto completo
                full_text = data.get('text', '')
                if not full_text: 
                    if callback: self.root.after(0, callback)
                    return

                # Preparar UI para Streaming y Debug
                self.root.after(0, lambda: self.log_to_chat("SISTEMA", f"Enviando {len(full_text)} caracteres a la IA para corrección..."))
                self.root.after(0, lambda: self.log_stream_start("IA"))
                
                accumulated_text = ""
                try:
                    # Petición con stream=True
                    with requests.post("http://127.0.0.1:8000/beautify_lyrics", json={"text": full_text}, stream=True) as res:
                        if res.status_code == 200:
                            for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    accumulated_text += chunk
                                    # Actualizar chat en tiempo real
                                    self.root.after(0, lambda c=chunk: self.log_stream_chunk(c))
                        else:
                            self.root.after(0, lambda: self.log_stream_chunk(f"Error HTTP: {res.status_code}"))
                except Exception as e:
                    self.root.after(0, lambda: self.log_stream_chunk(f"Error Conexión: {e}"))
                
                self.root.after(0, self.log_stream_end)

                # Guardar solo si hubo respuesta válida
                if accumulated_text and "ERROR" not in accumulated_text:
                    data['text'] = accumulated_text
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    txt_path = os.path.splitext(self.audio_file)[0] + ".txt"
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(accumulated_text)
                    
                    self.root.after(0, lambda: messagebox.showinfo("IA", "✅ Letra procesada y guardada."))
            except Exception as e:
                print(e)
            finally:
                if callback:
                    self.root.after(0, callback)

        threading.Thread(target=process).start()

    def generate_seed(self):
        import random
        self.entry_seed.delete(0, tk.END)
        self.entry_seed.insert(0, str(random.randint(1, 999999)))

    def update_config_file(self, event=None):
        """Edita src/config.py con la resolución seleccionada"""
        config_path = os.path.join("src", "config.py")
        if not os.path.exists(config_path):
            return
        
        res_str = self.combo_res.get()
        try:
            w, h = res_str.split('x')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            content = re.sub(r'WIDTH\s*=\s*\d+', f'WIDTH = {w}', content)
            content = re.sub(r'HEIGHT\s*=\s*\d+', f'HEIGHT = {h}', content)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Config actualizada: {w}x{h}")
        except Exception as e:
            print(f"Error actualizando config: {e}")

    def move_videos(self):
        target_dir = "RENDERS"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        count = 0
        for file in os.listdir('.'):
            if file.endswith(".mp4") and os.path.isfile(file):
                try:
                    shutil.move(file, os.path.join(target_dir, file))
                    count += 1
                except Exception as e:
                    print(f"Error moviendo {file}: {e}")
        messagebox.showinfo("Organización Completa", f"Se han movido {count} videos a la carpeta '{target_dir}'.")

    def run_script(self, script_name):
        if not os.path.exists(script_name):
            messagebox.showerror("Error", f"No se encuentra el archivo: {script_name}")
            return
            
        if not self.audio_file:
            messagebox.showwarning("Atención", "Por favor selecciona una canción primero.")
            return

        self.status_label.config(text=f"Ejecutando: {script_name}...", fg="#00ff00")
        
        # Ejecutar en hilo separado para no congelar la GUI
        t = threading.Thread(target=self._execute, args=(script_name,))
        t.start()

    def _execute(self, script_name):
        try:
            # Ejecutar en NUEVA CONSOLA para ver progreso
            cmd = [sys.executable, script_name, self.audio_file]
            
            # Agregar bandera de duración si hay texto
            dur_str = self.entry_duration.get().strip()
            if dur_str:
                cmd.extend(["--duration", dur_str])
            
            # Agregar Seed
            seed_str = self.entry_seed.get().strip()
            if seed_str:
                cmd.extend(["--seed", seed_str])

            # Agregar opción de Espíritus
            if not self.var_spirits.get():
                cmd.append("--no-spirits")

            # Agregar opción de Nota Dominante (Chroma)
            if self.var_chroma.get():
                cmd.append("--chroma")

            # Agregar Motores seleccionados
            selected_engines = [eng for eng, var in self.vars_engines.items() if var.get()]
            if selected_engines:
                cmd.append("--engines")
                cmd.extend(selected_engines)
            
            self.root.after(0, lambda: self.status_label.config(text=f"Corriendo {os.path.basename(script_name)}..."))
            if self.run_process_with_logging(cmd, script_name):
                self.root.after(0, lambda: self.status_label.config(text=f"✅ {os.path.basename(script_name)} finalizado.", fg="#00ff00"))
            else:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ Error en {os.path.basename(script_name)}.", fg="red"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error de Ejecución", str(e)))

    def run_all_scripts(self):
        """Ejecuta todos los scripts secuencialmente para probar errores."""
        if not self.audio_file:
            messagebox.showwarning("Atención", "Por favor selecciona una canción primero.")
            return
        
        if not messagebox.askyesno("Diagnóstico", "Esto ejecutará todos los scripts uno por uno.\n\nSi no definiste duración, se usarán 15s por script para ir rápido.\n\n¿Continuar?"):
            return

        self.status_label.config(text="Iniciando diagnóstico completo...", fg="orange")
        # Ejecutar en hilo para no congelar la ventana
        t = threading.Thread(target=self._execute_all)
        t.start()

    def _execute_all(self):
        errors = []
        dur_str = self.entry_duration.get().strip()
        
        # Si no hay duración, forzamos 15s para que el test sea rápido
        if not dur_str:
            dur_str = "15"
            print("⚠️ MODO DIAGNÓSTICO: Forzando duración de 15s.")

        total = len(self.scripts)
        for i, (name, script_path) in enumerate(self.scripts):
            if not os.path.exists(script_path):
                errors.append(f"❌ {name}: Archivo no encontrado")
                continue

            msg = f"[{i+1}/{total}] Probando: {name}..."
            self.root.after(0, lambda m=msg: self.status_label.config(text=m, fg="yellow"))
            print(f"\n{'='*40}\n{msg}\n{'='*40}")

            cmd = [sys.executable, script_path, self.audio_file]
            cmd.extend(["--duration", dur_str])

            if not self.run_process_with_logging(cmd, f"Diagnóstico: {name}"):
                errors.append(f"❌ {name}: Falló. Ver render_errors.log")

        # Reporte final
        if errors:
            report = "\n".join(errors)
            self.root.after(0, lambda: messagebox.showerror("Diagnóstico Finalizado", f"Se encontraron errores:\n\n{report}"))
            self.root.after(0, lambda: self.status_label.config(text="Diagnóstico finalizado con errores.", fg="red"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Diagnóstico Finalizado", "✅ Todos los scripts funcionaron correctamente."))
            self.root.after(0, lambda: self.status_label.config(text="Diagnóstico finalizado exitosamente.", fg="#00ff00"))

    def process_song_workflow(self):
        """Flujo de trabajo paso a paso para procesar una canción completa."""
        if not self.audio_file:
            messagebox.showwarning("Atención", "Por favor selecciona una canción primero.")
            return

        # --- PASO 1: EXTRACCIÓN DE LETRA ---
        if messagebox.askyesno("Paso 1/5: Letra", "¿Deseas extraer la letra con Whisper?\n\n(Selecciona 'No' si ya tienes el archivo .json generado)"):
            self.extract_lyrics(callback=self._step_1_5_beautify, confirm=False)
        else:
            self._step_1_5_beautify()

    def _step_1_5_beautify(self):
        # --- PASO 2: BEAUTIFY (LINDA LETRA) ---
        if messagebox.askyesno("Paso 2/5: Embellecer", "¿Quieres que la IA corrija y segmente la letra para video musical?"):
            self.beautify_lyrics_ai(callback=self._step_2_edit)
        else:
            self._step_2_edit()

    def _step_2_edit(self):
        # --- PASO 3: EDICIÓN DE LETRA ---
        if messagebox.askyesno("Paso 3/5: Edición", "¿Deseas abrir el editor para revisar/modificar la letra?"):
            self.edit_lyrics(wait=True)
        
        self._step_3_ai_style()

    def _step_3_ai_style(self):
        # --- PASO 4: ESTILO IA ---
        if messagebox.askyesno("Paso 4/5: Estilo IA", "¿Quieres definir el estilo visual describiéndolo al Director IA?"):
            prompt = simpledialog.askstring("Director IA", "Describe cómo quieres que sea el video:\n(Ej: 'Oscuro, cyberpunk, con lluvia y neón')")
            if prompt:
                self.apply_ai_config(prompt_override=prompt, callback=self._step_4_config)
            else:
                self._step_4_config()
        else:
            self._step_4_config()

    def _step_4_config(self):
        # --- PASO 5: SELECCIÓN DE MODOS Y ESTILOS ---
        win = tk.Toplevel(self.root)
        win.title("Paso 5/5: Configuración de Render")
        win.geometry("500x650")
        win.configure(bg="#1e1e1e")
        
        tk.Label(win, text="SELECCIONA LOS MODOS DE RENDER", font=("Helvetica", 12, "bold"), bg="#1e1e1e", fg="#00ffcc").pack(pady=10)
        
        # Checkboxes para Scripts
        frame_scripts = tk.Frame(win, bg="#1e1e1e")
        frame_scripts.pack(fill='both', expand=True, padx=20)
        
        script_vars = []
        for name, path in self.scripts:
            # Lógica de selección inteligente basada en la IA
            is_selected = True # Por defecto todos si no hay IA
            
            if self.ai_render_modes:
                # Si la IA sugirió modos, solo activamos esos
                # Buscamos coincidencia parcial (ej: "God Mode" en "🚀 God Mode (Estándar)")
                is_selected = any(mode.lower() in name.lower() for mode in self.ai_render_modes)
            
            var = tk.BooleanVar(value=is_selected)
            script_vars.append(var)
            cb = tk.Checkbutton(frame_scripts, text=name, variable=var, bg="#1e1e1e", fg="white", selectcolor="#333", font=("Arial", 10))
            cb.pack(anchor='w', pady=2)
            
        tk.Label(win, text="ESTILOS VISUALES", font=("Helvetica", 12, "bold"), bg="#1e1e1e", fg="#ff00ff").pack(pady=10)
        
        # Checkboxes para Estilos
        style_vars = {
            'flash': tk.BooleanVar(value=self.var_flash.get()),
            'kaleido': tk.BooleanVar(value=self.var_kaleido.get()),
            'spirits': tk.BooleanVar(value=self.var_spirits.get())
        }
        
        frame_styles = tk.Frame(win, bg="#1e1e1e")
        frame_styles.pack(fill='x', padx=20)
        
        tk.Checkbutton(frame_styles, text="⚡ Flash / Epilepsia", variable=style_vars['flash'], bg="#1e1e1e", fg="#ff5555", selectcolor="#333").pack(anchor='w')
        tk.Checkbutton(frame_styles, text="🔮 Caleidoscopio", variable=style_vars['kaleido'], bg="#1e1e1e", fg="#00ffcc", selectcolor="#333").pack(anchor='w')
        tk.Checkbutton(frame_styles, text="👻 Espíritus", variable=style_vars['spirits'], bg="#1e1e1e", fg="#00ffcc", selectcolor="#333").pack(anchor='w')
        tk.Checkbutton(frame_styles, text="🎨 Nota (Chroma)", variable=self.var_chroma, bg="#1e1e1e", fg="#ffff00", selectcolor="#333").pack(anchor='w')

        tk.Label(win, text="🧠 MODO IA: MÁXIMA POTENCIA ACTIVADO", font=("Consolas", 9), bg="#1e1e1e", fg="#ffff00").pack(pady=15)

        btn_go = ttk.Button(win, text="🚀 INICIAR PROCESAMIENTO", command=lambda: self._step_5_process(script_vars, style_vars, win))
        btn_go.pack(fill='x', padx=20, pady=20)

    def _step_5_process(self, script_vars, style_vars, win):
        # Recopilar selección
        selected_scripts = [self.scripts[i] for i, var in enumerate(script_vars) if var.get()]
        
        # Actualizar variables globales
        self.var_flash.set(style_vars['flash'].get())
        self.var_kaleido.set(style_vars['kaleido'].get())
        self.var_spirits.set(style_vars['spirits'].get())
        
        win.destroy()
        
        if not selected_scripts:
            messagebox.showwarning("Error", "Debes seleccionar al menos un modo de render.")
            return

        dur_str = self.entry_duration.get().strip()
        
        print(f"\n{'='*50}\n🧠 INICIANDO PROCESAMIENTO INTELIGENTE\n{'='*50}")
        print(f"📂 Archivo: {os.path.basename(self.audio_file)}")
        print(f"🎞️ Modos seleccionados: {len(selected_scripts)}")
        
        self.status_label.config(text="🚀 Procesando Canción (Máxima Potencia)...", fg="#00ffcc")
        # Ejecutar en hilo para no congelar la GUI
        t = threading.Thread(target=self._execute_sequence, args=(selected_scripts,))
        t.start()

    def _execute_sequence(self, scripts_to_run):
        dur_str = self.entry_duration.get().strip()
        seed_str = self.entry_seed.get().strip()
        
        # Crear carpeta de sesión única
        session_name = f"Session_{int(time.time())}"
        session_dir = os.path.join(self.base_dir, "RENDERS", session_name)
        os.makedirs(session_dir, exist_ok=True)
        print(f"📁 Guardando renders en: {session_dir}")

        # Argumentos base
        base_args = []
        if dur_str:
            base_args.extend(["--duration", dur_str])
        if seed_str:
            base_args.extend(["--seed", seed_str])
        if not self.var_spirits.get():
            base_args.append("--no-spirits")
        if not self.var_kaleido.get():
            base_args.append("--no-kaleido")
        if not self.var_flash.get():
            base_args.append("--no-flash")
        if self.var_chroma.get():
            base_args.append("--chroma")
        
        # Pasar paleta de color
        base_args.extend(["--cmap", self.ai_palette])
        
        # Motores seleccionados
        selected_engines = [eng for eng, var in self.vars_engines.items() if var.get()]
        
        total = len(scripts_to_run)
        for i, (name, script_path) in enumerate(scripts_to_run):
            if not os.path.exists(script_path):
                print(f"⚠️ Saltando {name}: Archivo no encontrado.")
                continue

            msg = f"[{i+1}/{total}] Renderizando: {name}..."
            self.root.after(0, lambda m=msg: self.status_label.config(text=m, fg="yellow"))
            print(f"\n{'='*50}\n{msg}\n{'='*50}")

            # Definir salida específica en la carpeta de sesión
            script_base = os.path.splitext(os.path.basename(script_path))[0]
            output_path = os.path.join(session_dir, f"{script_base}.mp4")
            
            cmd = [sys.executable, script_path, self.audio_file] + base_args 
            cmd.extend(["--output", output_path])
            
            # Añadir engines si corresponde
            if selected_engines:
                cmd.append("--engines")
                cmd.extend(selected_engines)

            if not self.run_process_with_logging(cmd, name):
                print(f"❌ Error ejecutando {name}. Revisa render_errors.log")
            else:
                print(f"✅ {name} completado.")

        # Ejecutar Director IA al final
        self.root.after(0, lambda: self.status_label.config(text="🎬 Ejecutando Director IA...", fg="cyan"))
        print(f"\n{'='*50}\n🎬 EJECUTANDO DIRECTOR IA\n{'='*50}")
        
        director_script = os.path.join(self.base_dir, "src", "director_ai.py")
        if os.path.exists(director_script):
            cmd_dir = [sys.executable, director_script, self.audio_file]
            if dur_str:
                cmd_dir.extend(["--duration", dur_str])
            cmd_dir.extend(["--clips_dir", session_dir])
            
            if self.run_process_with_logging(cmd_dir, "Director IA"):
                try:
                    self.root.after(0, lambda: messagebox.showinfo("¡Proceso Terminado!", f"✅ Proceso completo.\n\nCarpeta: {session_dir}"))
                    self.root.after(0, lambda: self.status_label.config(text="Secuencia finalizada con éxito.", fg="#00ff00"))
                    # Abrir carpeta automáticamente (Windows)
                    if os.name == 'nt':
                        os.startfile(session_dir)
                except RuntimeError:
                    pass # La ventana se cerró antes de terminar
            else:
                try:
                    self.root.after(0, lambda: messagebox.showerror("Error Director IA", "Falló el Director IA. Revisa render_errors.log"))
                except RuntimeError:
                    pass
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "No se encontró src/director_ai.py"))

    def run_director(self):
        """Lanza el script de edición automática."""
        if not self.audio_file:
            messagebox.showwarning("Atención", "Por favor selecciona una canción primero.")
            return
            
        script_path = os.path.join(self.base_dir, "src", "director_ai.py")
        if not os.path.exists(script_path):
            # Si no existe, crearlo al vuelo (opcional, pero mejor tener el archivo)
            messagebox.showerror("Error", "No se encontró src/director_ai.py")
            return

        self.status_label.config(text="🎬 El Director IA está editando el video...", fg="cyan")
        t = threading.Thread(target=self._execute, args=(script_path,))
        t.start()

    def run_process_with_logging(self, cmd, description):
        """Ejecuta un proceso capturando stderr y logueando errores."""
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=None, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1,
                encoding='utf-8', 
                errors='replace'
            )
            
            stderr_lines = []
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    sys.stderr.write(line)
                    sys.stderr.flush()
                    stderr_lines.append(line)
            
            if process.returncode != 0:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with open("render_errors.log", "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*20} ERROR REPORT {'='*20}\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"Context: {description}\n")
                    f.write(f"Command: {cmd}\n")
                    f.write("-" * 10 + " Traceback " + "-" * 10 + "\n")
                    f.write("".join(stderr_lines))
                    f.write("="*54 + "\n")
                return False
            return True
        except Exception as e:
            with open("render_errors.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] EXCEPTION in {description}: {e}\n")
            return False

    def on_closing(self):
        """Cierra la aplicación y mata el proceso de IA si existe."""
        if self.ai_process:
            try:
                print("🛑 Cerrando servidor IA...")
                self.ai_process.terminate()
            except Exception as e:
                print(f"Error cerrando IA: {e}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizerLauncher(root)
    root.mainloop()
