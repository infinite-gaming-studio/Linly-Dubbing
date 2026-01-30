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
| **依赖安装** | 基础 | 按依赖图顺序安装 |

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

#### Cell 2: 安装依赖 (改进版)
- ✅ 安装系统依赖
- ✅ **先安装所有子模块的基础依赖** (新增)
- ✅ 应用兼容性补丁
- ✅ 优雅处理pynini失败
- ✅ 按正确顺序安装子模块

**预计时间**: 3-5 分钟

**关键改进**:
- 安装顺序：系统依赖 → 子模块基础依赖 → 核心requirements → 子模块
- 自动安装 `dora-search` (demucs依赖)
- pynini 失败不会阻塞安装

#### Cell 3: 下载 AI 模型
- ✅ 下载 wav2vec2 模型
- ✅ 下载 HuggingFace 模型 (带重试机制)

**预计时间**: 10-15 分钟

#### Cell 4: 启动 WebUI (增强版)
- ✅ 配置环境变量
- ✅ **验证关键模块导入** (新增)
- ✅ 启动 Gradio WebUI

**预计时间**: 1 分钟

## 🐛 常见问题及解决方案

### Q: `ModuleNotFoundError: No module named 'dora'`
**A**: 这是 demucs 的依赖问题。最新版本的notebook已经自动安装 `dora-search`。  
如果仍然出现，手动执行：
```bash
!pip install dora-search
```

### Q: pynini 安装失败
**A**: pynini 不是核心依赖，失败不影响主要功能。notebook会显示警告但继续执行：
```
⚠️ pynini installation failed (non-critical, continuing...)
```

### Q: TTS 子模块安装失败
**A**: notebook会自动重试，首先尝试完整安装，失败后使用 `--no-deps`:
1. 第一次尝试: `pip install -e submodules/TTS`
2. 失败后重试: `pip install -e submodules/TTS --no-deps`
3. 使用 `sys.path` 作为后备方案

### Q: GPU 未检测到
**A**: 
1. 检查 Kaggle 设置是否启用了 GPU
2. 重启 notebook
3. 确认配额未用尽

### Q: 模型下载太慢或超时
**A**: 
1. 下载脚本已包含重试机制（最多5次）
2. 如果持续失败，检查 Internet 是否启用
3. 可以使用 Kaggle Dataset 预缓存模型

### Q: WebUI 无法访问
**A**:
1. 检查防火墙设置
2. 确认 Gradio 链接未过期（默认72小时）
3. 重新运行 Cell 4

### Q: Import Error 在启动时
**A**: notebook 会在启动前验证所有关键导入：
```python
from tools.step000_video_downloader import download_from_url
from tools.step010_demucs_vr import separate_all_audio_under_folder
```
如果失败，会自动尝试安装缺失的依赖包。

## 📊 资源使用预估

| 资源 | 使用量 | 备注 |
|------|--------|------|
| **磁盘空间** | ~20 GB | 代码 + 模型 |
| **内存 (RAM)** | ~10-15 GB | 运行时 |
| **GPU 内存** | ~8-12 GB | 每个 T4 |
| **网络流量** | ~15 GB | 首次下载 |

## 🔧 高级故障排除

### 依赖安装顺序

notebook 使用以下顺序安装依赖，以确保兼容性：

1. **系统依赖** → 2. **子模块基础依赖** → 3. **核心requirements** → 4. **子模块可编辑安装**

这个顺序很重要！如果手动修改，请保持此顺序。

### 手动修复依赖问题

如果自动安装失败，可以手动执行：

```python
# 安装所有基础依赖
!pip install dora-search diffq einops julius lameenc tqdm treetable
!pip install cython scipy soundfile librosa scikit-learn
!pip install transformers encodec unidecode num2words

# 然后安装子模块
!pip install -e submodules/demucs
!pip install -e submodules/whisper
!pip install -e submodules/whisperX
!pip install -e submodules/TTS
```

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

