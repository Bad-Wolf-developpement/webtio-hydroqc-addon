import os

directory = "./lib/hydroqc"

import_fix = "from __future__ import annotations"

for root, subdirectories, files in os.walk(directory):
    for file in files:
        ext = file.split(".")
        ext = ext[len(ext) - 1]
        if ext == "py" and "__" not in file:
            with open(os.path.join(root, file), 'r+') as f:
                content = f.read()
                f.seek(0,0)
                f.write(import_fix.rstrip('\r\n') + '\n' + content)