import os, sys, json
import pandas as pd
from argparse import ArgumentParser
from more_itertools import sliced





def json_description(path,json_file,term):
    '''
    :param path: path to ds id
    :param json_file: name of the json file
    :param term: BIDS term passed to this function
    :return: description of the given BIDS term
    '''


    pathtojson = os.path.join(path,json_file)

    #load json file as a dictionary
    with open(pathtojson) as d:
        json_read = json.load(d)

    #look for the term and its description in the dictionary extract the description if found
    for key in json_read:
        if key == term:
            for empty in json_read[term]:
                if empty == 'Description':
                    term_des = json_read[term]['Description']
                    return term_des
                else:
                    continue






def main(argv):
    parser = ArgumentParser(description='This program will extract BIDS terms from participants.tsv files and associate them with their'
                                        ' dataset ID and save the output in a csv file')

    parser.add_argument('-ds_dir', dest='directory', required=True, help="Path to directory to extract datasets IDs")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output dir to save csv file")
    args = parser.parse_args()



    #list ds ID's inside the given directory and set path
    dsid = os.listdir(args.directory)
    path = args.directory

    df_tuples = []
    state = ''
    st = ''


    #acress every ds individually
    for i in dsid:
        #add ds ID to the end of the path to access the dataset
        path = os.path.join(path, i)
        if os.path.isdir(path):
            tsv_extract = os.listdir(path)


            #extract participant.tsv file from a dataset
            for filename in tsv_extract:
                #search for participants.json file in the data set
                if filename == 'participants.json':
                    state = 1
                #search for phenotype directory in the data set
                if filename == 'phenotype':
                    st = 1

                #search for phenotype directory in the data set
                if filename == 'participants.tsv':
                    pathtotsv = os.path.join(path, filename)
                    #read tsv file
                    r_tsv = pd.read_csv(pathtotsv, error_bad_lines=False)



                    # extract terms (column names) from participants.tsv dataframe
                    for c in r_tsv.columns:
                        #create a list with all terms in the tsv file
                        term_list = c.split("\t")
                        while '' in term_list:
                            term_list.remove('')
                        #create a list with ds ID to match to each term
                        ds_list = i*len(term_list)
                        ds = ds_list.split('ds')
                        #takeout any empty items in the list
                        while '' in ds:
                            ds.remove('')

                        #assigns YES or NO to answer whether the data set has a participants.json file
                        term_des = []
                        if state == 1:
                            json_file = 'participants.json'
                            for term in term_list:
                                if term == 'participant_id':
                                    term_list.remove('participant_id')
                                term_des.append(json_description(path,json_file, term))
                        else:
                            continue

                        #assigns YES or NO to answer whether the data set has a phenotype directory
                        if st == 1:
                            val = 'YES'*len(term_list)
                            VAL = list(sliced(val,3))
                        else:
                            val = 'NO'*len(term_list)
                            VAL = list(sliced(val,2))


                        #pair each term with the appropriate ds ID
                        tuples = list(zip(term_list,ds,term_des,VAL))
                        df_tuples.extend(tuples)


        path = args.directory
        state = ''
        st = ''





    #create and save data frame to csv
    df = pd.DataFrame(df_tuples)
    df.to_csv(args.output_dir+'Openneuro_BIDS_terms_participantstsv.csv', header = ['Terms','ds_number','Json Term Description','Has phenotype dir?'], index=False)




    print('Terms have been extracted into a csv in your output directory')





if __name__ == '__main__':
    main(sys.argv[1:])