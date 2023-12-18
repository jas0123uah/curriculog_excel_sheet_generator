import json
import openpyxl
with open('./proposals.json', 'r') as f:
    data = f.read()
js = json.loads(data)
print(js[0])
print(len(js))
fields = list(map(lambda x: x['fields'], js))
js = [item for row in fields for item in row]
label_values = {}
for obj in js:
 # print(obj)
  label = obj["label"]
  value = obj["value"]
  
  if label not in label_values:
    label_values[label] = []
  
  label_values[label].append(value)

empty_labels = []  
for label, values in label_values.items():
  all_empty = True
  for value in values:
    if value != "" and value != []:
      all_empty = False
      break
  
  if all_empty:
    empty_labels.append(label)

print(empty_labels)
print(len(empty_labels))
wb = openpyxl.Workbook()
cs = wb.active
cs.append(empty_labels)
#for label in empty_labels:
wb.save('empty_labels.xlsx')
