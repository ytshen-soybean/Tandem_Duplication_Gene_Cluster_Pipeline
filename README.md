​                                                                                                                                               **Tandem Duplication Gene Cluster Pipeline**

 

**Overview**

A pipeline for identifying tandemly duplicated gene clusters at genome wide based on protein similarity, genomic distance, and clustering strategies. It is capable of identifying both Single-gene Tandem Duplication clusters (STDs), which contain only one homologous gene type, and Multi-gene Tandem Duplication clusters (MTDs) consisting of multiple homolog types.

 

**Schematic diagram of pipeline**

<img width="200" height="259" alt="image" src="https://github.com/user-attachments/assets/c358fe6b-f44b-43ff-ad55-1e2dddbe4d89" />


 
**Requirements**

\- Linux operating system

\- GNU coreutils (awk, sort, cat)

\- Python >= 3.7

 \- numpy >= 1.18

 \- scikit-learn >= 0.22

\- Perl >= 5.10 (core modules only)

\- DIAMOND >= 2.0

 

**Usage**

Run the **tandem_duplication_gene_cluster_pipeline.sh** step by step

Detailed information is below.

 

**Input file**

primary_protein.fasta 

*# A protein FASTA file containing only the representative transcript for each gene. Selection can be performed via jcvi tools or manual filtering. It is mandatory that protein IDs are sorted by their genomic coordinates. IDs must adhere to the format [Prefix]GXXXX00 (e.g., Gmax_01G002100), where 'G' is followed by six digits ending in '00'. To resolve ID incompatibilities, use seqkit replace for batch renaming or adjust the logic within s1_genepair_filter.py*

 

**Output files**

singlegene_tandem_repeat.txt

#Dection result of STD

*#Column 1: Unique identifier (ID) of the tandem duplication cluster.* 

*#Column 2: Comma-separated list of protein IDs contained within the cluster.* 

*#Column 3: Comma-separated group indices corresponding to each protein listed in the second column*

 

multigene_tandem_repeat.txt

#Dection result of STD

*#Column 1: Unique identifier (ID) of the tandem duplication cluster.* 

*#Column 2: Group IDs included within the cluster.*

*#Column 3: Comma-separated list of protein IDs contained within the cluster.* 

*#Column 4: Comma-separated group indices corresponding to each protein listed in the second column*

 

**Pipeline detail：**

*##**STEP1****：all-vs-all blast and filer for protein*

*#Custom parameters in DIAMOND, such as --id, --query-cover, and --subject-cover, can be adjusted based on specific research requirements*

`diamond makedb --in demo_primary_pro.fasta -d demo`

`diamond blastp -d demo -q demo_primary_pro.fasta -o demo.blast -p 40 --sensitive --evalue 1e-10 --quiet`

*#Alignment Processing*

*#Raw DIAMOND output is processed to exclude self-hits*

`awk '$1!=$2' demo.blast >demo_filter1.blast`

*#* *Only gene pairs located on the same chromosome retained* 

`awk '{print $1,$2,$0}' demo_filter1.blast >test.blast`

`awk '{gsub(/G.*/,"G",$1);print}' OFS="\t" test.blast >test-2.blast`

`awk '{gsub(/G.*/,"G",$2);print}' OFS="\t" test-2.blast >test-3.blast`

`awk '$1==$2' test-3.blast OFS="\t" >demo_filter2.blast`

`awk '{print $3,$4}' OFS="\t" demo_filter2.blast >demo_genepair_1.txt`

`rm test.blast test-2.blast test-3.blast demo_filter1.blast demo_filter2.blast`

*# Gene pairs are filtered to ensure the intergenic distance is $\le 50$ and non-zero* 

`python scripts/s1_genepair_filter.py <demo_genepair_1.txt >demo_genepair_2.txt` 

 

*##**STEP2**：Graph-Based Gene Grouping* 

