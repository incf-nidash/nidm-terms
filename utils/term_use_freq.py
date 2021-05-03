import os,sys
from os.path import isdir,isfile
from os import system
from os.path import join
from argparse import ArgumentParser
import glob2
from pyld import jsonld
import json
from collections import OrderedDict
from operator import getitem
import urllib.request as url
from urllib.parse import urlparse
import tempfile
from cognitiveatlas.api import get_concept, get_disorder
from nidm.experiment.Utils import fuzzy_match_terms_from_cogatlas_json
from rapidfuzz import fuzz

INTERLEX_BASE_URL = "https://scicrunch.org/api/1/ilx/search/curie/ILX:"
CONTEXT = "https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld"
INTERLEX_URI_FRAG = "http://uri.interlex.org"
COGATLAS_URI_FRAG = "http://cognitiveatlas.org"
COGATLAS_TASK_URI_FRAG = "http://cognitiveatlas.org/task/json/"

def write_jsonld(doc,output_dir):
    """
    This function writes out the jsonld structure to filename (with path)
    :param doc: jsonld dictionary
    :param filename: output filename and path
    :return:
    """


    # save JSON-LD file
    compacted = jsonld.compact(doc, CONTEXT)

    # this stuff added because pyld compaction function doesn't seem to replace some of the keys with
    # the ones from the context
    if "rdfs:label" in compacted.keys():
        compacted['label'] = \
            compacted['rdfs:label']
        del compacted['rdfs:label']

    compacted['associatedWith'] = "NIDM"

    if 'label' not in compacted:
        print(compacted)
    try:
        #print("writing output jsonld file: %s" %compacted['label'])
        with open(join(output_dir,compacted['label'] + '.jsonld'), 'w') as outfile:
            json.dump(compacted, outfile, indent=2)
    except:
        print(doc)

def get_cogatlas_task_properties(concept_url, concept_label, context):
    """
    Cogatlas tasks are a special case and need to be handled via URL
    :param concept_url: url of task concept
    :param context: nidm-terms concept document
    :return: jsonld document with concept details
    """

    # set up jsonld document for selected properties
    doc = {}
    # add type as schema.org/DefinedTerm
    doc['@type'] = context['@context']['Concept']

    result = urlparse(concept_url)
    try:
        concept_id = result.path.split("trm_")[1]
        # set up cogatlas task URL
        task_url = COGATLAS_TASK_URI_FRAG + "trm_" + concept_id
    except:
        print("can't split on trm_ from cogatlas url: %s" %concept_url)
        print("trying tsk_ prefix")
        try:
            concept_id = result.path.split("tsk_")[1]
            # set up cogatlas task URL
            task_url = COGATLAS_TASK_URI_FRAG + "tsk_" + concept_id
        except:
            print("can't split on tsk_ from cogatlas url: %s" %concept_url)
            return


    # use url.requests to get info about concept
    with url.urlopen(task_url) as response:
        concept_properties = json.loads(response.read())

    for entry in concept_properties.keys():
        if entry == 'name':
            doc[context['@context']['label']] = concept_properties[entry]
        elif entry == 'definition_text':
            doc[context['@context']['description']] = concept_properties[entry]
        elif entry == 'event_stamp':
            doc[context['@context']['version']] = concept_properties[entry]


    doc[context['@context']['url']['@id']] = concept_url

    # DEBUG
    if context['@context']['label'] not in list(doc.keys()):
        print("get_cogatlas_task_properties")
        print("no information found for url: %s" % concept_url)
        print("adding basic information (URL, label)")
        doc[context['@context']['label']] = concept_label
        doc[context['@context']['url']['@id']] = concept_url
    elif context['@context']['url'] not in list(doc.keys()):
        doc[context['@context']['url']['@id']] = concept_url

    return doc

