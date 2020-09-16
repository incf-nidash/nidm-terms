import reproschema
from reproschema import cli, jsonldutils
import os, sys
import json
from pyld import jsonld
import rdflib as rl
from argparse import ArgumentParser
import tempfile



def main(argv):
    parser = ArgumentParser(description='This tool will convert a series of BIDS specification terms in JSONLD format to'
                                        'a single turtle file.')

    parser.add_argument('-b', dest='bids_terms', required=True, help="Path to the NIDM-Terms/terms directory")

    args = parser.parse_args()

    print('Preparing for iteration...')

    # set path to bids terms jsonld's
    path = args.bids_terms
    # listing the Jsonld's of all BIDS specification terms
    terms_path = os.path.join(path,'terms/BIDS_Terms')
    bids_terms = os.listdir(terms_path)


    # open a temporary text file
    temp = open('temp.txt', 'w')

    #find all jsonld files
    for i in bids_terms:
        # select only BIDS jsonld files
        if i.endswith('.jsonld'):

            # add each file to the path to access it
            pathtojsonld = os.path.join(terms_path, i)
            print(i)
            # load the jsonld file
            file = reproschema.jsonldutils.load_file(pathtojsonld)

            # the following two lines are copied from reproschema-py library
            # (https://github.com/ReproNim/reproschema-py/blob/3a09b62dd2084d03051746b7992031495773d1f0/reproschema/jsonldutils.py#L103)
            kwargs = {"algorithm": "URDNA2015", "format": "application/n-quads"}
            nt = jsonld.normalize(file, kwargs)
            # write triples in a temporary text file
            temp.write(nt)

    # close temp file
    temp.close()


    # convert n-triples to a turtle file
    g = rl.Graph()
    g.parse('temp.txt', format='nt')
    g.bind('rs', 'http://schema.repronim.org/')
    ...
    g.serialize("BIDS_Terms.ttl", format="turtle")

    # delete temp file
    os.remove('temp.txt')




if __name__ == "__main__":
   main(sys.argv[1:])
