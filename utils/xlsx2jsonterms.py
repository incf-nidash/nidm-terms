
import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
from urllib.parse import urlparse
import tempfile
import urllib.request as ur
from urllib.parse import urlparse

def url_validator(url):
    '''
    Tests whether url is a valide url
    :param url: url to test
    :return: True for valid url else False
    '''
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])

    except:
        return False

def createCDEContext(filename=None):
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
        # "associatedTerms" : "http://www.w3.org/ns/prov#specializationOf",
        "unitCode" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#unitCode",
        "unitLabel" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#unitLabel",
        "valueType" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#valueType",
        "minimumValue" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#minimumValue",
        "maximumValue" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#maximumValue",
        "allowableValues" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#allowableValues",
        "provenance" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#provenance",
        "ontologyConceptID" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#ontologyConceptID",
        "subtypeCDEs" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#subtypeCDEs",
        "supertypeCDEs" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#supertypeCDEs",
        "relatedConcepts" : "https://docs.google.com/spreadsheets/d/1dZ48F8JKsD2IHp7oeC6xa_FvnFwaEBGEOn0V850OWJU/edit#gid=632728597#relatedConcepts",
        "levels" : "https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html"
    }

    # save context as filename
    if filename is not None:
        with open (filename,'w') as outfile:
                    json.dump(context,outfile,indent=2)

    return context

def main(argv):
    parser = ArgumentParser(description='This program will load in a custom Excel spreadsheet and create separate'
                                        'JSON files for each term in Column D, description in Column E, URL in'
                                        'Column F, and will add (as placeholder) columns A and B as isAbout.'
                                        'See https://docs.google.com/spreadsheets/d/1_hUJQRcMDIzWYTsVLDEoipTGrFHytXEaVBlrheVRlJA/edit')

    parser.add_argument('-xls', dest='xls_file', required=True, help="Path to XLS file to convert")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
    parser.add_argument('-context', dest='context', required=True, help="URL to context file")
    args = parser.parse_args()

    #open CSV file and load into
    df = pd.read_excel(args.xls_file)

    # here we're supporting amazon bucket-style file URLs where the expectation is the last parameter of the
    # see if we have a valid url
    url = url_validator(args.context)
    # if user supplied a url as a segfile
    if url is not False:

        #try to open the url and get the pointed to file
        try:
            #open url and get file
            opener = ur.urlopen(args.context)
            # write temporary file to disk and use for stats
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(opener.read())
            temp.close()
            context_file = temp.name
        except:
            print("ERROR! Can't open url: %s" %args.context)
            exit()

    # read in jsonld context
    with open(context_file) as context_data:
        context = json.load(context_data)
    # context = createCDEContext()
    doc = {}
    # loop through all rows and grab info if exists
    for (i,row) in df.iterrows():
        print("starting iteration...")
        print("processing term: %s" %row['BIDS_Term (Key)'])

        # column D "BIDS_Term (Key)" contains term label
        if pd.isnull(row['BIDS_Term (Key)']):
            continue
        else:
            # add type as schema.org/DefinedTerm
            doc['@type'] = context['@context']['DefinedTerm']
            doc[context['@context']['label']] = row['BIDS_Term (Key)']
            if not pd.isnull(row['BIDS_Definition (Value)']):
                print("\tFound BIDS_Definition")
                doc[context['@context']['description']] = str(row['BIDS_Definition (Value)'])
            if not pd.isnull(row['URL that provided the definitions']):
                try:
                    result = urlparse(row['URL that provided the definitions'])
                    print("\tFound URL that provided the definitions")
                    if bool(result.scheme):
                        doc[context['@context']['url']['@id']] = {"@id": row['URL that provided the definitions']}
                    else:
                        doc[context['@context']['comment']] = str(row['URL that provided the definitions'])
                except:
                    doc[context['@context']['comment']] = str(row['URL that provided the definitions'])
            if not pd.isnull(row['NIDM_Owl_Term']):
                print("\tFound NIDM_Owl_Term: %s" %row['NIDM_Owl_Term'] )
                if context['@context']['comment'] in doc:
                    doc[context['@context']['comment']] = str(doc[context['@context']['comment']]) + "\n" + str(row['NIDM_Owl_Term'])
                else:
                    doc[context['@context']['comment']] = str(row['NIDM_Owl_Term'])
            if not pd.isnull(row['NIDM_Term']):
                print("\tFound NIDM_Term")
                doc[context['@context']['isAbout']] = str(row['NIDM_Term'])
            #if not pd.isnull(row['InterLex']):
            #    doc[context['ilx_id']] = row['InterLex']
            if not pd.isnull(row['Candidate Terms']):
                print("\tFound Candidate Terms")
                doc[context['@context']['candidateTerms']] = str(row['Candidate Terms'])
            if not pd.isnull(row['Associated Term']):
                print("\tFound Associated Term")
                doc[context['@context']['relatedConcepts']] = str(row['Associated Term'])

            # placeholder for additional properties that need to be included in CDEs
            # doc[context['@context']["unitCode"]] = 'undefined'
            # doc[context['@context']["unitLabel"]] = 'undefined'
            # doc[context['@context']["valueType"]] = 'undefined'
            # doc[context['@context']["minimumValue"]] = 'undefined'
            # doc[context['@context']["maximumValue"]] = 'undefined'
            # doc[context['@context']["allowableValues"]] = 'undefined'
            # doc[context['@context']["provenance"]] = 'undefined'
            # doc[context['@context']["ontologyConceptID"]] = 'undefined'
            # doc[context['@context']["subtypeCDEs"]] = 'undefined'
            # doc[context['@context']["supertypeCDEs"]] = 'undefined'

            # write JSON file out
            compacted = jsonld.compact(doc,args.context)
            with open (join(args.output_dir,row['BIDS_Term (Key)'].replace("/","_")+".jsonld"),'w') as outfile:
                json.dump(compacted,outfile,indent=2)

            print("size of dict: %d" %sys.getsizeof(doc))
            doc.clear()


if __name__ == "__main__":
   main(sys.argv[1:])