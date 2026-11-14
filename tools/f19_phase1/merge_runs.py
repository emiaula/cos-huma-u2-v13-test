import json, sys
# merge base runs: later files replace rows (same lesson/view/vp) of earlier ones; then keep only rows of the given lessons
out, files = sys.argv[1], sys.argv[2:]
d = {}
for f in files:
    for r in json.load(open(f)): d[(r['lesson'], r['view'], r['vp'])] = r
json.dump(list(d.values()), open(out, 'w'), ensure_ascii=False)
print(len(d))
