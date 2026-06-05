import os

filepath = "explicacion funcionalidades/Manual_de_Usuario_2.tex"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Lines 280-295:")
for i in range(280, 295):
    if i < len(lines):
        print(f"{i+1}: {lines[i].strip()}")
