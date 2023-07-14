import re, requests, json

with open('Lêker_bi_kurdî.txt', 'r', encoding='utf-8') as f:
    leker_l = f.read().split('\n')
content_pattern = 'name="wpTextbox1">(.*?)</textarea>'
leker_d = dict()
count = 0
for leker_t in leker_l:
    leker_t = leker_t.replace(' ', '_')
    url = 'https://ku.wiktionary.org/w/index.php?title={title}&action=edit'.format(title=leker_t)
    r = requests.get(url)
    s = r.text
    content_search = re.search(content_pattern, s, re.DOTALL)
    if content_search:
        leker_d[leker_t] = content_search.group(1)
    else:
        print(leker_t, 'not found')
with open('leker.json', 'w', encoding='utf-8') as f:
    json.dump(leker_d, f, ensure_ascii=False)