import pandas as pd
# import sys

# sys.path.append("..")


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


if __name__ == '__main__':
    emission_df: pd.DataFrame = get_dataframe_from_csv(
        '../results/emissions.csv')
    execution_times_df: pd.DataFrame = get_dataframe_from_csv(
        '../results/execution_times_2023-07-26_14-17-05.csv')

    merged_df: pd.DataFrame = merge_benchmark_dataframes(
        emission_df, execution_times_df)
    merged_df.to_csv('../results/merged_results.csv')
