import os,sys
from argparse import ArgumentParser
import pandas as pd
from os.path import join
import json
import shutil
from bids_validator  import BIDSValidator



# This program updates the original participants.json and phenotype.json with the annotated OpenNeuro BIDS terms jsonld representations
# in order to have BIDS compliant json sidecar file for each OpenNeuro dataset.

# It has two missions:
## 1- Parse through the participants.tsv terms for each dataset and update participants.json sidecar file
## 2- Parse the phenotype directory, if found, and updates/ creates a json sidecar file for each tsv file


def save_sidecar(i,NIDM_dict,output_dir):
    '''

    Saves a copy of participants.json to the output directory

    '''

    ds_dir = os.path.join(output_dir,i)
    if not os.path.exists(ds_dir):
        os.mkdir(ds_dir, mode=0o777)


    with open(join(ds_dir, 'participants' + '.json'), 'w+') as O:
        json.dump(NIDM_dict,O,indent=2)






def levels_parser(jsonld_read, dict, term):
    '''
    This function parses the levels property in the jsonld file and switch it from a list to a dictionary
    to follow BIDS specifications.

    :param jsonld_read: dictionary created based off of the jsonld file
    :param dict: dictionary which includes term as dict a key, and jsonld dictionary as value
    :param term: the term extracted from participants.tsv or phenotype.tsv

    :return:
    Dictionary as a value of the key levels in the updated file
    '''

    # Open new dictionary
    levels_dict = {}

    # Extract the value of the key levels
    # (value would be a list with keys and values separated by a colon)
    for key in jsonld_read[term]:
        if key == 'levels':
            if isinstance(jsonld_read[term][key], list):
                for l in jsonld_read[term][key]:
                    split = l.split(':')
                    k = split[0]
                    v = split[1]
                    ## assign keys and values to levels dictionary
                    levels_dict[k] = v
                    ## assign levels dictionary to the json sidecar file dictionary
                    #dict[term]['levels'] = levels_dict
            elif isinstance(jsonld_read[term][key], str):
                split_str = jsonld_read[term][key].split(':')
                kk = split_str[0]
                vv = split_str[1]

                levels_dict[kk]=vv


    return levels_dict



def update_json(part_dict):

    '''
    takes jsonld dictionary and removes @context and @type for each term dict and update the term properties to be
    consistent with the BIDS specificantions

    '''


    # create a dictionary to map BIDS specification properties to our NIDM context properties
    nidmtobids = {'label':'LongName','description':'Description','levels':'Levels', 'hasUnit':'Units', 'url':'TermURL'}

    # open a new bids master dictionary
    bids_dict = {}


    # for each term in the jsonld dictionary
    for term in part_dict:

        # open a nested dictionary for that term
        bids_dict[term] = {}

        # parse through the keys and values of that term
        for key, val in part_dict[term].items():
            # exclude @context
            if key == '@context':
                continue
            # exclude @type
            if key == '@type':
                continue
            # update key description and add the appropriate value
            if key == 'description':
                bids_dict[term]['Description'] = part_dict[term]['description']
            # update key label and add the appropriate value
            if key == 'label':
                bids_dict[term]['LongName'] = part_dict[term]['label']
            # update key levels and add the appropriate value
            if key == 'levels':
                bids_dict[term]['Levels'] = levels_parser(part_dict,bids_dict,term)
            # update key hasunit and add the appropriate value
            if key == 'hasUnit':
                bids_dict[term]['Units'] = part_dict[term]['hasUnit']
            # update key schema:url and add the appropriate value
            if key == 'schema:url':
                bids_dict[term]['TermURL'] = part_dict[term]['schema:url']
            # update key derivative and add the appropriate value
            if key == 'derivative':
                bids_dict[term]['Derivative'] = part_dict[term]['derivative']
            # update key min value and add the appropriate value
            if key == 'minimumValue':
                bids_dict[term]['MinValue'] = part_dict[term]['minimumValue']
            # update key max value and add the appropriate value
            if key == 'maximumValue':
                bids_dict[term]['MaxValue'] = part_dict[term]['maximumValue']
            # add isAbout and its appropriate value
            if key == 'isAbout':
                bids_dict[term]['isAbout'] = {}
                bids_dict[term]['isAbout'] = part_dict[term]['isAbout']
            # add isPartOF and its appropriate value
            if key == 'isPartOf':
                bids_dict[term]['isPartOf'] = part_dict[term]['isPartOf']
            # add valueType and its appropriate value
            if key == 'valueType':
                bids_dict[term]['valueType'] = part_dict[term]['valueType']
            # add source_variable and its appropriate value
            if key == 'source_variable':
                bids_dict[term]['source_variable'] = part_dict[term]['source_variable']
            # add allowable value and its appropriate value
            if key == 'allowableValues':
                bids_dict[term]['allowableValues'] = part_dict[term]['allowableValues']


    return bids_dict


