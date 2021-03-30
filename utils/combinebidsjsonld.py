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
    parser.add_argument('-association', dest='association', required=False, default="BIDS", help="association"
                        "string to identify which terminology terms are associated with. Valid choices are"
                        "NIDM (default if parameter left out) or BIDS" )
    parser.add_argument('-jsonldFile', dest='jsonld', required=False, default=None, help =
                        "If an existing single-file jsonld is provided then new terms will be added"
                        "to it.")
    parser.add_argument('-outputDir', dest='outputDir', required=True, help="output directory + filename")

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

    # added by DBK to support adding to existing jsonld file
    if args.jsonld == None:
        #set a main dictionary
        main_dict = {}

        #assing @context to the main dict
        main_dict['@context'] = 'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld'
        main_dict['terms'] = []
    else:
        # load existing jsonld file
        with open(args.jsonld) as fp:
            main_dict = json.load(fp)

    for term in os.listdir(input):

        if (term == '.jsonld') or (os.path.splitext(term)[1] != ".jsonld"):
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
                elif key == '@type':
                    temp['@type'] = value
                elif key == 'description':
                    temp[context['@context']['description']] = value
                elif key == 'label':
                    temp[context['@context']['label']] = value
                elif key == 'comment':
                    temp[context['@context']['comment']] = value
                elif key == 'sameAs':
                    temp[context['@context']['sameAs']['@id']] = value
                elif key == 'wasDerivedFrom':
                    temp[context['@context']['wasDerivedFrom']['@id']] = value
                elif key == 'ilxId':
                    temp[context['@context']['ilxId']] = join('http://uri.interlex.org/'+value)
                elif key == 'candidateTerms':
                    temp[context['@context']['candidateTerms']] = value
                elif key == 'supertypeCDEs':
                    temp[context['@context']['supertypeCDEs']['@id']] = value
                elif key == 'subtypeCDEs':
                    temp[context['@context']['subtypeCDEs']['@id']] = value
                elif key == 'url':
                    temp[context['@context']['url']['@id']] = value
                elif key == 'closeMatch':
                    temp[context['@context']['closeMatch']] = value
                elif key == 'ontologyConceptID':
                    temp[context['@context']['ontologyConceptID']] = value
                elif key == 'relatedConcepts':
                    temp[context['@context']['relatedConcepts']] = value
                elif key == 'derivative':
                    temp[context['@context']['derivative']] = value
                elif key == 'citation':
                    temp[context['@context']['citation']] = value
                elif key == 'isAbout':
                    temp[context['@context']['isAbout']['@id']] = value
                elif key == 'isPartOf':
                    temp[context['@context']['isPartOf']['@id']] = value

                # Added by DBK to account for different associations
                if args.association == "BIDS":
                    temp[context['@context']['associatedWith']] = ["BIDS"]
                else:
                    temp[context['@context']['associatedWith']] = [args.association]




            main_dict['terms'].append(temp)

    compacted = jsonld.compact(main_dict,'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld')


    print(compacted)

    # modified by DBK so that output command line parameter contains filename to output
    with open (join(output),'a') as outfile:
        json.dump(compacted,outfile,indent=2)






if __name__ == "__main__":
   main(sys.argv[1:])


