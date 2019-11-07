
import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
from urllib.parse import urlparse

def main(argv):
    parser = ArgumentParser(description='This program will load in a custom Excel spreadsheet and create separate'
                                        'JSON files for each term in Column D, description in Column E, URL in'
                                        'Column F, and will add (as placeholder) columns A and B as isAbout.'
                                        'See https://docs.google.com/spreadsheets/d/1_hUJQRcMDIzWYTsVLDEoipTGrFHytXEaVBlrheVRlJA/edit')

    parser.add_argument('-xls', dest='xls_file', required=True, help="Path to XLS file to convert")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
    args = parser.parse_args()

    #open CSV file and load into
    df = pd.read_excel(args.xls_file)

    #statically coded context for JSON terms
    context = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "comment": "http://www.w3.org/2000/01/rdf-schema#comment",
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "schema": "http://schema.org/",
        "description": "http://purl.org/dc/terms/description",
        "isAbout": "http://purl.org/dc/terms/isAbout",
        "url": {"@id": "http://schema.org/url", "@type": "@id"},
        #"ilx_id" : "http://uri.interlex.org/base/ilx_0382972",
        "candidateTerms" : "http://purl.org/nidash/nidm#candidateTerms",
        "associatedTerms" : "http://www.w3.org/ns/prov#specializationOf"


    }

    # loop through all rows and grab info if exists
    for (i,row) in df.iterrows():
        print("processingi term: %s" %row['BIDS_Term (Key)'])
        doc = {}
        # column D "BIDS_Term (Key)" contains term label
        if pd.isnull(row['BIDS_Term (Key)']):
            continue
        else:

            doc[context['label']] = row['BIDS_Term (Key)']
            if not pd.isnull(row['BIDS_Definition (Value)']):
                doc[context['description']] = row['BIDS_Definition (Value)']
            if not pd.isnull(row['URL that provided the definitions']):
                try:
                    result = urlparse(row['URL that provided the definitions'])
                    if bool(result.scheme):
                        doc[context['url']['@id']] = {"@id": row['URL that provided the definitions']}
                    else:
                        doc[context['comment']] = row['URL that provided the definitions']
                except:
                    doc[context['comment']] = row['URL that provided the definitions']
            if not pd.isnull(row['NIDM_Owl_Term']):
                if context['comment'] in doc:
                    doc[context['comment']] = doc[context['comment']] + "\n" + row['NIDM_Owl_Term']
                else:
                    doc[context['comment']] = row['NIDM_Owl_Term']
            if not pd.isnull(row['NIDM_Term']):
                doc[context['isAbout']] = row['NIDM_Term']
            #if not pd.isnull(row['InterLex']):
            #    doc[context['ilx_id']] = row['InterLex']
            if not pd.isnull(row['Candidate Terms']):
                doc[context['candidateTerms']] = row['Candidate Terms']
            if not pd.isnull(row['Associated Term']):
                doc[context['associatedTerms']] = row['Associated Term']


            # write JSON file out
            compacted = jsonld.compact(doc,context)
            with open (join(args.output_dir,row['BIDS_Term (Key)'].replace("/","_")+".jsonld"),'w') as outfile:
                json.dump(compacted,outfile,indent=2)

if __name__ == "__main__":
   main(sys.argv[1:])