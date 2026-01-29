
import json
import os

nb_path = "colab_webui.ipynb"

def patch_notebook():
    if not os.path.exists(nb_path):
        print(f"Error: {nb_path} not found.")
        return

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # 1. Update dependency installation (existing logic)
    found_torch_patch = False
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = cell["source"]
            new_source = []
            modified = False
            for line in source:
                new_source.append(line)
                if "!uv pip install --system --force-reinstall \"numpy<2.0.0\" \"setuptools\"" in line:
                    if not any("torch==2.3.1" in l for l in source): 
                        new_source.append("\n")
                        new_source.append("# [CRITICAL] 强制重装 Torch 全家桶以确保版本兼容 (Fix: torch.library missing register_fake)\n")
                        new_source.append("!uv pip install --system --force-reinstall torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1\n")
                        modified = True
                        found_torch_patch = True
            
            if modified:
                cell["source"] = new_source

    # 2. Inject Videotrans UI Patch Cell
    patch_cell_id = "PatchVideotransUI"
    
    # Check if patch cell already exists
    patch_exists = any(c.get("metadata", {}).get("id") == patch_cell_id for c in nb["cells"])
    
    if not patch_exists:
        patch_source = [
            "# [Step 1.6] Patch videotrans library for Colab (Headless Support)\n",
            "# Fixes IndexError: list index out of range in set_process by mocking GUI components\n",
            "import os\n",
            "import site\n",
            "\n",
            "def patch_videotrans_tools():\n",
            "    # Find videotrans location in site-packages\n",
            "    site_packages = site.getsitepackages()\n",
            "    target_file = None\n",
            "    \n",
            "    for sp in site_packages:\n",
            "        possible_path = os.path.join(sp, 'videotrans', 'util', 'tools.py')\n",
            "        if os.path.exists(possible_path):\n",
            "            target_file = possible_path\n",
            "            break\n",
            "            \n",
            "    if not target_file:\n",
            "        # Fallback: try to import and get file\n",
            "        try:\n",
            "            import videotrans.util.tools\n",
            "            target_file = videotrans.util.tools.__file__\n",
            "        except ImportError:\n",
            "            print(\"Could not find videotrans to patch. It might not be installed yet.\")\n",
            "            return\n",
            "\n",
            "    print(f\"Patching {target_file}...\")\n",
            "    \n",
            "    with open(target_file, 'r', encoding='utf-8') as f:\n",
            "        content = f.read()\n",
            "\n",
            "    patch_code = \"\"\"\n",
            "\n",
            "# --- COLAB PATCH START ---\n",
            "# Mock UI components for headless execution\n",
            "class DummyUI:\n",
            "    def error(self, msg): print(f\"[UI Error] {msg}\")\n",
            "    def info(self, msg): print(f\"[UI Info] {msg}\")\n",
            "    def warning(self, msg): print(f\"[UI Warning] {msg}\")\n",
            "    def log(self, msg): print(f\"[UI Log] {msg}\")\n",
            "    def setText(self, text): print(f\"[UI Status] {text}\")\n",
            "    def set_value(self, val): pass\n",
            "\n",
            "# Ensure log_ui_ui exists and has elements\n",
            "if 'log_ui_ui' not in globals() or not log_ui_ui:\n",
            "    log_ui_ui = [DummyUI() for _ in range(5)]\n",
            "\n",
            "# Override set_process to be safe\n",
            "def set_process(text=None, step=None):\n",
            "    try:\n",
            "        if text:\n",
            "            print(f\"[Processing] {text}\")\n",
            "            if 'log_ui_ui' in globals() and len(log_ui_ui) > 0:\n",
            "                log_ui_ui[0].setText(text)\n",
            "        if step is not None:\n",
            "             if 'log_ui_ui' in globals() and len(log_ui_ui) > 1:\n",
            "                log_ui_ui[1].set_value(step)\n",
            "    except Exception as e:\n",
            "        print(f\"Error in set_process: {e}\")\n",
            "# --- COLAB PATCH END ---\n",
            "\"\"\"\n",
            "    \n",
            "    if \"# --- COLAB PATCH START ---\" in content:\n",
            "        print(\"File already patched.\")\n",
            "    else:\n",
            "        with open(target_file, 'a', encoding='utf-8') as f:\n",
            "            f.write(patch_code)\n",
            "        print(\"Patch applied successfully.\")\n",
            "\n",
            "try:\n",
            "    patch_videotrans_tools()\n",
            "except Exception as e:\n",
            "    print(f\"An error occurred while patching: {e}\")\n"
        ]
        
        new_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {
                "id": patch_cell_id
            },
            "outputs": [],
            "source": patch_source
        }
        
        # Insert after Step 1.4 (Dependency Install)
        # Find index of cell with id 'SmEIaKn1X1Hy'
        insert_idx = -1
        for i, cell in enumerate(nb["cells"]):
            if cell.get("metadata", {}).get("id") == "SmEIaKn1X1Hy":
                insert_idx = i
                break
        
        if insert_idx != -1:
            nb["cells"].insert(insert_idx + 1, new_cell)
            print(" injected patch cell after requirements install.")
        else:
            nb["cells"].append(new_cell)
            print(" appended patch cell to end.")

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    
    if found_torch_patch:
        print("Updated existing cells with torch pinning.")
    
    print("Notebook update complete.")

if __name__ == "__main__":
    patch_notebook()
