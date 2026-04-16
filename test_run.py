import sys
import platform
from pathlib import Path

# 引入我们刚才写的模块
from src.key_extractor import extract_key
from src.db_finder import batch_decrypt

def main():
    print("===" * 15)
    print("🚀 微信数据库解密临时测试启动！")
    print("===" * 15)

    # 1. 尝试提取密钥
    print("\n[第一步] 正在从内存提取密钥...")
    key = extract_key()
    
    if not key:
        print("\n❌ 密钥提取失败，请检查报错信息并确保微信正在运行。")
        sys.exit(1)

    print(f"\n🔑 你的微信密钥是: {key}")
    print("\n" + "===" * 15)
    print("🛑 关键操作提醒 (WAL 日志合并) 🛑")
    print("为了保证聊天记录不丢失，请现在进行以下操作：")
    print("1. 去电脑桌面/任务栏，右键正常【退出微信】")
    print("2. 确认微信已经彻底关闭后，回到这里")
    print("===" * 15)
    
    # 暂停程序，等待用户手动确认
    input("\n👉 如果你已经退出了微信，请按【回车键】继续解密过程：")

    # 2. 开始扫描并解密
    print("\n[第二步] 开始扫描并解密数据库...")
    
    # 判断当前是 Windows 还是 Mac，以便使用正确的解密参数（页大小 4096 vs 1024）
    sys_plat = platform.system().lower()
    plat = "windows" if sys_plat == "windows" else "mac"
    
    # 我们把解密后的文件统一输出到项目根目录的 output_test 文件夹里
    output_dir = Path("./output_test")
    
    # 调用批量解密函数
    decrypted_files = batch_decrypt(platform=plat, key_hex=key, output_dir=output_dir)
    
    if decrypted_files:
        print("\n🎉 测试圆满成功！")
        print(f"一共解密了 {len(decrypted_files)} 个数据库文件。")
        print(f"快去项目目录下的 {output_dir.name} 文件夹里看看吧！")
    else:
        print("\n⚠️ 未找到任何可以解密的文件或解密过程出错，请往上翻看红色报错信息。")

if __name__ == "__main__":
    main()