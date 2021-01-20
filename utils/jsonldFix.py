import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
import shutil
import tempfile
import urllib.request as ur
from urllib.parse import urlparse
import numpy as np
from rdflib.namespace import split_uri
import requests




def main(argv):
    parser = ArgumentParser(description='This script fixes the single bids json file. producing properly formatted jsonld')

    parser.add_argument('-input', dest='input', required=True, help="single bids jsonld file")
    parser.add_argument('-output', dest='output_dir', required=True, help="output directory ")
    parser.add_argument('-context', dest='cnt', required=True, help="path to the context file")

    args = parser.parse_args()

    #set output directory
    output = args.output_dir

    url = 'https://raw.githubusercontent.com/nqueder/terms/master/context/cde_context.jsonld'

    if url is not False:

        #try to open the url and get the pointed to file
        try:
            #open url and get file
            opener = ur.urlopen(url)
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


    old = args.input

    # read the bids json file
    with open(old) as j:
        old_json = json.load(j)

    temp_list = []
    temp_dict = {}
    for key,value in old_json.items():

        single_term = {}
        for k,v in value.items():

            single_term['@type'] = context['@context']['DataElement']
            single_term[context['@context']['label']] = value['label']

            if k == 'description':
                single_term[context['@context']['description']] = value['description']
            if k == 'comment':
                single_term[context['@context']['comment']] = value['comment']
            if k == 'sameAS':
                single_term[context['@context']['sameAs']] = value['sameAS']
            if k == 'wasDerivedFrom':
                single_term[context['@context']['wasDerivedFrom']['@id']] = value['wasDerivedFrom']
            if k == 'ilxId':
                single_term[context['@context']['ilxId']] = join('http://uri.interlex.org/'+value['ilxId'])
            if k == 'candidateTerms':
                single_term[context['@context']['candidateTerms']] = value['candidateTerms']
            if k == 'supertypeCDEs':
                single_term[context['@context']['supertypeCDEs']['@id']] = value['supertypeCDEs']
            if k == 'url':
                single_term[context['@context']['url']['@id']] = value['url']

            single_term[context['@context']['associatedWith']] = ["BIDS","NIDM"]


        temp_list.append(single_term)

    temp_dict['@context'] = url

    temp_dict['terms'] = temp_list

    compacted = jsonld.compact(temp_dict,args.cnt)


    print(compacted)

    with open ('BIDS_Terms.jsonld','w+') as outfile:
        json.dump(compacted,outfile,indent=2)






if __name__ == "__main__":
   main(sys.argv[1:])


