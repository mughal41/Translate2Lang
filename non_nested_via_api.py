import concurrent.futures
import requests_html
import time
import xml.etree.ElementTree as ET

start = time.perf_counter()
tree = ET.parse('src/strings.xml')
root = tree.getroot()


def translate(file, i, hostLang='en', targetLang='zh'):
    session = requests_html.HTMLSession()
    exe_time = time.perf_counter()
    response = session.get(
        f"http://translate.googleapis.com/translate_a/single?client=gtx&sl={hostLang}&tl={targetLang}&dt=t&q={file.text}")

    if response.status_code == 200:
        session.close()
        return {
            'row_num': i,
            'execution_time': time.perf_counter() - exe_time,
            'start': f"""<{file.tag} {file.keys()[0]}="{file.attrib.get('name', 'quantity')}">""",
            'translation': response.json(),
            'end': f"</{file.tag}>"
        }
    else:
        return False


def main(root):
    with concurrent.futures.ThreadPoolExecutor(60) as executor:
        results = []
        for i, line in enumerate(root):

            future = executor.submit(translate, line, i=i)
            results.append(future)
        data = []
        for future in concurrent.futures.as_completed(results):
            result = future.result()
            if result != False:
                data.append(result)

    return sorted(data, key=lambda x: x['row_num'])


result = main(root)

f = open('src/output/result2.txt', 'w')
i = 0
for r in result:
    i = i + 1
    try:
        f.write(f"{r['start']}{r['translation'][0][0][0]}{r['end']}\n")
    except:
        f.write(f"{r['start']}{r['end']}\n")

f.close()
print('total exe time: ', time.perf_counter() - start)