import os, sys, json
import pandas as pd
import prov.model as pm
from argparse import ArgumentParser
from more_itertools import sliced




def ValueType(pathtotsv,term):
    '''
    :param pathtotsv: path to the tsv file
    :param term: BIDS term
    :return: Type of input of the given term
    '''

    #open the tsv file as a data frame
    df = pd.read_csv(pathtotsv, error_bad_lines=False, sep = '\t')

    # iter through the rows based on the term and returns a value type
    for (i,row) in df.iterrows():
        if not pd.isnull(row[term]):
            if isinstance(row[term],int):
                return(pm.XSD["integer"])
            elif isinstance(row[term],str):
                return(pm.XSD["string"])
            elif isinstance(row[term],float):
                return(pm.XSD["float"])





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
    global state
    global st



    #acress every ds individually
    for i in dsid:
        #add ds ID to the end of the path to access the data set
        path = os.path.join(path, i)
        if os.path.isdir(path):
            tsv_extract = os.listdir(path)
            jp_extract = os.listdir(path)


            #extract participant.tsv file from a dataset
            for file_name in jp_extract:
                #search for participants.json file in the data set
                if file_name != 'participants.json':
                    state = ''
                elif file_name == 'participants.json':
                    state = 1
                    break

            for f in jp_extract:
                #search for phenotype directory in the data set
                if f != 'phenotype':
                    st = ''
                elif f == 'phenotype':
                    st = 1
                    break

            for filename in tsv_extract:
                #search for phenotype directory in the data set
                if filename != 'participants.tsv':
                    continue
                if filename == 'participants.tsv':
                    pathtotsv = os.path.join(path, filename)
                    #read tsv file
                    r_tsv = pd.read_csv(pathtotsv, error_bad_lines=False)

                    # extract terms (column names) from participants.tsv data frame
                    for c in r_tsv.columns:
                        #create a list with all terms in the tsv file
                        term_list = c.split("\t")
                        while '' in term_list:
                            term_list.remove('')
                        #remove the term participant id
                        for T in term_list:
                            if T == 'participant_id':
                                term_list.remove('participant_id')
                                continue
                        #create a list with ds ID to match to each term
                        ds_list = i*len(term_list)
                        ds = ds_list.split('ds')
                        #takeout any empty items in the ds list
                        while '' in ds:
                            ds.remove('')


                        term_des = []
                        term_long = []
                        term_level = []
                        term_levels = []
                        term_units = []
                        term_type = []
                        global s

                        #if the dataset doesn't have a participants.json file add an empty item to the list
                        if state == '':
                            for t in term_list:
                                term_des.extend([''])
                                term_long.extend([''])
                                term_levels.extend([''])
                                term_units.extend([''])
                                term_type.append(ValueType(pathtotsv,t))

                        #if the dataset has a participants.json file extract the appropriate term
                        elif state == 1:
                            json_file = 'participants.json'
                            pathtojson = os.path.join(path,json_file)
                            #load json file as a dictionary
                            with open(pathtojson) as d:
                                json_read = json.load(d)
                            for term in term_list:
                                if term == '"ISI"':
                                    term = 'ISI'
                                #call value type function to get the type of input and add it to the list
                                term_type.append(ValueType(pathtotsv,term))

                                s = ''
                                l = ''
                                lv = ''
                                u = ''

                                #look for a key that matches the term
                                for key in json_read:
                                    global term_ln
                                    global term_d
                                    if key == term:
                                        #look for term description in the json file
                                        for e in json_read[term]:
                                            if e == 'Description':
                                                term_d = json_read[term]['Description']
                                                term_des.append(term_d)
                                                s = 2
                                                break
                                            elif e != 'Description':
                                                s = 3
                                        #look for term long name in the json file
                                        for a in json_read[term]:
                                            if a == 'LongName':
                                                term_ln = json_read[term]['LongName']
                                                term_long.append(term_ln)
                                                l = 2
                                                break
                                            elif a != 'LongName':
                                                l = 3
                                        #look for term levels in the json file
                                        for b in json_read[term]:
                                            if b == 'Levels':
                                                for level in json_read[term]['Levels']:
                                                    key_lev = level + ':' + json_read[term]['Levels'][level]
                                                    term_level.append(key_lev)
                                                levels = [';'.join(term_level)]
                                                term_levels.extend(levels)
                                                term_level = []
                                                lv = 2
                                                break
                                            elif b != 'Levels':
                                                lv = 3
                                        #look for term units in the json file
                                        for c in json_read[term]:
                                            if c == 'Units':
                                                term_u = json_read[term]['Units']
                                                term_units.append(term_u)
                                                u = 2
                                                break
                                            elif c != 'Units':
                                                u = 3

                                    elif key != term:
                                        if s != 2:
                                            s = 1
                                        if l != 2:
                                            l = 1
                                        if lv != 2:
                                            lv =1
                                        if u != 2:
                                            u = 1

                                #if no description, long name, levels, or unit was found add an empty item to the list
                                if s == 1 or s == 3:
                                    term_des.extend([''])
                                    s = ''

                                if l == 1 or l == 3:
                                    term_long.extend([''])
                                    l = ''

                                if lv == 1 or lv == 3:
                                    term_levels.extend([''])
                                    lv = ''

                                if u == 1 or u == 3:
                                    term_units.extend([''])
                                    u = ''


                        #assigns YES or NO to answer whether the data set has a phenotype directory
                        if st == 1:
                            val = 'YES'*len(term_list)
                            VAL = list(sliced(val,3))
                        else:
                            val = 'NO'*len(term_list)
                            VAL = list(sliced(val,2))


                        #pair each term with the appropriate ds ID
                        tuples = list(zip(term_list,ds,term_des,term_long,term_levels,term_units,term_type,VAL))
                        df_tuples.extend(tuples)


        path = args.directory




    #create and save data frame to csv
    df = pd.DataFrame(df_tuples)
    df.to_csv(args.output_dir+'Openneuro_BIDS_terms_participantstsv.csv', header = ['Term','ds_number','Description', 'LongName','Levels','Units','ValueType','Has phenotype dir?'], index=False)



    print('Terms have been extracted into a csv in your output directory')






if __name__ == '__main__':
    main(sys.argv[1:])