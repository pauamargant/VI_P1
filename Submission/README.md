# Information Visualization: Project 1
*Authors*: [Pau A.](github.com/pauamargant), [David G.](github.com/dagalligit)

## Introduction
This Project aims to use visualization techniques to produce static visualizations about traffic accidents in new york city. Further detail about the task can be found in the included notebook. 

The project consists of the following files:
- `README.md`: This file, containing the description of the project.
- `process.ipynb`: The notebook containing the description of the process through which the visualizations were made and the analysisis of the results.
- `streamlit_site.py`: The python file containing the code for the streamlit site.
- `graphs.py`: The python file containing the code for the visualizations.

## How to run the project
In order to be able to run the notebook and, more importantly, the streamlit site, you will need to install the dependencies included in the requirements.txt file. To do so, you can run the following command in the terminal:
```bash
pip install -r requirements.txt
```
You can run the process notebook in a Google Colab environment or in a local jupyter notebook. In order to run it in a Google Colab environment, you will need to upload the dataset files and the `graphs.py` file to the environment. You will also need to install the dependencies in the environment. To do so you can upload the `requirements.txt` file to the environment and run the provided cell in the notebook.

You can run the streamlit site by running the following command in the terminal:
```bash
streamlit run streamlit_site.py
```
It is improtant to note that the streamlit visualization uses a pregenerated `svg` file of the map visualization. This is due to an existing bug in altair. Furthermore, due to the transformations which we make to the geopandas dataframe, we were not able to use the github file workaround. This remains an issue left to be solved.


## Data
The project use the following datasets:
- `dataset_v1.csv`: The preprocessed dataset, containing the information about the accidents.
- `new york city 2018-06-01 to 2018-08-31.csv` and `new york city 2020-06-01 to 2020-08-31.csv`: The datasets containing the information about the weather in new york city during the months of june, july and august of 2018 and 2020 respectively.
