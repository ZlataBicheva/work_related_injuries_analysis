import plotly.express as px
import pandas as pd
from us import states

# Columns to keep
columns_to_keep = ["id", "street_address", "city", "state", "zip_code", "establishment_type", "size", 
                   "type_of_incident", "dafw_num_away", "annual_average_employees", 
                   "total_hours_worked", "djtr_num_tr", "incident_outcome", "date_of_incident"]

def preprocess_data(DATA_PATH):
    """
    Preprocess the dataset by selecting specific columns and dropping missing values.
    """
    # Read the dataset
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # Filter relevant columns
    df = df[columns_to_keep]
    
    # Drop rows with missing values
    df.dropna(inplace=True)

    # Change the column type
    df['establishment_type'] = df['establishment_type'].astype(str).fillna('Unknown')
    df["incident_outcome"] = df["incident_outcome"].astype(str)
    df["type_of_incident"] = df["type_of_incident"].astype(str)
    df['size'] = df['size'].astype(str)

    # Binning djtr_num_tr
    df['djtr_num_tr_binned'] = pd.cut(
        df['djtr_num_tr'], 
        bins=[0, 40, 80, 120, 180, df['djtr_num_tr'].max() + 1], 
        labels=['0-40', '41-80', '81-120', '121-180', '181+'], 
        right=False
    )
    
    # Binning dafw_num_away
    df['dafw_num_away_binned'] = pd.cut(
        df['dafw_num_away'], 
        bins=[0, 5, 10, 20, 50, 100, df['dafw_num_away'].max() + 1], 
        labels=['0-5', '6-10', '11-20', '21-50', '51-100', '100+'], 
        right=False
    )
    
    # Binning annual_average_employees
    df['annual_average_employees_binned'] = pd.cut(
        df['annual_average_employees'], 
        bins=[0, 10, 50, 100, 500, 1000, df['annual_average_employees'].max() + 1], 
        labels=['0-10', '11-50', '51-100', '101-500', '501-1000', '1000+'], 
        right=False
    )
    
    # Binning total_hours_worked
    df['total_hours_worked_binned'] = pd.cut(
        df['total_hours_worked'], 
        bins=[0, 20000, 50000, 100000, 200000, df['total_hours_worked'].max() + 1], 
        labels=['0-20k', '20k-50k', '50k-100k', '100k-200k', '200k+'], 
        right=False
    )
    
    # Binning date_of_incident into monthly periods
    df['date_of_incident_binned'] = pd.to_datetime(df['date_of_incident']).dt.to_period('M').astype(str)
    
    return df




def group_by_state(df):
    """
    Group the dataset by state and count the occurrences of each state, then map to FIPS codes.
    """
    # Group the data by state and count occurrences
    state_counts = df.groupby('state').size().reset_index(name='occurrences')
    
    # Map state abbreviations to FIPS codes
    state_fips_mapping = {state.abbr: state.fips for state in states.STATES}
    manual_mapping = {
        "AS": "60",  # American Samoa
        "DC": "11",  # District of Columbia
        "GU": "66",  # Guam
        "MP": "69",  # Northern Mariana Islands
        "PR": "72",  # Puerto Rico
        "VI": "78"   # U.S. Virgin Islands
    }
    full_mapping = {**state_fips_mapping, **manual_mapping}
    
    # Add FIPS codes to the state counts DataFrame
    state_counts['FIPS'] = state_counts['state'].map(full_mapping)
    
    # # Ensure no missing FIPS codes
    state_counts = state_counts.dropna(subset=['FIPS'])
    state_counts['FIPS'] = state_counts['FIPS'].astype(str)
    
    # # Handle missing or invalid data in occurrences
    state_counts['occurrences'] = state_counts['occurrences'].fillna(0)
    state_counts['occurrences'] = pd.to_numeric(state_counts['occurrences'], errors='coerce')
    
    return state_counts

