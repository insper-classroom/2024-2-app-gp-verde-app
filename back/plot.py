import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import os

def plot_heatmap_from_file(txt_path, sample_name, output_dir="analysis/heatmaps"):
    """
    Plota um heatmap 2D a partir de um arquivo TXT contendo os dados de cobertura.
    """
    # Ler o arquivo TXT em um DataFrame
    df = pd.read_csv(txt_path, sep="\t")
    z_scored_matrix = df.values

    # Calcular a média, mínimo e máximo, ignorando NaNs
    mean_value = np.nanmean(z_scored_matrix)
    min_value = np.nanmin(z_scored_matrix)
    max_value = np.nanmax(z_scored_matrix)

    # Definir o valor de NaN como um valor menor que o mínimo
    nan_value = min_value - 0.1
    z_scored_matrix_filled = np.where(np.isnan(z_scored_matrix), nan_value, z_scored_matrix)

    # Definir colormap ajustado
    colors = ["#00004B", "#ADD8E6", "#FFFFFF", "#FFA500", "#FF0000"]
    cmap = LinearSegmentedColormap.from_list("custom_colormap", colors)

    # Plotar o heatmap
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(z_scored_matrix_filled, cmap=cmap, cbar=True,
                          cbar_kws={'orientation': 'horizontal'},
                          vmin=nan_value, vmax=max(max_value, mean_value + (mean_value - min_value)))

    # Configurar o layout do gráfico
    max_bins = z_scored_matrix.shape[1] // 2
    plt.axvline(x=max_bins, color="black", linewidth=1.5)
    plt.axvline(x=max_bins, color="white", linestyle="--", linewidth=1.5)
    plt.xticks([])
    plt.yticks([])
    plt.ylabel("Chromosome", fontsize=14)

    # Personalizar a barra de cores
    colorbar = heatmap.collections[0].colorbar
    colorbar.set_ticks([nan_value, min_value, 0, mean_value, max_value])
    colorbar.set_ticklabels(['NaN', str(round(min_value)), "0", str(round(mean_value)), str(round(max_value))])
    colorbar.ax.set_title("Normalized Coverage", fontsize=14)

    # Salvar a imagem
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{sample_name}_2D_heatmap.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close()

    return output_path
