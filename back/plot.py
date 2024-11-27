import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import pandas as pd
import pickle

# Função auxiliar para escolher o melhor tamanho de janela de suavização para minimizar a última bin incompleta
def choose_best_window_size(length, min_size, max_size, step):
   best_remainder = float('inf')
   best_size = min_size
   
   for window_size in range(min_size, max_size + step, step):
      remainder = length % window_size
      
      if remainder < best_remainder:
         best_remainder = remainder
         best_size = window_size
         
   return best_size
   
# Função para suavizar as coberturas dentro de uma janela menor ideal
def smooth_normalized_coverage(df, arm_lengths, min_size, max_size, step):

   # Dicionário para armazenar coberturas suavizadas
   smoothed_cov_dict = {}
   
   # Itera sobre cada braço cromossômico
   for arm, length in arm_lengths.items():
      # Seleciona o melhor tamanho de janela para o comprimento atual
      window_size = choose_best_window_size(length, min_size, max_size, step)

      # Filtra os dados do DataFrame para o braço atual
      arm_data = df[df['chrom'] == int(arm[0])]  # Pega o cromossomo
      if not arm_data.empty:
         smoothed_cov = []

         # Cria janelas com o tamanho otimizado
         for start in range(0, length, window_size):
            end = start + window_size
            window_data = arm_data[(arm_data['start'] >= start) & (arm_data['end'] <= end)]
            
            # Calcula a mediana se houver dados na janela
            if not window_data.empty:
               median_cov = window_data['corrected_cov'].median()
               smoothed_cov.append(median_cov)
            else:
               smoothed_cov.append(np.nan)  # Atribui NaN para janelas vazias

         # Remove o último bin se for incompleto
         if len(smoothed_cov) > 0 and (length % window_size) != 0:
            smoothed_cov = smoothed_cov[:-1]

         smoothed_cov_dict[arm] = smoothed_cov

   return smoothed_cov_dict

# Função para criar o array de input na CNN com alinhamento dos braços cromossômicos
def create_2d_array(smoothed_cov_dict):
   # Determina o número máximo de bins suavizados para padding
   max_bins = max(len(smoothed_cov_dict[arm]) for arm in smoothed_cov_dict)

   # Inicializa a matriz 2D com valores indefinidos (e.g., NaN)
   input_matrix = np.full((22, max_bins * 2), np.nan)  # Dobra o tamanho para incluir ambos os braços

   # Preenche a matriz com dados de cobertura suavizada
   for i in range(1, 23):  # Apenas os 22 autossomos
      p_arm = f"{i}p"
      q_arm = f"{i}q"
      
      if p_arm in smoothed_cov_dict and q_arm in smoothed_cov_dict:

         # Preenche o braço p à esquerda (invertendo a ordem)
         input_matrix[i-1, max_bins - len(smoothed_cov_dict[p_arm]):max_bins] = smoothed_cov_dict[p_arm]

         # Preenche o braço q à direita
         input_matrix[i-1, max_bins:max_bins + len(smoothed_cov_dict[q_arm])] = smoothed_cov_dict[q_arm]

   return input_matrix

# Função para transformação da matriz por z score
def z_score_transform(matrix):
   # Ignorar NaNs para cálculo de média e desvio padrão
   defined_bins = matrix[~np.isnan(matrix)]
   mean_val = np.mean(defined_bins)
   std_val = np.std(defined_bins)
   
   # Z-score com centralização em 1
   z_scored_matrix = 1 + (matrix - mean_val) / std_val
   
   return z_scored_matrix

# Função para plotar o heatmap a partir da matriz
def plot_heatmap(z_scored_matrix, sample_name, vmin=-3, vmax=3, nan_value=-5):

   # Substituir NaNs pelo valor extremo definido
   z_scored_matrix_filled = np.where(np.isnan(z_scored_matrix), nan_value, z_scored_matrix)

   # Definir colormap ajustado, onde NaN usa uma cor fora da escala
   colors = ["#00004B", "#ADD8E6", "#FFFFFF", "#FFA500", "#FF0000"]  # Cor extra para NaN
   cmap = LinearSegmentedColormap.from_list('custom_colormap', colors)

   # Plotar o heatmap
   plt.figure(figsize=(12, 8))
   heatmap = sns.heatmap(z_scored_matrix_filled, cmap=cmap, cbar=True, 
                        cbar_kws={'orientation': 'horizontal'},
                        vmin=nan_value, vmax=vmax)  # Incluir valores de NaN na escala

   # Adicionar linha tracejada para o centrômero
   max_bins = z_scored_matrix.shape[1] // 2
   plt.axvline(x=max_bins, color='black', linewidth=1.5)
   plt.axvline(x=max_bins, color='white', linestyle='--', linewidth=1.5)

   # Remover o eixo x, mantendo apenas o rótulo do eixo y
   plt.xticks([])
   plt.yticks([])
   plt.ylabel('Chromosome', fontsize=14) 

   # Personalizar a barra de cores
   colorbar = heatmap.collections[0].colorbar
   colorbar.set_ticks([nan_value, vmin, 0, vmax])  # Inclui o valor de NaN como um tick
   colorbar.set_ticklabels(['NaN', str(round(vmin)), 0, str(round(vmax))])  # Define os rótulos dos ticks
   colorbar.ax.set_title('Normalized Coverage', fontsize=14) 

   # Definir o título
   plt.title(f'CNN Bins - {sample_name}', fontsize=16)

   # Salvar figura
   file_name = f'{sample_name}_2D_heatmap.png'
   plt.savefig(file_name, format='png', dpi=300, bbox_inches='tight')