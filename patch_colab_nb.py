import json
import os

nb_path = 'colab_webui.ipynb'

if not os.path.exists(nb_path):
    print(f"Error: {nb_path} not found.")
    exit(1)

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Define new source code for the cells
conda_init_source = [
    "# [Step 1.0] 初始化 Conda 环境 (Initialize Conda)\n",
    "# 基于 README.md 建议，使用 Conda 管理 ffmpeg 和 pynini 等关键依赖\n",
    "# 注意：执行此单元格后内核会自动重启 (Notebook will restart after execution)\n",
    "try:\n",
    "    import condacolab\n",
    "    condacolab.check()\n",
    "    print(\"Conda environment already initialized.\")\n",
    "except ImportError:\n",
    "    !pip install -q condacolab\n",
    "    import condacolab\n",
    "    condacolab.install()"
]

system_deps_source = [
    "# [Step 1.3] 安装系统级及 Conda 依赖 (System & Conda Dependencies)\n",
    "# 优先安装 Conda 版本的 ffmpeg 和 pynini，这是 README 推荐的最佳实践\n",
    "!apt-get update -qq\n",
    "!apt-get install -y -qq build-essential libfst-dev espeak-ng libsndfile1 \\\n",
    "    libavfilter-dev libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev > /dev/null\n",
    "\n",
    "print(\"Installing ffmpeg and pynini via mamba...\")\n",
    "import condacolab\n",
    "!mamba install -y ffmpeg==7.0.2 pynini==2.1.5 -c conda-forge > /dev/null\n",
    "\n",
    "print(\"System & Conda dependencies installed.\")\n",
    "!ffmpeg -version | head -n 1"
]

python_deps_source = [
    "# [Step 1.4] Python 依赖安装 (Python Dependencies via uv)\n",
    "# 我们使用 'uv' 进行极速安装。Colab 环境需要特定版本的库以保证 ASR/TTS 兼容性。\n",
    "\n",
    "# 1. 安装 uv\n",
    "!pip install -q uv\n",
    "\n",
    "# 2. [CRITICAL] 强制重装核心库 (Fix for numpy, setuptools, torch compatibility)\n",
    "print(\"Installing core compute libraries... This might take a minute.\")\n",
    "# numpy<2.0.0 and torch==2.3.1 are strictly required\n",
    "!uv pip install --system --force-reinstall \"numpy<2.0.0\" \"setuptools\" \"loguru\" \"yt-dlp\" torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1\n",
    "\n",
    "# 3. 运行时修补 (Runtime Patching)\n",
    "# 将 numpy==1.26.3 修改为 numpy<2.0.0 以提高灵活性\n",
    "!sed -i 's/numpy==1.26.3/numpy<2.0.0/g' requirements.txt\n",
    "\n",
    "# [CRITICAL] Patch TTS submodule for Python 3.12 support (Colab uses 3.12)\n",
    "import os\n",
    "if os.path.exists('submodules/TTS/setup.py'):\n",
    "    !sed -i 's/if Version(python_version) < Version(\"3.9\") or Version(python_version) >= Version(\"3.12\"):/# if Version(python_version) < Version(\"3.9\") or Version(python_version) >= Version(\"3.12\"):/g' submodules/TTS/setup.py\n",
    "    !sed -i 's/    raise RuntimeError(\"TTS requires python >= 3.9 and < 3.12 \" \"but your Python version is {}\".format(sys.version))/#     raise RuntimeError(\"TTS requires python >= 3.9 and < 3.12 \" \"but your Python version is {}\".format(sys.version))/g' submodules/TTS/setup.py\n",
    "    !sed -i 's/python_requires=\">=3.9.0, <3.12\",/python_requires=\">=3.9.0, <3.13\",/g' submodules/TTS/setup.py\n",
    "    print(\"Patched TTS for Python 3.12 compatibility.\")\n",
    "\n",
    "# 4. 安装项目及子模块依赖\n",
    "print(\"Installing project requirements...\")\n",
    "!uv pip install --system -r requirements.txt\n",
    "!uv pip install --system -r requirements_module.txt\n",
    "\n",
    "print(\"Python dependencies installed successfully.\")\n",
    "\n",
    "# 5. 验证关键包\n",
    "try:\n",
    "    import yt_dlp\n",
    "    import loguru\n",
    "    print(\"✅ yt-dlp and loguru installed successfully.\")\n",
    "except ImportError as e:\n",
    "    print(f\"❌ Verification failed: {e}. Attempting recovery...\")\n",
    "    !pip install yt-dlp loguru"
]

# Find and update cells
found_system = False
found_python = False
conda_init_exists = any(c.get('metadata', {}).get('id') == 'CondaInit' for c in nb['cells'])

if not conda_init_exists:
    # Insert at the beginning or after some intro
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"id": "CondaInit"},
        "outputs": [],
        "source": conda_init_source
    }
    nb['cells'].insert(2, new_cell) # After Step 1.1 intro markdown
    print("Inserted CondaInit cell.")

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
    print("Notebook patched successfully.")
else:
    print(f"Warning: Could not find all cells. System: {found_system}, Python: {found_python}")
    # Still write if we did something
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
