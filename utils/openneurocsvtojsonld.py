import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
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




def level_parser(df_row,doc,context):

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


    semicolon_splits = row.split(';')
    colon_splits = row.split(':')

    for s in colon_splits:
        if s.count(';') == 2:
            case = 2
            break
        elif s.count(';') == 1 or s.count(';') == 0:
            case = 1


    if case == 1:
        for i in semicolon_splits:
            c_split = i.split(':')
            levels[c_split[0]] = c_split[1]
            all_val.append(c_split[0])
            if c_split[0].isdigit():
                state = 1
            else:
                state = ''

    elif case == 2:
        semicolon1 = row.split(';',2)
        semicolon2 = row.rsplit(';',2)

        csplit = semicolon1[-1].split(':')
        levels[csplit[0]] = csplit[1]
        all_val.append(csplit[0])
        if csplit[0].isdigit():
            state = 1
        else:
            state = ''

        csplit1 = semicolon2[0].split(':')
        levels[csplit1[0]] = csplit1[1]
        all_val.append(csplit1[0])
        if csplit1[0].isdigit():
            state = 1
        else:
            state = ''


    if state == 1:
        minimum = min(all_val)
        maximum = max(all_val)

        doc[context['@context']['minimumValue']] = int(minimum)
        doc[context['@context']['maximumValue']] = int(maximum)



    doc[context['@context']['levels']] = levels

    doc[context['@context']['allowableValues']] = all_val

    case = ''



def isAbout_parser(df_row,doc,context):

    # extract the levels column from the data frame
    row = df_row['isAbout']

    isabouts = []


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row) :
        return

    semicolon_splits = row.split(';')

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
    #loop through all rows and grab info if exists
    for (i,row) in df.iterrows():
        print('starting iteration...')
        print('processing term: %s'%row['Term'])


        #add type as schema.org/DefinedTerm
        doc['@type'] = context['@context']['DefinedTerm']
        doc[context['@context']['label']] = row['Term']

        if not pd.isnull(row['Description']):
                print("\tFound OpenNeuro_Definition")
                doc[context['@context']['description']] = str(row['Description'])

        if not pd.isnull(row['ValueType']):
            print("\tFound OpenNeuro_ValueType")
            doc[context['@context']['valueType']] = str(row['ValueType'])


        if not pd.isnull(row['Units']):
            print("\tFound OpenNeuro_Units")
            doc[context['@context']['unitLabel']] = str(row['Units'])


        isAbout_parser(row,doc,context)

        level_parser(row,doc,context)



        # write JSON file out
        compacted = jsonld.compact(doc,args.context)
        with open (join(args.output_dir,row['Term'].replace("/","_")+".jsonld"),'w+') as outfile:
            json.dump(compacted,outfile,indent=2)

        print("size of dict: %d" %sys.getsizeof(doc))
        doc.clear()





if __name__ == "__main__":
   main(sys.argv[1:])


