import re
import requests

# WeTest 官方实时优选源镜像（GitHub 内部千兆直连，无任何拦截）
SOURCE_URL = "https://raw.githubusercontent.com/gshtwy/CF-DNS-Clone/refs/heads/main/wetest-cloudflare-v4.txt"


def fetch_and_save():
    print("⏳ 正在拉取 WeTest 官方实时优选数据...")
    try:
        resp = requests.get(SOURCE_URL, timeout=15)
        if resp.status_code != 200:
            print("❌ 获取远程数据失败")
            return

        lines = resp.text.strip().split("\n")

        telecom = []
        mobile = []
        unicom = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 提取 IP:端口 和 备注
            # 常见格式形如: 104.16.x.x:443#电信 或 104.16.x.x#电信
            parts = line.split("#")
            addr = parts[0].strip()
            tag = parts[1].strip() if len(parts) > 1 else ""

            # 补齐 443 端口
            if ":" not in addr:
                addr = f"{addr}:443"

            if "电信" in tag:
                telecom.append(f"{addr}#私享电信")
            elif "移动" in tag:
                mobile.append(f"{addr}#私享移动")
            elif "联通" in tag:
                unicom.append(f"{addr}#私享联通")

        # 每个分类精选前 10 个（精简不臃肿）
        file_map = {
            "telecom.txt": telecom[:10],
            "mobile.txt": mobile[:10],
            "unicom.txt": unicom[:10],
        }

        for filename, ip_list in file_map.items():
            with open(filename, "w", encoding="utf-8") as f:
                for item in ip_list:
                    f.write(f"{item}\n")
            print(f"✅ 生成 {filename} 成功，共 {len(ip_list)} 个节点")

        print("🎉 全部处理完毕！")

    except Exception as e:
        print(f"❌ 运行异常: {e}")


if __name__ == "__main__":
    fetch_and_save()
