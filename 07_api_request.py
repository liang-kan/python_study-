import requests


def main():
    url = "https://api.github.com/events"
    print(f"Requesting {url}...")

    try:
        response = requests.get(url, timeout=10)

        # --- 在这里打个断点 (Breakpoint) ---
        if response.status_code == 200:
            events = response.json()  # 将 JSON 解析为 List[Dict]

            print(f"Fetched {len(events)} events.")

            # 拿第一条数据演示
            if events:
                first_event = events[0]
                print(f"First Event Type: {first_event.get('type')}")
                print(f"Repo Name: {first_event.get('repo', {}).get('name')}")
        else:
            print("Failed to fetch data.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()