*#* *Since a single gene may associate with multiple partners in the filtered alignment, graph theory principles are applied to cluster all interconnected genes into a single primary group.* 

`perl scripts/s2_gene_group.pl demo_genepair_2.txt demo_genepair_grouping.txt`

 

*##**STEP3**：Merging Overlapping Gene Groups*

*#* *All groups are reordered based on the genomic index of their starting gene*

`sort -k 2,2 demo_genepair_grouping.txt -o demo_genepair_grouping_sort.txt`

*#* *ensure that the starting gene ID of each subsequent group follows the index of the preceding group*

`perl scripts/s3a_gene_group_check.pl demo_genepair_grouping_sort.txt`

*#* *Groups containing genes with overlapping genomic positions are merged*

`perl scripts/s3b_group_merge.pl demo_genepair_grouping_sort.txt >demo_genepair_grouping_sort_merge.txt`

 

*## **STEP4**：Refined Sub-grouping via DBSCAN Clustering*

*#* *Overlapping groups are further partitioned based on precise intergenic distances. The DBSCAN (Density-Based Spatial Clustering of Application with Noise) algorithm was employed, using a default min_samples=2. The “eps” (epsilon) parameter is automatically determined via the distribution of the shortest K-distances. For groups with >2 genes: If the identified eps <= 2, it is capped at 2. For groups with exactly 2 genes: If eps > 2, the genes are assigned a marker of "-1" (no grouping)*

*#The output includes the original input data supplemented by intergenic distance values, the optimized eps (epsilon) parameter, and specific gene grouping markers.*

`python scripts/s4a_mergegroup_splitmark.py <demo_genepair_grouping_sort_merge.txt > demo_genepair_grouping_sort_merge_splitmark.txt`

*#A file is generated consisting of two columns: the gene ID and its corresponding original group information. If a single gene is found to be assigned to more than one group, the system will trigger an error.*

`python scripts/s4b_1vs1_format.py demo_genepair_grouping.txt > demo_genepair_grouping_1vs1.txt`

*#Utilizing the grouping markers, the merged groups are partitioned and re-organized into refined clusters*

`python scripts/s4c_merge_split.py demo_genepair_grouping_sort_merge_splitmark.txt demo_genepair_grouping_1vs1.txt retain_group.txt filter_group.txt`

 

*## **STEP5**：The retain group of previous step are categorized based on their complexity.* 

*#When cluster containing only one original group, its STD. When cluster containing more than one original group, its MTD.* 

`python scripts/s5_group_classify.py retain_group.txt retain_multi_group.txt retain_single_group.txt`

 

*## **STEP6**：The MTD of previous step undergone a secondary splitting process*

*#* *If a specific groupID within a cluster contains only a single gene, that ID is removed. If all members of a groupID are located at the start or end of a cluster, they are cleaved into a new group. The remaining genes are processed iteratively; any resulting groups with fewer than three genes are excluded from the output.*

`python scripts/s6_multigroup_split.py retain_multi_group.txt retain_multi_group_split.txt` 

*#* *The group of previous step are categorized again. When cluster containing only one original group, its STD. When cluster containing more than one original group, its MTD.*

`python scripts/s5_group_classify.py retain_multi_group_split.txt retain_multi_group_multi_group.txt retain_multi_group_single_group.txt`

 

*## **STEP7**：The gene groups identified from various stages are merged, sorted, and finalized into the standard output files.*

`cat retain_single_group.txt retain_multi_group_single_group.txt | sort -k2,2 | awk '{print "STD"NR, $2,$3}' OFS="\t" >singlegene_tandem_repeat.txt`

`awk '{print "MTD"NR,$1,$2,$3}' OFS="\t" retain_multi_group_multi_group.txt > multigene_tandem_repeat.txt`

`mkdir process`

`mv demo_*.txt *_group.txt *_split.txt demo_primary_pro.fasta demo.dmnd demo.blast process`

**CONTACT**
Please email to shenyanting@yzwlab.cn


