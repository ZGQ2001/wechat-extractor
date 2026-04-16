import sys
import frida
import psutil

def get_js_code():
    return """
    // 自动寻找微信的核心逻辑库
    var modules = Process.enumerateModules();
    var targetModule = null;
    for (var i = 0; i < modules.length; i++) {
        var m = modules[i];
        if (m.name.toLowerCase() === "weixin.dll" || m.name.toLowerCase() === "wechatdb.dll") {
            targetModule = m;
            break;
        }
    }

    if (targetModule) {
        console.log("[+] 发现微信核心库: " + targetModule.name + " 地址: " + targetModule.base);
        
        // 尝试寻找 sqlite3_key_v2 (这是 SQLCipher 开锁的终极入口)
        var symbols = targetModule.enumerateExports();
        var key_v2_addr = null;
        for (var j = 0; j < symbols.length; j++) {
            if (symbols[j].name.indexOf("sqlite3_key_v2") !== -1 || symbols[j].name.indexOf("sqlite3_key") !== -1) {
                key_v2_addr = symbols[j].address;
                break;
            }
        }

        if (key_v2_addr) {
            Interceptor.attach(key_v2_addr, {
                onEnter: function (args) {
                    var keyPtr = args[1]; // 第二个参数通常是密钥指针
                    var keyLen = args[2].toInt32();
                    if (keyLen >= 32) {
                        var keyHex = b2h(keyPtr.readByteArray(keyLen));
                        send({ type: 'intercept', key: keyHex, source: 'SQLite_Internal' });
                    }
                }
            });
            console.log("[+] 🎯 已成功挂载到内部数据库函数!");
        }
    }

    // 依然保留对系统库的监控作为备选
    var pbkdf2 = Module.findExportByName("bcrypt.dll", "BCryptDeriveKeyPBKDF2");
    if (pbkdf2) {
        Interceptor.attach(pbkdf2, {
            onEnter: function (args) {
                this.pbSalt = args[3];
                this.cbSalt = args[4].toInt32();
                this.pbKey = args[6];
                this.cbKey = args[7].toInt32();
            },
            onLeave: function (retval) {
                if (this.cbKey >= 32) {
                    send({ 
                        type: 'intercept', 
                        salt: b2h(this.pbSalt.readByteArray(this.cbSalt)),
                        key: b2h(this.pbKey.readByteArray(this.cbKey)),
                        source: 'System_BCrypt'
                    });
                }
            }
        });
        console.log("[+] 🎯 已成功挂载到系统加密库!");
    }

    function b2h(buffer) {
        return Array.prototype.map.call(new Uint8Array(buffer), x => ('00' + x.toString(16)).slice(-2)).join('');
    }
    """

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']
        print("\n" + "✨" * 15)
        print(f"💎 抓到情报! [来源: {p.get('source')}]")
        if 'salt' in p: print(f"📍 Salt: {p['salt']}")
        print(f"🔑 Key : {p['key']}")
        print("✨" * 15)

def main():
    print("🚀 正在启动 4.1.8.29 智能识别监听系统...")
    
    # 获取所有同名进程
    pids = [p.pid for p in psutil.process_iter() if p.name().lower() == "weixin.exe"]
    
    if not pids:
        print("❌ 未找到 Weixin.exe 进程，请确保微信已运行。")
        return

    session = None
    for pid in pids:
        try:
            # 尝试附加到每一个 PID 看看
            temp_session = frida.attach(pid)
            # 检查这个进程有没有加载 weixin.dll
            modules = [m.name.lower() for m in temp_session.enumerate_modules()]
            if "weixin.dll" in modules or "wechatdb.dll" in modules:
                session = temp_session
                print(f"✅ 成功锁定核心主进程! (PID: {pid})")
                break
            else:
                temp_session.detach()
        except Exception:
            continue

    if not session:
        print("❌ 遍历了所有进程，但未能成功穿透核心防护。请尝试以管理员权限重启 VS Code。")
        return

    try:
        script = session.create_script(get_js_code())
        script.on('message', on_message)
        script.load()
        print("\n🎧 正在全力监听底层信号...")
        print("🚨 【动作指示】：请【重新登录微信】或在群聊间反复横跳！")
        sys.stdin.read()
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    main()