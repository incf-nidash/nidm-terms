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




# parse lists with different string formats
def parseRV(df_row,doc,context):
    '''
    This function parse ValueRange strings with different formats and assigns them to the proper jsonld terms.

    :param df_row:
    :param doc:
    :param context:
    :return: row, doc, context
    '''
    # extract the ValueRange column from the data frame
    row = df_row['ValueRange']


    minimum=9999999999999
    maximum=-999999999999
    additional_values=[]
    level=[]


    # passes over rows with no values
    if isinstance(row,float) and np.isnan(row) :
        return

    # split value range at colons and semicolons
    semicolon_splits = row.split(';')
    colon_splits = row.split("::")

    # parse and evaluate values separated by semicolons only and assigns them to allowable values
    if len(semicolon_splits) > 1:
        for token in semicolon_splits:
            if token.isdigit() and len(level) == 0:
                additional_values.append(int(token))
                doc[context['@context']['allowableValues']] = semicolon_splits
            elif not token.isdigit():
                level.append(token)
                doc[context['@context']['allowableValues']] = semicolon_splits
            elif token.isdigit() and len(level) > 0:
                level.append(token)
    elif not semicolon_splits[0][0].isdigit():
        additional_values.append(semicolon_splits)
        doc[context['@context']['allowableValues']] = additional_values
    if len(additional_values) > 1:
        minimum = min(additional_values)
        maximum = max(additional_values)
        doc[context['@context']['minimumValue']] = int(minimum)
        doc[context['@context']['maximumValue']] = int(maximum)


    # parse and evaluate values separated by colons and semicolons and return min and max values
    if len(colon_splits) > 1:
        for token in colon_splits:
            token=token.rstrip().lstrip()
            if token.isdigit():
                if int(token) < minimum:
                    minimum = int(token)
                    additional_values.append(minimum)
                elif int(token) > maximum:
                    maximum = int(token)
                allowable_range = list(range(int(minimum),int(maximum)))
                allowable_range.append(maximum)
                doc[context['@context']['allowableValues']] = allowable_range
            minimum1 = minimum
            temp = token.split(';')
            # detect out of range values, set the maximum number, and include them in allowable values
            if len(temp) > 1:
                maximum = max(temp)
                min_range = int(min(temp))
                additional_values.append(temp)
                allowable_range = list(range(int(minimum1),int(min_range)))
                allowable_range.append(min_range)
                doc[context['@context']['allowableValues']] = allowable_range
                # in the case of out of range negative numbers this statement adjust the minimum and maximum values and still includes the negative number in allowable values
                if min_range < 0:
                    allowable_range = list(range(int(minimum1),int(maximum)))
                    allowable_range.append(int(maximum))
                    allowable_range.append(min_range)
                    doc[context['@context']['allowableValues']] = allowable_range

        # assign minimum and maximum values
        doc[context['@context']['minimumValue']] = int(minimum)
        doc[context['@context']['maximumValue']] = int(maximum)




def parseNotes(df_row,doc,context):

    row = df_row['Notes']
    # passes over rowns with no values


    split_string = []
    equal_split = []
    levels = []
    check = ''
    split_at_space = []
    levels1n2 = []
    word = ''
    lev1n2 = []
    equalsplit = []


    if isinstance(row,float) and np.isnan(row) :
        return

    if row == '?':
        return

    split_at_semicolon = row.split(';')


    if len(split_at_semicolon) > 1:
        for s in range (0, len(split_at_semicolon)):
            semi_string = split_at_semicolon[s]
            for l in semi_string:
                if semi_string[0] == 'In years':
                    doc[context['@context']['unitLabel']] = semi_string[0]
                elif l == '=':
                    equalsplit = semi_string.split('=')
                    #lev1 = equalsplit[0]
                    #lev2 = equalsplit[1]
                    #lev1n2 = [[lev1],[lev2]]
                    equalsplit.append(equalsplit)
                doc[context['@context']['levels']] = str(equalsplit)


        #for x in split_at_semicolon:
         #   equal_split = x.split('=')
         #   level1 = equal_split[0]
          #  level2 = equal_split[1]
           # levels1n2 = [[level1],[level2]]
            #levels1n2.append(levels1n2)
                    #assign levels
        #doc[context['@context']['levels']] = str(levels1n2)


    else:
        string = row
        equal_split_t = string.split('=')
        space_split = string.split()

        if len(equal_split_t) > 1:
            doc[context['@context']['levels']] = equal_split_t
        for element in space_split:
            for z in element:
                if z == ':':
                    colon_split = space_split.split(':')
                    level_1 = colon_split[0]
                    level_2 = colon_split[1]
                    doc[context['@context']['levels']] = str[[level_1],[level_2]]
                else:
                    split_string = string.split()
                    if split_string[0] == 'Enter':
                        doc[context['@context']['allowableValues']] = '0'
                        doc[context['@context']['unitLabel']] = string
                    else:
                        #assign text to an appropriate property
                        doc[context['@context']['unitLabel']] = string

