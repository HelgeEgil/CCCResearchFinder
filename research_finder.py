from Bio import Entrez
from time import sleep
import pandas as pd
from tqdm import tqdm
from thefuzz import fuzz

def fuzzyMatch(string: str, listOfStrings: list):
	bestScore = 0
	bestItem = None
	for item in listOfStrings:
		simScore = fuzz.ratio(string.lower(), item.lower())
		if simScore > bestScore:
			bestScore = simScore
			bestItem = item

	return bestItem, bestScore

with open("data/author_list_from_hus.csv", "r", encoding='utf-8') as input_file:
	line = input_file.readlines()[0]
	author_list_hus = line.split(",")

Entrez.email = "helge.pettersen@helse-bergen.no"
Entrez.retmax = 10

dict_keys = ['Item', 'Id', 'PubDate', 'EPubDate', 'Source', 'AuthorList', 
				'FirstAuthor', 'SecondAuthor', 'LastAuthor', 'AuthorListInDepartment', 
				'IsFirstSecondOrLastInDepartment',
				'Title', 'Volume', 'Issue', 'Pages', 'LangList', 'NlmUniqueID', 'ISSN', 
				'ESSN', 'PubTypeList', 'RecordStatus', 'PubStatus', 'ArticleIds', 'DOI', 'History', 
				'References', 'HasAbstract', 'PmcRefCount', 'FullJournalName', 'ELocationID', 'SO',]

d = {k: list() for k in dict_keys}

all_ids = set()

for this_author in tqdm(author_list_hus):
	handle = Entrez.esearch(db="pubmed", retmax=10, term=f"{this_author}[author] AND 2021/01/09:2024/01/09[dp]")
	record = Entrez.read(handle)

	idList = [k for k in record["IdList"] if k not in all_ids]
	all_ids.update(idList)

	idListStr = ",".join(idList)
	handle.close()

	if len(idList) == 0:
		continue

	sleep(0.34)

	handle = Entrez.esummary(db="pubmed", id=idListStr, retmode="xml")
	records = Entrez.parse(handle)
	for record in records:
		for k,v in record.items():
			if type(v) == type(list()):
				d[k].append(", ".join(v))
			else:
				d[k].append(v)

		current_author_list = record["AuthorList"]
		current_authors_at_hus = [k for k in current_author_list if k in author_list_hus]
		
		if len(current_authors_at_hus) == 0:
			current_authors_at_hus.append(this_author)

		d["AuthorListInDepartment"].append(", ".join(current_authors_at_hus))
		d["FirstAuthor"].append(current_author_list[0])

		if len(current_author_list) > 1:
			d["SecondAuthor"].append(current_author_list[1])
		else:
			d["SecondAuthor"].append("")

		if current_author_list[0] in current_authors_at_hus:
			d["IsFirstSecondOrLastInDepartment"].append(1)
		elif len(current_author_list) > 1 and current_author_list[1] in current_authors_at_hus:
			d["IsFirstSecondOrLastInDepartment"].append(1)
		elif len(current_author_list) > 1 and current_author_list[-1] in current_authors_at_hus:
			d["IsFirstSecondOrLastInDepartment"].append(1)
		else:
			d["IsFirstSecondOrLastInDepartment"].append(0)

	handle.close()
	sleep(0.34)

df = pd.DataFrame(d)
df.to_excel("output/output_from_researchfinder.xlsx", index=False)