import os,sys
from argparse import ArgumentParser
from os.path import join
import json



def main(argv):

    parser = ArgumentParser(description='This script updates BIDS specification terms with newly added properties')

    parser.add_argument('-in', dest='input', required=True, help="Path BIDS Specification terms directory")
    parser.add_argument('-out', dest='out', required=True, help='')

    args = parser.parse_args()


    path = args.input

    output_path = args.out


    terms_list = os.listdir(path)


    dict = {}

    for term in terms_list:
        term_path = os.path.join(path, term)
        print('Updating %s' % term)

        with open (term_path) as j:
            term_dict = json.load(j)

        for key, value in term_dict.items():

            if key != 'candidateTerms':
                if key == 'provenance':
                    continue

                else:
                    dict[key] = value

        dict['associatedWith'] = ['BIDS','NIDM']

            #if 'candidateTerms' in term_dict:
                #del term_dict['candidateTerms']


        with open(join(output_path,term), 'w+') as r:
            json.dump(dict,r,indent=2)




if __name__ == "__main__":
   main(sys.argv[1:])