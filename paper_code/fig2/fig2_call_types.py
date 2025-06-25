# -*- coding: utf-8 -*-
"""
@author: Dori M. Grijseels
"""


import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import silhouette_score

import umap
import hdbscan


def convert_to_R(data, columns):
    shape = data.shape
    index = pd.MultiIndex.from_product([range(s)for s in shape], names=columns)
    df = pd.DataFrame({'data': data.flatten()}, index=index).reset_index()
    return df


def clean_call_types(all_calls):
    all_calls['call_type'] = all_calls['call_type'].replace('gr', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('tw', '?')
    all_calls['call_type'] = all_calls['call_type'].replace('?', 'other')
    all_calls['call_type'] = all_calls['call_type'].replace('oc', 'co')
    return all_calls


def plot_cluster_results(clusters, data):
    # link call types animal ids etc to clusters
    class_data = np.asarray(data)
    classes = np.unique(class_data)
    
    hm_result = np.full((max(clusters), len(classes)), np.nan)
    for c in range(max(clusters)):
        temp = class_data[clusters==(c+1)]
        for j, cl in enumerate(classes):
            hm_result[c, j] = sum(temp==cl)
            
    return hm_result, classes


data_folder = r'..\metadata'
out_folder = r'data'

all_calls = pd.read_csv(os.path.join(data_folder, 'vae_features_dataset_v3.csv'))
all_calls = clean_call_types(all_calls)

# Include only no-touch recordings
all_calls = all_calls[~all_calls['isolate']]

# Create list of all features to include
features = [  'zero_crossings', 'duration', 
            'mean_entropy',  'voiced_perc', 'bandwidth', 'n_peaks']
vae_features = []
n_latent_means = 32
for i in range(n_latent_means):
	vae_features+=[f'latent_mean_{i}']
    
all_features = features + vae_features
all_features_np = np.array(all_features)

# Create dataset for UMAP/random forest
X = all_calls[all_features].to_numpy()
y = all_calls['call_type'].to_numpy()


############### Fig 2A ####################
## Perform UMAP embedding
x_norm = StandardScaler().fit_transform(X)
reducer = umap.UMAP()
embedding = reducer.fit_transform(x_norm)

# Create new DF to plot UMAP in R
umap_df = all_calls[['call_type', 'timepoint', 'animal_id', 'colony']]
umap_df['umap_1'] = embedding[:,0]
umap_df['umap_2'] = embedding[:,1]
umap_df.to_csv(os.path.join(out_folder, 'umap_embedding.csv'), index=False)


############### Fig 2C, E-F ####################
# Calculate high-dimensional embedding
clusterable_embedding = umap.UMAP(
    n_neighbors=30,
    min_dist=0.0,
    n_components=16,
    random_state=42,
).fit_transform(x_norm)


# Perform HDBSCAN clustering
labels = hdbscan.HDBSCAN(
    min_samples=400,
    min_cluster_size=400,
).fit_predict(clusterable_embedding)

# Save out clustering
all_calls_temp = all_calls
all_calls_temp['clusters'] = labels
all_calls_temp['umap_1'] = embedding[:,0]
all_calls_temp['umap_2'] = embedding[:,1]
all_calls_temp.to_csv(os.path.join(out_folder, 'hdbscan_clusters.csv'), index=False)

############### Fig 2D Cluster membership ####################
y_temp = all_calls['call_type'].to_numpy()
hm_result, classes = plot_cluster_results(labels+2, y_temp)


clust_df = convert_to_R(hm_result, [ 'cluster', 'call_type'])
clust_df['call_type'] = classes[clust_df['call_type'].values]

clust_df.to_csv(os.path.join(out_folder, 'clust_vs_call_type.csv'), index=False)


############### Fig 2G Typicality analysis ####################
clusterer  = hdbscan.HDBSCAN(
    min_samples=400,
    min_cluster_size=400,prediction_data=True
).fit(clusterable_embedding)
soft_clusters = hdbscan.all_points_membership_vectors(clusterer)

pup_id = all_calls['animal_id'].unique()
timepoints  = all_calls['timepoint'].unique()
membership_by_ct = pd.DataFrame(columns=['call_type', 'max_mem', 'typicality'])
call_types= all_calls['call_type'].unique()
for pid in pup_id:
    for ct in call_types:
        # get all the labels from this file
        inc  =np.logical_and(all_calls['animal_id']==pid, all_calls['call_type']==ct)
        if sum(inc) > 0:
            temp = all_calls[inc]
            max_mem = np.max(soft_clusters[inc,:], axis=1)
            sort_clusters = np.sort(soft_clusters[inc,:], axis=1)
            entry_ct =  pd.DataFrame.from_dict({
                'animal_ID':  [pid],
                'colony': [temp['colony'].values[0]],
                'call_type': [ct],
                 "max_mem":[np.nanmean(max_mem)],
                 'typicality': [np.nanmean(sort_clusters[:,2]-sort_clusters[:,1])]
            })
            membership_by_ct = pd.concat([membership_by_ct, entry_ct], ignore_index=True)

membership_by_ct.to_csv(os.path.join(out_folder,'membership_by_ct.csv'))


############### Fig S5A Feature correlations ####################
feat_corrs = all_calls[all_features].corr(method='spearman')
feat_corrs_df = convert_to_R(feat_corrs.to_numpy(), ['feat1', 'feat2'])
feat_corrs_df['feat1'] = all_features_np[feat_corrs_df['feat1'].values]
feat_corrs_df['feat2'] = all_features_np[feat_corrs_df['feat2'].values]
feat_corrs_df.to_csv(os.path.join(out_folder, 'feat_correlation.csv'), index=False)


############### Fig S5B Random Forest ####################
# Stratified cross-validation
n_folds = 5
skf = StratifiedKFold(n_splits=5)
skf.get_n_splits(X, y)
mean_cm = np.full([n_folds, 6, 6], np.nan)
for i, (train_index, test_index) in enumerate(skf.split(X, y)):

    print(f"Fold {i}:")
    print(f"  Train: index={train_index}")
    print(f"  Test:  index={test_index}")
    ## Run random forest
    X_train = X[train_index,:]
    y_train = y[train_index]
    X_test = X[test_index,:]
    y_test = y[test_index]
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    cm = confusion_matrix(y_test, y_pred)
    cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    mean_cm[i, :,:] = cmn
 

meaned_cm = np.nanmean(mean_cm, axis=0)
cm_df = convert_to_R(meaned_cm, [ 'true', 'predicted'])

call_types = np.unique(y)
cm_df['true'] = call_types[cm_df['true'].values]
cm_df['predicted'] = call_types[cm_df['predicted'].values]

cm_df.to_csv(os.path.join(out_folder, 'random_forest.csv'), index=False)


############### Fig S5C Silhouette scores ####################
min_samples = [10, 100, 200, 300, 400, 500]
min_cluster_size = [10, 100, 200, 300, 400, 500]

sil_score = np.full((len(min_samples),len(min_cluster_size)), np.nan)
n_of_clusters = np.full((len(min_samples), len(min_cluster_size)), np.nan)
for i, min_samp in enumerate(min_samples):
    for j, min_cluster in enumerate(min_cluster_size):
    
        # Create a subplot with 1 row and 2 columns
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)
    
        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        clusterer =  hdbscan.HDBSCAN(
            min_samples=min_samp,
            min_cluster_size=min_cluster,
        )
        cluster_labels = clusterer.fit_predict(clusterable_embedding)
        cluster_labels = cluster_labels+1
        n_clusters = max(cluster_labels)+1
        n_of_clusters[i,j] = n_clusters
    
        # Calculate avearge silhouette score
        silhouette_avg = silhouette_score(clusterable_embedding, cluster_labels)
        sil_score[i,j] = silhouette_avg

