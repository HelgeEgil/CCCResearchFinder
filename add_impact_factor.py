import pandas as pd
from pprint import pprint
import re
import openpyxl
from matplotlib import pyplot as plt
from thefuzz import fuzz
import numpy as np
import json

def firstInName(string):
	stringBuilder = ""
	for name in string.split(" "):
		stringBuilder += name[0]
	return stringBuilder

with open("data/author_list_from_hus.csv", "r", encoding='utf-8') as input_file:
	line = input_file.readlines()[0]
	authorList = line.split(",")

authorList = [k.lower() for k in authorList]

# not found elsewhere, this list was complied from the journals' official sites 
with open("data/manual_journals.json", "r") as input_file:
	manual_journals = json.load(input_file)

for k,v in manual_journals:
	if not v:
		manual_journals[k] = np.nan

def getListOfJournals() -> set:
	df = pd.read_excel("data/output_from_researchfinder.xlsx", engine="openpyxl")
	return df

def loadImpactFactor() -> dict:
	impactFactor = dict()

	with open("data/impact_factor.csv") as file:
		for line in file.readlines():
			parsed = line.split(";")
			num = parsed[2]
			idx = parsed[0]
			
			# Manual fixes in this file, parsing errors etc.
			if "P" in num:
				numfloat = float(num[1:])
			elif "S" in num and len(num)>2:
				numfloat = float(num[2:])
			elif "S" in num and len(num) == 2:
				numfloat = float(num[1:])
			elif "N" in num:
				numfloat = float(num[1:])
			elif "R" in num:
				numfloat = float(parsed[3])
			elif num == "":
				numfloat = float(parsed[3])
			elif parsed[0] == "5073":
				numfloat = 2.5
			elif parsed[0] == ' & C"':
				continue
			elif parsed[0] == "5271":
				numfloat = float(num[1:])
			elif parsed[0] == "5272":
				numfloat = 2.4
			elif parsed[0] == '2.4"':
				continue
			elif idx == "5846":
				numfloat = 2.1
			elif idx == "6002":
				numfloat = 2
			elif idx == "6073":
				numfloat = 2
			elif idx == "6534":
				numfloat = 1.8
			elif idx == "6609":
				numfloat = 1.7
			elif idx == "7012":
				numfloat = 1.6
			elif idx == ' E"':
				continue
			elif idx == "7393":
				numfloat = 1.4
			elif idx == '1.4"':
				continue
			elif idx == '8710':
				numfloat = 0.7
			elif idx == '9427':
				numfloat = 0.2
			elif idx == '9484':
				break
			else:
				numfloat = float(num)

			impactFactor[parsed[1].lower().strip()] = float(numfloat)

	return impactFactor

def matchJournalsToImpactFactor(df: pd.DataFrame) -> dict:

	journals = set(df.FullJournalName)

	impactFactor = loadImpactFactor()
	res = dict()
	yes = 0
	manual = 0
	fuzzy = 0

	for journal in journals:
		if journal.lower() in impactFactor:
			res[journal] = impactFactor[journal.lower()]
			yes += 1
		else:
			if journal in manual_journals:
				res[journal] = manual_journals[journal]
				manual += 1
			else:
				highestMatch, _ = fuzzyMatch(journal, impactFactor)
				fuzzy += 1
				if highestMatch:
					res[journal] = impactFactor[highestMatch]

	tot = yes + manual + fuzzy
	print("yes: ", yes/tot, "manual: ", manual/tot, "fuzzy: ", fuzzy/tot)
	return res

def fuzzyMatch(string: str, listOfStrings: list):
	bestScore = 0
	bestItem = None
	for item in listOfStrings:
		simScore = fuzz.ratio(string.lower(), item.lower())
		if simScore > bestScore:
			bestScore = simScore
			bestItem = item

	return bestItem, bestScore

def addImpactFactorToExcel(impactFactorMap):
	df["Impact Factor"] = df["FullJournalName"].map(impactFactorMap)
	df.to_excel("output/output_from_researchfinder_with_impactfactor.xlsx")

if __name__ == "__main__":
	df = getListOfJournals()
	impactFactorMap = matchJournalsToImpactFactor(df)
	addImpactFactorToExcel(impactFactorMap)