import httpx
import time
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

CLEAR_SCREEN = "\033[H\033[J"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://show.bilibili.com/",
    "Origin": "https://show.bilibili.com"
}

TARGET_INTERVAL = 1.0

def get_status_color(status: str) -> str:
    if status in ["已售罄", "不可售"]:
        return RED
    elif status == "预售中":
        return GREEN
    elif status in ["未开售", "已停售"]:
        return YELLOW
    return RESET

def monitor_ticket(project_id: str):
    url = f"https://show.bilibili.com/api/ticket/project/getV2?version=134&id={project_id}"

    while True:
        start_time = time.perf_counter()
        
        try:
            with httpx.Client(headers=HEADERS, timeout=2) as client:
                response = client.get(url)

            if response.status_code == 412:
                output_text = f"{RED}触发风控{RESET}"
            elif response.status_code != 200:
                output_text = f"{RED}请求失败 [{response.status_code}]{RESET}"
            else:
                data = response.json()
                if not data.get("success"):
                    output_text = f"{RED}接口返回异常{RESET}"
                else:
                    pd = data["data"]
                    now = datetime.now().strftime("%H:%M:%S")
                    screens = pd["screen_list"]

                    output_lines = [
                        f"{GREEN}当前时间：{now}{RESET}",
                        f"{BLUE}项目名称：{pd['name']}{RESET}",
                        "当前状态："
                    ]
                    for screen in screens:
                        output_lines.append(f"{YELLOW}{screen['name']}{RESET}")
                        for ticket in screen["ticket_list"]:
                            price = ticket["price"] / 100
                            status = ticket["sale_flag"]["display_name"]
                            color = get_status_color(status)
                            line = f"  └─ {ticket['desc']} ¥{price:.2f} {color}{status}{RESET}"
                            output_lines.append(line)
                    output_text = "\n".join(output_lines)

        except Exception:
            output_text = f"{RED}网络/数据请求异常{RESET}"

        print(f"{CLEAR_SCREEN}{output_text}", end="")

        elapsed = time.perf_counter() - start_time
        sleep_time = max(0.0, TARGET_INTERVAL - elapsed)
        time.sleep(sleep_time)

if __name__ == "__main__":
    pid = input("请输入票务项目ID：").strip()
    if not pid:
        print(f"{RED}项目ID不能为空！{RESET}")
        exit()
    print("\033[H\033[J", end="")
    monitor_ticket(pid)