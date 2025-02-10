import csv
import pandas as pd
import simplejson as json
from pathlib import Path

# example files from data.europa

example_files = [
    {"id": 1, "name": "Realschulen Schulabgaengerinnen nach Abschluss", "title": "de-nrw-dortmund-realschulen_schulabgaengerinnen_nach_abschluss_seit_1990.csv"},
    {"id": 2, "name": "Steueraufkommen nach ausgewaehlten Steuerarten bei den dortmunder Finanzaemtern", "title": "de-nrw-dortmund-steueraufkommen_nach_ausgewaehlten_steuerarten_bei_den_dortmunder_finanzaemtern_seit_1990.csv"},
    {"id": 3, "name": "Straftaten nach Art", "title": "de-nrw-dortmund-straftaten_nach_art_seit_1990.csv"},
    {"id": 4, "name": "Strassenverkehrsunfaelle mit Personen und schwerwiegendem Sachschaden nach Ortslagen", "title": "de-nrw-dortmund-strassenverkehrsunfaelle_mit_personen-_und_schwerwiegendem_sachschaden_nach_ortslagen_seit_1990.csv"},
    {"id": 5, "name": "Studierende der TU Dortmund insgesamt und nach Fakultaeten im Wintersemester", "title": "de-nrw-dortmund-studierende_der_tu_dortmund_insgesamt_und_nach_fakultaeten_im_wintersemester_seit_1990.csv"},
    {"id": 6, "name": "Versorgung mit Energie und Wasser", "title": "de-nrw-dortmund-versorgung_mit_energie_und_wasser_seit_1994.csv"},
    {"id": 7, "name": "Witterungsverhaeltnisse", "title": "de-nrw-dortmund-witterungsverhaeltnisse_seit_1990.csv"},
    {"id": 8, "name": "Abgang von Arbeitslosen", "title": "de-nrw-dortmund-zu-_und_abgang_von_arbeitslosen_seit_1990.csv"},
]

# example_9 = 'altersstruktur_statistischeRaumeinheiten_31122019_0.csv'
# example_10 = 'wahllokale-20210926.csv'

# example_11 = 'suspension_of_economic_activity.csv'
# example_12 = '2021-dublin-city-cycle-counts-08122021.csv'
# example_13 = 'Equiv_BlackCarbon_AETH_2022.csv'
# example_14 = 'estat_urb_ceduc_en.csv'
# example_15 = 'TRA26.20231027122908.csv'
# example_16 = 'balances_comptables_communes_et_ML_2019.csv'
# example_17 = 'messergebnisse_zur_radioaktivität_in_tageskost.csv'
# example_18 = 'estat_lfsa_agaed_en.csv'
# example_19 = 'estat_isoc_cicce_usen2_en.csv'
# example_20 = 'estat_urb_lfermor_en.csv'


#  example_big_file = 'dataset-boja_2023.csv'    # file size 360mb, took about 55 sec to parse -> resulted JSON file size 776mb

# Get the directory of the current script to formulate a relative path
current_dir = Path(__file__).parent

def generate_report(file_id):
    file_title = next((file['title'] for file in example_files if file['id'] == file_id), None)
    if not file_title:
        print('File not found')
    else:
        print(file_title) 
        # chosen example file

        ###########  CSV Parser ###############
        file_path = current_dir / "example_files" / file_title

        # Determine the delimeter of the CSV file
        with open(file_path, 'r', encoding='iso8859-15', errors='replace') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.readline())
            sep = dialect.delimiter

        # Create Dataframe out of the CSV file
        df = pd.read_csv(file_path, sep=sep)
        # Transform the Dataframe into a json object
        json_object = df.to_dict(orient='records')

        ###########  Decision Tree ###############

        # Identify potential timeseries and non-numerical columns
        time_lables = []
        numerical_labels = []
        non_numerical_labels = []

        for col in df.columns:
            non_empty_values = df[col].dropna() # values except NaN
            if non_empty_values.empty:
                continue  # skip columns with completely empty values (otherwise .is_numeric_dtype in line 65 will pass it as numerical)

            # Numerical columns 
            if pd.api.types.is_numeric_dtype(non_empty_values):
                numerical_labels.append(col)
                # Check if all numerical values of a column are within the specified range, then it could indicate a year column
                if all(1800 <= float(value) <= 2100 for value in non_empty_values):
                    time_lables.append(col)
                    non_numerical_labels.append(col)
            else:
                # Categorical columns
                try:
                    # Check if the column can represent a timeseries
                    pd.to_datetime(non_empty_values, errors='raise')
                    time_lables.append(col)
                    non_numerical_labels.append(col)
                except ValueError:
                    non_numerical_labels.append(col)

        # set default view 
        default_view = 'numerical' if len(numerical_labels) > 0 else 'categorical'

        # set default chart type for numerical view 
        default_numerical_view = 'line' if len(time_lables) > 0 else 'bar'

        # set default X&Y-Indicators for Numerical View
        default_x = ''
        if time_lables:
            default_x = time_lables[0]
        elif non_numerical_labels:
            default_x = non_numerical_labels[0]
        # avoid setting default x and y to the same label
        default_y = ''
        if numerical_labels and len(numerical_labels) > 0 and numerical_labels[0] != default_x:
            default_y = numerical_labels[0]
        elif numerical_labels and len(numerical_labels) > 1 and numerical_labels[0] == default_x :
            default_y = numerical_labels[1]

        # Categorize non-numerical columns
        non_numerical_columns = [] # full object containing column label, categories and their count, and optimal view-option. Example: [{'column': 'Jahr', 'categories': {'cat_x': count, 'cat_y': count, ...}, 'view_chart': 'pie'},]
        for catCol in non_numerical_labels:
            non_empty_values =df[catCol].dropna()
            if non_empty_values.empty:
                continue
            category_counts = non_empty_values.value_counts().to_dict()
            # add the column as a categorical column, mark the count of each category and the suitable view type for that column
            non_numerical_columns.append({'column': catCol, 'categories': category_counts, 'view_chart': 'pie' if len(category_counts) <= 20 else 'bar'})


        # Categorical View: set default column label
        max_categories = 0
        default_cat_label = non_numerical_columns[0]['column'] if len(non_numerical_columns) > 0 else ''
        default_cat_view = non_numerical_columns[0]['view_chart'] if len(non_numerical_columns) > 0 else ''

        for column in non_numerical_columns:
            unique_categories = len(column['categories'])
            # Avoid columns that have only one occurence of each category
            if unique_categories > max_categories and any(e > 1 for e in column['categories'].values()):
                max_categories = unique_categories
                default_cat_label = column['column']
                default_cat_view = column['view_chart']

        # construct and build JSON record
        json_record = {
            'default_view_options': {
                'default_view': default_view,
                'default_numerical_view': default_numerical_view,
                'default_categorical_view': default_cat_view,
                'default_axes': {
                    'numerical_chart': {
                    "x": default_x,
                    "y": default_y,
                    },
                    'categorical_chart': default_cat_label
                }
            },
            'labels': {
                'all_labels': df.columns.tolist(),
                'numerical_labels': numerical_labels,
                'categorical_labels': non_numerical_labels,
                'time_labels': time_lables,
            },
            'data': json_object,
            'categorized': non_numerical_columns,
        }    

        return json_record