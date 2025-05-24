# B站收藏夹仓库管理器

一个类似Git的B站收藏夹批量下载和同步工具，支持音频/视频下载、增量同步、智能管理。

## ✨ 特性

- 🎯 **Git风格管理**：init初始化、pull同步更新，操作直观
- 📊 **数字ID系统**：每个仓库都有唯一ID，支持ID或名称操作
- 🎵 **灵活下载模式**：支持仅音频、仅视频或完整视频下载
- 📱 **多清晰度支持**：从360P到4K，自动适配最高可用清晰度
- 🔄 **增量同步**：智能检测变化，只下载新增内容，自动删除移除的视频
- 🏗️ **仓库系统**：每个收藏夹独立管理，支持批量操作
- ⚙️ **配置管理**：支持运行时修改下载模式和清晰度
- 📁 **智能路径管理**：自动创建目录结构，支持自定义存储位置

## 🚀 快速开始

### 环境要求

- Python 3.7+
- FFmpeg（用于音视频处理）
- requests库

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/bilibili-favlist-manager.git
cd bilibili-favlist-manager
```

2. **安装Python依赖**
```bash
pip install requests
```

3. **安装FFmpeg**

**Windows:**
```bash
# 使用Chocolatey（推荐）
choco install ffmpeg

# 或使用winget
winget install FFmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

4. **运行程序**
```bash
python bilibiliFavlistRepos.py
```

## 📖 使用教程

### 首次运行

程序首次运行时会要求配置仓库存储目录：

```
请设置仓库存储目录:
这个目录将用于存储所有B站收藏夹的下载内容
请输入目录路径 (默认: bili_repos): D:\MyBilibiliDownloads
✓ 仓库目录已设置为: D:\MyBilibiliDownloads
```

### 基本命令

#### 1. 初始化仓库 (`init`)

```bash
命令: init
请输入收藏夹链接: https://space.bilibili.com/309874814/favlist?fid=3125287314&ftype=create
请输入仓库名（留空使用收藏夹标题）: 我的音乐收藏

可选清晰度:
80: 高清 1080P
64: 高清 720P
...

请选择清晰度 (默认80-高清1080P): 80
下载模式 (1: 视频, 2: 仅音频, 默认2): 2

✓ 仓库已初始化
  仓库ID: 1
  收藏夹: 我的音乐收藏
  ...
  
开始首次同步...
```

#### 2. 同步更新 (`pull`)

```bash
命令: pull
现有仓库列表:
📁 [1] 我的音乐收藏
📁 [2] 学习视频

请输入仓库ID或名称: 1    # 或输入 "我的音乐收藏"

正在同步仓库: 我的音乐收藏
本地视频: 25 个
云端视频: 27 个
需要删除: 1 个
需要下载: 3 个
...
```

#### 3. 列出仓库 (`list`)

```bash
命令: list
现有仓库列表:
================================================================================
📁 [1] 我的音乐收藏
   收藏夹: 精选音乐合集
   UP主: 音乐达人
   模式: 仅音频
   清晰度: 高清 1080P
   视频数量: 127
   最后同步: 2024-01-15T10:30:45

📁 [2] 编程学习
   收藏夹: Python教程集合
   UP主: 编程老师
   模式: 视频
   清晰度: 高清 1080P
   视频数量: 45
   最后同步: 2024-01-14T15:20:30
```

#### 4. 更新仓库属性 (`update`)

```bash
命令: update
请输入要更新的仓库ID或名称: 1

当前配置:
  仓库: [1] 我的音乐收藏
  模式: 仅音频
  清晰度: 高清 1080P

可修改项:
1. 下载模式
2. 清晰度
3. 两者都修改
请选择 (1/2/3): 1

下载模式:
1. 仅音频
2. 视频
请选择 (1/2): 2

✓ 仓库配置已更新
  下载模式: 仅音频 → 视频

注意: 下载模式已改变，建议:
- 删除现有音频文件，重新下载视频
- 或保留音频文件，新视频将下载为视频

是否重新下载所有文件? (y/n, 默认n): y
```

#### 5. 重新配置目录 (`config`)

```bash
命令: config
请设置仓库存储目录:
请输入目录路径 (默认: bili_repos): E:\NewLocation
✓ 仓库目录已设置为: E:\NewLocation
```

## 📁 目录结构

