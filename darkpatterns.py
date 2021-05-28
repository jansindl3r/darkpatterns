import re
import json
import markdown
from pathlib import Path 
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from bs4 import BeautifulSoup

base = Path(__file__).parent

env = Environment(loader=FileSystemLoader(str(base/"templates")), extensions=['jinja2.ext.loopcontrols'])
env.trim_blocks = True
env.lstrip_blocks = True
env.globals.update(zip=zip)


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
            with open(path/entry.stem/"file.html", "r") as input_file:
                illustration = env.from_string(input_file.read()).render()
            interactive = True
            illustration_type = "html"
        else:
            interactive = False
            try:
                with open(illustration.parent/f"{illustration.parent.stem}.svg", "r") as input_file:
                    illustration = input_file.read() 
            except:
                illustration = ""
            illustration = illustration.replace("<path", '<path vector-effect="non-scaling-stroke"')
            # illustration = str((illustration.parent/f"{illustration.parent.stem}.svg").relative_to(base))
            illustration_type = "image"
        
        if entry.stem in ["5_Limitovana_nabidka", "23_Pridruzena_slova", "7_Nutnost_prihlaseni"]:
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
    output_file.write(BeautifulSoup(template.render(**context), 'html.parser').prettify())
        