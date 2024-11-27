import numpy as np
import pandas as pd

def choose_best_window_size(length, min_size, max_size, step):
    best_remainder = float('inf')
    best_size = min_size
    for window_size in range(min_size, max_size + step, step):
        remainder = length % window_size
        if remainder < best_remainder:
            best_remainder = remainder
            best_size = window_size
    return best_size

def smooth_normalized_coverage(df, arm_lengths, min_size, max_size, step):
    smoothed_cov_dict = {}
    for arm, length in arm_lengths.items():
        window_size = choose_best_window_size(length, min_size, max_size, step)
        arm_data = df[df['chrom'] == int(arm[0])]
        if not arm_data.empty:
            smoothed_cov = []
            for start in range(0, length, window_size):
                end = start + window_size
                window_data = arm_data[(arm_data['start'] >= start) & (arm_data['end'] <= end)]
                if not window_data.empty:
                    median_cov = window_data['corrected_cov'].median()
                    smoothed_cov.append(median_cov)
                else:
                    smoothed_cov.append(np.nan)
            if len(smoothed_cov) > 0 and (length % window_size) != 0:
                smoothed_cov = smoothed_cov[:-1]
            smoothed_cov_dict[arm] = smoothed_cov
    return smoothed_cov_dict

def create_2d_array(smoothed_cov_dict):
    max_bins = max(len(smoothed_cov_dict[arm]) for arm in smoothed_cov_dict)
    input_matrix = np.full((22, max_bins * 2), np.nan)
    for i in range(1, 23):
        p_arm = f"{i}p"
        q_arm = f"{i}q"
        if p_arm in smoothed_cov_dict and q_arm in smoothed_cov_dict:
            input_matrix[i-1, max_bins - len(smoothed_cov_dict[p_arm]):max_bins] = smoothed_cov_dict[p_arm]
            input_matrix[i-1, max_bins:max_bins + len(smoothed_cov_dict[q_arm])] = smoothed_cov_dict[q_arm]
    return input_matrix

def process_new_sample(file_content, chr_arms, min_size, max_size, step):
    corrected_df = pd.read_csv(file_content, sep='\t')
    smoothed_cov = smooth_normalized_coverage(corrected_df, chr_arms, min_size, max_size, step)
    cov_matrix = create_2d_array(smoothed_cov)
    return np.nan_to_num(cov_matrix)