```
D:\MyBilibiliDownloads\          # 用户指定的基础目录
├── bili_config.json             # 全局配置文件（程序目录下）
├── 我的音乐收藏\                 # 仓库1（音频模式）
│   ├── .bili_repo.json          # 仓库配置文件
│   ├── 歌曲1.m4a
│   ├── 歌曲2.m4a
│   └── ...
├── 编程学习\                     # 仓库2（视频模式）
│   ├── .bili_repo.json
│   ├── Python基础教程.mp4
│   ├── 数据结构讲解.mp4
│   └── ...
└── 其他收藏夹\
    └── ...
```

## ⚙️ 配置说明

### 清晰度选项

| 代码 | 描述 |
|------|------|
| 120 | 超清 4K |
| 116 | 高清 1080P60 |
| 112 | 高清 1080P+ |
| 80 | 高清 1080P（推荐） |
| 74 | 高清 720P60 |
| 64 | 高清 720P |
| 32 | 清晰 480P |
| 16 | 流畅 360P |

### 下载模式

- **仅音频**：下载m4a格式音频文件
- **视频**：下载mp4格式视频文件（包含音频）

### 配置文件格式

**全局配置** (`bili_config.json`)：
```json
{
  "base_dir": "D:\\MyBilibiliDownloads"
}
```

**仓库配置** (`.bili_repo.json`)：
```json
{
  "repo_id": 1,
  "fid": "3125287314",
  "repo_name": "我的音乐收藏",
  "fav_title": "精选音乐合集",
  "fav_upper": "音乐达人",
  "quality": 80,
  "audio_only": true,
  "created_time": "2024-01-15T10:00:00",
  "last_sync": "2024-01-15T10:30:45",
  "video_list": {
    "BV1xx411x7xx": {
      "title": "歌曲名称",
      "upper": "UP主名",
      "duration": 240,
      "pubdate": 1641945600,
      "download_time": "2024-01-15T10:05:30"
    }
  }
}
```

## 🔧 高级功能

### 批量操作

可以通过脚本实现批量操作：

```bash
# 同步所有仓库
for i in {1..5}; do
    echo "pull $i" | python bilibiliFavlistRepos.py
done
```

### 定时同步

配置定时任务实现自动同步：

**Windows (计划任务):**
```batch
@echo off
cd /d "C:\path\to\your\project"
echo pull 1 | python bilibiliFavlistRepos.py
```

**Linux/macOS (crontab):**
```bash
# 每天2点同步ID为1的仓库
0 2 * * * cd /path/to/project && echo "pull 1" | python bilibiliFavlistRepos.py
```

### 网络代理

如果需要使用代理，可以设置环境变量：

```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python bilibiliFavlistRepos.py
```

## ❓ 常见问题

### Q: 提示"收藏夹可能是私密的或需要登录访问"

A: 这种情况下程序无法访问私密收藏夹。解决方案：
1. 将收藏夹设为公开
2. 或考虑添加登录功能（需要手动实现）

### Q: 下载速度很慢

A: 可能的原因和解决方案：
1. 网络问题：检查网络连接
2. B站限速：程序已内置延时机制，避免请求过快
3. 服务器负载：换个时间段试试

### Q: FFmpeg相关错误

A: 确保FFmpeg正确安装：
```bash
ffmpeg -version  # 应该显示版本信息
```

如果没有安装，参考前面的安装步骤。

### Q: 文件名包含特殊字符导致错误

A: 程序会自动清理文件名中的非法字符，将其替换为下划线。

### Q: 硬盘空间不足

A: 
1. 检查可用空间
2. 考虑使用仅音频模式（文件更小）
3. 定期清理不需要的文件

### Q: 如何备份/迁移仓库？

A: 
1. 备份整个基础目录
2. 保留所有`.bili_repo.json`配置文件
3. 在新环境中运行`config`命令设置新路径

## 🤝 贡献

欢迎提交Issues和Pull Requests！

### 开发环境设置

1. Fork本项目
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交Pull Request

### 代码规范

- 使用Python 3.7+语法
- 遵循PEP 8代码规范
- 添加适当的注释和文档
- 确保新功能有相应的错误处理

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

本工具仅供学习和个人使用，请遵守相关法律法规和平台服务条款。用户需对使用本工具的行为负责。

---

如果这个工具对您有帮助，请考虑给个⭐️！