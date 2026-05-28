# Bengaluru Ward Climate-Vulnerability Clustering

**An unsupervised K-Means clustering of 198 BBMP wards into four climate-vulnerability archetypes, derived from satellite-based measurements of surface temperature, urbanisation, vegetation, and water-body proximity. The analysis is conducted as foundational research for the [Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum) climate-intelligence platform.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange.svg) ![Pandas](https://img.shields.io/badge/Pandas-2.0+-lightgrey.svg)

![Cluster centroids heatmap](./figures/centroid_heatmap.png)

---

## Motivation

Climate-vulnerability assessments of urban wards in India are typically expressed as a one-dimensional ranking — average temperature, slum density, or recorded flood incidents — and used to prioritise interventions accordingly. This framing assumes that vulnerability has a single dominant axis, and that wards differ from one another primarily in degree rather than in kind.

The present analysis examines whether that assumption holds for Bengaluru. By applying unsupervised clustering to a small set of ward-level satellite-derived features, the analysis asks the data, without prior labels, how many distinct ward typologies the city contains and what distinguishes one from another. The result is intended both as a standalone characterisation of Bengaluru's intra-city heterogeneity and as a baseline against which future supervised models in the Bengaluru Quorum platform can be evaluated.

---

## Results

### Selection of the number of clusters

K-Means was fitted for k = 2 to k = 10, with silhouette score and the within-cluster sum of squared errors (inertia) used jointly to select k. Silhouette score was maximised at **k = 4** (s = 0.352), and the inertia curve exhibits a corresponding softening at the same value. Both diagnostics are reported below.

![Elbow and silhouette plots](./figures/elbow_silhouette.png)

### Cluster centroids and archetypes

Four distinct ward archetypes emerge. Centroid values are reported in their original feature units, with z-scored centroids visualised in the heading image:

| Cluster | Wards | Surface temperature (°C) | Urban index | Vegetation index | Water index | Archetype |
|---|---|---|---|---|---|---|
| **0** | 42 | **38.0** | **+0.017** | −0.093 | −0.132 | Concrete heat islands |
| **1** | 39 | **35.5** | −0.026 | **+0.159** | −0.150 | Green peri-urban |
| **2** | 79 | 36.4 | −0.008 | −0.114 | **+0.114** | Lake-adjacent moderate-density |
| **3** | 38 | 37.3 | +0.001 | +0.138 | **−0.163** | Water-stressed mixed |

The archetypes can be characterised as follows.

**Cluster 0 — Concrete heat islands.** Representative wards: *Rajagopal Nagar, K R Market, Hegganahalli.* These wards exhibit the highest mean surface temperatures (38.0 °C), the densest built environment, and the lowest vegetation cover. They correspond closely to the cool-roof intervention priorities identified independently in the companion supervised analysis ([bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)).

**Cluster 1 — Green peri-urban.** Representative wards: *Devara Jeevanahalli, Shanthi Nagar, Jakkasandra.* These are the city's coolest and most vegetated wards, with the lowest urbanisation index. From a policy perspective, these wards represent the city's preservation set — they require anticipatory zoning controls rather than retrofit interventions.

**Cluster 2 — Lake-adjacent moderate-density.** The largest cluster (n = 79). Representative wards: *Subhash Nagar, Gandhinagar, Agrahara Dasarahalli.* These wards are average on temperature and built-up density, but exhibit significantly above-average water-body proximity. They represent latent blue–green infrastructure capital — water features that could anchor future climate-adaptive design.

**Cluster 3 — Water-stressed mixed.** Representative wards: *Kengeri, Peenya Industrial Area, Anjanapura.* These wards combine moderately elevated temperatures and moderate built density with the most severe water deficit in the dataset (z = −1.28). The thermal axis alone would not identify them as priority; the joint structure does.

### Feature separability across clusters

![Feature distributions by cluster](./figures/feature_distributions.png)

The four clusters occupy distinct regions of the feature space across multiple axes simultaneously rather than separating along a single dimension. Cluster 3 is differentiated from Cluster 2 primarily on the water axis, despite considerable overlap in surface temperature, demonstrating that vulnerability is not reducible to thermal stress alone.

### Low-dimensional structure

![PCA scatter](./figures/pca_scatter.png)

A two-component PCA projection accounts for **94.7%** of total variance (PC1: 62.8%, PC2: 31.9%). The high recoverability of the cluster structure in two dimensions indicates that the four-archetype solution reflects a genuine low-dimensional signal in the data rather than a high-dimensional artefact.

### Geographic distribution of archetypes

![Zone × Cluster heatmap](./figures/zone_cluster_heatmap.png)

The clusters are unevenly distributed across BBMP administrative zones:

- **Concrete heat islands (Cluster 0)** concentrate in the **West (14 wards), East (9), and South (9)** zones, and are absent from Yelahanka.
- **Green peri-urban (Cluster 1)** is concentrated in the **East (21 wards)** and **Yelahanka (5)** — the city's relatively under-developed northern and eastern fringes.
- **Water-stressed (Cluster 3)** is concentrated in **Rajarajeswari Nagar (9), Mahadevapura (8), and Bommanahalli (7)** — the peripheral zones associated with the most rapid recent expansion of the urban footprint.

The geographic concentration of each archetype within specific zones provides qualitative validation of the clustering and corresponds to the lived experience of Bengaluru's spatial development.

---

## Method

1. **Dataset.** 198 BBMP wards × 4 features: `surface_temp` (long-term mean LST, 2022–2024, MODIS-derived), `urban_index`, `veg_index`, and `water_index` (Sentinel-2 derived ward-aggregated indices). Features were extracted via Google Earth Engine and aggregated to ward geometry using `ee.Reducer.mean()`.
2. **Preprocessing.** No missing values were present in the feature set after extraction. `StandardScaler` was applied to normalise features, as the original scales differ by several orders of magnitude (surface temperature ranges 34–39 °C; urban index ranges approximately −0.05 to +0.04).
3. **Model selection.** K-Means was fitted for k ∈ {2, …, 10}, with `n_init=20` random initialisations at each k. Best k was chosen by maximum silhouette score; the elbow plot was used as a secondary sanity check.
4. **Final fit.** k = 4 was fitted with `n_init=50` to reduce sensitivity to initial centroid placement.
5. **Interpretation.** Centroids were inverse-transformed to original feature units for reporting. Cluster profiles were validated qualitatively by inspecting the three highest-temperature wards within each cluster against existing domain knowledge of Bengaluru's spatial structure.

---

## Discussion

### Vulnerability is not one-dimensional

The clearest finding is the orthogonality of thermal and hydrological stress in the cluster structure. Cluster 3 (water-stressed mixed) and Cluster 0 (concrete heat islands) both contain wards that would be flagged as "vulnerable" in conventional rankings, but their dominant stress vectors differ. An intervention budget allocated purely on thermal severity — for example, to cool-roof retrofits — would systematically under-prioritise Cluster 3 wards whose primary constraint is water availability. The clustering provides a basis for typology-aware intervention allocation rather than uniform ranking-based prioritisation.

### Suitability of K-Means

K-Means was chosen over density-based alternatives (e.g. DBSCAN) on the basis of the feature space geometry. An exploratory DBSCAN fit produced a single dominant cluster containing approximately 90% of wards with the remainder flagged as noise — a result consistent with a feature distribution that varies continuously along a small number of latent axes rather than forming discrete dense regions. The high silhouette score at k = 4 (s = 0.352, well above the chance baseline for four-cluster random partitions of this dataset) confirms that meaningful structure exists despite the absence of natural density gaps.

### Convergence with supervised analysis

Cluster 0 — identified here through unsupervised partitioning — contains the same wards (Rajagopal Nagar, Hegganahalli, Peenya Industrial Area) that the companion supervised LST-regression model ([bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)) ranks at the top of its cool-roof prioritisation. The convergence of two methodologically independent approaches on the same intervention set strengthens confidence that the identified high-vulnerability wards reflect a robust underlying signal rather than an artefact of either method.

---

## Limitations

- **Ward boundary set.** The analysis uses the older 198-ward BBMP boundary set rather than the current 369-ward Greater Bengaluru Authority boundary, for consistency with the existing satellite feature extraction. Re-extraction of features onto the GBA boundary is identified as the natural extension of this work.
- **Feature scope.** Four features were used. The inclusion of population density, elevation/slope, drainage network proximity, and historical flood incidence would likely separate the water-stressed cluster into flood-prone and water-deficient sub-archetypes.
- **Temporal aggregation.** Features are derived from long-term means and therefore lag rapid contemporary change. A ward currently undergoing transition from peri-urban to densely built may be misclassified under its historical typology.
- **Cluster shape assumptions.** K-Means imposes spherical, equal-variance clusters. The disproportionate size of Cluster 2 (n = 79) suggests that a Gaussian Mixture Model permitting anisotropic and unequal-variance clusters might split it into more homogeneous sub-groups.
- **Absence of spatial constraints.** The clustering treats wards as exchangeable points in feature space. A spatially-constrained method (e.g. SKATER, ClustGeo) would yield geographically contiguous clusters, more directly actionable for intervention planning but less informative as typology discovery. The present work prioritises typology; a follow-on study could examine the spatial variant.

---

## Project structure

```
bengaluru-ward-climate-clustering/
├── data/
│   ├── Bengaluru_Ward_Master_Stats.csv       # 198 wards × 4 features (input)
│   ├── Bengaluru_Ward_Temp_Stats.csv         # Raw LST extracts
│   ├── Bengaluru_Ward_Urban_Stats.csv        # Raw urbanisation extracts
│   ├── Bengaluru_Ward_Veg_Stats.csv          # Raw vegetation extracts
│   ├── Bengaluru_Ward_Water_Stats.csv        # Raw water-index extracts
│   ├── wards_with_clusters.csv               # Output: 198 wards + cluster label
│   └── cluster_profiles.csv                  # Output: per-cluster feature means
├── figures/
│   ├── elbow_silhouette.png
│   ├── feature_distributions.png
│   ├── pca_scatter.png
│   ├── centroid_heatmap.png
│   └── zone_cluster_heatmap.png
├── run_analysis.py                           # End-to-end reproducible pipeline
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Reproducibility

```bash
git clone https://github.com/Rupali-Gauravaram/bengaluru-ward-climate-clustering.git
cd bengaluru-ward-climate-clustering
pip install -r requirements.txt
python run_analysis.py
```

All randomised steps are seeded (`random_state=42`); outputs are deterministic.

---

## Related work

- **[bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)** — Supervised LST prediction and cool-roof prioritisation on the same 198-ward dataset. Cluster 0 of the present analysis converges on the same priority wards identified by that model.
- **[Bengaluru_LST_Prediction_API](https://github.com/Rupali-Gauravaram/Bengaluru_LST_Prediction_API)** — The original Land Surface Temperature prediction API on which the UHI work is built.
- **Bengaluru Quorum** ([LinkedIn](https://linkedin.com/company/bengaluru-quorum)) — The climate-intelligence platform for which these ward archetypes provide foundational typology.

---

## Author

**Rupali Gauravaram** — Climate Tech ML Engineer, founder of [Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum). MSc Climate Resilience & Environmental Sustainability (University of Liverpool, 2024). Advanced AI/ML certification, IIT Roorkee (anticipated May 2026).

[LinkedIn](https://linkedin.com/in/rupali99) · [GitHub](https://github.com/Rupali-Gauravaram) · [Blog: Chai & Code](https://chaiandcode.wordpress.com)
