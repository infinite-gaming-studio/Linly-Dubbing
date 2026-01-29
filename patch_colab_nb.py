import json

nb_path = 'colab_webui.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Define new source code for the cells
system_deps_source = [
    "# [Step 1.3] 安装系统级依赖 (System Dependencies)\n",
    "# 优先安装系统库，确保 C++ 编译环境就绪\n",
    "!apt-get update -qq\n",
    "!apt-get install -y -qq build-essential libfst-dev ffmpeg espeak-ng libsndfile1 \\\n",
    "    libavfilter-dev libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev > /dev/null\n",
    "print(\"System dependencies installed.\")\n",
    "!ffmpeg -version | head -n 1"
]

python_deps_source = [
    "# [Step 1.4] Python 依赖安装 (Python Dependencies via uv)\n",
    "# 我们使用 'uv' 进行极速安装。Colab 环境需要特定版本的库以保证 ASR/TTS 兼容性。\n",
    "\n",
    "# 1. 安装 uv\n",
    "!pip install -q uv\n",
    "\n",
    "# 2. [CRITICAL] 准备构建环境 (Fix for pynini build failure)\n",
    "print(\"Installing build dependencies (Cython)...\")\n",
    "!uv pip install --system Cython\n",
    "\n",
    "# 3. [CRITICAL] 强制重装核心库 (Fix for numpy, setuptools, torch compatibility)\n",
    "print(\"Installing core compute libraries... This might take a minute.\")\n",
    "# numpy<2.0.0 is required for many binary extensions\n",
    "# torch==2.3.1 is required for compatibility with the current code base and fake tensor support\n",
    "!uv pip install --system --force-reinstall \"numpy<2.0.0\" \"setuptools\" torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1\n",
    "\n",
    "# 4. 运行时修补 (Runtime Patching)\n",
    "# 将 numpy==1.26.3 修改为 numpy<2.0.0 以提高灵活性\n",
    "!sed -i 's/numpy==1.26.3/numpy<2.0.0/g' requirements.txt\n",
    "\n",
    "# [CRITICAL] Patch TTS submodule for Python 3.12 support (Colab uses 3.12)\n",
    "!sed -i 's/if Version(python_version) < Version(\"3.9\") or Version(python_version) >= Version(\"3.12\"):/# if Version(python_version) < Version(\"3.9\") or Version(python_version) >= Version(\"3.12\"):/g' submodules/TTS/setup.py\n",
    "!sed -i 's/    raise RuntimeError(\"TTS requires python >= 3.9 and < 3.12 \" \"but your Python version is {}\".format(sys.version))/#     raise RuntimeError(\"TTS requires python >= 3.9 and < 3.12 \" \"but your Python version is {}\".format(sys.version))/g' submodules/TTS/setup.py\n",
    "!sed -i 's/python_requires=\">=3.9.0, <3.12\",/python_requires=\">=3.9.0, <3.13\",/g' submodules/TTS/setup.py\n",
    "print(\"Patched dependencies for Python 3.12 compatibility.\")\n",
    "\n",
    "# 5. 安装项目及子模块依赖\n",
    "print(\"Installing project requirements...\")\n",
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
        # Reset execution state
        cell['execution_count'] = None
        cell['outputs'] = []
        found_system = True
    elif cell.get('metadata', {}).get('id') == 'SmEIaKn1X1Hy':
        cell['source'] = python_deps_source
        # Reset execution state
        cell['execution_count'] = None
        cell['outputs'] = []
        found_python = True

if found_system and found_python:
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Notebook patched successfully.")
else:
    print(f"Error: Could not find all cells. System: {found_system}, Python: {found_python}")
    exit(1)
