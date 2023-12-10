import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime, timedelta, time

def calculate_distance_matrix(df):
    df = pd.read_csv(df)
    G = nx.from_pandas_edgelist(df, 'id_start', 'id_end', ['distance'], create_using=nx.DiGraph())

    toll_locations = list(G.nodes)

    distance_matrix = pd.DataFrame(index=toll_locations, columns=toll_locations)

    for source in toll_locations:
        for target in toll_locations:
            if source == target:
                distance_matrix.loc[source, target] = 0
            elif pd.isna(distance_matrix.loc[source, target]):
                try:
                    distance = nx.shortest_path_length(G, source=source, target=target, weight='distance')
                    distance_matrix.loc[source, target] = distance
                    distance_matrix.loc[target, source] = distance  
                except nx.NetworkXNoPath:
                    distance_matrix.loc[source, target] = float('nan')
                    distance_matrix.loc[target, source] = float('nan')

    distance_matrix.to_csv('distance_matrix.csv')
    return distance_matrix

def unroll_distance_matrix(distance_matrix):
    distance_matrix = pd.read_csv('distance_matrix.csv')
    distance_matrix_reset = distance_matrix.reset_index()

    unrolled_df = pd.melt(distance_matrix_reset, id_vars='index', var_name='id_end', value_name='distance')

    unrolled_df.columns = ['id_start', 'id_end', 'distance']

    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    unrolled_df.reset_index(drop=True, inplace=True)
    unrolled_df.to_csv('unroll_distance_matrix.csv')
    return unrolled_df



def find_ids_within_ten_percentage_threshold(df, reference_value):
    df = pd.read_csv(df)
     
    reference_rows = df[df['id_start'] == reference_value]

    reference_avg_distance = reference_rows['distance'].mean()

    
    lower_threshold = reference_avg_distance * 0.9
    upper_threshold = reference_avg_distance * 1.1

    
    within_threshold_rows = df[(df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]

    
    result_list = sorted(within_threshold_rows['id_start'].unique().tolist())

    return result_list

def calculate_toll_rate(df):
    
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df

def calculate_time_based_toll_rates(df):

    df = pd.read_csv(df)
    
    time_ranges = {
        'weekday_morning': {'start': time(0, 0, 0), 'end': time(10, 0, 0), 'discount_factor': 0.8},
        'weekday_afternoon': {'start': time(10, 0, 1), 'end': time(18, 0, 0), 'discount_factor': 1.2},
        'weekday_evening': {'start': time(18, 0, 1), 'end': time(23, 59, 59), 'discount_factor': 0.8},
        'weekend': {'start': time(0, 0, 0), 'end': time(23, 59, 59), 'discount_factor': 0.7}
    }

    
    df['start_time'] = pd.to_datetime(df['start_time']).dt.time
    df['end_time'] = pd.to_datetime(df['end_time']).dt.time

    for time_range, params in time_ranges.items():
        mask = (df['start_time'] >= params['start']) & (df['end_time'] <= params['end'])
        df.loc[mask, 'start_day'] = df.loc[mask, 'start_timestamp'].dt.day_name()
        df.loc[mask, 'end_day'] = df.loc[mask, 'end_timestamp'].dt.day_name()
        df.loc[mask, 'moto'] *= params['discount_factor']
        df.loc[mask, 'car'] *= params['discount_factor']
        df.loc[mask, 'rv'] *= params['discount_factor']
        df.loc[mask, 'bus'] *= params['discount_factor']
        df.loc[mask, 'truck'] *= params['discount_factor']

    return df