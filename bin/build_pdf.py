# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
import io, os, re, subprocess, sys, html
import markdown

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(D, sys.argv[1]) if len(sys.argv) > 1 else os.path.join(D, "GATE.md")
BASE = os.path.splitext(os.path.basename(SRC))[0]
OUT_HTML = os.path.join(D, "_%s.html" % BASE)
MMD = os.path.join(D, "_mmd_%s" % BASE)
os.makedirs(MMD, exist_ok=True)

text = io.open(SRC, encoding="utf-8").read()

# 1. extract the mermaid blocks and render them to SVG
bloques = re.findall(r"```mermaid\n(.*?)```", text, re.S)
svgs = []
for i, b in enumerate(bloques, 1):
    mmd = os.path.join(MMD, "d%d.mmd" % i)
    svg = os.path.join(MMD, "d%d.svg" % i)
    io.open(mmd, "w", encoding="utf-8").write(b)
    if not os.path.exists(svg):
        r = subprocess.run(
            ["npx", "-y", "-p", "@mermaid-js/mermaid-cli@11.4.2", "mmdc",
             "-i", mmd, "-o", svg, "-b", "white", "-w", "1400"],
            capture_output=True, text=True)
        if not os.path.exists(svg):
            print("diagram %d failed:\n%s" % (i, r.stderr[-800:]), file=sys.stderr)
            sys.exit(1)
    s = io.open(svg, encoding="utf-8").read()
    s = re.sub(r"^<\?xml[^>]*\?>\s*", "", s)
    svgs.append(s)
    print("diagram %d rendered" % i)

# 2. swap the blocks for markers before converting
def marker(m, c=[0]):
    c[0] += 1
    return "\n\n@@DIAGRAM%d@@\n\n" % c[0]
text = re.sub(r"```mermaid\n.*?```", marker, text, flags=re.S)

body = markdown.markdown(
    text, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
    extension_configs={"toc": {"title": "Contents"}})

for i, s in enumerate(svgs, 1):
    body = body.replace("<p>@@DIAGRAM%d@@</p>" % i,
                            '<div class="diagram">%s</div>' % s)

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.55 -apple-system, "Helvetica Neue", Arial, sans-serif;
       color: #1a1a1a; margin: 0; }
h1 { font-size: 23pt; line-height: 1.2; margin: 0 0 6pt; letter-spacing: -0.4pt; }
h2 { font-size: 14.5pt; margin: 26pt 0 8pt; padding-bottom: 4pt;
     border-bottom: 1.5px solid #d8d8d8; break-after: avoid; break-inside: avoid; }
h3 { font-size: 11.5pt; margin: 16pt 0 5pt; color: #333; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
p { margin: 0 0 8pt; }
ul, ol { margin: 0 0 8pt; padding-left: 18pt; }
li { margin-bottom: 3pt; }
strong { color: #000; }
code { font: 9.3pt "SF Mono", Menlo, Consolas, monospace;
       background: #f2f2f4; padding: 1px 4px; border-radius: 3px; }
table { border-collapse: collapse; width: 100%; margin: 10pt 0 14pt;
        font-size: 9.3pt; break-inside: avoid; }
th { text-align: left; background: #f2f4f7; border-bottom: 1.5px solid #c8ccd2;
     padding: 5pt 7pt; font-weight: 600; }
td { border-bottom: 1px solid #e6e6e6; padding: 5pt 7pt; vertical-align: top; }
hr { border: 0; border-top: 1px solid #e2e2e2; margin: 20pt 0; }
.diagram { break-inside: avoid; margin: 14pt 0 18pt; text-align: center; }
.diagram svg { max-width: 100%; max-height: 225mm; height: auto; }
.toc { background: #f7f8fa; border: 1px solid #e2e5ea; border-radius: 5px;
       padding: 10pt 16pt; margin: 16pt 0 22pt; font-size: 9.8pt; break-inside: avoid; }
.toc > ul { padding-left: 14pt; margin: 4pt 0; }
.toc ul ul { display: none; }
.toc a { color: #1a1a1a; text-decoration: none; }
.toctitle { font-weight: 600; font-size: 10.5pt; display: block; margin-bottom: 2pt; }
h2 { break-before: auto; }
"""

doc = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>GATE — Governed, Assisted, Traceable Engineering</title>
<style>%s</style></head><body>%s</body></html>""" % (CSS, body)
io.open(OUT_HTML, "w", encoding="utf-8").write(doc)
print("HTML written")
