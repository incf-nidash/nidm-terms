import os,sys
from argparse import ArgumentParser
import pandas as pd
from pyld import jsonld
from os.path import join
import json
import shutil
import tempfile
import urllib.request as ur
from urllib.parse import urlparse
import numpy as np


# added by DBK
from os import system
try:
    from cognitiveatlas.api import get_concept, get_disorder
except ImportError:
    system('python -m pip install cognitiveatlas')
    from cognitiveatlas.api import get_concept, get_disorder
import requests



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

    print("\tFound OpenNeuro_levels")

    #split each row in levels at semicolon
    semicolon_splits = row.split(';')
    #split each row in levels at colon
    colon_splits = row.split(':')

    # set a case number based on whether the level string has an additional semicolon in text or not
    for s in colon_splits:
        if s.count(';') == 2:
            case = 2
            break
        elif s.count(';') > 2 or s.count('!') > 0:
            case = 3
            break
        elif s.count(';') == 1 or s.count(';') == 0 and s.count('!') == 0:
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


    elif case == 3:

        excount = row.count('!')
        if excount == 1:
            semisplit = row.split(';')
            for g in semisplit:
                colonsplit = g.split(':')
                levels[colonsplit[0]] = colonsplit[1]
                all_val.append(colonsplit[0])

                if colonsplit[0].isdigit():
                    state = 1
                else:
                    state = ''

        elif excount > 1:

            exsplit = row.split('!')

            for l in exsplit:
                colon = l.split(':',1)
                levels[colon[0]] = colon[1]
                all_val.append(colon[0])

                if colon[0].isdigit():
                    state = 1
                else:
                    state = ''


    # assign levels to the jsonld property levels
    doc[context['@context']['levels']] = []
    for key,value in levels.items():
        doc[context['@context']['levels']].append(key + ":" + value)


    # assign allowable values to allowableValues in jsonld property
    doc[context['@context']['allowableValues']] = all_val


    # if the key in the level property is digit assign a minimum and a maximum value
    if state == 1:
        while '' in all_val:
            all_val.remove('')

        if len(all_val) > 1:

            negval = []
            posval = []
            f = ''

            for a in all_val:
                if a[0] == '-':
                    s = 1
                    break
                elif a.isdigit():
                    s = 0
                elif a == 'Nothing':
                    s = 2
                    break
                for pr in a:
                    if pr == '(':
                        f = 'break'


            if f == 'break':
                return

            elif s == 2:
                return

            elif s == 1:
                for b in all_val:
                    if b[0] == '-':
                        negval.append(b)
                        minimum = max(negval)
                    elif b[0].isdigit():
                        posval.append(b)
                        maximum = max(all_val)

            elif s == 0:
                minimum = min(all_val)
                all_val.sort(key=lambda x: int(str(x)))
                maximum = all_val[-1]




            doc[context['@context']['minimumValue']] = minimum
            doc[context['@context']['maximumValue']] = maximum

    case = ''



def CogAt_WO_json(row2, isabouts):


    if isinstance(row2,float) and np.isnan(row2):
        return

    semicolon_splits2 = row2.split(';')

    for q in semicolon_splits2:
        q = q.rstrip().lstrip()
        url_validator(q)

        if q is not False:
            isabouts.append(q)



def get_isAbout_label(url):
    '''
    Added by DBK to get labels for isAbout urls
    :param url: url to get label for
    :return: string label
    '''


    scicrunch_base_uri = 'https://scicrunch.org/api/1/ilx/search/curie/'

    # load user's api key from environment variable. If not found then exit with error message
    try:
        user_key = os.environ["INTERLEX_API_KEY"]
    except KeyError:
        print("Please set the environment variable INTERLEX_API_KEY")
        sys.exit(1)

    if "cognitiveatlas" in url:
        #skip for things that aren't concepts or disorders for the time being
        if ("concept" not in url) and ("disorder" not in url):
            # for now if we don't have a concept or disorder url from cogatlas then just return nothing for label
            # will need to work with cog atlas folks about how to retrieve tasks and other types from cog atlas
            return ""
        #print(url)
        # parse out id of term and get using cog atlas python tool...
        id = url.rsplit('/',1)[0].rsplit('/',1)[1]
        # don't know if this is a concept or disorder so we'll try both
        try:
            tmp = get_concept(id=id,silent=True)
            label = tmp.json['name'].lower()
            #print("cogatlas concept label: %s" %(isAbout_term_labels[url]))
        except:
            tmp = get_disorder(id=id,silent=True)
            label = tmp.json['name'].lower()
            #print("cogatlas disorder label: %s" %isAbout_term_labels[url])

    elif "interlex" in url:
        # get label for interlex terms
        payload={}
        headers={}
        full_url = scicrunch_base_uri + url.rsplit('/',1)[1].replace('_',':').rstrip("']'") + "?key=" + user_key
        #print(full_url)
        response = requests.request("GET",full_url,headers=headers,data=payload)
        # response is a json dictionary. here we want the label
        label= response.json()["data"]["label"].lower()
        #print("interlex label: %s" %isAbout_term_labels[url] )

    return label


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
<<<<<<< HEAD