def rangeParser(row,doc,resDoc,context):

    row = row['ValueRange']


    if not pd.isnull(row):
        print("\tFound NDA_ValueRange")


        split_at_colon = row.split('::')


        if len(split_at_colon) > 1:


            split_at_semi_after_colon = split_at_colon[1].split(';')

            if len (split_at_semi_after_colon) > 1:
                resDoc[context['@context']['minValue']] = split_at_colon[0].rstrip().lstrip()
                resDoc[context['@context']['maxValue']] = split_at_semi_after_colon[0].rstrip().lstrip()

                doc[context['@context']['responseOptions']['@id']] = resDoc
                return doc

            elif len(split_at_semi_after_colon) == 1:
                resDoc[context['@context']['minValue']] = split_at_colon[0].rstrip().lstrip()
                resDoc[context['@context']['maxValue']] = split_at_colon[1].rstrip().lstrip()

                doc[context['@context']['responseOptions']['@id']] = resDoc
                return doc



        elif len(split_at_colon) == 1:
            split_at_semicolon = row.split(';')

            #check if the value of the string is numerical value
            for item in split_at_semicolon:
                for c in item:
                    if c.isdigit() is True and len(split_at_semicolon) == 2:
                        ##set min and max values
                        resDoc[context['@context']['minValue']] = split_at_semicolon[0].rstrip().lstrip()
                        resDoc[context['@context']['maxValue']] = split_at_semicolon[1].rstrip().lstrip()

                        doc[context['@context']['responseOptions']['@id']] = resDoc
                        return doc


                    else:
                        #set list of strings to allowable values
                        resDoc[context['@context']['allowableValues']] = split_at_semicolon
                        doc[context['@context']['responseOptions']['@id']] = resDoc

                        return doc







def choicesParser(row, doc, resDoc,context):

    row = row['Notes']

    allowableValues = []

    choices = []

    choice = {}

    if not pd.isnull(row):
        print("\tFound NDA_Notes")

        split_at_semicolon = row.split(';')

        if len(split_at_semicolon) > 1:

            for item in split_at_semicolon:
                item.rstrip()
                item.lstrip()

                split_at_equal = item.split('=')

                if len(split_at_equal) == 1:
                    resDoc[context['@context']['allowableValues']] = split_at_semicolon
                    doc[context['@context']['responseOptions']['@id']] = resDoc
                    return doc

                elif len(split_at_equal) > 1:

                    choice[context['@context']['name']] = split_at_equal[0].rstrip().lstrip()
                    choice[context['@context']['value']] = split_at_equal[1].rstrip().lstrip()

                    choices.append(choice)
                    choice = {}

        elif len(split_at_semicolon) == 1:

            split_at_single_equal = split_at_semicolon[0].split('=')

            if len(split_at_single_equal) > 1:

                choice[context['@context']['name']] = split_at_single_equal[0].rstrip().lstrip()
                choice[context['@context']['value']] = split_at_single_equal[1].rstrip().lstrip()

                resDoc[context['@context']['choices']] = choice
                doc[context['@context']['responseOptions']['@id']] = resDoc

            elif len(split_at_single_equal) == 1:
                doc[context['@context']['comment']] = split_at_single_equal[0]
                return doc



        ##Add an if statement to test if choices has a single dict or and array and assign to response options
        if len(choices) == 0:
            return doc
        elif len(choices) == 1:
            resDoc[context['@context']['choices']] = choices[0]
            doc[context['@context']['responseOptions']['@id']] = resDoc
        elif len(choices) > 1:
            resDoc[context['@context']['choices']] = choices
            doc[context['@context']['responseOptions']['@id']] = resDoc

        return doc





