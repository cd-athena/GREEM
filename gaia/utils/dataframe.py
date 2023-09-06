import pandas as pd

def get_dataframe_from_csv(csv_path: str) -> pd.DataFrame:
    '''Returns a pandas dataframe from a CSV file'''
    return pd.read_csv(csv_path)


def merge_benchmark_dataframes(
        emission_df: pd.DataFrame,
        execution_times_df: pd.DataFrame
) -> pd.DataFrame:
    '''Merges emisstion and execution_time pandas dataframes'''
    merged_df = pd.merge(emission_df, execution_times_df, left_index=True, right_index=True)

    return merged_df



def merge_benchmark_and_monitoring_dataframes(
    encoding_results: pd.DataFrame,
    monitoring_df: pd.DataFrame,
    idle_df: pd.DataFrame
) -> pd.DataFrame:
    
    add_idle_energy_to_encoding_results(encoding_results, idle_df)
    
    df_colums: list[str] = ['fan_speed', 'fb_memory_usage.used', 'fb_memory_usage.free',
            'utilization.gpu_util', 'utilization.memory_util',
            'temperature.gpu_temp',
            'clocks.graphics_clock', 'clocks.sm_clock', 'clocks.mem_clock',
            ]

    df_value_dict: dict[
        int, dict[str, object]
        ] = dict()

    for enc_row_idx, encoding_row in encoding_results.iterrows():
        
        df_value_dict[enc_row_idx] = dict()
        
        temp_df = monitoring_df.loc[
            (monitoring_df['current_video'] == encoding_row['video_name']) &
            (monitoring_df['bitrate'] == encoding_row['bitrate'])
            ]
        
        df_value_dict[enc_row_idx].update({'value.count': len(temp_df)})
        
        describe_df = temp_df[df_colums].describe()
        for df_col in df_colums:
            
            temp_dict = {
                f'{df_col}.mean': describe_df[df_col].mean(), 
                f'{df_col}.min': describe_df[df_col].min(), 
                f'{df_col}.max': describe_df[df_col].max(),
                f'{df_col}.std': describe_df[df_col].std(),
            }
            
            df_value_dict[enc_row_idx].update(temp_dict)
    
    copy_df = pd.DataFrame.from_dict(df_value_dict).transpose()
    copy_df = copy_df.convert_dtypes({'value.count': int})
    
    merge_df = pd.merge(encoding_results, copy_df, left_index=True, right_index=True)
    return merge_df

def add_idle_energy_to_encoding_results(
    encoding_results_df: pd.DataFrame,
    idle_df: pd.DataFrame
) -> None:
    idle_df = idle_df.transpose()
    idle_df_seconds = float(idle_df['cpu_energy']) / float(idle_df['cpu_energy_per_second'])
    cpu_idle_energy_per_second = float(idle_df['cpu_energy_per_second'])
    gpu_idle_energy_per_second = float(idle_df['gpu_energy'][0]) / idle_df_seconds
    mem_idle_energy_per_second = float(idle_df['ram_energy'][0]) / idle_df_seconds
    
    encoding_results_df['idle_energy.duration.cpu'] = encoding_results_df['duration'] * cpu_idle_energy_per_second
    encoding_results_df['idle_energy.duration.gpu'] = encoding_results_df['duration'] * gpu_idle_energy_per_second
    encoding_results_df['idle_energy.duration.mem'] = encoding_results_df['duration'] * mem_idle_energy_per_second

if __name__ == '__main__':
    # emission_df: pd.DataFrame = get_dataframe_from_csv(
    #     '../results/emissions.csv')
    # execution_times_df: pd.DataFrame = get_dataframe_from_csv(
    #     '../results/execution_times_2023-07-26_14-17-05.csv')

    # merged_df: pd.DataFrame = merge_benchmark_dataframes(
    #     emission_df, execution_times_df)
    # merged_df.to_csv('../results/merged_results.csv')
    
    encoding_results_df = pd.read_csv('test/encoding_results_2023-09-04_16-47-55.csv', index_col=0)
    print('encoding results', len(encoding_results_df))
    monitoring_df = pd.read_csv('test/monitoring_stream.csv', index_col=0)
    print('monitoring results', len(monitoring_df))
    idle_df = pd.read_csv('test/encoding_idle_time.csv', index_col=0)
    print('idle results', len(idle_df))
    # print(idle_df.transpose().columns)
    
    print('encoding results before method', len(encoding_results_df.columns))
    # add_idle_energy_to_encoding_results(encoding_results_df, idle_df)
    merge_df = merge_benchmark_and_monitoring_dataframes(encoding_results_df, monitoring_df, idle_df)
    print('encoding results after method', len(merge_df.columns))
