import os
import re

print("\n---- CSS SCAN STARTING ----\n")

css_file = "assets/style.css"

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def get_selectors(css):
    selectors = []
    blocks = re.findall(r'([^{]+)\{', css)
    for block in blocks:
        parts = block.split(',')
        for p in parts:
            s = p.strip()
            if s != "":
                selectors.append(s)
    return selectors

html_text = ""
html_files = []

for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".html"):
            path = os.path.join(root, f)
            html_files.append(path)
            html_text += read_file(path)

css = read_file(css_file)

selectors = get_selectors(css)

unused = []

for s in selectors:

    if s.startswith("."):
        name = s[1:]
        if name not in html_text:
            unused.append(s)

    elif s.startswith("#"):
        name = s[1:]
        if name not in html_text:
            unused.append(s)

print("HTML files scanned:", len(html_files))
print("Selectors checked:", len(selectors))

print("\n---- RESULT ----\n")

if len(unused) == 0:
    print("No unused selectors found.")
else:
    print("Unused selectors:\n")
    for u in unused:
        print(u)

print("\n---- SCAN COMPLETE ----\n")