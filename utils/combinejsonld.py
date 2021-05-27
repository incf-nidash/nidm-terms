import os,sys
from argparse import ArgumentParser
from pyld import jsonld
from os.path import join,isfile
import json
import tempfile
import urllib.request as ur
import requests

def responseOptions(temp,context,value):

    #a new dictionary to add responseOptions properties to
    resOp = {}

    choice = {}

    for k, v in value:

        if k == 'valueType':
            resOp[context['@context']['valueType']] = v
        if k == 'datumType':
            resOp[context['@context']['datumType']] = v
        if k == 'unitCode':
            resOp[context['@context']['unitCode']] = v
        if k == 'minValue':
            resOp[context['@context']['minValue']] = v
        if k == 'maxValue':
            resOp[context['@context']['maxValue']] = v
        if k == 'allowableValues':
            resOp[context['@context']['allowableValues']] = v
        if k == 'choices':
            ##parse choices object if it's a single dictionary or if it's an array
            if isinstance(v,dict):
                for choicesKey, choicesVal in v:
                    if choicesKey == 'name':
                        choice[context['@context']['name']] = choicesVal
                    elif choicesKey == 'value':
                        choice[context['@context']['value']] = choicesVal

                resOp[context['@context']['choices']] = choice

            elif isinstance(v,list):
                for obj in v:
                    for choicesK, choicesV in obj:
                        if choicesK == 'name':
                            choice[context['@context']['name']] = choicesV
                        elif choicesK == 'value':
                            choice[context['@context']['value']] = choicesV

                        resOp[context['@context']['choices']] = choice

                        choice = {}

    temp[context['@context']['responseOptions']['@id']] = resOp

    return temp


def main(argv):
    parser = ArgumentParser(description='This script fixes the single bids json file. producing properly formatted jsonld')

    parser.add_argument('-input', dest='input', required=True, nargs='+', help="space separate list of directories to "
                                            "find jsonld files to combine")
    parser.add_argument('-type', dest='type', nargs='+', required=False, default=None, help="optional types to add to each"
                                                "term as a space separated list of urls "
                                            "( e.g. http://purl.org/nidash/nidm#PersonalDataElement or "
                                            "  http://purl.org/nidash/nidm#CommonDataElement or "
                                            " http://purl.org/nidash/nidm#Concept")

    parser.add_argument('-output', dest='output', required=True, help="output directory + filename. If"
                                            "jsonld file already exists, new terms will be added to it.")

    args = parser.parse_args()


    #set output directory
    output = args.output

    #if jsonld is provided set state to 1 if it's not provided set state to 0
    state = ''

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
    # if not isfile(output):
    #     #set a main dictionary
    #     main_dict = {}
    #
    #     #assing @context to the main dict
    #     main_dict['@context'] = 'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld'
    #     main_dict['terms'] = []
    #     #state = 0
    # else:
    # # load existing jsonld file
    #     with open(output) as fp:
    #         main_dict = json.load(fp)
    #     #state = 1


    #set a main dictionary
    main_dict = {}

    #assing @context to the main dict
    main_dict['@context'] = 'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld'
    main_dict['terms'] = []


    for input in args.input:

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
                        # add Nidm-Terms type if user selects
                        if args.type is not None:
                            # user may have added multiple types
                            for eachtype in args.type:
                                if '@type' in temp.keys():
                                    temp['@type'].append(eachtype)
                                else:
                                    temp['@type'] = []
                                    temp['@type'].append(eachtype)

                        if isinstance(value,list):
                            temp['@type'] = value
                        else:
                            temp['@type'] = value
                    elif key == 'description':
                        temp[context['@context']['description']] = value
                    elif key == 'label':
                        temp[context['@context']['label']] = value
                    elif key == 'sourceVariable':
                        temp[context['@context']['sourceVariable']] = value
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
                        temp[context['@context']['relatedConcepts']['@id']] = value
                    elif key == 'derivative':
                        temp[context['@context']['derivative']] = value
                    elif key == 'citation':
                        temp[context['@context']['citation']] = value
                    elif key == 'isAbout':
                        temp[context['@context']['isAbout']['@id']] = value
                    elif key == 'isPartOf':
                        temp[context['@context']['isPartOf']['@id']] = value
                    elif key == 'responseOptions':
                        temp[context['@context']['responseOptions']['@id']] = value
                    elif key == 'responseOptions':
                        responseOptions(temp,context,value)
                    elif key == 'associatedWith':
                        temp[context['@context']['associatedWith']['@id']] = value

                    # Added by DBK to account for different associations
                    #if args.association == "BIDS":
                    #    temp[context['@context']['associatedWith']] = ["BIDS"]
                    #else:
                    #    temp[context['@context']['associatedWith']] = [args.association]




                main_dict['terms'].append(temp)

    compacted = jsonld.compact(main_dict,'https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld')


    # #Added by Nqueder
    for d in compacted['terms']:
        if 'http://schema.org/url' in d:
            d['url'] = d['http://schema.org/url']
            del d['http://schema.org/url']
        if 'http://uri.interlex.org/ilx_0770184' in d:
            d['supertypeCDEs'] = d['http://uri.interlex.org/ilx_0770184']
            del d['http://uri.interlex.org/ilx_0770184']
        if 'owl:sameAs' in d:
            d['sameAs'] = d['owl:sameAs']
            del d['owl:sameAs']


    print('single jsonld file has been successfully created in', output)

    ## Added my Nazek Queder
    # if jsonld is provided modify and save in the same file else rewrite the file
    #if state == 1:
    #    # modified by DBK so that output command line parameter contains filename to output
    #    with open (join(args.jsonld),'a') as outfile:
    #
    #        json.dump(compacted,outfile,indent=2)

    #elif state == 0:
    with open (join(output),'w+') as outfile:
        json.dump(compacted,outfile,indent=2)



if __name__ == "__main__":
   main(sys.argv[1:])


