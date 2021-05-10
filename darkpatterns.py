import re
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
    text_entries = list(path.glob("*.txt"))
    text_entries = sorted(text_entries, key=lambda x:int(x.name.split('_')[0]))
    context = {
        "entries" : [],
    }
    for text_entry in text_entries:
        illustration = (path/(text_entry.stem+".png")).relative_to(base)
        illustration_type = "image"
        if illustration.exists():
            illustration = str(illustration)
        else:
            if (path/text_entry.stem/"file.html").exists():
                with open(path/text_entry.stem/"file.html", "r") as input_file:
                    illustration = env.from_string(input_file.read()).render()
                    illustration_type = "html"
            else:
                illustration = str(illustration)
        
        with open(text_entry) as input_file:
            content = markdown.markdown(input_file.read())
            soup = BeautifulSoup(content, "html.parser")
            soup.find("p").name = "h3"
            hint = soup.find("p", string=re.compile("[H,h]int"))
            if hint is not None:
                hint_content = re.match(r"\([H,h]int:\ ?(.*)\)", hint.string).group(1)
                hint.decompose()
            else:
                hint_content = None
            context['entries'].append((soup.prettify(), illustration, illustration_type, hint_content))
    
    with open(path/"text.md", "r") as input_file:
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
    output_file.write(template.render(**context))
        