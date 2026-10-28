import json
import re
import requests

API_URL = "https://api.hostmonit.com/get_optimization_ip"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://stock.hostmonit.com/CloudFlareYes",
    "Content-Type": "application/json",
}
payload = json.dumps({"key": "i-am-a-bot"})


def clean_latency(latency_str):
    nums = re.findall(r"\d+", str(latency_str))
    return int(nums[0]) if nums else 9999


def fetch_and_save():
    print("⏳ 开始抓取 HostMonit 优选 IP...")
    try:
        response = requests.post(API_URL, headers=headers, data=payload, timeout=15)
        ip_list = response.json().get("info", [])
        if not ip_list:
            print("❌ 获取数据为空！")
            return

        categorized = {"telecom": [], "mobile": [], "unicom": []}
        for item in ip_list:
            ip = item.get("ip")
            latency = str(item.get("latency", "999ms"))
            loss = str(item.get("loss", "0%"))
            line = str(item.get("line", "")).upper()

            if "0" not in loss:
                continue

            if "CT" in line or "电信" in line:
                categorized["telecom"].append(
                    {"ip": ip, "latency": latency, "tag": "电信"}
                )
            elif "CM" in line or "移动" in line:
                categorized["mobile"].append(
                    {"ip": ip, "latency": latency, "tag": "移动"}
                )
            elif "CU" in line or "联通" in line:
                categorized["unicom"].append(
                    {"ip": ip, "latency": latency, "tag": "联通"}
                )

        file_map = {
            "telecom.txt": categorized["telecom"],
            "mobile.txt": categorized["mobile"],
            "unicom.txt": categorized["unicom"],
        }

        for filename, ips in file_map.items():
            sorted_ips = sorted(ips, key=lambda x: clean_latency(x["latency"]))[:20]
            with open(filename, "w", encoding="utf-8") as f:
                for item in sorted_ips:
                    f.write(
                        f"{item['ip']}:443#私享{item['tag']}-{item['latency']}\n"
                    )
            print(f"✅ 生成 {filename} 成功")

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    fetch_and_save()
