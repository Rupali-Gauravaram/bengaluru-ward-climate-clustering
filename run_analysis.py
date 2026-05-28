"""
Bengaluru Ward Climate-Vulnerability Clustering
End-to-end K-Means analysis on 198 BBMP ward-level climate features.
"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 110

DATA = 'data/Bengaluru_Ward_Master_Stats.csv'
FIGDIR = 'figures'

df = pd.read_csv(DATA)
print(f"Loaded {len(df)} wards")
print(df.head())
print('\nDescribe:')
print(df.describe())

# ── Feature set ──────────────────────────────────────────────────────────────
features = ['surface_temp', 'urban_index', 'veg_index', 'water_index']
X = df[features].copy()
print(f"\nFeature matrix: {X.shape}")
print(f"NaNs per col:\n{X.isna().sum()}")

# Drop any NaN rows
mask = X.notna().all(axis=1)
X = X.loc[mask].reset_index(drop=True)
df_clean = df.loc[mask].reset_index(drop=True)
print(f"After NaN drop: {len(X)} wards")

# ── Standardise ──────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Elbow + silhouette to pick k ────────────────────────────────────────────
ks = range(2, 11)
inertias = []
silhouettes = []
for k in ks:
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))
    print(f"k={k}: inertia={km.inertia_:.1f}, silhouette={silhouettes[-1]:.3f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(list(ks), inertias, 'o-', color='#2E7D62')
ax1.set_xlabel('Number of clusters (k)')
ax1.set_ylabel('Inertia (within-cluster SSE)')
ax1.set_title('Elbow plot')
ax2.plot(list(ks), silhouettes, 'o-', color='#C84B31')
ax2.set_xlabel('Number of clusters (k)')
ax2.set_ylabel('Silhouette score')
ax2.set_title('Silhouette score by k')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/elbow_silhouette.png', bbox_inches='tight')
plt.close()

# Pick best k by silhouette
best_k = list(ks)[int(np.argmax(silhouettes))]
print(f"\nBest k by silhouette: {best_k}")

# ── Final fit ────────────────────────────────────────────────────────────────
km = KMeans(n_clusters=best_k, random_state=42, n_init=50)
df_clean['cluster'] = km.fit_predict(X_scaled)
print(f"\nCluster sizes:\n{df_clean['cluster'].value_counts().sort_index()}")

# Cluster centroids in original scale
centroids_scaled = km.cluster_centers_
centroids = pd.DataFrame(
    scaler.inverse_transform(centroids_scaled),
    columns=features,
)
centroids.index.name = 'cluster'
print("\nCluster centroids (original scale):")
print(centroids.round(3))

# ── Profile each cluster ────────────────────────────────────────────────────
profile = df_clean.groupby('cluster')[features].mean().round(3)
profile['ward_count'] = df_clean['cluster'].value_counts().sort_index()
print("\nCluster profiles:")
print(profile)

# Sample wards per cluster
print("\nSample wards per cluster:")
for c in sorted(df_clean['cluster'].unique()):
    sample = df_clean[df_clean['cluster'] == c].nlargest(3, 'surface_temp')['Ward_Name'].tolist()
    print(f"  Cluster {c}: {sample}")

# ── Visualisations ──────────────────────────────────────────────────────────
# 1. Feature distribution by cluster
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, feat in zip(axes.ravel(), features):
    sns.boxplot(data=df_clean, x='cluster', y=feat, ax=ax, palette='viridis')
    ax.set_title(feat)
plt.suptitle(f'Feature distributions across {best_k} clusters', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/feature_distributions.png', bbox_inches='tight')
plt.close()

# 2. PCA scatter
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
fig, ax = plt.subplots(figsize=(9, 6))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=df_clean['cluster'], cmap='viridis',
                     s=60, alpha=0.85, edgecolors='white', linewidth=0.5)
ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
ax.set_title(f'Bengaluru wards projected onto first 2 principal components ({best_k} clusters)')
plt.colorbar(scatter, label='Cluster')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/pca_scatter.png', bbox_inches='tight')
plt.close()
print(f"\nPCA explained variance: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%")

# 3. Cluster centroid heatmap (z-scores)
centroids_z = pd.DataFrame(centroids_scaled, columns=features)
centroids_z.index.name = 'cluster'
fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(centroids_z, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
            cbar_kws={'label': 'Standardised value (z-score)'})
ax.set_title('Cluster centroids (standardised feature values)')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/centroid_heatmap.png', bbox_inches='tight')
plt.close()

# 4. Zone × cluster crosstab (where do clusters cluster geographically?)
zone_cluster = pd.crosstab(df_clean['Zone'], df_clean['cluster'])
print(f"\nZone × Cluster crosstab:\n{zone_cluster}")
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(zone_cluster, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
ax.set_title('Ward count by Zone × Cluster')
plt.tight_layout()
plt.savefig(f'{FIGDIR}/zone_cluster_heatmap.png', bbox_inches='tight')
plt.close()

# ── Save outputs ────────────────────────────────────────────────────────────
df_clean.to_csv('data/wards_with_clusters.csv', index=False)
profile.to_csv('data/cluster_profiles.csv')
print("\nDone. Outputs in data/ and figures/")
