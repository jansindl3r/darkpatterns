import re
import json
import markdown
from pathlib import Path 
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from bs4 import BeautifulSoup
from random import random
import htmlmin

base = Path(__file__).parent

env = Environment(loader=FileSystemLoader(str(base/"templates")), extensions=['jinja2.ext.loopcontrols'])
env.trim_blocks = True
env.lstrip_blocks = True
env.globals.update(zip=zip)

def stroke_1px(svg_file):
    matches = list(re.finditer(r"stroke-width:(\d+\.?\d*)px+?", svg_file))
    for match in matches[::-1]:
        left, right = match.span(1)
        svg_file = svg_file[:left] + "1" + svg_file[right:]
    return svg_file

def randomize_id(svg_file):
    matches = list(re.finditer(r"(_clip\d+)", svg_file))
    ids = {}
    for match in matches[::-1]:
        clip_id = match.group()
        if clip_id not in ids:
            ids[clip_id] = f"clip_{round(random()*100000000000000)}"
        left, right = match.span()
        svg_file = svg_file[:left] + ids[clip_id] + svg_file[right:]
    return svg_file

def categories(path):
    with open(base/"square_entries.json") as input_file:
        square_entries = json.load(input_file)
    text_entries = list(path.glob("*"))
    text_entries = filter(lambda x:x.is_dir(), text_entries)
    text_entries = sorted(text_entries, key=lambda x:int(x.name.split('_')[0]))
    context = {
        "entries" : [],
    }
    for entry in text_entries:
        illustration = entry/"file.html"
        if illustration.exists():
            svgs = {}
            for svg in entry.glob("*.svg"):
                with open(svg, "r") as input_file:
                    svg_file = input_file.read()
                    svg_file = randomize_id(svg_file)
                    svg_file = stroke_1px(svg_file)
                    matches = list(re.finditer(r"(style)=", svg_file))
                    for match in matches[::-1]:
                        left = match.span(1)[0]
                        svg_file = svg_file[:left] + ' vector-effect="non-scaling-stroke" ' + svg_file[left:]

                    svgs[svg.stem] = svg_file
            with open(path/entry.stem/"file.html", "r") as input_file:
                illustration = env.from_string(input_file.read()).render({"svgs": svgs})
            interactive = True
            illustration_type = "html"
        else:
            interactive = False
            try:
                with open(illustration.parent/f"{illustration.parent.stem}.svg", "r") as input_file:
                    illustration = stroke_1px(input_file.read())
                    illustration = randomize_id(illustration)
                    # illustration = input_file.read())
            except:
                illustration = ""
            illustration = illustration.replace("<path", '<path vector-effect="non-scaling-stroke"')
            illustration_type = "image"
        
        if entry.stem in ["5_Limitovana_nabidka", "23_Pridruzena_slova", "7_Nutnost_prihlaseni", "4_Skryte_predplatne", "8_Falesne_recenze"]:
            interactive = False
            
        with open(entry/f"{entry.stem}.txt") as input_file:
            content = markdown.markdown(input_file.read())
            soup = BeautifulSoup(content, "html.parser")
            soup.find("p").name = "h3"
            hint = soup.find("p", string=re.compile("[H,h]int"))
            if hint is not None:
                hint_content = re.match(r"\([H,h]int:?\ ?(.*)\)", hint.string).group(1)
                hint.decompose()
            else:
                hint_content = None
        context['entries'].append((soup.prettify(), illustration, illustration_type, hint_content, entry.stem in square_entries, interactive))
    
    with open(path/"Kategorie_uvod.txt", "r") as input_file:
        context['content'] = markdown.markdown(input_file.read())
    template = env.get_template('categories.html')
    return template.render(**context)

def text(path):
    with open(path/"text.md") as input_file:
        return markdown.markdown(input_file.read())

def intro(path):
    context = {
        "content": text(path)
        }
    template = env.get_template('intro.html')
    return template.render(**context)

subfolders = [
    ("ÚVOD", intro), 
    ("KATEGORIE", categories), 
    ("UŽITEČNÉ PLUGINY", text),
    ("UŽITEČNÉ ODKAZY", text), 
    ("O PROJEKTU", text), 
    ]

context = {
    "entries": []
}

for subfolder, func in subfolders:
    if func is None:
        continue
    context['entries'].append(func(base/"data"/subfolder))


template = env.get_template('main.html')


with open("index.html", "w+") as output_file:
    html = template.render(**context)
    html = htmlmin.minify(html, remove_comments=True, remove_empty_space=True)
    output_file.write(html)
        