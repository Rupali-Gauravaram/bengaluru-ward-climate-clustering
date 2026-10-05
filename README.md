# Bengaluru Ward Climate-Vulnerability Clustering

**I used K-Means clustering to group Bengaluru's 198 BBMP wards into four climate-vulnerability types, based on satellite measurements of surface temperature, urbanisation, vegetation, and water. The work was done as background research for the [Bengaluru Quorum](https://linkedin.com/company/bengaluru-quorum) climate-intelligence platform.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange.svg) ![Pandas](https://img.shields.io/badge/Pandas-2.0+-lightgrey.svg)

![Cluster centroids heatmap](./figures/centroid_heatmap.png)

---

## Motivation

Climate vulnerability in Indian cities is usually shown as a single ranking: average temperature, slum density, or number of flood incidents. That assumes vulnerability has one main cause, and that wards differ only in how much of it they have.

This project checks whether that holds for Bengaluru. I applied clustering to a small set of ward-level satellite features and let the data show, without any labels, how many types of ward the city has and what separates them. The result describes how varied the city is, and gives a baseline for later supervised models in Bengaluru Quorum.

---

## Results

### Choosing the number of clusters

I fitted K-Means for k = 2 to k = 10, and used the silhouette score together with inertia (the within-cluster sum of squared errors) to choose k. The silhouette score was highest at **k = 4** (0.352), and the inertia curve flattens at the same point.

![Elbow and silhouette plots](./figures/elbow_silhouette.png)

### The four ward types

Centroid values are shown in their original units. The image at the top shows the same centroids as z-scores.

| Cluster | Wards | Surface temperature (°C) | Urban index | Vegetation index | Water index | Type |
|---|---|---|---|---|---|---|
| **0** | 42 | **38.0** | **+0.017** | −0.093 | −0.132 | Concrete heat islands |
| **1** | 39 | **35.5** | −0.026 | **+0.159** | −0.150 | Green peri-urban |
| **2** | 79 | 36.4 | −0.008 | −0.114 | **+0.114** | Lake-adjacent moderate-density |
| **3** | 38 | 37.3 | +0.001 | +0.138 | **−0.163** | Water-stressed mixed |

**Cluster 0: Concrete heat islands.** Example wards: *Rajagopal Nagar, K R Market, Hegganahalli.* These have the highest surface temperatures (38.0 °C), the densest built-up areas, and the least vegetation. They closely match the cool-roof priority wards found separately in my supervised analysis ([bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)).

**Cluster 1: Green peri-urban.** Example wards: *Devara Jeevanahalli, Shanthi Nagar, Jakkasandra.* These are the coolest and greenest wards, with the lowest urban index. For policy, they are the wards to protect: they need zoning controls ahead of development, not retrofits.

**Cluster 2: Lake-adjacent moderate-density.** The largest group (79 wards). Example wards: *Subhash Nagar, Gandhinagar, Agrahara Dasarahalli.* They are average on temperature and built-up density but well above average on water. Their lakes and water bodies could anchor future climate-adaptive design.

**Cluster 3: Water-stressed mixed.** Example wards: *Kengeri, Peenya Industrial Area, Anjanapura.* They combine fairly high temperatures and moderate density with the largest water deficit in the dataset (z = −1.28). Temperature alone would not flag them as a priority. Looking at all the features together does.

### How the features separate the clusters

![Feature distributions by cluster](./figures/feature_distributions.png)

The four clusters differ on several features at once, not on one. Cluster 3 differs from Cluster 2 mainly on water, even though their temperatures overlap a lot. This shows that vulnerability is more than heat.

### The structure in two dimensions

![PCA scatter](./figures/pca_scatter.png)

A two-component PCA keeps **94.7%** of the total variance (PC1: 62.8%, PC2: 31.9%). The clusters are still clearly visible in two dimensions, which suggests the four types reflect real structure in the data.

### Where the clusters are in the city

![Zone × Cluster heatmap](./figures/zone_cluster_heatmap.png)

The clusters are spread unevenly across the BBMP zones:

- **Concrete heat islands (Cluster 0)** are mostly in the **West (14 wards), East (9), and South (9)** zones, with none in Yelahanka.
- **Green peri-urban (Cluster 1)** is mostly in the **East (21 wards)** and **Yelahanka (5)**, the less developed northern and eastern edges.
- **Water-stressed (Cluster 3)** is mostly in **Rajarajeswari Nagar (9), Mahadevapura (8), and Bommanahalli (7)**, the outer zones where the city has grown fastest.

