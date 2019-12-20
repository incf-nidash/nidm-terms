# Term JSON-LD Files

In the following directories terms are stored in [JSON-LD](https://json-ld.org/spec/latest/json-ld/) files.  JSON-LD offers a compromise between being easy to with in popular programming languages as is the case with [JSON](https://www.w3schools.com/whatis/whatis_json.asp), offering human-readable, language-independent communication of data objects consisting of attribute-value pairs in a hierarchical organization, and linked data which is vital for both describing vocabularies and using the web to connect related data that wasn't previously linked.

In NIDM-Terms we start by creating a JSON-LD file for each proposed term.  The terms are then discussed on GitHub, additional properties as outlined below are suggested by the community, and the terms are currated by putting them in context with related terms, super / sub type common data elements and ultimately added to [Interlex](https://scicrunch.org/nidm-terms) for ease of use.

Often people don't know about how their proposed terms should be linked with related concepts or other common data elements.  Don't worry, this is where our broader community comes in.  Submit a term with the most information you have and ask for others to help fill in the missing information!

To begin:

* Read the term property definitions below
* Fork the GitHub [terms](https://github.com/NIDM-Terms/terms) repository
* Copy the [TermTemplate.jsonld](https://github.com/NIDM-Terms/terms/blob/master/terms/TermTemplate.jsonld) file and rename it as the label of your proposed term
* Fill in as much information in the JSON-LD file as you can and create a [pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) to the main repository


## Term Properties Defined

  * "description": 
  * "url":
  * "label":
  * "valueType":
  * "unitCode":
  * "unitLabel":
  * "maximumValue":
  * "minimumValue":
  * "allowableValues":
  * "isAbout":
  * "hasMeasurementType":
  * "hasDatumType":
  * "provenance":
  * "subtypeCDEs":
  * "supertypeCDEs":
  * "relatedConcepts":
  * "termSet":
