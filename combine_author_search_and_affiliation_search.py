import pandas as pd
from pprint import pprint

affiliation = pd.read_excel("Keywords from PUBMED list.xlsx", engine='openpyxl')
authors = pd.read_excel("output/output_from_researchfinder_with_impactfactor.xlsx", engine='openpyxl')

title_affiliation = affiliation['PMID'].values
title_authors = authors['Id'].values

print(len(title_affiliation))
print(len(title_authors))

combined = set()

combined.update(title_affiliation)
combined.update(title_authors)

print(len(combined))

missing = [k for k in title_affiliation if k not in title_authors]

missing_articles = affiliation[affiliation['PMID'].isin(missing)]
missing_articles.to_excel("results/Publications from PUBMED missing in first list.xlsx")