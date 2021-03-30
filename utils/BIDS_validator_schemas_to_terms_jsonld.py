import os,sys
from os.path import isdir,isfile,join
from os import system
from argparse import ArgumentParser
import glob2
from pyld import jsonld
import json

from urllib.parse import urlparse
import tempfile
import urllib.request as ur
from urllib.parse import urldefrag

context_url = ("https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld")



def create_jsonld(schema_file, context, outdir, common_file=None):
    '''
    This function will parse the BIDS schema document and convert the relevant properites to NIDM-Terms json-ld
    term definition file.
    :param schema_file: BIDS schema file loaded into json structure
    :param context: NIDM-Terms loaded json-ld context
    :param outdir: Directory to save NIDM-Terms json-ld file
    :param common_file: BIDS common_definitions.json loaded into a json structure. Useful because other BIDS schema
    files reference things in the common file.
    :return: None
    '''

    global context_url

    # loop through definitions keys and check whether a json-ld term definition exists in args.out else create one
    for key in schema_file['definitions']:
        # check if there exists a json-ld file in args.out for this key
        if not isfile(join(outdir, key + ".jsonld")):
            # create a new json-ld document for this term
            doc = {}
            # add basic information such as @type, term label, and association with BIDS project
            doc['@type'] = context['@context']['CommonDataElement']
            doc[context['@context']['label']] = key
            doc[context['@context']['associatedWith']] = 'BIDS'
            # add the rest of the properties
            doc = add_properties_from_schema(doc, context, schema_file['definitions'][key])
            # write out json-ld file for this term
            compacted = jsonld.compact(doc, context_url)
            # this stuff added because pyld compaction function doesn't seem to replace some of the keys with
            # the ones from the context
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
            with open(join(outdir, key.replace("/", "_") + ".jsonld"), 'w') as outfile:
                json.dump(compacted, outfile, indent=2)


def add_properties_from_schema(jsonld_doc,context,schema_term):
    '''
    This function will parse the properties in schema_dict
    and assign them to the correct NIDM-Terms properties
    :param jsonld_doc: dictionary to store NIDM-Terms style properties
    :param context: context dictionary for json-ld NIDM-Terms style properties
    :param schema_term: BIDS schema dictionary of current key to store as NIDM-Terms json-ld
    :return: jsonld document updated with properties of current schema term.
    '''

    bidsschema_properites = {

        'type': context['@context']['valueType'],
        'enum': context['@context']['responseOptions']['@id'],
        'minimum': context['@context']['minValue'],
        'maximum': context['@context']['maxValue']
    }
    bids_types_to_xsd_types = {
        'number': context['@context']['xsd']['@id'] + 'decimal',
        'integer': context['@context']['xsd']['@id'] + 'integer',
        'string': context['@context']['xsd']['@id'] + 'string',
        'object': context['@context']['xsd']['@id'] + 'complexType'
    }

    # cycle through the properties and use the lookup table to translate BIDS schema properties
    # to NIDM-Terms properties
    for property in schema_term.keys():
        # if this property is a key in the bidsschema_properites
        if property in bidsschema_properites:
            # select appropriate NIDM-Terms property via lookup and assign value from BIDS schema
            # if this is a value type then convert from BIDS to XSD types
            if (not (type(schema_term[property]) is list)) and (schema_term[property] in bids_types_to_xsd_types):
                jsonld_doc[bidsschema_properites[property]] = bids_types_to_xsd_types[schema_term[property]]
            # special case of enumerated responseOptions
            elif property == 'enum':


                jsonld_doc[bidsschema_properites[property]] = {}

                choices = []
                for item in schema_term[property]:
                    temp_dict = {}
                    temp_dict[context['@context']['value']] = item
                    choices.append(temp_dict.copy())

                levels = {}
                levels[context['@context']['choices']] = choices
                jsonld_doc[bidsschema_properites[property]] = levels


        # 'format' appears to modify types 'string' to indicate a URI
        elif property == 'format':
             if schema_term[property] == 'uri':
                 jsonld_doc[bidsschema_properites['type']] = 'xsd:anyURI'
        # these are special cases with no easy NIDM-Terms equivalent lookup
        elif property == 'anyOf':
            # WIP anyOf is a list of dictionaries so I guess we'll encode these as a list of valuetypes if key is 'type'?
            for subproperty, subvalue in enumerate(schema_term[property]):
                for item in subvalue.keys():
                    if item == 'type':
                        # if we haven't parsed a property like this before then add a list type
                        if bidsschema_properites[item] not in jsonld_doc:
                            jsonld_doc[bidsschema_properites[item]] = []
                            jsonld_doc[bidsschema_properites[item]].append(
                                bids_types_to_xsd_types[schema_term[property][subproperty][item]])
                        else:
                            jsonld_doc[bidsschema_properites[item]].append(
                                bids_types_to_xsd_types[schema_term[property][subproperty][item]])
                    elif item == "additionalProperties":
                        if type(schema_term[property][subproperty][item]) is dict:
                            for key in schema_term[property][subproperty][item].keys():
                                if bidsschema_properites[key] not in jsonld_doc:
                                    jsonld_doc[bidsschema_properites[key]] = []
                                    jsonld_doc[bidsschema_properites[key]].append(
                                        bids_types_to_xsd_types[schema_term[property][subproperty]
                                        ["additionalProperties"][key]])
                                elif bids_types_to_xsd_types[schema_term[property][subproperty] \
                                        ["additionalProperties"][key]] not in jsonld_doc[bidsschema_properites[key]]:
                                    jsonld_doc[bidsschema_properites[key]].append(
                                        bids_types_to_xsd_types[schema_term[property][subproperty]
                                        ["additionalProperties"][key]])

        # this property appears to be indicating the value can be a list of valueTypes
        # elif property == 'items':

    # before returning check if there's a description field and if not add one that's empty as placeholder for a
    # definition
    if context['@context']['description'] not in jsonld_doc:
        jsonld_doc[context['@context']['description']] = ""
    return jsonld_doc

