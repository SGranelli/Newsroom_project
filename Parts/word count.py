import re

document = open('data.csv', 'r')
print(document['brand'])

frequency = {}
document_text = open('data.csv', 'r')
text = document_text.read().lower()
pattern = re.findall(r'\b[a-z]{3,}\b', text)
for word in pattern:
    count = frequency.get(word,0)
    frequency[word] = count +1
frequency_list = frequency.keys()
for words in frequency_list:
    print(words,frequency[words])