# NIDM-Terms

## Project Description
### THE NEUROIMAGING DATA MODEL: FAIR DESCRIPTORS OF BRAIN INITIATIVE IMAGING EXPERIMENTS NIH RF1 MH120021

Reuse of existing neuroscience data relies, in part, on our ability to understand the experimental design and study data. Historically, a description of the experiment is provided in textual documents, which are often difficult to search, lack the details necessary for data reuse, and are hampered by differences in terminologies across related fields of neuroscience. Our vision is to build on existing resources to create annotation and discovery tools that are based on a metadata standard expressive enough to provide unambiguous descriptions of the experimental methods and metadata. In this proposal, we develop the Experiment component of the Neuroimaging Data Model (NIDM-E), a metadata format leveraging techniques from the semantic web, capable of precisely describing information about the design and intent of an experiment, experimental subject characteristics, and the acquired data. The deliverables of this project focus on developing the terminologies to support NIDM-E and description of BRAIN datasets.

#### Core Project Team

* [David Keator](www.davidkeator.com) - UC Irvine
* [Karl Helmer](https://www.nmr.mgh.harvard.edu/user/6787) – MGH / Harvard
* [Jeff Grethe](https://profiles.ucsd.edu/jeffrey.grethe) – UC San Diego
* [Jean-Baptiste Poline](https://www.mcgill.ca/neuro/jean-baptiste-poline-0) – McGill
* [Satra Ghosh](https://satra.cogitatum.org/group/) – MIT
* [Theo G.M. VanErp](https://www.faculty.uci.edu/profile.cfm?faculty_id=5812) - UC Irvine

### Getting Started

* **How do I search for terms?**

	* As work on the grant matures there will be many ways to search for terms.  Below is a list of available methods to perform broad term searches.  
		* Use our [NIDM-Terms SciCrunch](https://scicrunch.org/nidm-terms) site 
		* Annotating existing BIDS datasets using [PyNIDM's](https://github.com/INCF-NIDASH/PyNIDM) bidsmri2nidm tool		
			* The bidsmri2nidm tool will iterate over your BIDS dataset and help you create JSON "sidecar" files for variables in the TSV files contained.  During annotation, a query for each variable will be sent to the InterLex terminology server allowing the user to select which term is appropriate to annotate their data or provides the capability to add a new term.
		* Annotate existing CSV files using [PyNIDM's](https://github.com/INCF-NIDASH/PyNIDM) csv2nidm tool
			* Similar to the BIDS example, this tool will create a JSON mapping file which relates your variables to terms in the NIDM-Terms vocabulary.  
		* WIP: Use our javascript tool
		
			* This tool works in a similar fashion to bidsmri2nidm and csv2nidm where one can query the InterLex and select terms to annotate a data file and/or create new terms when needed.
			* This tool is a work in progress and will be linked when ready for testing.
		
* **How do I submit new terms and where do they go?**

	* NIDM-Terms is a community-driven vocabulary seeded with terms from prior neuroimaging-based data annotations and existing project (e.g. [ReproSchemas](https://github.com/ReproNim/reproschema), [mentalhealthDB](https://github.com/ChildMindInstitute/mhdb), etc.).  Because it is a community-driven vocabulary, we are developing step-by-step procedures for submitting new terms, community discussion around submitted terms, curration of new terms which connect them (when possible) to existing, related terms, or broader concepts putting new terms in context of other known entities.	
	* WIP: Options for submitting new terms
	
		* Using the [NIDM-Terms GitHub repository](https://github.com/NIDM-Terms/terms/blob/master/terms/README.md)
		* Submit via our website [NIDM-Terms SciCrunch](https://scicrunch.org/nidm-terms)
			* When you submit a new term via the NIDM-Terms website, a JSON-LD file describing the new term and properties will be created and submitted to this archive (see [README](https://github.com/NIDM-Terms/terms/blob/master/terms/README.md))
			* Contributors who have choosen to participate in our community vocabulary building activities by watching this repo or cloning it will receive a notice that a new term has been submitted as a pull request.
			* Discussion / edits to the submitted term will ensue in the typical way social coding is done in GitHub
			* Once discussion has ended and the participating community has decided the term is appropriately well-defined for the NIDM-Terms vocabulary, it will be merged with the NIDM-Terms GitHub repository and pushed to the [NIDM-Terms SciCrunch](https://scicrunch.org/nidm-terms)site for broad use.
				* For those interested in using the JSON-LD files directly, the term description files will remain in this repository as well.
				* For those interested in using/querying terms via [OWL](https://www.w3.org/OWL/)representations, there will be a content negotiation layer added to the [NIDM-Terms SciCrunch](https://scicrunch.org/nidm-terms) site to download the NIDM-Terms vocabulary in common RDF serialization formats.

* **WIP: How do I contribute to NIDM-Terms?**
	 
	 * We are firm supporters of open science and inclusivity.  We are always happy to have interested people involved. Below are some steps to get involved.
	 * Create a free account on our [NIDM-Terms SciCrunch](https://scicrunch.org/nidm-terms)site and click "Join the NIDM Terminology Community" link
	 * Fork our [NIDM-Terms GitHub repository](https://github.com/NIDM-Terms/terms)

* **WIP: Term curration and Governance**
	* We are currently working on a governance structure for this work.  We are basing it on other open science projects.  Please stay tuned for more information.
	  
### Demos

BIDS Sidecar File - OpenNeuro Concept Query Demo: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NIDM-Terms/terms/master?filepath=utils%2Fquery_demo)
	* In this query demonstration we use the NIDM-Terms augmented BIDS JSON sidecar files which now contain concept-level associations between selected dataset-specific variables and broader concepts.  Using this mechanism we can load each of the BIDS sidecar files, create an internal dictionary of dataset x concept and then build a query to find datasets based on user-selected concepts. 
	
NIDM - OpenNeuro Concept Query Demo: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NIDM-Terms/terms/master?filepath=utils%2Fquery_demo)
	* Compared to the BIDS sidecar file query demonstration, this one uses the NIDM semantic web documents directly.  Because we used the pynidm tool [bidsmri2nidm](https://github.com/incf-nidash/PyNIDM/blob/master/nidm/experiment/tools/bidsmri2nidm.py), we have access within the NIDM file to other imaging-related metadata beyond just the information contained in the BIDS sidecar file. If one were interested in loading the NIDM files into a RDFLib graph object one could use the RDFLib SPARQL query engine directly to perform queries.  Because we have many OpenNeuro datasets (> 150), we benefit from having a graph-based database server perform the query.  In this example, we have loaded the OpenNeuro dataset NIDM files into the ReproLake graph resource.  Here we simply post a SPARQL query to that resource and retrieve the results.

### Concept Use Frequency

Currently we've mined the OpenNeuro database and annotated the datasets to include high-level concept annotations to improve search across datasets.  We've also formalized the terms used in the canonical BIDS specification.  Below are the frequencies of use of concepts for those annotations. 

[Frequency Chart](https://github.com/NIDM-Terms/terms/blob/master/terms/concept_freq.md) 