def get_cogatlas_properties(concept_id, context, cogatlas_concepts, cogatlas_disorders):
    """
    This function will return a json-ld document of selected properties from a cogatlas concept or disorder
    :param concept_id: Cogatlas concept ID
    :param context: NIDM-Terms concept file
    :param cogatlas_concepts: json document of cogatlas concepts
    :param cogatlas_disorders: json document of cogatlas disorders
    :return:
    """
    # set up jsonld document for selected properties
    doc = {}
    # add type as schema.org/DefinedTerm
    doc['@type'] = context['@context']['Concept']

    concept_found = False
    for entry in cogatlas_concepts.json:
        if entry['name'].lower() == concept_id['label'].lower():
            doc[context['@context']['label']] = entry['name']
            doc[context['@context']['description']] = entry['definition_text']
            doc[context['@context']['url']['@id']] = concept_id['@id']
            if 'event_stamp' in entry:
                doc[context['@context']['version']] = entry['event_stamp']
            elif 'def_event_stamp' in entry:
                doc[context['@context']['version']] = entry['def_event_stamp']
            concept_found = True
    if not concept_found:
        for entry in cogatlas_disorders.json:
            if entry['name'].lower() == concept_id['label'].lower():
                doc[context['@context']['label']] = entry['name']
                doc[context['@context']['description']] = entry['definition']
                doc[context['@context']['url']['@id']] = concept_id['@id']
                doc[context['@context']['version']] = entry['event_stamp']

    # Here we couldn't find this concept so we'll just store the label and url from our annotations
    if context['@context']['label'] not in list(doc.keys()):
        print("get_cogatlas_properties")
        print("no information found for url: %s" % concept_id)
        print("adding basic information (URL, label)")
        doc[context['@context']['label']] = concept_id['label']
        doc[context['@context']['url']['@id']] = concept_id['@id']
    elif context['@context']['url'] not in list(doc.keys()):
        doc[context['@context']['url']['@id']] = concept_id['@id']


    return doc


