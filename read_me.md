第一步：蛋白序列all-all的比对
##每个基因选择primary_protein，可以通过jcvi自带的format工具去选择，也可以根据自己的策略去选择。利用diamond进行基因组蛋白序列之间多对多的比对。
##根据严格程度，也可以设置比对相似度，coverage百分比（--id 80 --query-cover 80 --subject-cover 80）等参数
diamond makedb --in TZX248_primary_protein.fasta -d TZX248
diamond blastp -d TZX248 -q TZX248_primary_protein.fasta -o Soy.blast -p 40 --sensitive --evalue 1e-10 --quiet   （691004行）
##整理blast结果
#过滤自身与自身的比对
awk '$1!=$2' Soy.blast >Soy_filter1.blast （637699行）
#筛选同一个染色体内部基因的比对，得到内部基因对。
awk '$1!=$2' Soy.blast >Soy_filter1.blast
awk '{print $1,$2,$0}' Soy_filter1.blast >test.blast
awk '{gsub(/G.*/,"G",$1);print}' OFS="\t" test.blast >test-2.blast
awk '{gsub(/G.*/,"G",$2);print}' OFS="\t" test-2.blast >test-3.blast
awk '$1==$2' test-3.blast OFS="\t" >Soy_filter2.blast (62176行)
awk '{print $3,$4}' OFS="\t" Soy_filter2.blast >Soy_genepair_1.txt
rm test.blast test-2.blast test-3.blast Soy_filter2.blast
#保留比对基因对之间距离<=50且不为0的基因对（基因的距离用ID中G后面的四位来衡量，后面两位被忽略。Chr13 rDNA区间的基因有一些后两位不一样，这些基因忽略不管）
python step1_genepair_filter.py <Soy_genepair_1.txt >Soy_genepair_2.txt  （27633行）

第二步：将基因按照比对结果进行分组
#筛选后的比对基因对中，一个基因可能和多个基因关联。利用图的原理，将所有有关联的基因分为一个group
perl step2_gene_group.pl Soy_genepair_2.txt Soy_genepair_grouping.txt  （3498个group）

第三步：将包含的基因在位置上有重叠的group合并到一起
#按照每个group的起始基因的编号，将group重新进行排序
sort -k 2,2 Soy_genepair_grouping.txt -o Soy_genepair_grouping_sort.txt
#检查排序的结果，确保下一个group的起始基因ID在上一个group的起始基因ID之后。
perl step3_gene_group_check.pl Soy_genepair_grouping_sort.txt
#将包含的基因在位置上有重叠的group合并到一起
perl step4_group_merge.pl Soy_genepair_grouping_sort.txt >Soy_genepair_grouping_sort_merge.txt （2284个group）

第四步：按照基因之间的距离，将重叠的group重新分组。
#根据深度学习中的DBSCAN聚类方法，关键参数min_samples=2，eps通过基因之间的最短K距离的分布来自动识别。如果mergegroup中的基因多于2个，那么如果eps<=2,则设置为2.如果mergegroup中的基因有2个，那么如果eps>2,则该group的基因的分组marker为“-1”（不分组）.
#输出结果是在输入结果的基础上增加了基因之间的距离值、最佳eps值、基因的分组marker
python step5_mergegroup_splitmark.py <Soy_genepair_grouping_sort_merge.txt >Soy_genepair_grouping_sort_merge_splitmark.txt
#准备一个基因对应原始group的文件，每行两列，分别为基因和对应的group信息。如果一个基因属于两个group，则会报错
python step6_1vs1_format.py Soy_genepair_grouping.txt >Soy_genepair_grouping_1vs1.txt
#根据基因的分组marker，将mergegroup重新进行分组。需要额外提供一个基因对应原始group的文件，用来输出分为一组的基因的原始的group信息，同时决定所属新group的名称
python step7_merge_split.py Soy_genepair_grouping_sort_merge_splitmark.txt Soy_genepair_grouping_1vs1.txt retain_group.txt filter_group.txt （保留group2715个， 过滤掉174个）

第五步：对上一步的retain_group，按照group是否包含1个以上的原始group，分为single gene group和multi gene group两类
python step8_group_classify.py retain_group.txt retain_multi_group.txt retain_single_group.txt （single gene group 2119个, multiple gene group 596个）

第六步：对上一步multiple gene group再次进行拆分，如果一个group中某个groupID只有一个基因，则去掉该groupID,如果groupID全部在group的起始或者终止位置，则将该group切分为一个新的group，剩下的group依次进行处理，如果最后剩余基因少于3个，则不输出
#拆分group
python step9_multigroup_split.py retain_multi_group.txt retain_multi_group_split.txt 
#根据拆分的结果，分为包含单个groupID的group和包含多个groupID的group
python step8_group_classify.py retain_multi_group_split.txt retain_multi_group_multi_group.txt retain_multi_group_single_group.txt  （single gene group 429个, multiple gene group 167个）

第七步：将不同步骤拆分的single gene group进行合并，修改文件名称
cat retain_single_group.txt retain_multi_group_split_single.txt | sort -k2,2 >singlegene_tandem_repeat.txt  （single gene group 2548个）
mv retain_multi_group_multi_group.txt multigene_tandem_repeat.txt （multiple gene group 167个）
