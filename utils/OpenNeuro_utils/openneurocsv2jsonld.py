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
from rdflib.namespace import split_uri


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




def responseOptions_parser(df_row,context):
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

    little_doc = {}
    levels = {}
    all_val = []
    global case
    global state
    global minimum
    global maximum


    #assign type of the input value to the ValueType property in doc
    if not pd.isnull(df_row['ValueType']):
        print("\tFound OpenNeuro_ValueType")
        little_doc[context['@context']['valueType']] = str(df_row['ValueType'])


    #assign unit label to hasUnit property in doc
    if not pd.isnull(df_row['Units']):
        print("\tFound OpenNeuro_Units")
        little_doc[context['@context']['unitCode']] = str(df_row['Units'])


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row):
        return little_doc

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


    levels_dict = {}
    list = []

    # assign levels to the jsonld property levels

    for key,value in levels.items():
        levels_dict[context['@context']['value']] = key
        levels_dict[context['@context']['name']] = value

        dict_copy = levels_dict.copy()
        list.append(dict_copy)


    little_doc[context['@context']['choices']] = list



    # if key in the level property is digit assign a minimum and a maximum value
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


            # changed by DBK
            #doc[context['@context']['minValue']] = minimum
            #doc[context['@context']['maxValue']] = maximum

            little_doc[context['@context']['minValue']] = minimum
            little_doc[context['@context']['maxValue']] = maximum


    # assign allowable values to allowableValues in jsonld property
    #doc[context['@context']['allowableValues']] = all_val


    case = ''



    return little_doc


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
        label = response.json()["data"]["label"].lower()
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


    isabouts = []


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row):
        return

    semicolon_splits = row.split(';')

    while '' in semicolon_splits:
        semicolon_splits.remove('')


    # Added by DBK
    doc[context['@context']['isAbout']['@id']]=[]


    #split the string by semicolon and validate each URL using the url_validator function
    for s in semicolon_splits:

        s = s.rstrip().lstrip()


        if url_validator(s) is not False:
            # added by DBK to get labels for isabout URLs
            # first make sure we have an InterLex API key stored as an environment variable
            label = get_isAbout_label(s)
            #isabouts.append(s+":"+label)


            # Changed by DBK
            doc[context['@context']['isAbout']['@id']].append({'@id':s,context['@context']['label']:label})
            #doc[context['@context']['isAbout']][s] = label
            #doc[context['@context']['isAbout']].append(isabouts)


    print("\tFound OpenNeuro_isAbout")




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



