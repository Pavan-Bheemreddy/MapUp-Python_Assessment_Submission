import pandas as pd
import numpy as np


def generate_car_matrix(df):
    df = pd.read_csv(df)
    car_df = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)
    np.fill_diagonal(car_df.values, 0)
    return car_df

def get_type_count(df):
    df = pd.read_csv(df)
    def car_count_conditions(value):
        if value <= 15:
            return 'low'
        elif value <= 25:
            return 'medium'
        else:
            return 'high'

    df['car_type'] = df['car'].apply(car_count_conditions)
    car_type_counts = df['car_type'].value_counts().to_dict()
    sorted_car_type_counts = dict(sorted(car_type_counts.items()))
    return sorted_car_type_counts


def get_bus_indexes(df):
    df = pd.read_csv(df)
    req_list = []
    bus_data = df['bus']
    doubled_mean = 2 * (df['bus'].mean())
    for index, value in enumerate(bus_data):
        if value > doubled_mean:
            req_list.append(index)
    return req_list


def filter_routes(df):
    df = pd.read_csv(df)
    grouped_routes = df.groupby('route')
    route_avg_truck = grouped_routes['truck'].mean()

    selected_routes_mask = route_avg_truck > 7
    selected_routes = route_avg_truck[selected_routes_mask].index.tolist()

    sorted_routes = sorted(selected_routes)
    return sorted_routes


def multiply_matrix(df):
    df = pd.read_csv(df)
    df_copy = df.copy()
    def matrix_logic(x):
        if x > 20:
            return round(x * 0.75,1)
        else:
            return round(x * 1.25,1)
    df_copy = df_copy.applymap(matrix_logic)
    return df_copy


def verify_timestamp_completeness():
    df = pd.read_csv('dataset-2.csv')
    df['start_timestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])
    df['end_timestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])
    df['duration'] = df['end_timestamp'] - df['start_timestamp']
    expected_duration = pd.to_timedelta(1, unit='D')


    condition = (
        (df['duration'] != expected_duration) | 
        (df['start_timestamp'].dt.time != pd.to_datetime('00:00:00').time()) |  
        (df['end_timestamp'].dt.time != pd.to_datetime('23:59:59').time()) 
    )
    result_series = df[condition].groupby(['id', 'id_2']).any()['start_timestamp'].fillna(False)
    return result_series