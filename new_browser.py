from DrissionPage import ChromiumOptions, ChromiumPage
import os

# 设置基础路径
base_path = r"D:\Browser"


# 获取当前最大的文件夹编号
def get_max_folder_number():
    if not os.path.exists(base_path):
        return 0
    folders = [f for f in os.listdir(base_path) if f.isdigit()]
    return max(map(int, folders)) if folders else 0


if __name__ == "__main__":
    # 确保基础路径存在
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # 获取当前最大的文件夹编号
    max_number = get_max_folder_number()

    # 询问要创建的浏览器分身数量
    count = int(input("请输入要创建的浏览器分身数量: "))
    # 创建指定数量的浏览器分身
    for i in range(max_number + 1, max_number + count + 1):
        # 为每个分身创建一个唯一的用户数据路径
        user_data_dir = os.path.join(base_path, str(i))

        # 如果文件夹已存在，则跳过
        if os.path.exists(user_data_dir):
            print(f"第 {i} 个浏览器分身已存在，跳过创建。")
            continue

        # 创建ChromiumOptions对象
        co = ChromiumOptions()

        # 设置用户数据路径
        co.set_paths(user_data_path=user_data_dir)

        # 创建ChromiumPage对象
        page = ChromiumPage(co)

        # 访问一个网页以初始化浏览器配置
        page.get('https://www.example.com')

        print(f"已创建第 {i} 个浏览器分身，路径: {user_data_dir}")

        # 关闭浏览器
        page.quit()

    print("所有浏览器分身已创建完成。")
