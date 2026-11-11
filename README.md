[![Website](https://img.shields.io/badge/Website-jiande.is--a.si-8A3B12)](https://jiande.is-a.si)
[![Google Scholar](https://img.shields.io/badge/Google_Scholar-4285F4?logo=googlescholar&logoColor=white)](https://scholar.google.com/citations?user=VwRAV8kAAAAJ&hl=en)
[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--9357--2977-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-9357-2977)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jiandewu/)

- **Now:** observation-aware forecasting of respiratory hospitalizations
  (COVID-19, influenza, RSV), and LLM tools for surveillance data
- **Before:** RNA-seq, DNA methylation, and single-cell analyses of TCGA and
  GEO cohorts, focused on breast cancer; earlier, GPU and cluster parallel
  particle filtering for target tracking
- **Tools:** Python, PyTorch, R, LLM APIs and MCP, GitHub Actions, C/C++, CUDA, HPC (Slurm)

## AI and LLM systems

| Project | Description |
| --- | --- |
| [resplens](https://github.com/jiandewu/resplens) | Reliability-aware AI toolkit for US respiratory surveillance data, with MCP tools and evaluated document retrieval. Reranked hybrid retrieval reaches Recall@5 0.86 on held-out questions (BM25: 0.48). [Case study](https://jiande.is-a.si/projects/resplens/) |
| [plugins](plugins/) | Claude Code plugin marketplace and Codex skills for Pandoc paper builds (BibTeX, CSL, DOCX templates), multi-repository Git commits, and weekly work logs. |

## Forecasting and public health data

| Project | Description |
| --- | --- |
| [covid-transformer-multisource](https://github.com/DMA-PRIME/covid-transformer-multisource) | Transformer model fusing multiple data sources for county-level COVID-19 case and death forecasting; code for the *Epidemics* (2025) paper. 81.9% agreement at five weeks ahead, against 61.2% for persistence and 59.9% for ARIMA. [Case study](https://jiande.is-a.si/projects/covid-transformer/) |
| [ObsAwareData](https://github.com/DMA-PRIME/ObsAwareData) | Weekly COVID-19, influenza, and RSV surveillance data for the 50 US states and DC (NHSN, NSSP, NWSS, Census), with reliability flags and source-release provenance. CC BY 4.0. |
| [ObsAwareData-pipeline](https://github.com/jiandewu/ObsAwareData-pipeline) | Archive of CDC releases and the pipeline that builds ObsAwareData. |

## Bioinformatics

| Project | Description |
| --- | --- |
| [tcga-brca-analysis](https://github.com/jiandewu/tcga-brca-analysis) | TCGA breast cancer RNA-seq, miRNA, and DNA methylation analyses, focused on TNBC. |
| [pancancer-methylation](https://github.com/jiandewu/pancancer-methylation) | DNA methylation (DMP, DMR, survival) across TCGA BRCA, COAD, LUAD, and PRAD. |
| [star-jum-splicing-workflow](https://github.com/jiandewu/star-jum-splicing-workflow) | Two-pass STAR and JUM workflow for RNA-seq alternative splicing. |

More workflows (TCGA colorectal and lung, scRNA-seq, edgeR/limma) in my
[repositories](https://github.com/jiandewu?tab=repositories).

## Selected publications

- **Wu, J.** et al. (2025). [A deep learning approach for enhancing pandemic prediction](https://doi.org/10.1016/j.epidem.2025.100865). *Epidemics*. [[code](https://github.com/DMA-PRIME/covid-transformer-multisource)]
- **Wu, J.** & Hicks, C. (2021). [Breast cancer type classification using machine learning](https://doi.org/10.3390/jpm11020061). *Journal of Personalized Medicine*.
- **Wu, J.** et al. (2020). [Unraveling the genomic-epigenomic interaction landscape in triple negative and non-triple negative breast cancer](https://doi.org/10.3390/cancers12061559). *Cancers*.
- Jilkov, V. P. & **Wu, J.** (2015). [Efficient GPU-accelerated implementation of particle and particle flow filters for target tracking](https://isif.org/media/efficient-gpu-accelerated-implementation-particle-and-particle-flow-filters-target-tracking). *Journal of Advances in Information Fusion*.

Full list on [Google Scholar](https://scholar.google.com/citations?user=VwRAV8kAAAAJ&hl=en).
