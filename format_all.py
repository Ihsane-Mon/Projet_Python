import os
import subprocess


def run(cmd: str):
    print(f"\n=== {cmd} ===")
    subprocess.run(cmd, shell=False, check=False)


def python_files(root="."):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".venv"]]
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(cur, f)


if __name__ == "__main__":
    # 1) Nettoyage trailing spaces + newline final
    for path in python_files():
        print(f"Clean: {path}")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cleaned = [line.rstrip() + "\n" for line in lines]
        if cleaned and not cleaned[-1].endswith("\n"):
            cleaned[-1] += "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(cleaned)

    # 2) isort : ordre des imports
    run("python -m isort .")

    # 3) autopep8 : style général
    run("python -m autopep8 --in-place --recursive --aggressive --aggressive .")