def visualize_state_map(state_counts):
    """
    Visualize a choropleth map of the United States with data based on state occurrences.
    """
    
    # Ensure at least some non-zero occurrences
    if state_counts['occurrences'].sum() == 0:
        print("Error: All occurrences are zero. The map will not display colors.")
        return
    
    # Plot the choropleth map
    fig = px.choropleth(
        state_counts,
        locations='state',  # Use FIPS codes for geographical locations
        locationmode="USA-states",
        color='occurrences',  # Color based on occurrences
        scope='usa',  # Restrict map to the USA
        color_continuous_scale='Reds'  # Optional: Choose a color scale
    )

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Amount of Injuries",  # Title for the color bar
            # tickvals=[0, 2957, 11252, 21016, 113262],  # Custom tick values
            # ticktext=["0", "3k", "11k", "21k", "113k"],  # Custom tick labels
            tickformat = ",.0f"
        )
    )

    return fig


   # Functions for map
# def group_by_state_data(df):
#     """
#     Group the dataset by state and count the occurrences of each state, then map to FIPS codes.
#     """
#     # Copy the df
#     df_copy_map = df.copy()
#     # Group the data by state and count occurrences
#     state_counts = df_copy_map.groupby('state').size().reset_index(name='occurrences')
    
#     # Map state abbreviations to FIPS codes
#     state_fips_mapping = {state.abbr: state.fips for state in states.STATES}
#     manual_mapping = {
#         "AS": "60",  # American Samoa
#         "DC": "11",  # District of Columbia
#         "GU": "66",  # Guam
#         "MP": "69",  # Northern Mariana Islands
#         "PR": "72",  # Puerto Rico
#         "VI": "78"   # U.S. Virgin Islands
#     }
#     full_mapping = {**state_fips_mapping, **manual_mapping}
    
#     # Add FIPS codes to the state counts DataFrame
#     state_counts['FIPS'] = state_counts['state'].map(full_mapping)
   
    
#     # # Ensure no missing FIPS codes
#     state_counts = state_counts.dropna(subset=['FIPS'])
#     state_counts['FIPS'] = state_counts['FIPS'].astype(str)
    
#     # # Handle missing or invalid data in occurrences
#     state_counts['occurrences'] = state_counts['occurrences'].fillna(0)
#     state_counts['occurrences'] = pd.to_numeric(state_counts['occurrences'], errors='coerce')
    
#     return state_counts


def bin_columns(df):
    """
    Bins specific columns of the input DataFrame and adds new columns with binned values.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing the required columns.
        
    Returns:
        pd.DataFrame: The DataFrame with additional binned columns.
    """
    # Binning djtr_num_tr
    df['djtr_num_tr_binned'] = pd.cut(
        df['djtr_num_tr'], 
        bins=[0, 40, 80, 120, 180, df['djtr_num_tr'].max() + 1], 
        labels=['0-40', '41-80', '81-120', '121-180', '181+'], 
        right=False
    )
    
    # Binning dafw_num_away
    df['dafw_num_away_binned'] = pd.cut(
        df['dafw_num_away'], 
        bins=[0, 5, 10, 20, 50, 100, df['dafw_num_away'].max() + 1], 
        labels=['0-5', '6-10', '11-20', '21-50', '51-100', '100+'], 
        right=False
    )
    
    # Binning annual_average_employees
    df['annual_average_employees_binned'] = pd.cut(
        df['annual_average_employees'], 
        bins=[0, 10, 50, 100, 500, 1000, df['annual_average_employees'].max() + 1], 
        labels=['0-10', '11-50', '51-100', '101-500', '501-1000', '1000+'], 
        right=False
    )
    
    # Binning total_hours_worked
    df['total_hours_worked_binned'] = pd.cut(
        df['total_hours_worked'], 
        bins=[0, 20000, 50000, 100000, 200000, df['total_hours_worked'].max() + 1], 
        labels=['0-20k', '20k-50k', '50k-100k', '100k-200k', '200k+'], 
        right=False
    )
    
    # Binning date_of_incident into monthly periods
    df['date_of_incident_binned'] = pd.to_datetime(df['date_of_incident']).dt.to_period('M').astype(str)
    
    return df






if __name__ == '__main__':
    # Path to the dataset
    DATA_PATH = r"C:\Users\zlata\OneDrive\Документы\tue_y2\q2\JBI100\dashframework_1\data\ita_case_detail_data_2023_through_8-31-2023.csv"
    
    # Preprocess the data
    df = preprocess_data(DATA_PATH)
    
    # Group by state and get counts
    state_counts = group_by_state(df)
    print(state_counts)
    
    # Visualize the choropleth map
    fig = visualize_state_map(state_counts)
    fig.show()