def jsonld_dict(df,context,args):
    '''
    Creates compacted dictionary for every term passed and the main dictionary d.

    :param context: context file as a jsonld dictionary
    :param args: pass arguments
    :return:

    dictionary d with a compatced jsonld file for each row (i.e. term) passed
    '''

    #set a new main dictionary
    main_dict = {}
    terms_list = []


    main_dict['@context'] = args.context



    for i, row in df.iterrows():
        print('processing term: %s'%row['sourceVariable'])

        doc = {}

        # dictionary to contain elements of response options
        #ro_dict = {}

        # Added by DBK
        #doc['@context'] = context_url

        #add type as schema.org/DataElement
        doc['@type'] = context['@context']['DataElement']
        doc[context['@context']['sourceVariable']] = row['sourceVariable']

        ro_dict = responseOptions_parser(row,context)

        #assign Long Name to the label property in doc
        if not pd.isnull(row['LongName']):
            print("\tFound OpenNeuro Label")
            doc[context['@context']['label']] = str(row['LongName'])

        #assign description to the description property in doc
        if not pd.isnull(row['Description']):
            print("\tFound OpenNeuro_Definition")
            doc[context['@context']['description']] = str(row['Description'])

        #assign unit label to measureOf property in doc
        if not pd.isnull(row['measureOf']):
            print("\tFound OpenNeuro_measureOf")
            doc[context['@context']['measureOf']] = str(row['measureOf'])

        #assign unit label to datumType property in doc
        if not pd.isnull(row['datumType']):
            print("\tFound OpenNeuro_measureOf")
            doc[context['@context']['datumType']] = str(row['datumType'])

        #assign unit label to datumType isPartOf in doc
        if not pd.isnull(row['isPartOf']):
            print("\tFound OenNeuro_isPartOf")
            doc[context['@context']['isPartOf']] = str(row['isPartOf'])

        #assign unit label to Derivative property in doc
        if not pd.isnull(row['Derivative']):
            print('\tFound OpenNeuro_Derivative')
            doc[context['@context']['derivative']] = bool(2)

        #assign unit label to url property in doc
        if not pd.isnull(row['Term_URL']):
            print('\tFound OpenNeuro_TermURL')
            doc[context['@context']['url']['@id']] = str(row['Term_URL'])

        #assign unit label to Min value property in doc
        if not pd.isnull(row['Minimum Value']):
            print('\tFound OpenNeuro_minimum value')
            if isinstance(row['Minimum Value'],int):
                ro_dict[context['@context']['minValue']] = int(row['Minimum Value'])
            if isinstance(row['Minimum Value'],float):
                ro_dict[context['@context']['minValue']] = float(row['Minimum Value'])

        #assign unit label to Max value property in doc
        if not pd.isnull(row['Maximum Value']):
            print('\tFound OpenNeuro_maximum value')
            if isinstance(row['Maximum Value'],int):
                ro_dict[context['@context']['maxValue']] = int(row['Maximum Value'])
            if isinstance(row['Maximum Value'],float):
                ro_dict[context['@context']['maxValue']] = float(row['Maximum Value'])

        # allowable values based on given min and max values in the spreadsheet
        #if not pd.isnull(row['Minimum Value']) and not pd.isnull(row['Maximum Value']):
            #all_vall = np.arange(int(row['Minimum Value']), int(row['Maximum Value'])).tolist()
            #all_vall.append(int(row['Maximum Value']))
            #doc[context['@context']['allowableValues']] = all_vall

        isAbout_parser(row,doc,context)
        isPartOf_parser(row,doc,context)

        # assign response options properties
        if bool(ro_dict):
            doc[context['@context']['responseOptions']['@id']] = ro_dict


        # add property to specify that the term is associated with NIDM
        doc[context['@context']['associatedWith']] = str('NIDM')

        #Added by DBK
        #with open("/Users/dbkeator/Downloads/temp/test.jsonld","w") as fp:
        #    json.dump(doc,fp,indent=4)

        #add each term dict to terms_list
        terms_list.append(doc)

    #assign terms_list to property terms
    main_dict[context['@context']['terms']['@id']] = terms_list

    #compact jsonld file
    compacted = jsonld.compact(main_dict,args.context)

    #hack terms to replace it with prov:hasMember after compaction
    compacted['terms'] = compacted['prov:hasMember']
    del compacted['prov:hasMember']

    # DBK hacking isAbout which in compacted form still uses the URL as the key
    # so simple hack, which is still valid json-ld, is to replace the key
    # with the string isAbout
    #obj_nm,obj_term = split_uri('http://uri.interlex.org/ilx_0381385')


    # for loop added by NQ to access isAbout from the term list in the compacted file
    # for term in compacted['terms']:

        # if "http://uri.interlex.org/ilx_0381385" in term.keys():
        #     term['isAbout'] = term["http://uri.interlex.org/ilx_0381385"]
        #     del term["http://uri.interlex.org/ilx_0381385"]


    return compacted





