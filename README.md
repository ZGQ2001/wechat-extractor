# WeChat Chat History Export Tool

本工具用于导出用户自身的微信 PC/Mac 端聊天记录，将其转换为可读的 CSV/HTML/JSON 格式。

## ⚠️ 安全与合规声明
- 本工具仅用于个人数据备份和导出。
- 严禁用于非法窃取他人隐私。
- 密钥仅在本地处理，绝不上传网络。

## 安装步骤

### 环境要求
- Python 3.10+
- macOS 用户：需关闭 SIP (System Integrity Protection) 才能提取密钥。
- Windows 用户：需以管理员权限运行。

### 安装依赖
```bash
pip install -r requirements.txt
```

## 使用示例

### 1. 仅提取密钥 (Mac)
```bash
sudo python wechat_export.py --platform mac --extract-key
```

### 2. 导出所有记录 (Windows)
```bash
# 以管理员身份运行终端
python wechat_export.py --platform windows --format all
```

### 3. 使用已有密钥导出
```bash
python wechat_export.py --platform mac --key 64char_hex_key --format html
```

## 常见问题 (FAQ)
- **Mac 提示 SIP enabled?**
  请进入恢复模式执行 `csrutil disable` 并重启。
- **Windows 提取密钥失败?**
  请确保微信已登录且处于运行状态，并检查 `config/wx_version_offsets.json` 中的偏移量是否与当前版本匹配。
