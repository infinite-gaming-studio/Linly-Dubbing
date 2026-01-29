
import json
import os
import site
import sys

# Path to the notebook itself (in case we want to patch it from within, though usually we run this from a cell)
nb_path = "colab_webui.ipynb"

def patch_tts_compatibility():
    """Patch TTS submodule for Python 3.12 support."""
    setup_path = 'submodules/TTS/setup.py'
    if os.path.exists(setup_path):
        print(f"Patching {setup_path} for Python 3.12 compatibility...")
        with open(setup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the version check
        old_check = 'if Version(python_version) < Version("3.9") or Version(python_version) >= Version("3.12"):'
        new_check = '# if Version(python_version) < Version("3.9") or Version(python_version) >= Version("3.12"):'
        content = content.replace(old_check, new_check)
        
        old_raise = '    raise RuntimeError("TTS requires python >= 3.9 and < 3.12 "'
        new_raise = '#     raise RuntimeError("TTS requires python >= 3.9 and < 3.12 "'
        content = content.replace(old_raise, new_raise)
        
        old_req = 'python_requires=">=3.9.0, <3.12",'
        new_req = 'python_requires=">=3.9.0, <3.13",'
        content = content.replace(old_req, new_req)
        
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ TTS patched.")
    else:
        print("⚠️ TTS setup.py not found at submodules/TTS/setup.py. Skipping.")

def patch_matplotlib_backend():
    """Fix Matplotlib backend issue in Colab."""
    print("Patching Matplotlib backend for headless environment...")
    # We can set this globally in the current process and also suggest it for the notebook
    os.environ['MPLBACKEND'] = 'Agg'
    try:
        import matplotlib
        matplotlib.use('Agg')
        print("✅ Matplotlib backend set to 'Agg'.")
    except Exception as e:
        print(f"⚠️ Failed to set Matplotlib backend: {e}")

def patch_videotrans_tools():
    """Patch videotrans library for Colab (Headless Support)."""
    # Find videotrans location in site-packages
    site_packages = site.getsitepackages()
    target_file = None
    
    for sp in site_packages:
        possible_path = os.path.join(sp, 'videotrans', 'util', 'tools.py')
        if os.path.exists(possible_path):
            target_file = possible_path
            break
            
    if not target_file:
        # Fallback: try to import and get file
        try:
            import videotrans.util.tools
            target_file = videotrans.util.tools.__file__
        except ImportError:
            print("⚠️ Could not find videotrans to patch. It might not be installed yet.")
            return

    print(f"Patching {target_file} for headless UI support...")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    patch_code = """

# --- COLAB PATCH START ---
# Mock UI components for headless execution
class DummyUI:
    def error(self, msg): print(f"[UI Error] {msg}")
    def info(self, msg): print(f"[UI Info] {msg}")
    def warning(self, msg): print(f"[UI Warning] {msg}")
    def log(self, msg): print(f"[UI Log] {msg}")
    def setText(self, text): print(f"[UI Status] {text}")
    def set_value(self, val): pass

# Ensure log_ui_ui exists and has elements
if 'log_ui_ui' not in globals() or not log_ui_ui:
    log_ui_ui = [DummyUI() for _ in range(5)]

# Override set_process to be safe
def set_process(text=None, step=None):
    try:
        if text:
            print(f"[Processing] {text}")
            if 'log_ui_ui' in globals() and len(log_ui_ui) > 0:
                log_ui_ui[0].setText(text)
        if step is not None:
             if 'log_ui_ui' in globals() and len(log_ui_ui) > 1:
                log_ui_ui[1].set_value(step)
    except Exception as e:
        print(f"Error in set_process: {e}")
# --- COLAB PATCH END ---
"""
    
    if "# --- COLAB PATCH START ---" in content:
        print("File already patched.")
    else:
        with open(target_file, 'a', encoding='utf-8') as f:
            f.write(patch_code)
        print("✅ videotrans patch applied successfully.")

def verify_dependencies():
    """Verify critical dependencies."""
    print("Verifying critical dependencies...")
    critical_packages = ['yt_dlp', 'loguru', 'torch', 'pynini']
    missing = []
    for pkg in critical_packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} is installed.")
        except ImportError:
            missing.append(pkg)
            print(f"❌ {pkg} is MISSING.")
    
    if missing:
        print(f"Error: Missing packages: {missing}")
        # We don't exit here, let the user decide or try to install manually
    else:
        print("✅ All critical dependencies verified.")

def patch_gradio_compatibility():
    """Gradio compatibility is now handled in webui.py directly."""
    print("✅ Gradio compatibility handled in webui.py.")
    pass

def run_all_patches():
    print("Running all Colab patches...")
    patch_gradio_compatibility()
    patch_tts_compatibility()
    patch_matplotlib_backend()
    patch_videotrans_tools()
    verify_dependencies()
    print("All patches completed.")

if __name__ == "__main__":
    run_all_patches()
