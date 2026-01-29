
import json
import os

nb_path = "colab_webui.ipynb"

def patch_notebook():
    if not os.path.exists(nb_path):
        print(f"Error: {nb_path} not found.")
        return

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    found = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = cell["source"]
            new_source = []
            modified = False
            for line in source:
                new_source.append(line)
                if "!uv pip install --system --force-reinstall \"numpy<2.0.0\" \"setuptools\"" in line:
                    if not any("torch==2.3.1" in l for l in source): # Avoid duplicate insertion
                        new_source.append("\n")
                        new_source.append("# [CRITICAL] 强制重装 Torch 全家桶以确保版本兼容 (Fix: torch.library missing register_fake)\n")
                        new_source.append("!uv pip install --system --force-reinstall torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1\n")
                        modified = True
                        found = True
            
            if modified:
                cell["source"] = new_source

    if found:
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=2, ensure_ascii=False)
        print("Successfully patched colab_webui.ipynb with torch pinning.")
    else:
        print("Target line not found or already patched.")

if __name__ == "__main__":
    patch_notebook()
