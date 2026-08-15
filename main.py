import subprocess
import questionary

def main():
    options = {
        "🌟ldks": "input_get_ldks.py",
        "🌟drxsw": "input_get_drxsw.py",
        "🌟quanben": "input_get_quanben.py",
    }

    your_choice = questionary.select(
        "Please select a module to run:",
        choices=[
            f"{key}" for key in options
        ],
        # default="🌟drxsw",        # 默认首选项
        qmark="🌈",
        pointer="👉",
        # use_shortcuts=True,       # 启用键盘快捷键
        # selected_symbol="✔"       # 选中项的符号(多选时使用)
    ).ask()

    if your_choice:
        print(f"🔄 Running {options[your_choice]}...\n")
        subprocess.run(["python", options[your_choice]])
    else:
        print("❌ No selection, exiting program.")

if __name__ == "__main__":
    main()