def get_interlex_concept_properties(concept_url,context):
    """
    This function will return a json-ld document of selected properties from a interlex concept
    :param concept_id: Interlex concept ID
    :param context: NIDM-Terms context file
    :return: json-ld dictionary of selected properties
    """

    try:
        api_key = os.environ['INTERLEX_API_KEY']
    except:
        print("Error getting your API key for InterLex.  Please set an environment variable \'INTERLEX_API_KEY\'"
              "with your API key from scicrunch.org and re-run")
        exit(1)

    # parse concept ID from concept_url
    #print(concept_url)
    result = urlparse(concept_url)
    concept_id = result.path.split("ilx_")[1]
    # use url.requests to get info about concept
    with url.urlopen(INTERLEX_BASE_URL+concept_id+"?key="+api_key) as response:
        concept_properties = json.loads(response.read())

    # set up jsonld document for selected properties
    doc = {}
    # add type as schema.org/DefinedTerm
    doc['@type'] = context['@context']['Concept']

    # mappings of InterLex properties to NIDM-Term properties
    for key in concept_properties['data']:
        if key == 'label':
            doc[context['@context']['label']] = concept_properties['data'][key]
        elif key == 'definition':
            doc[context['@context']['description']] = concept_properties['data'][key]
        elif key == 'url':
            doc[context['@context']['url']['@id']] = concept_url
        elif (key == 'comment') and (bool(concept_properties['data'][key])):
            doc[context['@context']['comment']] = concept_properties['data'][key]
        elif (key == 'version') and (bool(concept_properties['data'][key])):
            doc[context['@context']['version']] = concept_properties['data'][key]
        elif (key == 'superclasses' and (bool(concept_properties['data'][key]))):
            doc[context['@context']['supertypeCDEs']['@id']] = []
            for supertypes in concept_properties['data'][key]:
                doc[context['@context']['supertypeCDEs']['@id']].append(concept_url[:concept_url.rfind('/')]
                            +"/"+supertypes['ilx'])

    #     # Here we couldn't find this concept so we'll just store the label and url from our annotations
    if context['@context']['label'] not in list(doc.keys()):
        print("get_interlex_concept_properties")
        print("no label found: %s" % concept_url)
    elif context['@context']['url'] not in list(doc.keys()):
        doc[context['@context']['url']['@id']] = concept_url


    return doc



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

    parser.add_argument('-jsonld', dest='jsonld', nargs='+', default=[], required=True, help="space separated list"
                                                "of directories to evaluate for jsonld files.")
    parser.add_argument('-outfile', dest='outfile', required=True, help="Output file for markdown table, full path")
    parser.add_argument('-jsonld_output_dir', dest='jsonld_output_dir', required=True, help = "This is a directory"
                                "where we'll store the concept json-ld files using the NIDM-Terms properties")

    args = parser.parse_args()

    isAbout_terms = {}
    total_concept_count = 0

    # download context file for json-ld files of concepts used
    # try to open the url and get the pointed to file
    try:
        # open url and get file
        opener = url.urlopen(CONTEXT)
        # write temporary file to disk and use for stats
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(opener.read())
        temp.close()
        context_file = temp.name
    except:
        print("ERROR! Can't open url: %s" % CONTEXT)
        exit()
    # load downloaded context
    with open(context_file) as context_data:
            context = json.load(context_data)

    # Retrieve cognitive atlas concepts and disorders
    cogatlas_concepts = get_concept(silent=True)
    cogatlas_disorders = get_disorder(silent=True)

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

                                # add concept to dictionary
                                total_concept_count = add_to_dict(id, isabout_entry, isAbout_terms, total_concept_count)

                                if INTERLEX_URI_FRAG in isabout_entry['@id']:
                                    # for storing concept as json-ld file
                                    concept_jsonld = get_interlex_concept_properties(isabout_entry['@id'], context)
                                elif (COGATLAS_URI_FRAG in isabout_entry['@id']) and ("task" not in isabout_entry['@id']):
                                    concept_jsonld = get_cogatlas_properties(isabout_entry,context,
                                            cogatlas_concepts,cogatlas_disorders)
                                elif "task" in isabout_entry['@id']:
                                    concept_jsonld = get_cogatlas_task_properties(isabout_entry,context)

                                else:
                                    continue
                                # write concept jsonld file
                                write_jsonld(concept_jsonld, args.jsonld_output_dir)

                        # else it's a dictionary with a single isAbout entry
                        else:
                            total_concept_count = add_to_dict(id, json_tmp['terms'][term], isAbout_terms,
                                                              total_concept_count)
                            if INTERLEX_URI_FRAG in json_tmp['terms'][term]:
                                # for storing concept as json-ld file
                                concept_jsonld = get_interlex_concept_properties(json_tmp['terms'][term]['@id'], context)
                            elif COGATLAS_URI_FRAG in json_tmp['terms'][term]['@id'] and \
                                ("task" not in json_tmp['terms'][term]['@id']):
                                concept_jsonld = get_cogatlas_properties(json_tmp['terms'][term],context,
                                                                         cogatlas_concepts, cogatlas_disorders)
                            elif "task" in json_tmp['terms'][term]:
                                concept_jsonld = get_cogatlas_task_properties(json_tmp['terms'][term], context)

                            else:
                                continue
                            # write concept jsonld file
                            write_jsonld(concept_jsonld, args.jsonld_output_dir)


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
                                    if INTERLEX_URI_FRAG in isabout_entry['@id']:
                                        # for storing concept as json-ld file
                                        concept_jsonld = get_interlex_concept_properties(isabout_entry['@id'], context)
                                    elif COGATLAS_URI_FRAG in isabout_entry['@id'] and \
                                            ("task" not in isabout_entry['@id']):
                                        concept_jsonld = get_cogatlas_properties(isabout_entry,context,
                                                    cogatlas_concepts, cogatlas_disorders)
                                    elif "task" in isabout_entry['@id']:
                                        concept_jsonld = get_cogatlas_task_properties(isabout_entry['@id'],
                                                    isabout_entry['label'],context)

                                    else:
                                        continue
                                    # write concept jsonld file
                                    write_jsonld(concept_jsonld, args.jsonld_output_dir)

                            else:
                                total_concept_count = add_to_dict(id, term[property], isAbout_terms,
                                                                  total_concept_count)
                                if INTERLEX_URI_FRAG in term[property]['@id']:
                                    # for storing concept as json-ld file
                                    concept_jsonld = get_interlex_concept_properties(term[property]['@id'], context)
                                elif COGATLAS_URI_FRAG in term[property]['@id'] and \
                                            ("task" not in term[property]['@id']):
                                    concept_jsonld = get_cogatlas_properties(term[property],
                                        context,cogatlas_concepts, cogatlas_disorders)
                                elif "task" in term[property]['@id']:
                                    concept_jsonld = get_cogatlas_task_properties(term[property]['@id'],
                                                term[property]['label'], context)
                                else:
                                    continue
                                # write concept jsonld file
                                write_jsonld(concept_jsonld, args.jsonld_output_dir)

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


    # if a single-file jsonld file already exists than add these terms to it else create a new one
    output_dir = os.path.split(args.jsonld_output_dir)[0]
    if isfile(join(output_dir, "NIDM_Concepts.jsonld")):
        cmd = "python " + join(sys.path[0], "combinebidsjsonld.py") + " -inputDir " + args.jsonld_output_dir + " -outputDir " + \
              join(output_dir, "NIDM_Concepts.jsonld") + " -association \"NIDM\"" + " -jsonld " + \
              join(output_dir, "NIDM_Concepts.jsonld")
    else:
        cmd = "python " + join(sys.path[0], "combinebidsjsonld.py") + " -inputDir " + args.jsonld_output_dir + " -outputDir " + \
              join(output_dir, "NIDM_Concepts.jsonld") + " -association \"NIDM\""

    print(cmd)
    system(cmd)


if __name__ == "__main__":
   main(sys.argv[1:])
