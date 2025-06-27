## Research Progress Update (2025-06-27 12:42:04)

Analyzed mouse liver scRNA-seq data from `/Users/jamesbolepan/Documents/research_LiverStress_Immune/rds_manual_extract/liver_liveTissue_RNA.h5ad`. Preprocessing included normalization, log transformation, identification of highly variable genes, PCA, neighbor graph computation, and UMAP embedding. Visualizations include a UMAP plot of "Pdcd1" expression and a violin plot of "Pdcd1" expression by cell type.

![UMAP plot showing Pdcd1 expression](notebook_images/notebook_liver_analysis_1_cell5_out1.png)
![Violin plot of Pdcd1 expression by cell type](notebook_images/notebook_liver_analysis_1_cell6_out1.png)

---

## Research Progress Update (2025-06-27 12:48:58)

A new analysis pipeline was introduced for `liver_liveTissue_RNA.h5ad`, including data normalization, log transformation, PCA, UMAP, and Leiden clustering. Visualizations of UMAP embeddings colored by cell types and Leiden clusters were generated.

![UMAP plot colored by celltypes_figure2plot](aln_output/notebook_images/notebook_1_liver_1_cell4_out1.png)
![UMAP plot colored by leiden clusters](aln_output/notebook_images/notebook_1_liver_1_cell6_out2.png)

---

