# Kaggle 部署指南 - Linly-Dubbing

## 📋 简介

`kaggle_webui.ipynb` 是专门为 **Kaggle 双 T4 GPU 环境**优化的 Linly-Dubbing 部署 notebook。相比 Colab 版本，它更简洁、更高效。

## 🎯 主要优化

与 `colab_webui.ipynb` 相比的改进：

| 特性 | Colab 版本 | Kaggle 版本 |
|------|-----------|------------|
| **步骤数量** | 5 个 cell | 4 个 cell |
| **环境初始化** | 需要 Conda (重启内核) | 无需 Conda |
| **包管理器** | uv + pip | pip only |
| **GPU 检测** | ❌ | ✅ |
| **缓存优化** | 基础 | 智能缓存 |
| **用户反馈** | 简单 | 详细进度显示 |

## 🚀 使用步骤

### 1. 准备 Kaggle 环境

1. 登录 [Kaggle.com](https://www.kaggle.com)
2. 创建新的 Notebook
3. 上传 `kaggle_webui.ipynb`
4. 在设置中启用：
   - **Accelerator**: GPU T4 x2
   - **Internet**: On

### 2. 按顺序执行 Cells

#### Cell 1: 克隆仓库并检查 GPU
- ✅ 自动检测 GPU 数量和型号
- ✅ 克隆项目仓库
- ✅ 初始化子模块

**预计时间**: 1-2 分钟

#### Cell 2: 安装依赖
- ✅ 安装系统依赖 (build-essential, libfst-dev)
- ✅ 安装 PyTorch 2.3.1
- ✅ 应用兼容性补丁
- ✅ 安装 pynini 和所有项目依赖
- ✅ 验证关键包

**预计时间**: 3-5 分钟

#### Cell 3: 下载 AI 模型
- ✅ 下载 wav2vec2 模型 (360 MB)
- ✅ 下载 HuggingFace 模型:
  - XTTS-v2 (~2 GB)
  - Qwen1.5-4B-Chat (~8 GB)
  - faster-whisper-large-v3 (~3 GB)

**预计时间**: 10-15 分钟（取决于网络速度）

**总下载量**: ~15 GB

💡 **优化提示**: 模型会缓存在工作目录，再次运行时会跳过已下载的文件。

#### Cell 4: 启动 WebUI
- ✅ 配置环境变量
- ✅ 启动 Gradio WebUI
- ✅ 生成公共访问链接

**预计时间**: 1 分钟

成功启动后，会显示类似以下的公共 URL:
```
Running on public URL: https://xxxxx.gradio.live
```

## 📝 配置说明

### 默认配置

默认使用以下免费服务:
- **翻译**: Qwen1.5-4B-Chat (本地)
- **TTS**: Edge TTS / XTTS-v2
- **ASR**: WhisperX / FunASR

### 可选配置

#### 使用 OpenAI API (推荐更好的翻译质量)

1. 在 Cell 4 执行前，添加额外的 cell:
```python
import os
# 编辑 .env 文件
with open('.env', 'a') as f:
    f.write('\nOPENAI_API_KEY=sk-your-api-key-here\n')
    f.write('MODEL_NAME=gpt-3.5-turbo\n')
```

2. 然后继续执行 Cell 4

#### 启用说话人分离

如果需要使用 pyannote 进行说话人分离:

1. 在 [HuggingFace](https://huggingface.co/settings/tokens) 获取 API token
2. 申请访问 [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. 在 Cell 4 中取消注释以下行:
```python
os.environ['HF_TOKEN'] = 'your_huggingface_token_here'
```

## ⚡ 性能优化建议

### 1. 利用双 GPU

Linly-Dubbing 会自动检测并使用可用的 GPU。双 T4 可以:
- 并行处理音视频分离
- 加速模型推理

### 2. 重用缓存

Kaggle notebook 的工作目录在会话间会被清理，但你可以:
- 将模型保存到 Kaggle Dataset
- 从 Dataset 加载模型而非重新下载

修改 Cell 3，添加 Dataset 挂载代码:
```python
# 假设你已创建了一个包含模型的 Kaggle Dataset
from kaggle_datasets import KaggleDatasets
dataset_path = KaggleDatasets().get_gcs_path('your-username/linly-dubbing-models')
!ln -s {dataset_path}/models /kaggle/working/Linly-Dubbing/models
```

### 3. 减少内存占用

如果遇到内存不足:
- 在 WebUI 中处理较短的视频片段
- 使用较小的 batch size
- 关闭不需要的功能（如唇形同步）

## 🐛 常见问题

### Q: pynini 安装失败
**A**: 确保 Cell 2 中系统依赖安装成功。如果失败，手动执行:
```bash
!apt-get install -y build-essential libfst-dev
!pip install pynini==2.1.5
```

### Q: GPU 未检测到
**A**: 
1. 检查 Kaggle 设置是否启用了 GPU
2. 重启 notebook
3. 确认配额未用尽

### Q: 模型下载太慢
**A**: 
1. 使用 Kaggle Dataset 预缓存模型
2. 考虑分批下载大模型
3. 检查 Internet 是否启用

### Q: WebUI 无法访问
**A**:
1. 检查防火墙设置
2. 确认 Gradio 链接未过期（默认72小时）
3. 重新运行 Cell 4

## 📊 资源使用预估

| 资源 | 使用量 | 备注 |
|------|--------|------|
| **磁盘空间** | ~20 GB | 代码 + 模型 |
| **内存 (RAM)** | ~10-15 GB | 运行时 |
| **GPU 内存** | ~8-12 GB | 每个 T4 |
| **网络流量** | ~15 GB | 首次下载 |

## 🎓 下一步

成功部署后，你可以:
1. 上传视频进行翻译/配音测试
2. 尝试不同的 TTS 引擎
3. 调整翻译模型和参数
4. 探索唇形同步功能

## 📚 相关链接

- [项目主页](https://github.com/Kedreamix/Linly-Dubbing)
- [完整文档](https://github.com/Kedreamix/Linly-Dubbing/blob/main/README.md)
- [问题反馈](https://github.com/Kedreamix/Linly-Dubbing/issues)

---

**祝使用愉快！🎉**
