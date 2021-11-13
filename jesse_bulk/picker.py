import pandas as pd
import pathlib

def filter_and_sort_dna_df(csv_path : str, cfg: dict):
    dna_df = pd.read_csv(csv_path, encoding='utf-8', sep='\t')

    # old csv
    if 'dna' not in dna_df:
        dna_df = pd.read_csv(csv_path, encoding='utf-8')
        dna_df.rename(columns={"training_log.win-rate": "training_log.win_rate",
                               "training_log.PNL": "training_log.net_profit_percentage",
                               "testing_log.win-rate": "testing_log.win_rate",
                               "testing_log.PNL": "testing_log.net_profit_percentage"}, inplace = True)

    dna_df.drop_duplicates(subset=['dna'], inplace=True)

    for metric in cfg['filter_dna']['training'].items():
        key = metric[0]
        min_value = metric[1]['min']
        if min_value and min_value != 'None':
            dna_df.drop(dna_df[dna_df[f'training_log.{key}'] < min_value].index, inplace = True)
        max_value = metric[1]['max']
        if max_value and max_value != 'None':
            dna_df.drop(dna_df[dna_df[f'training_log.{key}'] > max_value].index, inplace = True)

    for metric in cfg['filter_dna']['testing'].items():
        key = metric[0]
        min_value = metric[1]['min']
        if min_value and min_value != 'None':
            dna_df.drop(dna_df[dna_df[f'testing_log.{key}'] < min_value].index, inplace = True)
        max_value = metric[1]['max']
        if max_value and max_value != 'None':
            dna_df.drop(dna_df[dna_df[f'testing_log.{key}'] > max_value].index, inplace = True)

    dna_df.sort_values(by=[cfg['sort_by']], ascending=False, inplace=True)
    old_name = pathlib.Path(csv_path).stem
    new_path = pathlib.Path(csv_path).with_stem(f'{old_name}-picked')
    dna_df.to_csv(new_path, header=True, index=False, encoding='utf-8', sep='\t')

    return dna_df

