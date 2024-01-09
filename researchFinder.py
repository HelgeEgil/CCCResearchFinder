from Bio import Entrez
from time import sleep
import pandas as pd
from tqdm import tqdm

with open("authorList.csv", "r", encoding='utf-8') as input_file:
	line = input_file.readlines()[0]
	author_list_hus = line.split(",")

Entrez.email = "helge.pettersen@helse-bergen.no"
Entrez.retmax = 10

dict_keys = ['Item', 'Id', 'PubDate', 'EPubDate', 'Source', 'AuthorList', 
				'LastAuthor', 'AuthorListInDepartment', 'Title', 'Volume', 'Issue', 'Pages', 
				'LangList', 'NlmUniqueID', 'ISSN', 
				'ESSN', 'PubTypeList', 'RecordStatus', 'PubStatus', 'ArticleIds', 'DOI', 'History', 
				'References', 'HasAbstract', 'PmcRefCount', 'FullJournalName', 'ELocationID', 'SO']

d = {k: list() for k in dict_keys}

for this_author in tqdm(author_list_hus):
	handle = Entrez.esearch(db="pubmed", retmax=10, term=f"{this_author}[author] AND 2021/01/09:2024/01/09[dp]")
	record = Entrez.read(handle)
	idList = record["IdList"]
	idListStr = ",".join(idList)
	handle.close()

	sleep(0.5)

	handle = Entrez.esummary(db="pubmed", id=idListStr, retmode="xml")
	try:
		records = Entrez.parse(handle)
		for record in records:
			for k,v in record.items():
				if type(v) == type(list()):
					d[k].append(", ".join(v))
				else:
					d[k].append(v)

			current_author_list = record["AuthorList"]
			current_authors_at_hus = list()
			for author in current_author_list:
				if author in author_list_hus:
					current_authors_at_hus.append(author)
			d["AuthorListInDepartment"].append(", ".join(current_authors_at_hus))
		handle.close()
	except:
		print(f"Could not find any publications from {author}")
		pass
	sleep(0.5)

df = pd.DataFrame(d)
df.to_excel("output.xlsx", index=False)