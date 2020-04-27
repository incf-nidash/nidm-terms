import os, sys
import json
import pandas as pd
from argparse import ArgumentParser




def main(argv):
    parser = ArgumentParser(description='This program will extract BIDS dataset identification and assign them to ')

    parser.add_argument('-ds_dir', dest='directory', required=True, help="Path to directory to extract datasets IDs")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output dir to save csv file")
    args = parser.parse_args()


    #list ds ID's inside the given directory and set path
    dsid = os.listdir(args.directory)
    path = args.directory

    df_tuples = []
    global author
    global ref
    global T_name


    #acress every ds individually
    for i in dsid:
        #add ds ID to the end of the path to access the dataset
        path = os.path.join(path, i)
        ds = [i]
        ds_num = [e[2:] for e in ds]
        if os.path.isdir(path):
            dd_extract = os.listdir(path)

            #looks for the data description json file, converts it to a dictionary, and extracts elements of interest
            for filename in dd_extract:
                if filename == 'dataset_description.json':
                    pathtojson = os.path.join(path, filename)

                    with open(pathtojson) as f:
                        dd_read = json.load(f)

                    for key in dd_read:
                        if key == 'Authors':
                            author = [dd_read[key]]
                            break
                        else:
                            author = ['']
                            continue

                    for k in dd_read:
                        if k == 'ReferencesAndLinks':
                            ref = [dd_read[k]]
                            break
                        else:
                            ref = ['']
                            continue

                    for element in dd_read:
                        if element == 'Name':
                            T_name = [dd_read[element]]
                            break
                        else:
                            T_name = ['']
                            continue


        #craetes a tuple file with elements extracted to convert to a data frame
        tuples = list(zip(ds_num, T_name, author, ref))
        df_tuples.extend(tuples)


        path = args.directory



    #create and save data frame to csv
    df = pd.DataFrame(df_tuples)
    df.to_csv(args.output_dir+'Openneuro_BIDS_DSID_and_Contactinfo.csv', header = ['ds_number', 'Task Name','Author','Reference'], index=False)

    print('Data set identifications and contact information have been saved into a csv file in your output directory')





if __name__ == '__main__':
    main(sys.argv[1:])