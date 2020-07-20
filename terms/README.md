# Term JSON-LD Files

In the following directories terms are stored in [JSON-LD](https://json-ld.org/spec/latest/json-ld/) files.  JSON-LD offers a compromise between being easy to with in popular programming languages as is the case with [JSON](https://www.w3schools.com/whatis/whatis_json.asp), offering human-readable, language-independent communication of data objects consisting of attribute-value pairs in a hierarchical organization, and linked data which is vital for both describing vocabularies and using the web to connect related data that wasn't previously linked.

In NIDM-Terms we start by creating a JSON-LD file for each proposed term.  The terms are then discussed on GitHub, additional properties as outlined below are suggested by the community, and the terms are currated by putting them in context with related terms, super / sub type common data elements and ultimately added to [Interlex](https://scicrunch.org/nidm-terms) for ease of use.

Often people don't know about how their proposed terms should be linked with related concepts or other common data elements.  Don't worry, this is where our broader community comes in.  Submit a term with the most information you have and ask for others to help fill in the missing information!

To begin:

* Read the term property definitions below
* Fork the GitHub [terms](https://github.com/NIDM-Terms/terms) repository
* Copy the [TermTemplate.jsonld](https://github.com/NIDM-Terms/terms/blob/master/terms/TermTemplate.jsonld) file and rename it as the label of your proposed term
* Fill in as much information in the JSON-LD file as you can and create a [pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) to the main repository


## Term Properties

Below is an exhaustive set of possible term properties.  The specific term you are proposing will dictate which properties below are needed.  See examples below for more information.

  * **"description":** An explanation of the nature, scope, or meaning of the new term.
  * **"url":** Typically when adding a new term the URL will be automatically generated when it is incorporated into the NIDM-Terms terminology. 
  * **"label":** Label for the term
  * **"source_variable":** Variable name from dataset
  * **"valueType":** A value representation such as integer, float, string, date/time (e.g. xsd:int, xsd:float, xsd:string): see [XSD Data Types](https://www.w3schools.com/xml/schema_simple.asp)
  * **"datumType":** What type of datum it is (e.g. range,count,scalar etc.): see [IAO definitions](http://www.ontobee.org/ontology/STATO?iri=http://purl.obolibrary.org/obo/IAO_0000109) 
  * **"hasUnit":** Unit of measurement following [BIDS specification](https://bids-specification.readthedocs.io/en/stable/99-appendices/05-units.html) 
  * **"maximumValue":** The upper value of the data element
  * **"minimumValue":** The lower value of the data element
  * **"allowableValues":** For categorical variables the allowable values.  For example, handedness may be Right=1, Left=5, Ambidextrious=10 so the allowableValues is the set 1,5,10
  * **"levels":** Levels is a concept that corresponds to the [BIDS](https://bids.neuroimaging.io/) standard for categorical variables where you're mapping the value (often an integer) to some text string.  Using the handedness example from above, the levels would be {1=Right, 5=Left, 10=Ambidextrious}
  * **"isAbout":** Typically a broad context or concept related to the data element. Typically used to search across datasets. It is a link providing context for this term amongst broader terminologies.
  * **"isPartOf":** Used to link data elements to assessments (e.g. WASI_Vocab_Raw linked to [WASI scale](https://www.cognitiveatlas.org/task/id/tsk_4a57abb949f12/#)
  * **"measureOf":** Describe what the data element measures (e.g. volume, area, distance, intensity, health status, duration/period, intelligence) 
  * **"provenance":** A description of how the data element is recorded or derived, where it came from, etc.
  * **"subtypeCDEs":** This property is typically added during term curation.  It links the term to lower-level (child) terms in the NIDM-Terms terminology if applicable.
  * **"supertypeCDEs":** This property is typically added during term curation.  It links the term to higher-level (parent) terms in the NIDM-Terms terminology if applicable.

  

## Examples

WIP
