import re
import requests

alphabet = []
alp_temp = [ord('a'), ord('z'), ord('A'), ord('Z')]
for i in range(alp_temp[0], alp_temp[1]+1):
    alphabet.append(chr(i))
for i in range(alp_temp[2], alp_temp[3]+1):
    alphabet.append(chr(i))
url = 'https://ku.wiktionary.org/wiki/Kategorî:Lêker_bi_kurdî'
p = 1
urls = []
next_pattern = 'pagefrom=.*?#mw-pages'
with open('Lêker_bi_kurdî.txt', 'w', encoding='utf-8') as f:
    while True:
        r = requests.get(url)
        s = r.text
        url_search = re.search(next_pattern, s)
        si1 = s.index('rûpela pêş')
        si2 = s.index('printfooter')
        s = s[si1:si2]
        l = re.findall('<li><a href=.*title=.*>(.*)</a></li>', s)
        p += 1
        for j in range(1, len(l)):
            f.write(l[j] + '\n')
        if 'ḧîsandin' in l:
            f.close()
            break
        last = l[-1]
        if url_search:
            url = 'https://ku.wiktionary.org/w/index.php?title=Kategorî:Lêker_bi_kurdî&' + url_search.group()
        else:
            break
