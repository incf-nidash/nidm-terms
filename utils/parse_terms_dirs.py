import os,sys
from argparse import ArgumentParser
import pandas as pd
from os.path import join
import json
import shutil
from bids_validator  import BIDSValidator




def main(argv):

    parser = ArgumentParser(description='This script changes the type of the OpenNeuro JSONLD files')

    parser.add_argument('-input', dest='input', required=False, help="Path to OpenNeuro terms directory ")

    args = parser.parse_args()

    path = args.input

    #List the sub directories inside the root directory
    list_jsonld = os.listdir(args.input)


    # for each dataset
    for i in list_jsonld:
        if i == '.DS_Store':
            continue

        else:
            #set a path to that dataset in the jsonld directory
            ds_path = os.path.join(path,i)

            # check if that dataset exist in the jsonld directory
            ## if it does not exist print an error message
            if not os.path.exists(ds_path):
                print("ERROR!", i, "json sidecar file did not update")
            ## if yes start the updating process
            elif os.path.exists(ds_path):
                ## set path to the particupants.jsonld file in the jsonld directory
                part_file = os.path.join(ds_path, 'participants.jsonld')


                with open(part_file) as jld:
                    jld_file = json.load(jld)


                temp = {}

                for key, value in jld_file.items():
                    if key == '@context':
                        temp['@context'] = value

                        temp['@type'] = 'nidm:TermsCollection'

                    if key == 'terms':
                        temp['terms'] = value

                    elif key != '@context' and key != 'terms':
                        print('found a new property in:', part_file)



                with open (join(part_file),'w+') as outfile:
                    json.dump(temp,outfile,indent=2)


            #     # set path to phenotype directory and check if it has one
            #     pheno_check = os.path.join(ds_path,'phenotype')
            #
            #     # if the original dataset doesn't have phenotype directory skip
            #     if not os.path.exists(pheno_check):
            #         continue
            #
            #     # if phenotype directory exists in phenotype directory start the updating process for those jsonld files as well
            #     elif os.path.exists(pheno_check):
            #         print('Updating phenotype directory of', i)
            #
            #         # parse the phenotype directory
            #         for root, dirs, files in os.walk(pheno_check, topdown=True):
            #             # check sub directories T1 and T2 for jsonld files
            #             for dir in dirs:
            #
            #                 # set path to that sub directory
            #                 sub_dir = os.path.join(pheno_check,dir)
            #
            #                 # parse the subdirectory looking for jsonld files
            #                 for subroot, subdirs, json_files in os.walk(sub_dir):
            #                     # check each file
            #                     for FL in json_files:
            #                         #if that file ends with .jsonld
            #                         if FL.endswith('.jsonld'):
            #                             #extract the name of the file
            #                             FL_name = FL[:-7]
            #                             print('\t',FL,'is being changed...')
            #                             #set path to the file in the jsonld directory
            #                             jsonld_sub_path = os.path.join(sub_dir,FL)
            #
            #                             #check if the path exist
            #                             if os.path.exists(jsonld_sub_path):
            #
            #
            #                                 with open(part_file) as jld:
            #                                     jld_file1 = json.load(jld)
            #
            #
            #                                 temp1 = {}
            #
            #                                 for key1, value1 in jld_file1.items():
            #                                     if key1 == '@context':
            #                                         temp1['@context'] = value1
            #
            #                                         temp1['@type'] = 'nidm:TermsCollection'
            #
            #                                     if key1 == 'terms':
            #                                         temp1['terms'] = value1
            #
            #                                     elif key1 != '@context' and key1 != 'terms':
            #                                         print('found a new property in:', jsonld_sub_path)
            #
            #
            #
            #                                 with open (join(jsonld_sub_path),'w+') as outfile:
            #                                     json.dump(temp1,outfile,indent=2)
            #
            #                         else:
            #                             continue
            #
            #                     break
            #
            #
            #             # check for jsonld files in phenotype directory
            #             for file in files:
            #                 #if found
            #                 if file.endswith('.jsonld'):
            #                     #extract the file name
            #                     file_name = file[:-7]
            #                     print('\t',file,'is being changed...')
            #                     #set path to the file
            #                     pheno_file_path = os.path.join(pheno_check,file)
            #
            #                     #check if the path exist
            #                     if os.path.exists(pheno_file_path):
            #
            #
            #                         with open(part_file) as jld:
            #                             jld_file2 = json.load(jld)
            #
            #
            #                         temp2 = {}
            #
            #                         for key2, value2 in jld_file2.items():
            #                             if key2 == '@context':
            #                                 temp2['@context'] = value2
            #
            #                                 temp2['@type'] = 'nidm:TermsCollection'
            #
            #                             if key2 == 'terms':
            #                                 temp2['terms'] = value2
            #
            #                             elif key2 != '@context' and key2 != 'terms':
            #                                  print('found a new property in:', pheno_file_path)
            #
            #
            #
            #                         with open (join(pheno_file_path),'w+') as outfile:
            #                             json.dump(temp2,outfile,indent=2)
            #
            #
            #                 else:
            #                     continue
            #
            #
            # print('Validation is complete in', i)




if __name__ == "__main__":
   main(sys.argv[1:])

