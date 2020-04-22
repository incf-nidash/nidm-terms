import os,sys
from argparse import ArgumentParser
import pandas as pd
from os.path import join
import json
from bids_validator  import BIDSValidator



# This program updates the original participants.json and phenotype.json with the annotated OpenNeuro BIDS terms jsonld representations
# in order to have BIDS compliant json sidecar file for each OpenNeuro dataset.

# It has two missions:
## 1- Parse through the participants.tsv terms for each dataset and update participants.json sidecar file
## 2- Parse the phenotype directory, if found, and updates/ creates a json sidecar file for each tsv file




def bids_sp_validator(path):

    validator = BIDSValidator()


    for p in path:
        print(validator.is_bids(p))




def levels_parser(jsonld_read, dict, term):
    '''
    This function parses the levels property in the jsonld file and switch is from a list to a dictionary
    to follow BIDS specifications.

    :param jsonld_read: dictionary created based off of the jsonld file
    :param dict: dictionary which includes term as dict a key, and jsonld dictionary as value
    :param term: the term extracted from participants.tsv or phenotype.tsv

    :return:
    The passed dictionary with levels property as a dictionary in which each level maps to a value
    '''

    # Open new dictionary
    levels_dict = {}

    # Extract the value of the key levels
    # (value would be a list with keys and values separated by a colon)
    for key in jsonld_read:
        if key == 'levels':
            for l in jsonld_read[key]:
                split = l.split(':')
                k = split[0]
                v = split[1]
                ## assign keys and values to levels dictionary
                levels_dict[k] = v
                ## assign levels dictionary to the json sidecar file dictionary
                dict[term]['levels'] = levels_dict


    return dict



def Phenotype(pathtophenotype,jsonld_path,i):
    '''
    If the dataset has a phenotype directory, this function creates/updates a BIDS compliant json sidecar file
    for each phenotype.tsv file in the directory based on our annotated OpenNeuro terms in jsonld representaions.

    :param pathtophenotype: path to the phenotype directory
    :param jsonld_path: path to terms' jsonld files
    :param i: index representing the OpenNeuro dataset number

    :return:
    An updated json sidecar file for each tsv file in the phenotype directory.
    '''



    global phenotype_dict
    global outfile


    #parse through the phenotype directory looking for assessment terms and matching jsonld files to update BIDS json sidecar files
    for root, dirs, files in os.walk(pathtophenotype, topdown=True):

        ##access sub-directories to extract assessment terms
        for dir in dirs:
            sub_dir = os.path.join(pathtophenotype, dir)
            ##access tsv files in sub-directories
            for subroot, subdirs, subfile in os.walk(sub_dir):
                for FL in subfile:
                    FL_name = FL[:-4]
                    if FL.endswith('.tsv'):
                        pheno_tsv = os.path.join(subroot, FL)
                        r_tsv = pd.read_csv(pheno_tsv, error_bad_lines=False)

                        #exract terms from tsv files
                        for c in r_tsv.columns:
                            #create a term list
                            term_list = c.split("\t")
                            while '' in term_list:
                                term_list.remove('')
                            for t in term_list:
                                if t == 'participant_id':
                                    term_list.remove('participant_id')

                            ## open a new dictionary for each tsv term list
                            phenotype_dict = {}

                            ## for each phenotype term find jsonld representation and update the json sidecar file
                            for pheno_term in term_list:
                                for ld in os.listdir(jsonld_path):
                                    if i.endswith(ld):
                                        jsonldpath = os.path.join(jsonld_path, ld)
                                        jsonld_term = os.listdir(jsonldpath)
                                        for j_ld in jsonld_term:
                                            ## If the jsonld file matches the term access it and extract the dictionary
                                            ## and add it to json sidecar file dictionary
                                            if j_ld.startswith(pheno_term):
                                                jsonld_file = os.path.join(jsonldpath, j_ld)
                                                with open(jsonld_file) as d:
                                                    jsonld_read = json.load(d)
                                                phenotype_dict[pheno_term] = jsonld_read
                                                ## Call levels parser to change the value of the property levels to a dictionary
                                                levels_parser(jsonld_read,phenotype_dict, pheno_term)

                        ## Write and update the original json sidecar file with our jsonld files based on the location of the original json file
                        for json_file in subfile:
                            if json_file.endswith('.json'):
                                json_file_name = json_file[:-5]
                                if json_file_name == FL_name:
                                    with open (join(sub_dir, json_file_name + '.json'),'w+') as outfile:
                                        json.dump(phenotype_dict,outfile,indent=2)




                                elif not json_file_name == FL_name:
                                    for jf in files:
                                        if jf.endswith('.json'):
                                            jf_name =  jf[-4:]
                                            if jf_name == FL_name:
                                                with open (join(sub_dir, jf_name + '.json'),'w+') as outfile:
                                                    json.dump(phenotype_dict,outfile,indent=2)

                            elif not json_file.endswith('.json'):
                                for f in files:
                                    if f.endswith('.json'):
                                        f = f[:-5]
                                        if f == FL_name:
                                            with open (join(pathtophenotype, f + '.json'),'w+') as outfile:
                                                json.dump(phenotype_dict, outfile, indent=2)



        ## Access tsv files that are in phenotype directory and outside of subdir like (T1 and T2 subdir)
        for tsv_file in files:
            global phenotypedict
            if tsv_file.endswith('.tsv'):
                tsv_file_name = tsv_file[:-4]
                pathtotsv = os.path.join(root, tsv_file)
                rtsv = pd.read_csv(pathtotsv, error_bad_lines=False)
                #extract terms from tsv files
                for col in rtsv.columns :
                    #create a term list
                    termlist = col.split("\t")
                    while '' in termlist:
                        termlist.remove('')
                    for T in termlist:
                        if T == 'participant_id':
                            termlist.remove('participant_id')

                    ## Create empty dictionary for updated json sidecar file
                    phenotypedict = {}

                    for phenoterm in termlist:
                        for ld in os.listdir(jsonld_path):
                            if i.endswith(ld):
                                jsonldterm = os.listdir(os.path.join(jsonld_path, ld))
                                for jld in jsonldterm:
                                    if jld.startswith(phenoterm):
                                        jsonldfile = os.path.join(os.path.join(jsonld_path,ld), jld)
                                        with open(jsonldfile) as d:
                                            jsonldread = json.load(d)

                                        phenotypedict[phenoterm] = jsonldread
                                        levels_parser(jsonldread,phenotypedict, phenoterm)

                                    else:
                                        continue


                ## Write and update the original json sidecar file with our jsonld files
                with open (join(root, tsv_file_name + '.json'),'w+') as outfile:
                    json.dump(phenotypedict,outfile,indent=2)

        return outfile