def json_check(d,datasets_path,l,source,args,context,pathtophenodir):
    '''

    This function checks if the original json sidecar files have extra data elements that are not included in in the tsv file
    (like MeasurmentMetadataTool) and return a complete dictionary ready to be written in the proper directory consistant with
    the original dataset number and sub-directories.

    :param d: main dictionary for every BIDS json file that contains little jsonld files for every term
    :param datasets_path: path to original BIDS dataset dir (in this case it's OpenNeuro)
    :param l: dataset number extracted from the passed data frame
    :param source: name of the json file that was passed (it could be participants.json or a name of the json file in phenotype )
    :param args: passed argument
    :param context: context file passed in the argument
    :param pathtophenodir: path to the new updated datasets
    :param subdirectory: session T1 or T2 if the original dataset has such directories
    :returns

    d: complete dictionary with data elements from both tsv file and json dictionary

    '''


    # add ds to the beginning  of the dataset number to be able to access that original directory
    l = 'ds'+l

    # open a new dictionary for each data element
    doc = {}

    # check if the passed data elements come from participants file
    if source == 'participants.json':
        ## set path to the original participants.json file
        part_path = os.path.join(datasets_path,l + '/' + 'participants.json')
        # check if the dataset has a participants.json file
        ## if not then the function will just return that passed dictionary (d) with nothing added to it
        if not os.path.exists(part_path):

            return d

        ## if the original dataset has a participants.json file
        elif os.path.exists(part_path):
            ## open the json file as a dictionary
            with open (part_path) as dict:
                part_json = json.load(dict)
            ## now check if the keys in teh original files are included in the new dictionary
            for key in part_json:

                if key in d.keys():
                    continue

                ## if a new key is found in the original json file and not in the d add that key
                elif not key in d.keys():

                    #add type as schema.org/DataElement
                    doc['@type'] = context['@context']['DataElement']
                    doc[context['@context']['sourceVariable']] = key

                    # loop through the data elements properties and change them to be consistent with cde_context.jsonld
                    # (https://github.com/nqueder/terms/blob/master/context/cde_context.jsonld)
                    for subkey in part_json[key]:

                        if subkey == 'Description':
                            print("\tFound OpenNeuro_Definition")
                            doc[context['@context']['description']] = str(part_json[key][subkey])

                        if subkey == 'LongName':
                            print("\tFound OpenNeuro_Definition")
                            doc[context['@context']['label']] = str(part_json[key][subkey])

                        if subkey == 'TermURL':
                            print('\tFound OpenNeuro_TermURL')
                            doc[context['@context']['url']['@id']] = str(part_json[key][subkey])

                        if subkey == 'Derivative':
                            print("\tFound OpenNeuro_Derivative")
                            doc[context['@context']['derivative']] = str(part_json[key][subkey])

                        if subkey == 'Citation':
                            print("\tFound OpenNeuro_Citation")
                            doc[context['@context']['citation']] = str(part_json[key][subkey])

                        doc[context['@context']['associatedWith']] = str('NIDM')

                    ## create a compacted file from the data element dictionary and the context file
                    compacted = jsonld.compact(doc,args.context)

                    ## write that compacted file as a dictionary in the the master dictionary d
                    d[key] = compacted

            # return updated master dictionary d
            return d

    # if the passed dictionary comes from a phenotype file
    else:
        # set path to the original phenotype directory
        ds_path = os.path.join(datasets_path,l + '/' + 'phenotype')

        # parse the directory to be able to access both files that are placed inside or outside of a sub directory
        for root, dirs, files in os.walk(ds_path, topdown=True):
            #access sub-directories to extract assessment terms
            for dir in dirs:

                #set path to the sub directory
                sub_dir = os.path.join(ds_path,dir)

                #access tsv files in sub-directories
                for subroot, subdirs, json_files in os.walk(sub_dir):

                    # look for file with .json extension in the files of sub directories like T1 or T2
                    for FL in json_files:
                        # if a file with .json extension and starts with the same name as the tsv file passed to this function
                        # set a path to the file and open it
                        if FL.endswith('.json') and FL.startswith(source):

                            j_dir = os.path.join(sub_dir, source+'.json')

                            save_j_path = os.path.join(pathtophenodir,dir)

                            # open json file as a dictionary
                            with open (j_dir) as f:
                                phenojson1 = json.load(f)

                            # check if each data element is in the master dictionary d
                            for k in phenojson1:

                                if k in d.keys():
                                    continue

                                elif not k in d.keys():

                                    #add type as schema.org/DataElement
                                    doc['@type'] = context['@context']['DataElement']
                                    doc[context['@context']['sourceVariable']] = str(k)

                                    #for each data element that is not in the master dictionary d access its properties
                                    # and change them to be consistent with context
                                    for subk in phenojson1[k]:


                                        if subk == 'Description':
                                            print("\tFound OpenNeuro_Definition")
                                            doc[context['@context']['description']] = str(phenojson1[k][subk])

                                        if subk == 'LongName':
                                            print("\tFound OpenNeuro_LongName")
                                            doc[context['@context']['label']] = str(phenojson1[k][subk])

                                        if subk == 'TermURL':
                                            print('\tFound OpenNeuro_TermURL')
                                            doc[context['@context']['url']['@id']] = str(phenojson1[k][subk])

                                        if subk == 'Derivative':
                                            print('\tFound OpenNeuro_Derivative')
                                            doc[context['@context']['derivative']] = str(phenojson1[k][subk])

                                        if subk == 'Citation':
                                            print('\tFound OpenNeuro_Citaion')
                                            doc[context['@context']['citation']] = str(phenojson1[k][subk])

                                        doc[context['@context']['associatedWith']] = str('NIDM')

                                    # compact file with doc and context
                                    compacted = jsonld.compact(doc,args.context)
                                    # add compacted file to the master dictionary d
                                    d[k] = compacted

                                #return updated master dictionary d
                                return d

            # not that we checked for json files in phenotype sub directories check files in phenotype
            for file in files:
                # if a file with .json extension and starts with the same name as the tsv file passed to this function
                # set a path to the file and open it
                if file.endswith('.json') and file.startswith(source):

                    file_path = os.path.join(ds_path,source+'.json')

                    # check if the directory has the desired json file
                    if os.path.exists(file_path):
                        # open the json file as a dictionary
                        with open (file_path) as g:
                            phenojson2 = json.load(g)

                        # check if each data element is in the master dictionary d
                        for kk in phenojson2:

                            if kk in d.keys():
                                continue

                            elif not kk in d.keys():

                                #add type as schema.org/DataElement
                                doc['@type'] = context['@context']['DataElement']
                                doc[context['@context']['sourceVariable']] = str(kk)

                                for subkk in phenojson2[kk]:


                                    if subkk == 'Description':
                                        print("\tFound OpenNeuro_Definition")
                                        doc[context['@context']['description']] = str(phenojson2[kk][subkk])

                                    if subkk == 'LongName':
                                        print("\tFound OpenNeuro_LongName")
                                        doc[context['@context']['label']] = str(phenojson2[kk][subkk])

                                    if subkk == 'TermURL':
                                        print('\tFound OpenNeuro_TermURL')
                                        doc[context['@context']['url']['@id']] = str(phenojson2[kk][subkk])

                                    if subkk == 'Derivative':
                                        print('\tFound OpenNeuro_Derivative')
                                        doc[context['@context']['derivative']] = str(phenojson2[kk][subkk])

                                    if subkk == 'Citation':
                                        print('\tFound OpenNeuro_Citation')
                                        doc[context['@context']['citation']] = str(phenojson2[kk][subkk])

                                    doc[context['@context']['associatedWith']] = str('NIDM')

                                # compact file with doc and context
                                compacted = jsonld.compact(doc,args.context)
                                # add compacted file to the master dictionary d
                                d[kk] = compacted

                            #return updated master dictionary d
                            return d

                    # if no json file is found return master dictionary d
                    elif not os.path.exists(file_path):

                        return d


