import os,sys
from os.path import isdir,isfile
from os import system
from argparse import ArgumentParser
import glob2
from pyld import jsonld
import json
from collections import OrderedDict
from operator import getitem

def add_to_dict(id,isAbout_dict,isAbout_terms, total_concept_count):

    for id in isAbout_dict.keys():
        if id == '@id':
            concept = str(isAbout_dict[id])
            #
            #
            # ADDED TO ACCOUNT FOR BUG IN CONTEXT FILES WHICH IS BEING FIXED (2/18/21)
            #
            #
            if 'ilx_id' in concept:
                concept = str("http://uri.interlex.org/base/" + concept.split(':')[1])
            else:
                concept = isAbout_dict[id]

            #################################################################
            if  concept in isAbout_terms.keys():
                # increment counter for this concept
                isAbout_terms[concept]['count'] = isAbout_terms[concept]['count'] + 1
                # increment total counter for all concepts
                # total_concept_count = total_concept_count + 1
            else:
                # add this concept to the running concept freq dictionary
                isAbout_terms[concept] = {}
                # add the count key and set
                isAbout_terms[concept]['count'] = 1
                # increment total counter for all concepts
                total_concept_count = total_concept_count + 1

            if concept in isAbout_terms.keys():
                isAbout_terms[concept]['label'] = isAbout_dict['label']
    return total_concept_count

def main(argv):
    parser = ArgumentParser(description='This program will find all *.jsonld files in the list of input'
                                        'directories and compute the frequency of use of isAbout concepts. '
                                        'The frequency table will be exported as a markdown table for use in'
                                        'web documents or GitHub README markdown files. ')

    parser.add_argument('-jsonld', dest='jsonld', nargs='+', default=[], required=True, help="space separated list of directories"
                                                                                 "to evaluate for jsonld files.")
    parser.add_argument('-outfile', dest='outfile', required=True, help="Output file for markdown table, full path")

    args = parser.parse_args()

    isAbout_terms = {}
    total_concept_count = 0

    # for each input directory
    for direct in args.jsonld:
        # find *.jsonld files
        files = glob2.glob(direct + '/**/*.jsonld',recursive=True)
        # loop through each file and get isAbout terms
        for file in files:
            # read file with json
            # open the file as a dictionary
            print("opening file: %s" %file)
            with open(file) as dct:
                json_tmp = json.load(dct)

            if type(json_tmp['terms']) is dict:
                # for each key (term) in jsonld file, check for isAbout property
                for term in json_tmp['terms'].keys():
                    # expanded = jsonld.expand(json_tmp[term])
                    # for jsonld files with only a single term we have a simple dictionary where the term label isn't
                    # the highest-level key so we handle differently
                    if term == 'isAbout':
                        if isinstance(json_tmp['terms'][term], list):
                            # if not a dictionary then a list of dictionaries
                            for isabout_entry in json_tmp['terms'][term]['isAbout']:
                                total_concept_count = add_to_dict(id, isabout_entry, isAbout_terms, total_concept_count)
                        # else it's a dictionary with a single isAbout entry
                        else:
                            total_concept_count = add_to_dict(id, json_tmp['terms'][term], isAbout_terms,
                                                              total_concept_count)


            elif type(json_tmp['terms']) is list:
                for term in json_tmp['terms']:
                    # expanded = jsonld.expand(json_tmp[term])
                    # for jsonld files with only a single term we have a simple dictionary where the term label isn't
                    # the highest-level key so we handle differently
                    for property in term:
                        if property == 'isAbout':
                            # for each concept in isAbout property
                            if isinstance(term[property], list):
                                for isabout_entry in term[property]:
                                    total_concept_count = add_to_dict(id, isabout_entry, isAbout_terms,
                                                                      total_concept_count)

                            else:
                                total_concept_count = add_to_dict(id, term[property], isAbout_terms,
                                                                  total_concept_count)

    # open markdown txt file
    md_file = open(args.outfile, "w")
    ## Added by NQ to test GitHub Actions
    print('opening output file in', args.outfile)
    # set up header of table
    md_file.write("| concept URL | label | use frequency (%) |\n")
    md_file.write("| ----------- | ----- | ----------------- |\n")


    # now cycle through isAbout_terms dictionary and compute frequencies
    for key in isAbout_terms.keys():
        isAbout_terms[key]['freq'] = (isAbout_terms[key]['count'] / total_concept_count) * 100.0

    res = OrderedDict(sorted(isAbout_terms.items(),
                             key=lambda x: getitem(x[1], 'freq'),reverse=True))


    # write markdown table sorted
    for key in res.keys():
        # add to markdown table file
        md_file.write("| %s | %s | %f |\n" %(key,res[key]['label'], res[key]['freq']))

    ##Added by NQ to show that the code finished running
    print('File has been successfully written in', md_file)


    md_file.close()






if __name__ == "__main__":
   main(sys.argv[1:])
