import requests
import csv
import time

# 模拟用户数据 API
API_URL = "https://jsonplaceholder.typicode.com/users"


def fetch_users():
    """从 API 获取数据"""
    print("Fetching users...")
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()


def save_csv(users, filename):
    """保存为 CSV"""
    headers = ["ID", "Name", "Email", "Website"]

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for user in users:
            row = [
                user['id'],
                user['name'],
                user['email'],
                user['website']
            ]
            writer.writerow(row)

    print(f"Successfully saved to {filename}")


def main():
    try:
        all_users = fetch_users()

        # 你的挑战作业：修改这里的逻辑
        # TODO: 尝试修改过滤条件，比如只导出 id > 5 的用户
        filtered_users = [u for u in all_users if u['id']>5]

        if not filtered_users:
            print("No users matched the criteria.")
            return

        timestamp = int(time.time())
        filename = f"users_{timestamp}.csv"

        save_csv(filtered_users, filename)

    except Exception as e:
        print(f"App crashed: {e}")


if __name__ == "__main__":
    main()
