import glob
import json
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python rank.py <objective_dir>")
    print("Example: python rank.py objective_2021-03-31_14-15-45") 
    sys.exit()

obj_dir = sys.argv[1]
search_path = os.path.join(obj_dir, "*/", "result.json")
result_files = glob.glob(''.join(search_path))

#print(f"{result_files=}")
config_scores = {}
for result_file in result_files:
    try:
        with open(result_file) as f:
            d = json.load(f)
    except Exception as e:
        continue
    config_scores[json.dumps(d['config'])] = d['score']

sorted_scores = sorted(config_scores.items(), key=lambda item: item[1])
for s in sorted_scores:
    print(s)

sys.stdout.flush()
sys.stdout.close()
sys.stderr.flush()
sys.stderr.close()
