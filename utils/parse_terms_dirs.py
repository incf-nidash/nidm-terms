import os,sys
from argparse import ArgumentParser
import pandas as pd
from os.path import join
import json
import shutil
from bids_validator  import BIDSValidator




def main(argv):

    parser = ArgumentParser(description='This script parses the JSONLD terms sub directories and')

    parser.add_argument('-input', dest='input', required=False, help="Path to terms directory to validate")


    args = parser.parse_args()

    path = args.input

    #List the sub directories inside the root directory
    list_jsonld = os.listdir(args.input)


    # for each dataset
    for i in list_jsonld:
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



            ### Run the validator using the path to the jsonld file "part_file" ####
            stream = os.popen('reproschema -l DEBUG validate --shapefile validation/data_element_shape.ttl https://raw.githubusercontent.com/NIDM-Terms/terms/master/terms/NIDM_Concepts/Age.jsonld')
            output = stream.read()
            print(output)




            # set path to phenotype directory and check if it has one
            pheno_check = os.path.join(ds_path,'phenotype')

            # if the original dataset doesn't have phenotype directory skip
            if not os.path.exists(pheno_check):
                continue

            # if phenotype directory exists in phenotype directory start the updating process for those jsonld files as well
            elif os.path.exists(pheno_check):
                print('Updating phenotype directory of', i)

                # parse the phenotype directory
                for root, dirs, files in os.walk(pheno_check, topdown=True):
                    # check sub directories T1 and T2 for jsonld files
                    for dir in dirs:

                        # set path to that sub directory
                        sub_dir = os.path.join(pheno_check,dir)

                        # parse the subdirectory looking for jsonld files
                        for subroot, subdirs, json_files in os.walk(sub_dir):
                            # check each file
                            for FL in json_files:
                                #if that file ends with .jsonld
                                if FL.endswith('.jsonld'):
                                    #extract the name of the file
                                    FL_name = FL[:-7]
                                    print('\t',FL,'is being validated...')
                                    #set path to the file in the jsonld directory
                                    jsonld_sub_path = os.path.join(sub_dir,FL)

                                    #check if the path exist
                                    if os.path.exists(jsonld_sub_path):


                                        print('')
                                        ### Run the validator using the path to the jsonld file "part_file" ####

                                else:
                                    continue

                            break


                    # check for jsonld files in phenotype directory
                    for file in files:
                        #if found
                        if file.endswith('.jsonld'):
                            #extract the file name
                            file_name = file[:-7]
                            print('\t',file,'is being validated...')
                            #set path to the file
                            pheno_file_path = os.path.join(pheno_check,file)

                            #check if the path exist
                            if os.path.exists(pheno_file_path):


                                print('')
                                ### Run the validator using the path to the jsonld file "part_file" ####


                        else:
                            continue


        print('Validation is complete in', i)




if __name__ == "__main__":
   main(sys.argv[1:])