sil_df = convert_to_R(sil_score, [ 'min_sample', 'min_cluster'])

min_samples = np.array(min_samples)
min_cluster_size = np.array(min_cluster_size)

sil_df['min_sample'] = min_samples[sil_df['min_sample'].values]
sil_df['min_cluster'] = min_cluster_size[sil_df['min_cluster'].values]

sil_df.to_csv(os.path.join(out_folder, 'sil_scores.csv'), index=False)


############### Fig S5 cluster usage ####################
sound_types = all_calls_temp['clusters'].unique()
pup_id = all_calls_temp['animal_id'].unique()
timepoints  = all_calls_temp['timepoint'].unique()
sound_counts = pd.DataFrame(columns=['timepoint', 'animal_ID', 'colony']+ sound_types.tolist())

for id in pup_id:
    for tp in timepoints:
        # get all the labels from this file
        df_temp = all_calls_temp[np.logical_and(all_calls['animal_id']==id, all_calls['timepoint']==tp)]
        if len(df_temp)>0:
            timepoint = df_temp['timepoint'].iloc[0]
            animalID = df_temp['animal_id'].iloc[0]
            colony = df_temp['colony'].iloc[0]
            number_of_sounds = len(df_temp)
            sound_count_array = np.zeros((sound_types.__len__(), ))
    
            for s,sound_type in enumerate(sound_types):
            
                # Calculate percentage calls per dataset
                curr_count = len(df_temp[df_temp['clusters']==sound_type])
                sound_count_array[s] = curr_count/number_of_sounds

            sound_counts.loc[len(sound_counts.index)] = [timepoint,animalID,colony] + sound_count_array.tolist()  
        

count_data =pd.DataFrame(columns=['data','vocal_type', 'day', 'vocal_int', 'timepoint', 'animal_id'])
all_animals = sound_counts['animal_ID'].unique()
for animal in all_animals:
    df_temp = sound_counts[sound_counts['animal_ID'] == animal]
    timepoint = df_temp['timepoint'].iloc[0]
    animalID = df_temp['animal_ID'].iloc[0]
    counts =df_temp[sound_types].values
    timepoints  = df_temp['timepoint'].unique()
    
    count_data_temp = convert_to_R(counts, ['timepoint', 'vocal_int'])
    count_data_temp['day'] = timepoints[(count_data_temp['timepoint']).astype(int)]
    count_data_temp['vocal_type'] = sound_types[(count_data_temp['vocal_int']).astype(int)]
    count_data_temp['animal_id'] = animalID
    count_data_temp['colony'] =  df_temp['colony'].iloc[0]
    count_data = pd.concat([count_data, count_data_temp], ignore_index=True)
   

count_data.to_csv(os.path.join(out_folder,'clust_occ_by_animal.csv'), index=False) 

