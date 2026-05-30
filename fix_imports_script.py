import os
import re

module_map = {
    'api_ai': 'ai.api_ai',
    'director_ai': 'ai.director_ai',
    'audio_analyzer': 'audio.audio_analyzer',
    'procesamiento_audio': 'audio.procesamiento_audio',
    'motor_lyrics': 'audio.motor_lyrics',
    'config': 'core.config',
    'visual_entities': 'core.visual_entities',
    'video_utils': 'core.video_utils',
    'blender': 'core.blender',
    'crear_estructura': 'core.crear_estructura',
    'efectos_visuales': 'core.efectos_visuales',
    'nucleo_visual': 'core.nucleo_visual',
    'render_main_clasico': 'render.stable.render_main_clasico',
    'render_main_legacy': 'render.stable.render_main_legacy',
    'render_standard': 'render.stable.render_standard',
    'render_lenia': 'render.stable.render_lenia',
    'render_lbm': 'render.stable.render_lbm',
    'render_main_autoencoders': 'render.stable.render_main_autoencoders',
    'render_chaos': 'render.experimental.render_chaos',
    'render_ifs': 'render.experimental.render_ifs',
    'render_experimental': 'render.experimental.render_experimental',
}

base_dir = os.path.join(os.getcwd(), 'src')

sys_path_block = """
import sys
import os
# Hack para que los subdirectorios puedan ver los modulos de src/
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = current_dir
while not src_dir.endswith('src') and not src_dir.endswith('src\\\\') and not src_dir.endswith('src/'):
    parent = os.path.dirname(src_dir)
    if parent == src_dir:
        break
    src_dir = parent
if src_dir not in sys.path:
    sys.path.append(src_dir)
"""

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            for old_mod, new_mod in module_map.items():
                new_content = re.sub(fr'^from {old_mod} import', f'from {new_mod} import', new_content, flags=re.MULTILINE)
                new_content = re.sub(fr'^import {old_mod}(?!\s+as)', f'import {new_mod} as {old_mod}', new_content, flags=re.MULTILINE)

            if new_content != content:
                # Add the sys.path block right after the first imports or at the top
                if "import sys" not in new_content[:300]:
                    new_content = sys_path_block + new_content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated imports in {filepath}")
