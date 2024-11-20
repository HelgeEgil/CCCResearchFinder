import pandas as pd

df = pd.read_csv("data/pubmed_allHUS_2021-24_journal.csv")

title = df.Title.values

print("Analysing the PUBMED search term '(Haukeland University Hospital[affiliation] AND (2021:2024[pdat])) AND (Journal Article[Publication Type])\n")

keywords = ['cancer', 'oncology', 'onco', 'radiation', 'radiotherapy', 'RT',
			'tumor', 'malign', 'staging', 'metast', 'adjuvant', 'concurrent',
			'targeted therapy', 'immunotherapy', 'systemic treatment', 
			'cytostati', 'leukemi', 'carcinoma', 'cytoma', 'blastoma',
			'lymphoma', 'neoplasm', 'hodgkin', 'melanoma', 'mesothelioma',
			'sarcoma', 'glioma', 'cytoma', 'sezary', 'brachy', 'external beam',
			'proton therapy', 'photon therapy', 'vmat', 'imrt', 'intensity modulated',
			'proton computed tomography', 'tumour']

total = set()

for key in keywords:
	subset = [k for k in title if key in k.lower()]
	total.update(subset)
	print(f"The keyword {key} is contained in {len(subset)} of {len(title)} publications")


df_subset = df[df["Title"].isin(total)].reset_index()
print(df_subset)
df_subset.to_excel("results/Keywords from PUBMED list.xlsx")

print(f"In total {len(total)} publications of {len(title)} contained cancer-related keywords.")