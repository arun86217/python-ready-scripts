import os

def print_tree_one_level(path="."):
    items = sorted(os.listdir(path))

    for i, name in enumerate(items):
        full_path = os.path.join(path, name)
        connector = "└──" if i == len(items) - 1 else "├──"

        if os.path.isdir(full_path):
            print(f"{connector} {name}/")
        else:
            print(f"{connector} {name}")

if __name__ == "__main__":
    print(".")
    print_tree_one_level(".")
