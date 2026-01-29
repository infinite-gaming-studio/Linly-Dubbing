import json

nb_path = 'colab_webui.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Define new source code for the cells
# We keep the system deps cleaning, but ensure we don't suppress errors too aggressively if debugging is needed.
system_deps_source = [
    "# [Step 1.3] 安装系统级依赖 (System Dependencies)\n",
    "# 优先安装系统库，确保 C++ 编译环境就绪\n",
    "!apt-get update -qq\n",
    "!apt-get install -y -qq build-essential libfst-dev ffmpeg espeak-ng libsndfile1 \\\n",
    "    libavfilter-dev libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev > /dev/null\n",
    "print(\"System dependencies installed.\")\n",
    "!ffmpeg -version | head -n 1"
]

# Updated Python deps source with Runtime Patching
python_deps_source = [
    "# [Step 1.4] Python 依赖安装 (Python Dependencies via uv)\n",
    "# Colab 默认 Numpy 版本往往较高 (>=2.0)，而本项目依赖需要 Numpy < 2.0\n",
    "# 由于代码是从 GitHub clone 的，我们需要在运行时修补 requirements.txt\n",
    "\n",
    "# 1. 运行时修补 (Runtime Patching)\n",
    "# 将 numpy==1.26.3 修改为 numpy<2.0.0 以避免与系统环境过分冲突，同时防止安装 2.0+\n",
    "!sed -i 's/numpy==1.26.3/numpy<2.0.0/g' requirements.txt\n",
    "print(\"Patched requirements.txt: Relaxed numpy constraint.\")\n",
    "\n",
    "# 2. 安装 uv (极速包管理器)\n",
    "!pip install uv\n",
    "\n",
    "# 3. 使用 uv 安装依赖\n",
    "print(\"Installing requirements with uv... This might take a minute.\")\n",
    "\n",
    "# 强制重装 numpy 确保版本正确 (<2.0.0)\n",
    "!uv pip install --system --force-reinstall \"numpy<2.0.0\" \"setuptools\"\n",
    "\n",
    "# 安装其余依赖\n",
    "!uv pip install --system -r requirements.txt\n",
    "!uv pip install --system -r requirements_module.txt\n",
    "\n",
    "print(\"Python dependencies installed successfully.\")"
]

# Find and update cells
found_system = False
found_python = False

for cell in nb['cells']:
    if cell.get('metadata', {}).get('id') == 'SystemDeps':
        cell['source'] = system_deps_source
        cell['execution_count'] = None
        cell['outputs'] = []
        found_system = True
    elif cell.get('metadata', {}).get('id') == 'SmEIaKn1X1Hy':
        cell['source'] = python_deps_source
        cell['execution_count'] = None
        cell['outputs'] = []
        found_python = True

if found_system and found_python:
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Notebook patched successfully (v2 with runtime sed).")
else:
    print(f"Error: Could not find all cells. System: {found_system}, Python: {found_python}")
    exit(1)
