import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
import shutil
import ast
from urllib.parse import urlparse
import tempfile
import urllib.request as ur
from urllib.parse import urlparse
import numpy as np




def url_validator(url):
    '''
    Test whether URL is a valid url
    :param url: URL to the context file
    :return: True for valid url and false for invalid url
    '''

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])

    except:
        return False




def level_parser(df_row,doc,context,compacted):
    '''
    Parse through term levels in the CVS file and assign them to a dictionary,
    and assign minimum, maximum, and allowable values to doc
    :param df_row:
    :param doc:
    :param context:
    :return: doc with assigned levels, minimum, maximum, and allowable values.
    '''

    # extract the levels column from the data frame
    row = df_row['Levels']


    levels = {}
    all_val = []
    global case
    global state
    global minimum
    global maximum


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row) :
        return

    #split each row in levels at semicolon
    semicolon_splits = row.split(';')
    #split each row in levels at colon
    colon_splits = row.split(':')

    # set a case number based on whether the level string has an additional semicolon in text or not
    for s in colon_splits:
        if s.count(';') == 2:
            case = 2
            break
        elif s.count(';') == 1 or s.count(';') == 0:
            case = 1

    # if level string doesn't contain semicolon in text
    if case == 1:
        # for every item in semicolon splits extract the key and value and assign it to levels dictionary
        for i in semicolon_splits:
            c_split = i.split(':')
            levels[c_split[0]] = c_split[1]
            all_val.append(c_split[0])
            # check if the level key is a string and set a state
            if c_split[0].isdigit():
                state = 1
            else:
                state = ''

    # else if the level string contain an extra semicolon in text
    elif case == 2:
        #skip a semicolons and split at the next one

        #left split
        semicolon1 = row.split(';',2)
        #right split
        semicolon2 = row.rsplit(';',2)


        #take the last item is left split at semicolon and extract the key and value and assign it to levels dictionary
        csplit = semicolon1[-1].split(':')
        levels[csplit[0]] = csplit[1]
        all_val.append(csplit[0])
        # check if the level key is a string and set a state
        if csplit[0].isdigit():
            state = 1
        else:
            state = ''

        #take the last item is right split at semicolon and extract the key and what it maps to and assign it to levels dictionary
        csplit1 = semicolon2[0].split(':')
        levels[csplit1[0]] = csplit1[1]
        all_val.append(csplit1[0])
        # check if the level key is a string and set a state
        if csplit1[0].isdigit():
            state = 1
        else:
            state = ''

    # if the key in the level property is digit assign a minimum and a maximum value
    if state == 1:
        minimum = min(all_val)
        maximum = max(all_val)

        doc[context['@context']['minimumValue']] = int(minimum)
        doc[context['@context']['maximumValue']] = int(maximum)

    # assign level dict to the jsonld property levels
    doc[context['@context']['levels']] = {}
    doc[context['@context']['levels']] = levels
    #compacted['@context']['levels'] = {}
    #compacted['@context']['levels'] = doc[context['@context']['levels']]


    # assign allowable values to allowableValues in jsonld property
    doc[context['@context']['allowableValues']] = all_val

    case = ''



def isAbout_parser(df_row,doc,context):
    '''
    parses the isAbout column, make a list of of URI for terms with more than one is about, and assign it to the isAbout section
    :param df_row:
    :param doc:
    :param context:
    :return:
    '''

    # extract the levels column from the data frame
    row = df_row['isAbout']

    isabouts = []


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row) :
        return

    semicolon_splits = row.split(';')

    #split the string by semicolon and validate each URL using the url_validator function
    for s in semicolon_splits:
        url_validator(s)

        if s is not False:
            isabouts.append(s)

    print("\tFound OpenNeuro_isAbout")
    doc[context['@context']['isAbout']] = str(isabouts)



def main(argv):
    parser = ArgumentParser(description='This program will load in a custom csv spreadsheet and create separate'
                                        'JSON files and add the appropriate properties for each term')

    parser.add_argument('-csv', dest='csv_file', required=True, help="Path to csv file to convert. NOTE: the spreadsheet must be in a comma-separated values format")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
    parser.add_argument('-context', dest= 'context', required=True, help='URL to context file')
    args = parser.parse_args()


    # open csv file and load into a data frame
    df = pd.read_csv(args.csv_file, encoding = 'latin-1', error_bad_lines=False)


    #check whether the context url is valid or not
    url = url_validator(args.context)


    # if user supplied a url as a segfile
    if url is not False:

        #try to open the url and get the pointed to file
        try:
            #open url and get file
            opener = ur.urlopen(args.context)
            # write temporary file to disk and use for stats
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(opener.read())
            temp.close()
            context_file = temp.name
        except:
            print("ERROR! Can't open url: %s" %args.context)
            exit()


    # read in jsonld context
    with open(context_file) as context_data:
        context = json.load(context_data)

    #starting a new python dictionary
    doc = {}

    # put data set Id's in a list
    ds_number = df['ds_number'].tolist()

    # create an empty list for non duplicated data set ID's
    ds_list = []
    for s in ds_number:
        if s not in ds_list:
            ds_list.append(s)


    # make directory for every dataset
    for dl in ds_list:
        l = str(dl).zfill(6)
        path_to_dir = os.path.join(args.output_dir, str(l))
        if os.path.exists(path_to_dir):
            shutil.rmtree(path_to_dir)
        ds_dir = os.mkdir(os.path.join(args.output_dir, str(l)))

        # lock the dataframe to only read rows with specific ds_number
        dataset = df.loc[df['ds_number'] == dl]

        #loop through all rows and grab info if exists
        for (i,row) in dataset.iterrows():
            print('starting iteration...')
            print('processing term: %s'%row['Term'])


            #add type as schema.org/DataElement
            doc['@type'] = context['@context']['DataElement']
            doc[context['@context']['source_variable']] = row['Term']

            #assign Long Name to the label property in doc
            if not pd.isnull(row['LongName']):
                print("\tFound OpenNeuro Label")
                doc[context['@context']['label']] = str(row['LongName'])

            #assign description to the description property in doc
            if not pd.isnull(row['Description']):
                print("\tFound OpenNeuro_Definition")
                doc[context['@context']['description']] = str(row['Description'])

            #assign type of the input value to the ValueType property in doc
            if not pd.isnull(row['ValueType']):
                print("\tFound OpenNeuro_ValueType")
                doc[context['@context']['valueType']] = str(row['ValueType'])

            #assign unit label to hasUnit property in doc
            if not pd.isnull(row['Units']):
                print("\tFound OpenNeuro_Units")
                doc[context['@context']['hasUnit']] = str(row['Units'])


            isAbout_parser(row,doc,context)
            #level_parser(row,doc,context)

            #write JSON file out
            compacted = jsonld.compact(doc,args.context)
            level_parser(row,doc,context,compacted)

            # opens pre-made directory with with a number that matches the ds ID and creates a jsonld file inside that directory
            with open (join((os.path.join(args.output_dir, str(l))), row['Term'].replace("/","_") + '.jsonld'),'w+') as outfile:
                json.dump(compacted,outfile,indent=2)

            print("size of dict: %d" %sys.getsizeof(doc))
            doc.clear()



if __name__ == "__main__":
   main(sys.argv[1:])

