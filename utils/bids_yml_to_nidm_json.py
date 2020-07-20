#!/Users/vanerp/anaconda3/bin/python
# This code reads in a BIDS .yml file and writest out a barebone .json or .jsonld file 
# for the yml prefix (e.g., "anat" for anat.yml), and for all the suffixes in the .yml file
# based on the example below.

# example BOLD
#{
#  "@context": "https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld",
#  "@type": "http://www.w3.org/2002/07/owl#Class",
#  "description": "bold",
#  "candidateTerms": "BOLD",
#  "comment": "To be discussed",
#  "label": "BOLD",
#  "provenance": "http://purl.org/nidash/bids",
#  "supertypeCDEs": "http://purl.org/nidash/nidm#ImageContrastType",
#  "sameAs": "http://purl.org/nidash/nidm#BloodOxygenLevelDependent",
#  "ilx_id": "ilx_0739352"
#}

import yaml
import json
import os

input_yaml_file="anat.yml"

# get the file_name and file_extension such that it can be added to a list
file_name, file_extension = os.path.splitext(input_yaml_file)
#print(file_name)
#print(file_extension)

# put the file_name into a list
list1 = [ file_name ]

# read in the yaml file, an parse it
with open(input_yaml_file, 'r') as stream:
	out = yaml.safe_load(stream)
	#print(out)
	#print('New Try 2')
        # print out the first list of suffixes, there may be multiple in each bids .yml file
	print(out[0]['suffixes'])
        # add the .yml file name to the list of suffixes
	list = list1 +  out[0]['suffixes']
	print(list)
	#for i in out[0]['suffixes']:
	# create a bare bone .json file for each file_name and suffix based on an the existing .json file BOLD.json listed at the bottom of this file
	for i in list:
		print(i)
		data = {"@context": "", "@type": "", "description": i, "candidateTerms": i, "comment": "To be discussed", "label": i, "provenance": "", "supertypeCDEs": "", "SameAs": "", "ilx_id": "" }
		print(data)
		jstr = json.dumps(data, indent=2)
		print(jstr)
		json_out_file = i + ".json"
		print("Writing:", json_out_file)
		with open(json_out_file, "w") as write_file:
			json.dump(data, write_file, indent=2)
		write_file.close()


