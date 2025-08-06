import subprocess

def main():
    options = {
        "ldks": "input_get_ldks.py",
        "drxsw": "input_get_drxsw.py",
    }

    print("可选模块：")
    for key in options:
        print(f"🌟{key}")

    yourchoice = input("请输入要运行的模块关键字：").strip().lower()

    if yourchoice in options:
        print(f"🔄 正在运行 {options[yourchoice]}...\n")
        subprocess.run(["python", options[yourchoice]])
    else:
        print("❌ 无效输入，请重新运行")

if __name__ == "__main__":
    main()
