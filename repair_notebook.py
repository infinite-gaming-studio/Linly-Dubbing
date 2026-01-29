import json
import os

path = '/Users/nvozi/Coding/ai-based-projects/Linly-Dubbing/colab_webui.ipynb'
if not os.path.exists(path):
    print(f"Error: {path} not found.")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

repo_url = 'https://github.com/infinite-gaming-studio/Linly-Dubbing.git'

found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and any('[Step 2]' in str(line) for line in cell['source']):
        cell['source'] = [
            '# [Step 2] 获取代码 (Get Code)\n',
            'import os\n',
            'if not os.path.exists(\'/content/Linly-Dubbing\'):\n',
            '    %cd /content/\n',
            f'    !git clone {repo_url} --depth 1\n',
            'else:\n',
            '    print(\'Project already cloned. Pulling latest changes...\')\n',
            '    %cd /content/Linly-Dubbing\n',
            '    !git pull\n',
            '\n',
            '%cd /content/Linly-Dubbing\n',
            '!git submodule update --init --recursive'
        ]
        found = True
        break

if found:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print('Notebook updated successfully.')
else:
    print('Step 2 cell not found.')