def main(argv):

    parser = ArgumentParser(description='This program updates the original participants.json and phenotype.json with the'
                                        'annotated OpenNeuro BIDS terms jsonld representations in order to have BIDS '
                                        'compliant json sidecar file for each OpenNeuro dataset.')

    parser.add_argument('-jsonld', dest='jsonld', required=True, help="Path to OpenNeuro jsonld directory")
    parser.add_argument('-ds_dir', dest='ds_dir', required=True, help="Path to OpenNeuro datasets directory")

    args = parser.parse_args()


    #list ds ID's inside the given directory and set path to both the OpenNeuro dataset directory and to jsonld directory
    dsid = os.listdir(args.ds_dir)
    term_path = args.ds_dir
    jsonld_path = args.jsonld


    global NIDM_p_dict


    #loops through the data sets and set a path to that data set
    for i in dsid:
        ##read only dataset directories
        if not i.startswith('ds'):
            continue

        ##reset path for each dataset
        path = os.path.join(term_path, i)
        if os.path.isdir(term_path):
            ## list items in dataset
            pt_extract = os.listdir(path)

            ## loop through the list of files in the dataset and extract terms from
            ## participants.tsv file and put them in a list
            for p_tsv in pt_extract:
                if p_tsv == 'participants.tsv':
                    pathtoptsv = os.path.join(path, p_tsv)
                    r_tsv = pd.read_csv(pathtoptsv, error_bad_lines=False)
                    for t in r_tsv.columns:
                        #create a list with all terms in the tsv file
                        term_list = t.split("\t")
                        while '' in term_list:
                            term_list.remove('')


                        ## create an empty dictionary for each participants.tsv term list
                        NIDM_p_dict = {}


                        ## loop through terms extracted from participants.tsv file
                        ## look for each term's jsonld file in the jsonld directory,
                        ## and add the terms and their properties to a new dictionary
                        for term in term_list:
                            ## if directory name in jsonld directory matches the dataset number access that directory and set path
                            for l in os.listdir(jsonld_path):
                                if i.endswith(l):
                                    jsonldpath = os.path.join(jsonld_path, l)
                                    jsonld_terms = os.listdir(jsonldpath)
                                    ## if the term in term list matches the jsonld file name open that file
                                    ## and add the term to the dictionary for sidecar file creation
                                    for ld in jsonld_terms:
                                        if ld.startswith(term):
                                            jsonld_file = os.path.join(jsonldpath, ld)
                                            with open(jsonld_file) as d:
                                                jsonld_read = json.load(d)
                                            NIDM_p_dict[term] = jsonld_read
                                            ## parse levels property and change it to dictionary
                                            levels_parser(jsonld_read, NIDM_p_dict,term)


                    ## Open a new json file and dump the created dictionary in it to update/replace the original participants.json file in each dataset
                    with open (join(path, "participants" + '.json'),'w+') as outfile:
                        json.dump(NIDM_p_dict,outfile,indent=2)

                    #bids_sp_validator(path)


                ## Check if the dataset has a phenotype directory. If yes, set path to it and call Phenotype function
                if p_tsv == 'phenotype':
                    pathtophenotype = os.path.join(path, p_tsv)
                    Phenotype(pathtophenotype, jsonld_path, i)



if __name__ == "__main__":
   main(sys.argv[1:])