This matches what is known about how Bengaluru has developed, which supports the clustering.

---

## Method

1. **Dataset.** 198 BBMP wards and 4 features: `surface_temp` (long-term mean LST, 2022 to 2024, from MODIS), `urban_index`, `veg_index`, and `water_index` (ward-level indices from Sentinel-2). The features were extracted in Google Earth Engine and averaged over each ward with `ee.Reducer.mean()`.
2. **Preprocessing.** There were no missing values. I applied `StandardScaler`, because the features are on very different scales (surface temperature runs from 34 to 39 °C, the urban index from about −0.05 to +0.04).
3. **Model selection.** K-Means for k from 2 to 10, with `n_init=20` random starts at each k. I chose k by the highest silhouette score and used the elbow plot as a second check.
4. **Final fit.** k = 4 with `n_init=50`, to make the result less dependent on the starting centroids.
5. **Interpretation.** I converted the centroids back to original units for reporting. I checked each cluster by looking at its three hottest wards against what is known about the city.

---

## Interpretation

### Vulnerability has more than one dimension

The clearest finding is that heat stress and water stress are separate. Cluster 3 (water-stressed) and Cluster 0 (concrete heat islands) would both be called "vulnerable" in a normal ranking, but for different reasons. A budget allocated only by temperature, for example to cool roofs, would overlook Cluster 3 wards, whose main problem is water. Grouping wards by type gives a better basis for choosing the right measure for each.

### Why K-Means

I chose K-Means over a density-based method such as DBSCAN because of how the data is distributed. A trial DBSCAN run put about 90% of wards in one cluster and marked the rest as noise. That fits data that varies smoothly, without dense separate groups. The silhouette score of 0.352 at k = 4 shows there is still meaningful structure.

### Agreement with the supervised analysis

Cluster 0 contains the same wards (Rajagopal Nagar, Hegganahalli, Peenya Industrial Area) that my LST regression model ([bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)) ranks highest for cool roofs. Two independent methods pointing to the same wards gives more confidence that the result is real and not a side effect of one method.

---

## Limitations

- **Ward boundaries.** The analysis uses the older 198-ward BBMP boundaries, not the current 369-ward Greater Bengaluru Authority boundaries, to stay consistent with the existing satellite data. Re-extracting the features for the new boundaries is the natural next step.
- **Feature scope.** Four features were used. Adding population density, elevation, distance to drains, and flood history would probably split the water-stressed cluster into flood-prone and water-short groups.
- **Long-term averages.** The features are long-term means, so they lag behind recent change. A ward that is rapidly densifying may still be grouped by its past.
- **Cluster shape.** K-Means assumes round clusters of similar size. The size of Cluster 2 (79 wards) suggests a Gaussian Mixture Model might split it into more uniform groups.
- **No spatial constraint.** The clustering does not use ward location. A spatially constrained method (for example SKATER or ClustGeo) would give connected clusters that are easier to act on, but less useful for finding types. This project focuses on types. A follow-up could look at the spatial version.

---

## Repository structure

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
├── run_analysis.py                           # Runs the whole analysis
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Reproduction

```bash
git clone https://github.com/Rupali-Gauravaram/bengaluru-ward-climate-clustering.git
cd bengaluru-ward-climate-clustering
pip install -r requirements.txt
python run_analysis.py
```

All random steps use a fixed seed (`random_state=42`), so the outputs are the same on every run.

---

## Related work

- **[bengaluru-uhi-prediction](https://github.com/Rupali-Gauravaram/bengaluru-uhi-prediction)**: supervised LST prediction and cool-roof ranking on the same 198 wards. Cluster 0 here contains the same priority wards.
- **[Bengaluru_LST_Prediction_API](https://github.com/Rupali-Gauravaram/Bengaluru_LST_Prediction_API)**: the original Land Surface Temperature prediction API that the UHI work builds on.
- **Bengaluru Quorum** ([LinkedIn](https://linkedin.com/company/bengaluru-quorum)): the climate-intelligence platform these ward types were developed for.

---

## Author

**Rupali Gauravaram**. MSc Climate Resilience & Environmental Sustainability (University of Liverpool, 2024). Advanced Certification in Data Science & AI (IIT Roorkee).

[LinkedIn](https://linkedin.com/in/rupali99) · [GitHub](https://github.com/Rupali-Gauravaram) · [Blog: Chai & Code](https://chaiandcode.wordpress.com)
