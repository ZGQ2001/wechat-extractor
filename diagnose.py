import subprocess
import pymem

def diagnose():
    print("===" * 15)
    print("🔍 正在扫描进程树与内存模块...")
    print("===" * 15)
    
    try:
        # 调用系统 tasklist 命令获取所有 weixin.exe 的 PID
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq weixin.exe" /NH', shell=True).decode('gbk', errors='ignore')
        lines = [line for line in output.split('\n') if 'weixin.exe' in line.lower()]
        
        pids = [int(line.split()[1]) for line in lines if len(line.split()) > 1]
        print(f"📦 共发现 {len(pids)} 个 weixin.exe 进程: {pids}\n")
        
        for pid in pids:
            try:
                pm = pymem.Pymem(pid)
                # 遍历该进程加载的所有 DLL，转小写对比
                modules = [m.name.lower() for m in pm.list_modules()]
                target_dlls = [m for m in modules if 'weixin' in m or 'wechat' in m]
                print(f"✅ PID: {pid} 附加成功 | 找到相关核心 DLL -> {target_dlls}")
            except Exception as e:
                print(f"⚠️ PID: {pid} 无法附加 (大概率是无权访问的沙盒/子进程)")
                
    except Exception as e:
        print(f"❌ 诊断脚本执行出错: {e}")

if __name__ == "__main__":
    diagnose()