# OCM_Snippet_Script
This repository contains:
<ul>
  <li>Three python applications written to automatically update OCM metadata with keyword snippets</li>
  <li>Three .txt thesaurus files used to validate the keywords within the XML metadata files</li>
</ul>

## Instructions
<ol>
  <li>Create your test environment</li>
  <ul>
    <li>Create a new directory and clone this repository</li>
    <li>Create a "latest" and "existing" directory</li> 
    <li>Replace the paths to latest and existing in the code with the paths to your directories</li>
    <li>Ensure that the keyword and ID snippets are located in your working directory and follow this naming convention: 
    inportID_keywords.xml and inportID_identifier.xml</li>
    <li>Make sure that there are metadata files in your latest directory for the script to pick up</li>. 
    <li>You might also want to add some metadata files to the existing directory to test functionality.</li>
  </ul>
  <li>Run OCMHarvest.py</li>
    <ul>
      <li>This script produces a list of metadata files that need to be modified. It then copies these files 
      to the "existing" directory.</li>
    </ul>
  
  <li>Run xpathTest.py</li>
    <ul>
      <li>This script takes a list of files (produced by OCMHarvest.py) and inserts keyword
      and ID snippets into these files.</li>
    </ul>

  <li>Run keywordValidate.py</li>
    <ul>
      <li>This script validates keywords for every file within the list created by OCMHarvest.py</li>
    </ul>
</ol>