def main(argv):
    parser = ArgumentParser(description='This program takes a costume csv spreadsheet with annotated terms extracted from '
                                        'both participants.tsv and phenotype.tsv files of OpenNeuro datasets and term properties. '
                                        'I will then create a jsonld representation for each term based on the provided context file.')

    parser.add_argument('-csv', dest='csv_file', required=True, help="Path to csv file to convert. NOTE: the spreadsheet must be in a comma-separated values format")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
    parser.add_argument('-ds_dir', dest='datasets', required=True, help="Path to OpenNeuro datasets directory")
    parser.add_argument('-context', dest= 'context', required=True, help='URL to context file')
    args = parser.parse_args()

    print('Preparing for iteration...')

    #set output directory
    output = args.output_dir

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
    #d = {}

    # put data set Id's in a list
    ds_number = df['ds_number'].tolist()
    # create an empty list for non duplicated dataset ID's
    ds_list = []
    for s in ds_number:
        if s not in ds_list:
            ds_list.append(s)


    global state


    # make directory for every dataset
    for dl in ds_list:
        l = str(dl).zfill(6)

        ## dataset 001107 has a unique structure
        ### files are placed inside a directory titled "eyetracking while movie watching, plus visual localizers"
        #if l == '001107':
            #path_to_dir1 = os.path.join(output,str(l))
        #    if os.path.exists(path_to_dir1):
         #       shutil.rmtree(path_to_dir1)
          #  path_to_dir1 = os.path.join(output,str(l))
           # os.mkdir(path_to_dir1)
            #pathtodataset = os.mkdir(os.path.join(path_to_dir1, 'eyetracking while movie watching, plus visual localizers'))

        #else:


        #create an output directory for each dataset in the main output directory passed to the argument
        path_to_dir = os.path.join(output, str(l))
        if os.path.exists(path_to_dir):
            shutil.rmtree(path_to_dir)
        pathtodataset = os.path.join(output, str(l))
        os.mkdir(pathtodataset, mode = 0o777)


        # lock the dataframe to only read rows with specific ds_number
        dataset = df.loc[df['ds_number'] == dl]

        print('PROCESSING TERMS FROM ds%s' %l)

        #loop through all rows and grab info if exists
        for (i,row) in dataset.iterrows():
            print('starting iteration...')
            #print('processing term: %s'%row['sourceVariable'])

            print(i,row)

            #loc data frame only at terms that are not phenotype terms
            par_ter = dataset.loc[dataset['Phenotype Term?'] == 'NO']

            d = jsonld_dict(par_ter,context,args)

            # loop through the rows and call function json_check to create a master dictionary d
            for ii, rr in par_ter.iterrows():
                print('processing term: %s'%rr['sourceVariable'])




            # opens pre-made directory with with a number that matches the ds ID and creates a jsonld file inside that directory
            with open (join(pathtodataset, 'participants' + '.jsonld'),'w+') as outfile:
                json.dump(json_check(d,args.datasets,str(l),'participants.json',args, context,''),outfile,indent=2)


            print("size of dict: %d" %sys.getsizeof(d))
            d.clear()



            # check if the original dataset dir has a phenotype dir,
            ## if it does create one in the same dataset output directory
            pathtods = args.datasets
            dataset_list = os.listdir(pathtods)
            for p in dataset_list:
                if p[2:] == l:
                    path = os.path.join(pathtods,p)
                    original_phenotype = os.path.join(path, 'phenotype')
                    if os.path.exists(original_phenotype):
                        pathtophenodir = os.path.join(pathtodataset, 'phenotype')
                        if os.path.exists(pathtophenodir):
                            shutil.rmtree(pathtophenodir)
                        os.mkdir(pathtophenodir)



                        #parse through the phenotype directory looking for assessment terms
                        for root, dirs, files in os.walk(original_phenotype, topdown=True):
                            #access sub-directories to extract assessment terms
                            for dir in dirs:
                                sub_dir = os.path.join(original_phenotype, dir)
                                subdir_output = os.path.join(pathtophenodir,dir)
                                os.mkdir(subdir_output)
                                #access tsv files in sub-directories
                                for subroot, subdirs, tsv_files in os.walk(sub_dir):
                                    for FL in tsv_files:
                                        if FL.endswith('.tsv'):
                                            FL_name = FL[:-4]
                                            p_tsv = os.path.join(subroot, FL)
                                            r_tsv = pd.read_csv(p_tsv, error_bad_lines=False)

                                            #exract terms from tsv files
                                            for c in r_tsv.columns :
                                                #create a term list
                                                term_list = c.split("\t")
                                                while '' in term_list:
                                                    term_list.remove('')
                                                for T in term_list:
                                                    if T == 'participant_id':
                                                        term_list.remove('participant_id')

                                                #include only terms that are extracted from the associated tsv file
                                                terms = dataset.loc[dataset['sourceVariable'].isin(term_list)]

                                                #lock pheno_ter dataframe to include only phenotype terms
                                                pheno_ter = terms.loc[terms['Phenotype Term?'] == 'YES']

                                                d = jsonld_dict(pheno_ter,context,args)

                                                #loop through those terms and if the term is a phenotype term pass it to jsonld_dict to create the master dictionary
                                                # for II, R in pheno_ter.iterrows():
                                                #
                                                #     print('starting iteration...')
                                                #     print('processing term: %s'%R['sourceVariable'])
                                                #
                                                #     if R['Phenotype Term?'] == 'YES':
                                                #         print('processing term: %s'%R['sourceVariable'])



                                            # opens pre-made directory with with a number that matches the ds ID and creates a jsonld file inside that directory
                                            with open (join(pathtophenodir, FL_name + '.jsonld'),'w+') as outfile:
                                                json.dump(json_check(d,args.datasets,str(l),FL_name,args,context,pathtophenodir),outfile,indent=2)


                                            print("size of dict: %d" %sys.getsizeof(d))
                                            d.clear()

                                    break


                            #look for tsv files in phenotype directory
                            for file in files:
                                if file.endswith('.tsv'):
                                    file_name = file[:-4]
                                    pathtotsv = os.path.join(root, file)
                                    rtsv = pd.read_csv(pathtotsv, error_bad_lines=False)
                                    #extract terms from tsv files
                                    for col in rtsv.columns :
                                        #create a term list
                                        termlist = col.split("\t")
                                        while '' in termlist:
                                            termlist.remove('')
                                        for t in termlist:
                                            if t == 'participant_id':
                                                termlist.remove('participant_id')

                                        #include only terms that are extracted from the associated tsv file
                                        ter = dataset.loc[dataset['sourceVariable'].isin(termlist)]

                                        #lock pheno_ter dataframe to include only phenotype terms
                                        phenoTer = ter.loc[ter['Phenotype Term?'] == 'YES']

                                        d = jsonld_dict(phenoTer,context,args)

                                        #loop through those terms and if the term is a phenotype term pass it to jsonld_dict to create the master dictionary
                                        # for I, r in ter.iterrows():
                                        #
                                        #     print('starting iteration...')
                                        #     print('processing term: %s'%r['sourceVariable'])
                                        #
                                        #     if r['Phenotype Term?'] == 'YES':
                                        #         print('processing term: %s'%r['sourceVariable'])



                                    # opens pre-made directory with with a number that matches the ds ID and creates a jsonld file inside that directory
                                    with open (join(pathtophenodir, file_name + '.jsonld'),'w+') as outfile:
                                        json.dump(json_check(d,args.datasets,str(l),file_name,args, context,pathtophenodir),outfile,indent=2)

                                    print("size of dict: %d" %sys.getsizeof(d))
                                    d.clear()

                            break

                # reset the path to its original state datasets
                path = args.datasets

            break




if __name__ == "__main__":
   main(sys.argv[1:])



