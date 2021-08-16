
import os,sys
from os import system
from os.path import isfile,basename
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

# additional 'associatedWith' mappings from imports to strings
ASSOCIATED_WITH={
    "bids_import.ttl" : "BIDS",
    "crypto_import.ttl": "CRYPTO",
    "dc_import.ttl" : "DC",
    "dicom_import.ttl" : "DICOM",
    "iao_import.ttl" : "IAO",
    "nfo_import.ttl" : "NFO",
    "obi_import.ttl" : "OBI",
    "ontoneurolog_instruments_import.ttl" : "ONTONEUROLOG",
    "pato_import.ttl" : "PATO",
    "prov-o" : "PROV",
    "prv_import.ttl" : "PRV",
    "sio_import.ttl" : "SIO"
}


def main(argv):
    parser = ArgumentParser(description='This program will load an OWL ontology/terminology file and create separate'
                                        'JSON-LD NIDM-Terms compliant files for each term')

    parser.add_argument('-owl', dest='owl_file', required=True,nargs='+', help="Comma separated list of "
                            "OWL files to convert.")
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
    for file in args.owl_file:
        g=Graph()
        g.parse(file.rstrip(","),format="turtle")

        # loop through OWL AnnotationProperties
        for so in g.subject_objects(predicate=RDF.type):
            #print(so)
            # create empty document dictionary
            doc={}
            # add type as schema.org/DefinedTerm
            doc['@type'] = []
            doc['@type'].append(NIDM+'CommonDataElement')

            # add associated with property
            doc[context['@context']['associatedWith']['@id']] = []
            doc[context['@context']['associatedWith']['@id']].append('NIDM')
            # if we have an additional 'associatedWith' string to add from a known import
            # add it
            if basename(file).rstrip(",") in ASSOCIATED_WITH.keys():
                doc[context['@context']['associatedWith']['@id']].append(ASSOCIATED_WITH[basename(file).rstrip(",")])
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
                elif (tuples[0] == OBO["IAO_0000115"]) or (tuples[0] == DCT["description"]) :
                    doc[context['@context']['description']] = tuples[1]
                elif tuples[0] == OWL["sameAs"]:
                    doc[context['@context']['sameAs']['@id']] = tuples[1]
                elif tuples[0] == OWL["closeMatch"]:
                    doc[context['@context']['closeMatch']] = tuples[1]
                elif tuples[0] == OBO["IAO_0000116"]:
                    if context['@context']['comment']['@id'] in doc:
                        doc[context['@context']['comment']['@id']].append(tuples[1])
                    else:
                        doc[context['@context']['comment']['@id']] = []
                        doc[context['@context']['comment']['@id']].append(str(tuples[1]))
                elif tuples[0] == RDFS["subClassOf"]:
                    doc[context['@context']['supertypeCDEs']['@id']] = tuples[1]
                elif tuples[0] == RDFS["comment"]:
                    if context['@context']['comment']['@id'] in doc:
                        doc[context['@context']['comment']['@id']].append(str(tuples[1]))
                    else:
                        doc[context['@context']['comment']['@id']] = []
                        doc[context['@context']['comment']['@id']].append(str(tuples[1]))
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
            if "http://uri.interlex.org/ilx_0770184" in compacted.keys():
                compacted['supertypeCDEs'] = \
                    compacted['http://uri.interlex.org/ilx_0770184']
                del compacted['http://uri.interlex.org/ilx_0770184']
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

            # Added by DBK to include a rdfs:label if one doesn't exist for term
            if 'label' not in compacted.keys():
                if 'candidateTerms' in compacted.keys():
                    compacted['label'] = \
                        compacted['candidateTerms']
                else:
                    # just parse subject of triple and use the local part as the label
                    url, fragment = urldefrag(so[0])
                    compacted['label'] = fragment

            ##Added by nqueder
            # prevent the file name from having spaces and/or commas
            label = compacted['label']
            label = label.replace(" ","")
            label = label.replace(",","")
            label = label.replace("(","")
            label = label.replace(")","")
            label = label.replace("/","")
            label = label.replace("'","")
            print(label)

            #compacted['associatedWith'] = "NIDM"
            with open (join(args.output_dir,label+".jsonld"),'w') as outfile:
                json.dump(compacted,outfile,indent=2)

    # Added code to now combine the separate json-ld files into a single file
    output_dir = os.path.split(args.output_dir)[0]
    # if a single-file jsonld file already exists than add these terms to it else create a new one
    if isfile(join(output_dir,basename(args.output_dir) + ".jsonld")):
        cmd = "python " + join(sys.path[0],"combinejsonld.py") + " -inputDir " + args.output_dir + " -outputDir " + \
            join(output_dir,basename(args.output_dir) + ".jsonld") + " -jsonld " + \
            join(output_dir, basename(args.output_dir) + ".jsonld")
    else:
        cmd = "python " + join(sys.path[0], "combinejsonld.py") + " -inputDir " + args.output_dir + " -outputDir " + \
              join(output_dir, basename(args.output_dir) + ".jsonld")

    print(cmd)
    system(cmd)




if __name__ == "__main__":
   main(sys.argv[1:])