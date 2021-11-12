import pandas as pd
import pathlib

def filter_and_sort_dna_df(csv_path : str, cfg):

    dna_df = pd.read_csv('data.csv', encoding='utf-8', sep ='\t')

    dna_df.drop_duplicates(subset=['dna'], inplace=True)

    for key, value in cfg['filter_dna']['training']:
        min_value = value['min']
        if min_value:
            dna_df.drop(dna_df[dna_df[f'training_log.{key}'] < min_value].index, inplace = True)
        max_value = value['max']
        if max_value:
            dna_df.drop(dna_df[dna_df[f'training_log.{key}'] > max_value].index, inplace = True)

    for key, value in cfg['filter_dna']['testing']:
        min_value = value['min']
        if min_value:
            dna_df.drop(dna_df[dna_df[f'testing_log.{key}'] < min_value].index, inplace = True)
        max_value = value['max']
        if max_value:
            dna_df.drop(dna_df[dna_df[f'testing_log.{key}'] > max_value].index, inplace = True)

    dna_df.sort_values(by=[cfg['sort_by']], inplace=True)
    old_name = pathlib.Path(csv_path).name
    new_path = pathlib.Path(csv_path).with_name(f'{old_name}-picked')
    dna_df.to_csv(new_path, header=True, index=False, encoding='utf-8', sep='\t')