=======
>>>>>>> dedacc83a26f3602fa90e49f050c0fb215168fe2

    isabouts = []


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row):
        return

    semicolon_splits = row.split(';')

    while '' in semicolon_splits:
        semicolon_splits.remove('')

    #split the string by semicolon and validate each URL using the url_validator function
    for s in semicolon_splits:

        s = s.rstrip().lstrip()


        if url_validator(s) is not False:
            # added by DBK to get labels for isabout URLs
            # first make sure we have an InterLex API key stored as an environment variable
            label = get_isAbout_label(s)
            isabouts.append(s+":"+label)


    doc[context['@context']['isAbout']] = []
    doc[context['@context']['isAbout']].append(isabouts)


<<<<<<< HEAD
    print("\tFound OpenNeuro_isAbout")


=======

    if len(isabouts) == 1:
        for i in isabouts:
            doc[context['@context']['isAbout']] = str(i)

    elif len(isabouts) > 1:
        doc[context['@context']['isAbout']] = []
        doc[context['@context']['isAbout']].append(isabouts)


    print("\tFound OpenNeuro_isAbout")


>>>>>>> dedacc83a26f3602fa90e49f050c0fb215168fe2


def isPartOf_parser(df_row,doc,context):

    # extract the levels column from the data frame
    row = df_row['isPartOf']

    ispartof = []


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row) :
        return

    semicolon_splits = row.split(';')

    #split the string by semicolon and validate each URL using the url_validator function
    for s in semicolon_splits:
        url_validator(s)

        if url_validator(s) is not False:
            ispartof.append(s)


        doc[context['@context']['isPartOf']] = []
        doc[context['@context']['isPartOf']].append(ispartof)


    print("\tFound OpenNeuro_isPartof")






def main(argv):
    parser = ArgumentParser(description='This program takes a costume csv spreadsheet with annotated terms extracted from '
                                        'both participants.tsv and phenotype.tsv files of OpenNeuro datasets and term properties. '
                                        'I will then create a jsonld representation for each term based on the provided context file.')

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
        os.mkdir(os.path.join(args.output_dir, str(l)))

        # lock the dataframe to only read rows with specific ds_number
        dataset = df.loc[df['ds_number'] == dl]

        #loop through all rows and grab info if exists
        for (i,row) in dataset.iterrows():
            print('starting iteration...')
            print('processing term: %s'%row['sourceVariable'])


            #add type as schema.org/DataElement
            doc['@type'] = context['@context']['DataElement']
            doc[context['@context']['source_variable']] = row['sourceVariable']

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

            #assign unit label to measureOf property in doc
            if not pd.isnull(row['measureOf']):
                print("\tFound OpenNeuro_measureOf")
                doc[context['@context']['measureOf']] = str(row['measureOf'])

            #assign unit label to datumType property in doc
            if not pd.isnull(row['datumType']):
                print("\tFound OpenNeuro_measureOf")
                doc[context['@context']['datumType']] = str(row['datumType'])

            if not pd.isnull(row['isPartOf']):
                print("\tFound OenNeuro_isPartOf")
                doc[context['@context']['isPartOf']] = str(row['isPartOf'])

            if not pd.isnull(row['Derivative']):
                print('\tFound OpenNeuro_Derivative')
                doc[context['@context']['derivative']] = str(row['Derivative'])

            if not pd.isnull(row['Term_URL']):
                print('\tFound OpenNeuro_TermURL')
                doc[context['@context']['url']['@id']] = str(row['Term_URL'])


            if not pd.isnull(row['Minimum Value']):
                print('\tFound OpenNeuro_minimum value')
                doc[context['@context']['minimumValue']] = str(row['Minimum Value'])

            if not pd.isnull(row['Maximum Value']):
                print('\tFound OpenNeuro_maximum value')
                doc[context['@context']['maximumValue']] = str(row['Maximum Value'])


            # allowable values based on given min and max values in the spreadsheet
            if not pd.isnull(row['Minimum Value']) and not pd.isnull(row['Maximum Value']):
                all_vall = np.arange(int(row['Minimum Value']), int(row['Maximum Value'])).tolist()
                doc[context['@context']['allowableValues']] = all_vall



            isAbout_parser(row,doc,context)
            isPartOf_parser(row,doc,context)
            level_parser(row,doc,context)

            #write JSON file out
            compacted = jsonld.compact(doc,args.context)


            # opens pre-made directory with with a number that matches the ds ID and creates a jsonld file inside that directory
            with open (join((os.path.join(args.output_dir, str(l))), row['sourceVariable'].replace("/","_") + '.jsonld'),'w+') as outfile:
                json.dump(compacted,outfile,indent=2)

            print("size of dict: %d" %sys.getsizeof(doc))
            doc.clear()



if __name__ == "__main__":
   main(sys.argv[1:])

