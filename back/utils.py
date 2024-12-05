import numpy as np
import pandas as pd

def choose_best_window_size(length, min_size, max_size, step):
    """
    Escolhe o melhor tamanho de janela para dividir o comprimento de um cromossomo
    de forma a minimizar o resto na divisão.
    
    Parâmetros:
    - length (int): Comprimento total do cromossomo.
    - min_size (int): Tamanho mínimo da janela.
    - max_size (int): Tamanho máximo da janela.
    - step (int): Incremento no tamanho da janela.

    Retorna:
    - int: O tamanho de janela que minimiza o resto da divisão.
    """
    best_remainder = float('inf')
    best_size = min_size
    for window_size in range(min_size, max_size + step, step):
        remainder = length % window_size
        if remainder < best_remainder:
            best_remainder = remainder
            best_size = window_size
    return best_size

def smooth_normalized_coverage(df, arm_lengths, min_size, max_size, step):
    """
    Suaviza a cobertura normalizada para cada braço cromossômico utilizando uma janela
    de tamanho ideal.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo as informações de cobertura corrigida.
    - arm_lengths (dict): Dicionário com os comprimentos dos braços cromossômicos (p e q).
    - min_size (int): Tamanho mínimo da janela.
    - max_size (int): Tamanho máximo da janela.
    - step (int): Incremento no tamanho da janela.

    Retorna:
    - dict: Dicionário contendo os valores suavizados de cobertura para cada braço.
    """
    smoothed_cov_dict = {}
    for arm, length in arm_lengths.items():
        # Determina o melhor tamanho de janela para o braço cromossômico
        window_size = choose_best_window_size(length, min_size, max_size, step)
        arm_data = df[df['chrom'] == int(arm[0])]  # Filtra os dados para o cromossomo específico
        if not arm_data.empty:
            smoothed_cov = []
            for start in range(0, length, window_size):
                end = start + window_size
                # Seleciona os dados dentro da janela atual
                window_data = arm_data[(arm_data['start'] >= start) & (arm_data['end'] <= end)]
                if not window_data.empty:
                    # Calcula a mediana da cobertura corrigida dentro da janela
                    median_cov = window_data['corrected_cov'].median()
                    smoothed_cov.append(median_cov)
                else:
                    smoothed_cov.append(np.nan)  # Caso não haja dados, insere NaN
            if len(smoothed_cov) > 0 and (length % window_size) != 0:
                smoothed_cov = smoothed_cov[:-1]  # Remove a última janela se incompleta
            smoothed_cov_dict[arm] = smoothed_cov
    return smoothed_cov_dict

def create_2d_array(smoothed_cov_dict):
    """
    Cria uma matriz 2D de cobertura a partir dos valores suavizados para todos os cromossomos.

    Parâmetros:
    - smoothed_cov_dict (dict): Dicionário contendo os valores suavizados de cobertura para cada braço.

    Retorna:
    - np.ndarray: Matriz 2D representando os valores de cobertura para cada cromossomo.
    """
    max_bins = max(len(smoothed_cov_dict[arm]) for arm in smoothed_cov_dict)  # Número máximo de bins
    input_matrix = np.full((22, max_bins * 2), np.nan)  # Matriz inicial preenchida com NaN
    for i in range(1, 23):  # Para cada cromossomo de 1 a 22
        p_arm = f"{i}p"  # Nome do braço p
        q_arm = f"{i}q"  # Nome do braço q
        if p_arm in smoothed_cov_dict and q_arm in smoothed_cov_dict:
            # Preenche os valores do braço p
            input_matrix[i-1, max_bins - len(smoothed_cov_dict[p_arm]):max_bins] = smoothed_cov_dict[p_arm]
            # Preenche os valores do braço q
            input_matrix[i-1, max_bins:max_bins + len(smoothed_cov_dict[q_arm])] = smoothed_cov_dict[q_arm]
    return input_matrix

def process_new_sample(file_content, chr_arms, min_size, max_size, step):
    """
    Processa um arquivo de cobertura para gerar uma matriz 2D de entrada para o modelo.

    Parâmetros:
    - file_content (str): Caminho para o arquivo de cobertura.
    - chr_arms (dict): Dicionário com os comprimentos dos braços cromossômicos.
    - min_size (int): Tamanho mínimo da janela.
    - max_size (int): Tamanho máximo da janela.
    - step (int): Incremento no tamanho da janela.

    Retorna:
    - np.ndarray: Matriz 2D representando os valores de cobertura normalizados e suavizados.
    """
    # Lê o arquivo de cobertura como um DataFrame
    corrected_df = pd.read_csv(file_content, sep='\t')
    # Suaviza a cobertura normalizada
    smoothed_cov = smooth_normalized_coverage(corrected_df, chr_arms, min_size, max_size, step)
    # Cria a matriz 2D
    cov_matrix = create_2d_array(smoothed_cov)
    # Substitui NaN por zeros
    return np.nan_to_num(cov_matrix)
