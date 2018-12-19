# offline_analysis
This repository hosts pipelines to extract features from raw data and a 
generator object to facilitate looping amongst subjects and pipelines. 

## Installation
First, install anaconda /!\ important: use Python in version 3.6+, not version 2.7.

Open a terminal, navigates to the code folder, and type

```
conda create -n offline python=3
source activate offline
conda install --yes --file requirements.txt
pip install git+https://github.com/OpenMindInnovation/datascience_utils
```

This will create a virtual environment and install all dependencies

## Run
```
python main.py --author author_name --config ./test/config/test.yaml --server path/to/database
```
This will :
0) load and parse the yaml config 
1) initialize a generator with: 
    1) a loader, initialized with the parameters specified in field "inputs" from config file
    2) a list of pipelines with the parameters specified in field "pipelines" from config file
2) run the generator, that is: 
    1) loop over all selected files
    2) loop over all listed pipelines
    3) concatenate features horizontaly and datasets vertically
3) save a feature matrice of size (nb_datasets x nb_features) into .pickle & .csv + a description file in .yml 

## Table of Contents 
### helpers
### pipelines
- **galvanic**: extract features from galvanic signal
- **cardiac**: extract features from cardiac signal
- **respiration**: extract features from respiration signal
- **vr_behavior**:...
- **vr_survey**:...
- **cognitive_tests**:...
- **eyetracking**:...
- **eeg**:...
- **psychometrics**:...
- **phenomenology**:...

### utils
- **analysis_config**: class to configurate the generator
- **generator**: class Generator to loop on datasets and extraction pipeline and compute the matrice of features
- **io**: class Loader to select and load data from database 
- **pipeline**: class with abstract method "run" to extract features from raw data

### test
- **config**: placeholder for yaml configs
- **tmp**: placeholder for output features 


## Authors 
Astrid Kibleur, David Ojedan Pierre Clisson, Raphaëlle Bertrand-Lalo

