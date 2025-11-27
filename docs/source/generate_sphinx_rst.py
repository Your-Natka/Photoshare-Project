import os

APP_DIR = "../app"  # шлях від папки docs/source
RST_DIR = "."        # тут будуть створюватися .rst файли у source/

def snake_case(name):
    return name.replace(".py", "").replace("/", "_")

def generate_module_rst(py_file, rst_path):
    module_name = py_file.replace("/", ".").replace(".py", "")
    title = os.path.basename(py_file).replace(".py", "")
    content = f"{title}\n{'='*len(title)}\n\n.. automodule:: {module_name}\n    :members:\n    :undoc-members:\n    :show-inheritance:\n"
    with open(rst_path, "w") as f:
        f.write(content)

def main():
    modules_rst = []
    for root, dirs, files in os.walk(APP_DIR):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, APP_DIR)
                rst_filename = os.path.join(RST_DIR, f"{snake_case(rel_path)}.rst")
                generate_module_rst(f"app.{rel_path.replace(os.sep, '.')}", rst_filename)
                modules_rst.append(os.path.basename(rst_filename))

    # Оновлюємо modules.rst
    with open(os.path.join(RST_DIR, "modules.rst"), "w") as f:
        f.write("Modules\n=======\n\n.. toctree::\n   :maxdepth: 2\n\n")
        for rst_file in sorted(modules_rst):
            f.write(f"   {rst_file.replace('.rst','')}\n")

    # Оновлюємо index.rst
    index_path = os.path.join(RST_DIR, "index.rst")
    with open(index_path, "w") as f:
        f.write(f"""PhotoShare Project
==================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
""")

if __name__ == "__main__":
    main()
