# Term JSON-LD Files

In the following directories terms are stored in [JSON-LD](https://json-ld.org/spec/latest/json-ld/) files.  JSON-LD offers a compromise between being easy to with in popular programming languages as is the case with [JSON](https://www.w3schools.com/whatis/whatis_json.asp), offering human-readable, language-independent communication of data objects consisting of attribute-value pairs in a hierarchical organization, and linked data which is vital for both describing vocabularies and using the web to connect related data that wasn't previously linked.

In NIDM-Terms we start by creating a JSON-LD file for each proposed term.  The terms are then discussed on GitHub, additional properties as outlined below are suggested by the community, and the terms are currated by putting them in context with related terms, super / sub type common data elements and ultimately added to [Interlex](https://scicrunch.org/nidm-terms) for ease of use.

Often people don't know about how their proposed terms should be linked with related concepts or other common data elements.  Don't worry, this is where our broader community comes in.  Submit a term with the most information you have and ask for others to help fill in the missing information!

Adding new terms without a graphical user interface:

* Read the term property definitions below
* Fork the GitHub [terms](https://github.com/NIDM-Terms/terms) repository
* Copy the [DataElementTemplate.jsonld](https://github.com/NIDM-Terms/terms/blob/master/terms/DataElementTemplate.jsonld) file and rename it as the label of your proposed term
* Fill in as much information in the JSON-LD file as you can and create a [pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) to the main repository

Adding new terms with a graphical user interface:

* Read the term property definitions below
* Open the NIDM-Terms [GUI](https://nidm-terms.github.io/)
* Read the 'About' page in the [GUI](https://nidm-terms.github.io/) for instructions on adding new terms 



## Data Element Properties

Below is an exhaustive set of possible term properties.  The specific term you are proposing will dictate which properties below are needed.  See examples below for more information.

  * **"description":** An explanation of the nature, scope, or meaning of the new term.
  * **"url":** Typically when adding a new term the URL will be automatically generated when it is incorporated into the NIDM-Terms terminology. If there's an existing url for this term, add it here.
  * **"label":** Label for the term
  * **"source_variable":** Variable name from dataset.  This applies to personal data elements which are data elements defined within a specific study, typicalled referred to as "study variables" vs. common data elements which are data elements defined by a community.  
  * **"valueType":** A value representation such as integer, float, string, date/time (e.g. xsd:int, xsd:float, xsd:string): see [XSD Data Types](https://www.w3schools.com/xml/schema_simple.asp). Typical types for terms include: xsd:boolean, xsd:integer, xsd:float, xsd:duration, xsd:dateTime, xsd:time, xsd:date, and xsd:anyURI.  For categorical variables please use xsd:complexType.
  * **"unitCode":** Unit of measurement.  Currently we don't have any standardized units measures so this is a simple string identifying the unit (e.g. years, millimeters, etc.)     
  * **"maxValue":** The upper value of the data element or NA if not applicable
  * **"minValue":** The lower value of the data element or NA if not applicable
  * **"allowableValues":** For categorical variables the allowable values.  For example, handedness may be Right=1, Left=5, Ambidextrious=10 so the allowableValues is the set 1,5,10
  * **"choices":** Choices is a concept that corresponds to the [BIDS](https://bids.neuroimaging.io/) "levels" standard for categorical variables where you're mapping the value (often an integer) to some text string.  Using the handedness example from above, the choices would be {1=Right, 5=Left, 10=Ambidextrious}.  To encode this in JSON we use the "choices" element as shown:
  	```
	"choices": [
		{
		"name": "Right",
		"value": "1"
		},
		{
		"name": "Left",
		"value": "5"
		},
		{
		"name": "Ambidextrious",
		"value": "10"
		}
	]
	```
  
  * **"isAbout":** Used to store a mapping to a broader concept related to the data element. These annotations can be used to search across datasets. Concept annotations should only be used for terms you think are useful to search across datasets.  For example, if one has a variable that measures "age at visit" with a particular frame of reference (e.g. postnatal) in a particular unit (e.g. months) and another dataset collected a variable "age at scan" with units "year" then we can annotate both variables with a broader concept of [age](http://uri.interlex.org/ilx_0100400) and use this to search for datasets with the concept of "age" without regarding how age was collected.  This approach helps with locating datasets that contain information desired by investigators while abstracting away from the complexity of how these data were stored in the datasets. Once datasets have been identified at this high level, the data dictionaries for each variable in each dataset can be further interrogated using the properties here to determine a proper mapping across variables prior to analysis.  "isAbout" entries using the [DataElementTemplate.jsonld](https://github.com/NIDM-Terms/terms/blob/master/terms/DataElementTemplate.jsonld) are formatted as follows.  Multiple "isAbout" annotations can be formatted in a similar fashion to "choices" using an array ([]) of dictionaries.
  	```
    "isAbout": {
      "@id": "http://uri.interlex.org/ilx_0100400",
      "label": "age"
    }
	```
  * **"associatedWith":**  This can be kept as it is in the [DataElementTemplate.jsonld](https://github.com/NIDM-Terms/terms/blob/master/terms/DataElementTemplate.jsonld).  It is used by the [Interlex](https://scicrunch.org/nidm-terms) information resource to group data elements into buckets where one can quickly query for all data elements that have been used in "NIDM" for example.  One can add additional strings here to do further groupings (e.g. "BIDS" if the data element is part of the canonical BIDS specification).
  
  ### Additional Properties
  
The following properties are not typically added by users for data element definitions.  These properties are added by currators who are linking information resources together (e.g. isPartOf, subtypeCDEs, supertypeCDEs).
  
  * **"isPartOf":** Used to link data elements to assessments (e.g. WASI_Vocab_Raw linked to [WASI scale](https://www.cognitiveatlas.org/task/id/tsk_4a57abb949f12/#).  Typically this is not added by the user and is often done as an additional annotation to link data elements with other clases of information.
  * **"measureOf":** Describe what the data element measures (e.g. volume, area, distance, intensity, health status, duration/period, intelligence).  
  * **"datumType":** What type of datum it is (e.g. range,count,scalar etc.): see [IAO definitions](http://www.ontobee.org/ontology/STATO?iri=http://purl.obolibrary.org/obo/IAO_0000109)
  * **"provenance":** A description of how the data element is recorded or derived, where it came from, etc.
  * **"subtypeCDEs":** This property is typically added during term curation.  It links the term to lower-level (child) terms in the NIDM-Terms terminology if applicable.
  * **"supertypeCDEs":** This property is typically added during term curation.  It links the term to higher-level (parent) terms in the NIDM-Terms terminology if applicable.

  

## Examples

### Example 1 - Categorical Personal Data Element

In this example, we have collected a variable in our study which stores the measurement of "gender". The variable name in our internal dataset to store this data is simply called "gender".  Our variable is categorical and internally we store "m" for "male" and "f" for "female".  In our JSON-LD representation for this term below we capture both the values "m" or "f" and their textual representation of "male" or "female".

For this variable we think it's a variable the community would want to query for across publicly available datasets.  For example, it's often the case that one would query for datasets that contain a measure of gender along with other measures such as datasets that have anatomical MRI images or a measure of age, etc.  Not all personal data elements need to have a concept association.  For example, a variable that stores scanner software version is likely not something one would use in a query across publicly available data.  With the isAbout property we're attempting to provide a high-level mechanism to query across datasets and thus one should restrict adding isAbout properties to the most relevant data elements.

How does one locate concepts to add in the isAbout property?  There are multiple ways to find these.  First, look in the already used for annotating datasets [NIDM-Concepts](https://nidm-terms.github.io/).  Next, if you can't find one there, check out [Cognitive Atlas](https://www.cognitiveatlas.org/) and [SciCrunch/Interlex](https://scicrunch.org/nidm-terms).  Even easier, if you want to do all of this using a command-line tool, check out [PyNIDM's](https://github.com/incf-nidash/PyNIDM) [csv2nidm](https://pynidm.readthedocs.io/en/latest/#csv-file-to-nidm-conversion) tool.

````
	{
	  "@context": "https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld",
	  "@type": "PersonalDataElement",
      "description": "gender of the participant",
      "sourceVariable": "gender",
      "associatedWith": "NIDM",
      "responseOptions": {
        "choices": [
        	{
           		"name": "male",
           		"value": "m"
			},
          	{
           		"name": "female",
            	"value": "f"
          	}
        ],
        "valueType": "xsd:string"
      },
      "isAbout": {
        "@id": "http://uri.interlex.org/ilx_0738437",
        "label": "gender"
      }
     }
````  

### Example 2 - Integer Personal Data Element

Similar to the example above, here we have a personal data element from a dataset where the internal variable name was "age at mri scan" is of valueType xsd:integer with valid age ranges from 10-80 years.  It has been associated with a concept for measuring age through the isAbout property.

````
	{
	  "@context": "https://raw.githubusercontent.com/NIDM-Terms/terms/master/context/cde_context.jsonld",
	  "@type": "PersonalDataElement",
      "description": "age of the participant at time the MRI scan was collected",
      "sourceVariable": "age at mri scan",
      "associatedWith": "NIDM",
      "responseOptions": {
        "valueType": "xsd:integer",
		"minValue":"10",
		"maxValue":"80",
		"unitCode":"years"
      },
      "isAbout": {
        "@id": "http://uri.interlex.org/ilx_0100400",
        "label": "age"
      }
     }
```` 

