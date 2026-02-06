##step1
diamond makedb --in demo_primary_pro.fasta -d demo
diamond blastp -d demo -q demo_primary_pro.fasta -o demo.blast -p 40 --sensitive --evalue 1e-10 --quiet
awk '$1!=$2' demo.blast >demo_filter1.blast
awk '{print $1,$2,$0}' demo_filter1.blast >test.blast
awk '{gsub(/G.*/,"G",$1);print}' OFS="\t" test.blast >test-2.blast
awk '{gsub(/G.*/,"G",$2);print}' OFS="\t" test-2.blast >test-3.blast
awk '$1==$2' test-3.blast OFS="\t" >demo_filter2.blast
awk '{print $3,$4}' OFS="\t" demo_filter2.blast >demo_genepair_1.txt
rm test.blast test-2.blast test-3.blast demo_filter1.blast demo_filter2.blast
python scripts/s1_genepair_filter.py <demo_genepair_1.txt >demo_genepair_2.txt 

##STEP2£ºGraph-Based Gene Grouping 
perl scripts/s2_gene_group.pl demo_genepair_2.txt demo_genepair_grouping.txt

##STEP3£ºMerging Overlapping Gene Groups
sort -k 2,2 demo_genepair_grouping.txt -o demo_genepair_grouping_sort.txt
perl scripts/s3a_gene_group_check.pl demo_genepair_grouping_sort.txt
perl scripts/s3b_group_merge.pl demo_genepair_grouping_sort.txt >demo_genepair_grouping_sort_merge.txt

## STEP4£ºRefined Sub-grouping via DBSCAN Clustering
python scripts/s4a_mergegroup_splitmark.py <demo_genepair_grouping_sort_merge.txt > demo_genepair_grouping_sort_merge_splitmark.txt
python scripts/s4b_1vs1_format.py demo_genepair_grouping.txt > demo_genepair_grouping_1vs1.txt
python scripts/s4c_merge_split.py demo_genepair_grouping_sort_merge_splitmark.txt demo_genepair_grouping_1vs1.txt retain_group.txt filter_group.txt

## STEP5£ºThe retain group of previous step are categorized based on their complexity. 
python scripts/s5_group_classify.py retain_group.txt retain_multi_group.txt retain_single_group.txt

## STEP6£ºThe MTD of previous step undergone a secondary splitting process
python scripts/s6_multigroup_split.py retain_multi_group.txt retain_multi_group_split.txt 
python scripts/s5_group_classify.py retain_multi_group_split.txt retain_multi_group_multi_group.txt retain_multi_group_single_group.txt

## STEP7£ºThe gene groups identified from various stages are merged, sorted, and finalized into the standard output files.
cat retain_single_group.txt retain_multi_group_single_group.txt | sort -k2,2 | awk '{print "STD"NR, $2,$3}' OFS="\t" >singlegene_tandem_repeat.txt
awk '{print "MTD"NR,$1,$2,$3}' OFS="\t" retain_multi_group_multi_group.txt > multigene_tandem_repeat.txt
mkdir process
mv demo_*.txt *_group.txt *_split.txt demo_primary_pro.fasta demo.dmnd demo.blast process