def resOptions(row,doc,context):

    resDoc = {}

    #get element's dataType
    if not pd.isnull(row['DataType']):
        print("\tFound NDA_DataType")

        if str(row['DataType']) == 'Integer':
            resDoc[context['@context']['valueType']] = "xsd:integer"
        elif str(row['DataType']) == 'String':
            resDoc[context['@context']['valueType']] = "xsd:string"
        elif str(row['DataType']) == 'Date':
            resDoc[context['@context']['valueType']] = "xsd:date"
        elif str(row['DataType']) == 'Float':
            resDoc[context['@context']['valueType']] = "xsd:decimal"


    choicesParser(row,doc,resDoc,context)

    rangeParser(row,doc,resDoc,context)

    if bool(resDoc) is False:
        return doc
    elif bool(resDoc) is True:
        doc[context['@context']['responseOptions']['@id']] = resDoc
        return doc



def main(argv):
    parser = ArgumentParser(description='This program will load in an NDA data dictionary as an Excel spreadsheet and create separate'
                                        'JSONLD files for each term. It will also create a single jsonld file that combines all of the terms.')

    parser.add_argument('-csv', dest='csv_file', required=True, help="Path to csv file to convert")
    parser.add_argument('-outOne', dest='output_dir1', required=True, help="Output directory to save the individual JSONLD files")
    parser.add_argument('-outTwo', dest='output_dir2', required=True, help="Output directory to save the single JSONLD file")
    args = parser.parse_args()

    #open CSV file and load into
    df = pd.read_csv(args.csv_file)


    # access the jsonld url
    url = ("https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld")
    # if user supplied a url as a segfile
    if url is not False:

        #try to open the url and get the pointed to file
        try:
            #open url and get file
            opener = ur.urlopen(url)
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


   # starting a new python dictionary
    doc = {}
    # loop through all rows and grab info if exists
    for (i,row) in df.iterrows():

        #skip subjectkey ElementName
        if row['ElementName'] == 'subjectkey':
            continue
        else:

            print("starting iteration...")
            print("processing term: %s" %row['ElementName'])


            # add type as schema.org/DefinedTerm
            doc['@type'] = context['@context']['CommonDataElement']
            doc[context['@context']['label']] = row['ElementName']

            if not pd.isnull(row['ElementDescription']):
                print("\tFound NDA_Definition")
                doc[context['@context']['description']] = str(row['ElementDescription'])


            resOptions(row,doc,context)





            #parseRV(row,doc,context)

            #parseNotes(row,doc,context)


            # placeholder for additional properties that need to be included in CDEs
            # doc[context['@context']["unitCode"]] = 'undefined'
            # doc[context['@context']["unitLabel"]] = 'undefined'
            # doc[context['@context']["provenance"]] = 'undefined'
            # doc[context['@context']["ontologyConceptID"]] = 'undefined'
            # doc[context['@context']["subtypeCDEs"]] = 'undefined'
            # doc[context['@context']["supertypeCDEs"]] = 'undefined'


           # write JSON file out
            compacted = jsonld.compact(doc,url)
            with open (join(args.output_dir1,row['ElementName'].replace("/","_")+".jsonld"),'w+') as outfile:
                json.dump(compacted,outfile,indent=2)

            print("size of dict: %d" %sys.getsizeof(doc))
            doc.clear()




if __name__ == "__main__":
   main(sys.argv[1:])
















