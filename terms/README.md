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
  * **"label":** Short label for the term
  * **"valueType":** 
  * **"unitCode":** The unit of measurement given using the UN/CEFACT Common Code (3 characters) or a URL. Other codes than the UN/CEFACT Common Code may be used with a prefix followed by a colon.  See the [Metric Interchange Format](https://people.csail.mit.edu/jaffer/MIXF/) for SI units and numerical value strings.
  * **"unitLabel":** A string or text indicating the unit of measurement. Useful if you cannot provide a standard unit code for [unitCode](https://units.unf.edu/) 
  * **"maximumValue":** The upper value of the term
  * **"minimumValue":** The lower value of the term
  * **"allowableValues":** For categorical variables the allowable values.  For example, handedness may be Right=1, Left=5, Ambidextrious=10 so the allowableValues is the set 1,5,10
  * **"levels":** Levels is a concept that corresponds to the [BIDS](https://bids.neuroimaging.io/) standard for categorical variables where you're mapping the value (often an integer) to some text string.  Using the handedness example from above, the levels would be {1=Right, 5=Left, 10=Ambidextrious}
  * **"isAbout":** This property is typically added during term curation.  It is a link to terms that this term "is about" providing context for this term amongst broader terminologies.
  * **"hasMeasurementType":**
  * **"hasDatumType":**
  * **"provenance":** A description of how the data element is recorded or derived.
  * **"subtypeCDEs":** This property is typically added during term curation.  It links the term to lower-level (child) terms in the NIDM-Terms terminology if applicable.
  * **"supertypeCDEs":** This property is typically added during term curation.  It links the term to higher-level (parent) terms in the NIDM-Terms terminology if applicable.
  * **"relatedConcepts":** This property is typically added during term curation where one can link this term to broader concepts.
  

## Examples

WIP