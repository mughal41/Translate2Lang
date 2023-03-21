import concurrent.futures
import requests_html
import time
import xml.etree.ElementTree as ET

tree = ET.parse('src/strings.xml')
root = tree.getroot()
start = time.perf_counter()


def translate(file, i, hostLang='en', targetLang='zh'):
    session = requests_html.HTMLSession()
    exe_time = time.perf_counter()
    response = session.get(
        f"http://translate.googleapis.com/translate_a/single?client=gtx&sl={hostLang}&tl={targetLang}&dt=t&q={file.text}",
        verify=False)

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


def thread_start(root):
    with concurrent.futures.ThreadPoolExecutor(len(root)) as executor:
        results = []
        i = 1
        for j, line in enumerate(root):
            if line.tag == 'plurals':
                future = executor.submit(translate, line, i=i)
                results.append(future)
                i = i + 1
                for k, nest_line in enumerate(line):
                    future = executor.submit(translate, nest_line, i=i)
                    results.append(future)
                    i = i + 1
            else:
                future = executor.submit(translate, line, i=i)
                results.append(future)
                i = i + 1

        data = []
        for future in concurrent.futures.as_completed(results):
            result = future.result()
            if result != False:
                data.append(result)

    return sorted(data, key=lambda x: x['row_num'])



result = thread_start(root)

f = open('src/output/result4.txt', 'w')
i = 0
for r in result:
    i = i + 1
    try:
        f.write(f"{r['start']}{r['translation'][0][0][0]}{r['end']}\n")
    except:
        f.write(f"{r['start']}{r['end']}\n")

f.close()
print('total exe time: ', time.perf_counter() - start)
