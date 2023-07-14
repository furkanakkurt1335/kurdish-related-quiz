import json, os, re

with open('leker.json', 'r', encoding='utf-8') as f:
  leker_d = json.load(f)

h2_pattern = '^== (.*?) ==$'
h3_pattern = '^=== (.*?) ===$'
h4_pattern = '^==== (.*?) ====$'
header_pattern = '^=+ .*? =+$'
meaning_pattern = '^# (.*?)$'
example_pattern = "^#[:*] (.*?)$"
z_pattern = '\* \{\{Z\|(en|tr)\}\}: .*$'
w_pattern = '\{\{W[+-]?\|(en|tr)\|(.*?)\}\}'

leker_parsed_d = dict()
leker_l = list(leker_d.keys())
for i, leker_t in enumerate(leker_l):
  info_t = leker_d[leker_t]
  is_kurdish_entry = False
  is_leker = False
  is_werger = False
  is_under_meaning = False
  if i % 100 == 0:
    print(i)
  for line in info_t.split('\n'):
    header_search = re.search(header_pattern, line)
    if header_search:
      is_under_meaning = False
    h2_search = re.search(h2_pattern, line)
    if h2_search:
      if h2_search.group(1) == '{{ziman|ku}}' or h2_search.group(1) == '{{ziman|kmr}}':
        is_kurdish_entry = True
        leker_parsed_d[leker_t] = {"meanings": []}
      else:
        is_kurdish_entry = False
    else:
      h3_search = re.search(h3_pattern, line)
      if h3_search:
        if h3_search.group(1) == 'Lêker':
          is_leker = True
          is_under_meaning = True
        else:
          is_leker = False
      else:
        h4_search = re.search(h4_pattern, line)
        if h4_search:
          if h4_search.group(1) == 'Werger':
            is_werger = True
          else:
            is_werger = False
        elif is_kurdish_entry:
          if is_leker:
            meaning_search = re.search(meaning_pattern, line)
            if meaning_search:
              meaning_t = meaning_search.group(1)
              if meaning_t == '{{mane?|ku}}':
                meaning_d = dict()
              else:
                meaning_d = {"meaning": meaning_t}
              leker_parsed_d[leker_t]['meanings'].append(meaning_d)
            else:
              example_search = re.search(example_pattern, line)
              if example_search:
                example_t = example_search.group(1)
                if example_t == '{{mînak?|ku}}':
                  pass
                elif 'examples' in meaning_d.keys():
                  meaning_d['examples'].append(example_search.group(1))
                else:
                  meaning_d['examples'] = [example_search.group(1)]
              elif is_werger:
                z_search = re.search(z_pattern, line)
                if z_search:
                  lang = z_search.group(1)
                  if 'translations' not in leker_parsed_d[leker_t].keys():
                    leker_parsed_d[leker_t]['translations'] = {lang: list()}
                  elif lang not in leker_parsed_d[leker_t]['translations'].keys():
                    leker_parsed_d[leker_t]['translations'][lang] = list()
                  w_search = re.findall(w_pattern, line)
                  if w_search:
                    w_l = [i[1] for i in w_search]
                    leker_parsed_d[leker_t]['translations'][lang].extend(w_l)
with open('leker_parsed.json', 'w', encoding='utf-8') as f:
  json.dump(leker_parsed_d, f, ensure_ascii=False)
