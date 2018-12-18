# offline_analysis
This repository hosts pipelines to extract features from raw data. 

## Table of Contents 
- galvanic
- cardiac
- respiration
- vr_behavior
- vr_survey
- cognitive_tests
- eyetracking
- eeg
- psychometrics
- phenomenology

## Installation
First, install anaconda /!\ important: use Python in version 3.6+, not version 2.7.

Open a terminal, navigates to the code folder, and type

```
conda create -n offline python=3
source activate offline
conda install --yes --file requirements.txt
pip install git+https://github.com/OpenMindInnovation/datascience_utils
```

This will create a virtual environment and install all dependencies.

## Authors 
Astrid Kibleur, Pierre Clisson, Raphaëlle Bertrand-Lalo