def main(argv):

    parser = ArgumentParser(description='This program updates the original participants.json and phenotype.json with the'
                                        'annotated OpenNeuro BIDS terms jsonld representations in order to have BIDS '
                                        'compliant json sidecar file for each OpenNeuro dataset.'

                                        'The program also saves a copy of each json sidecar file organized for each dataset in an'
                                        'output directory')

    parser.add_argument('-jsonld', dest='jsonld', required=True, help="Path to OpenNeuro jsonld directory")
    parser.add_argument('-ds_dir', dest='ds_dir', required=True, help="Path to OpenNeuro datasets directory")
    parser.add_argument('-out', dest='output_dir', required=True, help='Path to output directory')

    args = parser.parse_args()


    list_jsonld = os.listdir(args.jsonld)
    path_jsonld = args.jsonld


    #list ds ID's inside the given directory and set path to both the OpenNeuro dataset directory and to jsonld directory
    dsid = os.listdir(args.ds_dir)
    output = os.path.join(args.output_dir,'OpenNeuro_BIDS_json_sidecar')
    if not os.path.exists(output):
        os.mkdir(output)

    # for each dataset in the original openneuro dataset directory
    for i in dsid:
        #get the dataet number
        ds_num = i[2:]
        #set a path to that dataset in the jsonld directory
        check_path=os.path.join(path_jsonld,ds_num)

        # check if that dataset exist in the jsonld directory
        ## if it does not exist print an error message
        if not os.path.exists(check_path):
            print("ERROR!", i, "json sidecar file did not update")
        ## if yes start the updating process
        elif os.path.exists(check_path):
            ## set path to the particupants.jsonld file in the jsonld directory
            part_file = os.path.join(check_path,'participants.jsonld')

            # open the file as a dictionary
            with open (part_file) as dict:
                part_dict = json.load(dict)

            print("converting particicpants.jsonld to participants.json for", i)

            # call update json to convert from jsonld to BIDS compliant dictionary
            bids_dict = update_json(part_dict)
            # save the the dictionary as a json file in the appropriate output directory
            save_sidecar(i,bids_dict,output)


            # set path to phenotype directory and check if it has one
            pheno_check = os.path.join(check_path,'phenotype')

            # if the original dataset doesn't have phenotype directory skip
            if not os.path.exists(pheno_check):
                continue

            # if phenotype directory exists in phenotype directory start the updating process for those jsonld files as well
            elif os.path.exists(pheno_check):
                print('Updating phenotype directory of', i)
                #create a phenotype directory in the appropriate dataset
                path_to_new_ds = os.path.join(output,i)
                out_pheno = os.path.join(path_to_new_ds,'phenotype')
                if os.path.exists(out_pheno):
                    shutil.rmtree(out_pheno)
                os.mkdir(out_pheno)

                # parse the phenotype directory
                for root, dirs, files in os.walk(pheno_check, topdown=True):
                    # check sub directories T1 and T2 for jsonld files
                    for dir in dirs:

                        # set path to that sub directory
                        sub_dir = os.path.join(pheno_check,dir)
                        #create an equivalent subdirectory in the output directory
                        out_subdir = os.path.join(out_pheno,dir)
                        if os.path.exists(out_subdir):
                            shutil.rmtree(out_subdir)
                        os.mkdir(out_subdir)
                        # parse the subdirectory looking for jsonld files
                        for subroot, subdirs, json_files in os.walk(sub_dir):
                            # check each file
                            for FL in json_files:
                                #if that file ends with .jsonld
                                if FL.endswith('.jsonld'):
                                    #extract the name of the file
                                    FL_name = FL[:-7]
                                    print('\t',FL,'is updating...')
                                    #set path to the file in the jsonld directory
                                    jsonld_sub_path = os.path.join(sub_dir,FL)

                                    #open the file as a dictionary
                                    with open (jsonld_sub_path) as dd:
                                        sub_pheno_dict = json.load(dd)

                                    # call update json to convert from jsonld to BIDS compliant dictionary
                                    phenotype_dict = update_json(sub_pheno_dict)

                                    # save file in an equivalent directory in the output file
                                    with open(join(out_subdir, FL_name + '.json'), 'w+') as O:
                                        json.dump(phenotype_dict,O,indent=2)

                                else:
                                    continue

                            break


                    # check for jsonld files in phenotype directory
                    for file in files:
                        #if found
                        if file.endswith('.jsonld'):
                            #extract the file name
                            file_name = file[:-7]
                            print('\t',file,'is updating...')
                            #set path to the file
                            pheno_file_path = os.path.join(pheno_check,file)

                            #check if the path exist
                            if os.path.exists(pheno_file_path):

                                #open file as a dictionary
                                with open (pheno_file_path) as dictionary:
                                    pheno_dict = json.load(dictionary)

                                # call update json to convert from jsonld to BIDS compliant dictionary
                                ph_dict = update_json(pheno_dict)

                                # save file in an equivalent directory in the output file
                                with open(join(out_pheno,file_name + '.json'), 'w+') as r:
                                    json.dump(ph_dict,r,indent=2)

                        else:
                            continue


        print('conversion is complete in', i)




if __name__ == "__main__":
   main(sys.argv[1:])

