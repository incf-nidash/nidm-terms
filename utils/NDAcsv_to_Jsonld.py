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
    This function pareses ValueRange strings with different formats and assigns them to the proper jsonld terms.

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
    temp_level=''
    level=[]
    state=1
    #for digit in row:
    #    if row in '':
    #        continue
    #    else:
    #        if (digit.isdigit()):
    #            if (digit.isdigit()) and state==1:
    #                aval = aval + digit
    #                if digit == ':':
    #                    state=2
    #                elif digit ==':' and state==2:
    #                    state=3
    #                    minimum = aval
    #                elif (digit.isdigit()) and state==3:
    #                    maximum = maximum + digit
    #                elif digit == ';' and state==3:
    #                    additional_values = additional_values + digit
    #                    state=4
    #                elif digit.isdigit() and state==4:
    #                    additional_values = additional_values + digit
    #            else:
    #                values = values + digit
    #                values = digit.split(';')
    #        elif digit.isalpha() or digit.isalpha() and digit.isdigit():
    #            temp_level = temp_level + digit
    #            if digit == ';' and state == 1:
    #                level.append(temp_level)
    #                temp_level = ''


        #if (digit.isdigit()) and state==1:
         #   minimum=minimum + digit
        #elif digit == ':':
         #   state=2
         #   continue
        #elif (digit.isdigit()) and state==2:
         #   maximum=maximum + digit
        #elif digit == ';' and state==2:
         #  additional_values.append(digit)
         #  state=3
        #elif digit == ';' and state == 1:
         #   state=3
         #   continue
        #elif digit.isdigit() and state==3:
         #   additional_values.append(digit)
        #elif (digit.isalpha() and (state==1 or state==4)):
         #   level.append(digit)
         #   state = 4
        #elif digit == ';' and state == 4:
         #   continue
        #  temp_level=''





    if isinstance(row,float) and np.isnan(row) :
        return

    # split value range at colons and semicolons
    semicolon_splits = row.split(';')
    colon_splits = row.split("::")

    # parse and evaluate values separated by semicolons only
    if len(semicolon_splits) > 1:
        for token in semicolon_splits:
            if token.isdigit() and len(level) == 0:
                additional_values.append(int(token))
            elif not token.isdigit():
                level.append(token)
            elif token.isdigit() and len(level) > 0:
                level.append(token)
    elif not semicolon_splits[0][0].isdigit():
        additional_values.append(semicolon_splits)
    if len(additional_values) > 1:
        minimum = min(additional_values)
        maximum = max(additional_values)

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
            temp = token.split(';')
            if len(temp) > 1:
                maximum = max(temp)
                additional_values.append(temp)

        doc[context['@context']['minimumValue']] = int(minimum)
        doc[context['@context']['maximumValue']] = int(maximum)

    doc[context['@context']['allowableValues']] = additional_values






    #if (additional_values!='') and (int(additional_values) > int(maximum)):
    #    maximum = additional_values

#    if minimum != '' and maximum != '':
#        for i in range(int(minimum),int(maximum)):
#           doc[context['@context']['allowableValues']] = doc[context['@context']['allowableValues']] + "," + int(i)
#        if additional_values != '':
#           doc[context['@context']['allowableValues']] = doc[context['@context']['allowableValues']] + "," + str(additional_values)


#    if minimum != '':
#       doc[context['@context']['minimumValue']] = doc[context['@context']['minimumValue']] + "," + minimum
#
#    if maximum != '':
#        doc[context['@context']['maximumValue']] = doc[context['@context']['maximumValue']] + "," + maximum







def main(argv):
    parser = ArgumentParser(description='This program will load in a custom Excel spreadsheet and create separate'
                                        'JSON files for each term in Column D, description in Column E, URL in'
                                        'Column F, and will add (as placeholder) columns A and B as isAbout.'
                                        'See https://docs.google.com/spreadsheets/d/1_hUJQRcMDIzWYTsVLDEoipTGrFHytXEaVBlrheVRlJA/edit')

    parser.add_argument('-csv', dest='csv_file', required=True, help="Path to csv file to convert")
    parser.add_argument('-out', dest='output_dir', required=True, help="Output directory to save JSON files")
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
        print("starting iteration...")
        print("processing term: %s" %row['ElementName'])



        # add type as schema.org/DefinedTerm
        doc['@type'] = context['@context']['DefinedTerm']
        doc[context['@context']['label']] = row['ElementName']

        if not pd.isnull(row['ElementDescription']):
                print("\tFound NDA_Definition")
                doc[context['@context']['description']] = str(row['ElementDescription'])
        else:
            continue
        if not pd.isnull(row['DataType']):
                print("\tFound NDA_Definition")
                if str(row['DataType']) == 'Integer':
                    doc[context['@context']['valueType']] = "xsd:int"
                elif str(row['DataType']) == 'String':
                    doc[context['@context']['valueType']] = "xsd:string"
                elif str(row['DataType']) == 'Date':
                    doc[context['@context']['valueType']] = "xsd:date"
                elif str(row['DataType']) == 'Float':
                    doc[context['@context']['valueType']] = "xsd:decimal"
                elif str(row['DataType']) == 'GUID':
                    doc[context['@context']['valueType']] = "xsd:string"




        parseRV(row,doc,context)


        # placeholder for additional properties that need to be included in CDEs
        # doc[context['@context']["unitCode"]] = 'undefined'
        # doc[context['@context']["unitLabel"]] = 'undefined'
        # doc[context['@context']["valueType"]] = 'undefined'
        # doc[context['@context']["minimumValue"]] = 'undefined'
        # doc[context['@context']["maximumValue"]] = 'undefined'
        # doc[context['@context']["allowableValues"]] = 'undefined'
        # doc[context['@context']["provenance"]] = 'undefined'
        # doc[context['@context']["ontologyConceptID"]] = 'undefined'
        # doc[context['@context']["subtypeCDEs"]] = 'undefined'
        # doc[context['@context']["supertypeCDEs"]] = 'undefined'


       # write JSON file out
        compacted = jsonld.compact(doc,url)
        with open (join(args.output_dir,row['ElementName'].replace("/","_")+".jsonld"),'w+') as outfile:
            json.dump(compacted,outfile,indent=2)

        print("size of dict: %d" %sys.getsizeof(doc))
        doc.clear()

if __name__ == "__main__":
   main(sys.argv[1:])
















