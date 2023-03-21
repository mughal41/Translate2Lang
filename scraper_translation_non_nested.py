import concurrent.futures
import requests_html
import time
import xml.etree.ElementTree as ET

tree = ET.parse('src/strings.xml') # path to file
root = tree.getroot()
start = time.perf_counter()


def translate(file, i, hostLang='en', targetLang='fr'):
    session = requests_html.HTMLSession()
    exe_time = time.perf_counter()
    response = session.get(
        f"https://translate.google.com/m?&tl={targetLang}&q={file.text}&hl={hostLang}", verify=False)

    if response.status_code == 200:
        session.close()
        return {
            'row_num': i,
            'execution_time': time.perf_counter() - exe_time,
            'start': f"""<{file.tag} {file.keys()[0]}="{file.attrib.get('name', 'quantity')}">""",
            'translation': response.html.find('.result-container', first=True).text,
            'end': f"</{file.tag}>"
        }
    else:
        return False


def thread_start(root):
    with concurrent.futures.ThreadPoolExecutor(len(root)) as executor:
        results = []
        for i, file in enumerate(root):
            future = executor.submit(translate, file, i=i)
            results.append(future)
        data = []
        for future in concurrent.futures.as_completed(results):
            result = future.result()
            if result != False:
                data.append(result)

    return sorted(data, key=lambda x: x['row_num'])


result = thread_start(root)

f = open('src/output/result.txt', 'w')
i = 0
for r in result:
    i = i + 1
    try:
        f.write(f"{r['start']}{r['translation']}{r['end']}\n")
    except:
        f.write(f"{r['start']}{r['end']}\n")

f.close()
print('total exe time: ', time.perf_counter() - start)