
import os,sys
from os import system
from argparse import ArgumentParser
import pandas as pd
from rdflib import Graph,util,Namespace, Literal,RDFS,RDF, URIRef
from pyld import jsonld
from os.path import join
import json
from urllib.parse import urlparse
import tempfile
import urllib.request as ur
from urllib.parse import urldefrag


CONTEXT = "https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld"
# set up basic Namespaces to use
OWL = Namespace("http://www.w3.org/2002/07/owl#")
NIDM = Namespace("http://purl.org/nidash/nidm#")
SKOS = Namespace("https://www.w3.org/TR/2009/REC-skos-reference-20090818#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
DCT = Namespace("http://purl.org/dc/terms/")


def main(argv):
    parser = ArgumentParser(description='This program will load an OWL ontology/terminology file and create separate'
                                        'JSON-LD NIDM-Terms compliant files for each term')

    parser.add_argument('-owl', dest='owl_file', required=True, help="Path to XLS file to convert")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
    parser.add_argument('-context', dest='context', required=False, help="URL to context file. If not supplied then "
                                "standard NIDM-Terms location will be used "
                                "(https://github.com/NIDM-Terms/terms/blob/master/context/cde_context.jsonld)")
    args = parser.parse_args()


    # load context file
    if args.context is None:
        #try to open the url and get the pointed to file
        try:
            #open url and get file
            opener = ur.urlopen(CONTEXT)
            # write temporary file to disk and use for stats
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(opener.read())
            temp.close()
            context_file = temp.name
        except:
            print("ERROR! Can't open url: %s" %args.context)
            exit()
    else:
        context_file = args.context

    with open(context_file) as context_data:
            context = json.load(context_data)

    # load OWL file
    g=Graph()
    g.parse(args.owl_file,format="turtle")

    # loop through OWL AnnotationProperties
    for so in g.subject_objects(predicate=RDF.type):

        # create empty document dictionary
        doc={}
        # add type as schema.org/DefinedTerm
        doc['@type'] = []
        #doc['@type'].append(context['@context']['DefinedTerm'])
        #store term as localpart of subject identifier
        url, fragment = urldefrag(so[0])
        if fragment == "":
            continue
        doc[context['@context']['candidateTerms']] = fragment
        #store namespace of subject identifier as provenance
        #doc[context['@context']['provenance']] = url
        # loop through tuples and store in JSON-LD document
        for tuples in g.predicate_objects(subject=so[0]):
            if tuples[0] == RDFS["label"]:
                doc[context['@context']['label']] = tuples[1]
            elif tuples[0] == OBO["IAO_0000115"]:
                doc[context['@context']['description']] = tuples[1]
            elif tuples[0] == OWL["sameAs"]:
                doc[context['@context']['sameAs']['@id']] = tuples[1]
            elif tuples[0] == OWL["closeMatch"]:
                doc[context['@context']['closeMatch']] = tuples[1]
            elif tuples[0] == OBO["IAO_0000116"]:
                if context['@context']['comment'] in doc:
                    doc[context['@context']['comment']].append(tuples[1])
                else:
                    doc[context['@context']['comment']] = []
                    doc[context['@context']['comment']].append(str(tuples[1]))
            elif tuples[0] == RDFS["subClassOf"]:
                doc[context['@context']['supertypeCDEs']['@id']] = tuples[1]
            elif tuples[0] == RDFS["comment"]:
                if context['@context']['comment'] in doc:
                    doc[context['@context']['comment']].append(str(tuples[1]))
                else:
                    doc[context['@context']['comment']] = []
                    doc[context['@context']['comment']].append(str(tuples[1]))
            elif tuples[0] == RDF["type"]:
                doc['@type'].append(str(tuples[1]))

        # save JSON-LD file
        if args.context is None:
            compacted = jsonld.compact(doc,CONTEXT)
        else:
            compacted = jsonld.compact(doc,args.context)

        # this stuff added because pyld compaction function doesn't seem to replace some of the keys with
        # the ones from the context
        if "nidm:candidateTerms" in compacted.keys():
            compacted['candidateTerms'] = \
                compacted['nidm:candidateTerms']
            del compacted['nidm:candidateTerms']
        if "rdfs:label" in compacted.keys():
            compacted['label'] = \
                compacted['rdfs:label']
            del compacted['rdfs:label']
        if 'responseOptions' in compacted.keys():
            compacted['responseOptions']['choices'] = \
                compacted['responseOptions']['schema:itemListElement']
            del compacted['responseOptions']['schema:itemListElement']
            # for each item in the choices list
            delete_indices = []
            for index, entry in enumerate(compacted['responseOptions']['choices']):
                # choices are list of dictionaries so for each dictionary
                for entry_key in entry.keys():
                    if entry_key == 'schema:value':
                        compacted['responseOptions']['choices'].append({'value':
                            compacted['responseOptions']['choices'][index]['schema:value']})
                        delete_indices.append(index)
            for index in sorted(delete_indices, reverse=True):
                del compacted['responseOptions']['choices'][index]


        with open (join(args.output_dir,doc[context['@context']['candidateTerms']] +".jsonld"),'w') as outfile:
            json.dump(compacted,outfile,indent=2)

    # Added code to now combine the separate json-ld files into a single file
    output_dir = os.path.split(args.output_dir)[0]
    cmd = "python " + join(sys.path[0],"combinebidsjsonld.py") + " -inputDir " + args.output_dir + " -outputDir " + \
        join(output_dir,"NIDM_Terms.jsonld") + " -association \"NIDM\""
    print(cmd)
    system(cmd)




if __name__ == "__main__":
   main(sys.argv[1:])