import os,sys
from argparse import ArgumentParser
from pyld import jsonld
from os.path import join
import json
import tempfile
import urllib.request as ur
import requests




def main(argv):
    parser = ArgumentParser(description='This script fixes the single bids json file. producing properly formatted jsonld')

    parser.add_argument('-inputDir', dest='inputDir', required=True, help="single bids jsonld file")
    parser.add_argument('-outputDir', dest='outputDir', required=True, help="output directory ")

    args = parser.parse_args()

    #set an input directory
    input = args.inputDir

    #set output directory
    output = args.outputDir

    url = 'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld'

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


    #set a main dictionary
    main_dict = {}

    #assing @context to the main dict
    main_dict['@context'] = 'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld'
    main_dict['terms'] = []

    for term in os.listdir(input):

        if term == '.jsonld':
            continue
        else:
            #set path to the term
            path = os.path.join(input,term)

            #open every term as a dictionary
            with open(path) as t:
                term_dict = json.load(t)

            #set an empty dictionary
            temp = {}

            #remove @context and fix @type
            for key, value in term_dict.items():


                

                if key == '@context':
                    continue
                if key == '@type':
                    temp['@type'] = value
                if key == 'description':
                    temp[context['@context']['description']] = value
                if key == 'label':
                    temp[context['@context']['label']] = value
                if key == 'comment':
                    temp[context['@context']['comment']] = value
                if key == 'sameAs':
                    temp[context['@context']['sameAs']['@id']] = value
                if key == 'wasDerivedFrom':
                    temp[context['@context']['wasDerivedFrom']['@id']] = value
                if key == 'ilxId':
                    temp[context['@context']['ilxId']] = join('http://uri.interlex.org/'+value)
                if key == 'candidateTerms':
                    temp[context['@context']['candidateTerms']] = value
                if key == 'supertypeCDEs':
                    temp[context['@context']['supertypeCDEs']['@id']] = value
                if key == 'subtypeCDEs':
                    temp[context['@context']['subtypeCDEs']['@id']] = value
                if key == 'url':
                    temp[context['@context']['url']['@id']] = value
                if key == 'closeMatch':
                    temp[context['@context']['closeMatch']] = value
                if key == 'ontologyConceptID':
                    temp[context['@context']['ontologyConceptID']] = value
                if key == 'relatedConcepts':
                    temp[context['@context']['relatedConcepts']] = value
                if key == 'derivative':
                    temp[context['@context']['derivative']] = value
                if key == 'citation':
                    temp[context['@context']['citation']] = value
                if key == 'isAbout':
                    temp[context['@context']['isAbout']['@id']] = value
                if key == 'isPartOf':
                    temp[context['@context']['isPartOf']['@id']] = value



                temp[context['@context']['associatedWith']] = ["BIDS","NIDM"]



            main_dict['terms'].append(temp)

    compacted = jsonld.compact(main_dict,'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld')


    print(compacted)


    with open (join(output,'BIDS_Terms.jsonld'),'w+') as outfile:
        json.dump(compacted,outfile,indent=2)






if __name__ == "__main__":
   main(sys.argv[1:])