def get_jsonld_term_context(url):
    '''
    This function downloads the latest context document from the NIDM-Terms repository
    :param url: URL to context file to load
    :return: context dictionary
    '''
    # access the jsonld url

    # if user supplied a url as a segfile
    if url is not False:

        # try to open the url and get the pointed to file
        try:
            # open url and get file
            opener = ur.urlopen(url)
            # write temporary file to disk and use for stats
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(opener.read())
            temp.close()
            context_file = temp.name
        except:
            print("ERROR! Can't open url: %s" % args.context)
            exit()

    # read in jsonld context
    with open(context_file) as context_data:
        context = json.load(context_data)

    return context

def main(argv):
    parser = ArgumentParser(description='This program will parse all BIDS validator schemas located at:'
                    'https://github.com/bids-standard/bids-validator/tree/master/bids-validator/validators/json/schemas'
                    'and add json-ld term description files to the output directory if they do not exist. ')

    parser.add_argument('-dir', dest='dir', required=True, help="Diretory containing BIDS schemas")
    parser.add_argument('-out', dest='out', required=True, help="Directory to store json-ld term definitions if they"
                            "do not already exist for the BIDS schema key.")

    args = parser.parse_args()

    #grab context file for json-ld term definitions
    context = get_jsonld_term_context(context_url)
    #with open ("/Users/dbkeator/Documents/Coding/terms/context/cde_context.jsonld") as fp:
    #    context = json.load(fp)
    #context_url = context
    # step 1: open json schema files, start with the common_definitions.json as they are referenced from some of
    # the other schemas so we'll treat common_definitions.json differently than the rest so we can reference...

    # collect a list of json files in the schemas directory
    files = glob2.glob(args.dir + '/**/*.json',recursive=True)

    # check if common_definitions.json is in the glob2 results and if so parse it first...
    if join(args.dir,"common_definitions.json") in files:

        with open(join(args.dir,"common_definitions.json"), "r") as fp:
            common_file = json.load(fp)

        create_jsonld(common_file, context, args.out)

    #for file in files:
        # now cycle through the other schema files...ones that aren't the "common_definitions.json" file.
    #    if not (file == join(args.dir,"common_definitions.json")):
    #        with open(join(args.dir, file), "r") as fp:
    #            schema_file = json.load(fp)

    #    create_jsonld(schema_file, context, args.out,common_file)


    else:
        print("Error: no common_definitions.json file found, some references from other schema documents"
              "may not be able to be de-referenced and thus not have the correct terms properties!")
        print("Please re-run with input directory containing at least the common_definitions.json schema")






if __name__ == "__main__":
   main(sys.argv[1:])
