import sys
from collections import defaultdict

def get_gene_key(gene_id):
    """提取基因ID中G后的4位数字作为排序键"""
    g_index = gene_id.find('G')
    if g_index == -1:
        return 0
    number_part = gene_id[g_index+1:g_index+5]
    try:
        return int(number_part)
    except ValueError:
        return 0

def process_files(input1_path, input2_path, output1_path, output2_path):
    # 读取输入文件2，建立基因到group的字典
    gene_to_group = {}
    with open(input2_path, 'r') as f2:
        for line in f2:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                gene = parts[0]
                group = parts[1]
                gene_to_group[gene] = group

    # 处理输入文件1并分流输出
    with open(input1_path, 'r') as f1, \
         open(output1_path, 'w') as out1, \
         open(output2_path, 'w') as out2:

        for raw_line in f1:
            original_line = raw_line.rstrip('\n')
            line = original_line.strip()
            if not line:
                continue

            # 分割列并验证有效性
            parts = line.split()
            if len(parts) < 5:
                out2.write(f"{original_line}\n")
                continue

            try:
                genes = parts[1].split(',')
                group_nums = parts[4].split(',')
            except IndexError:
                out2.write(f"{original_line}\n")
                continue

            # 检查基因与分组编号数量是否匹配
            if len(genes) != len(group_nums):
                out2.write(f"{original_line}\n")
                continue

            # 基因分组逻辑
            groups_dict = defaultdict(list)
            for gene, num in zip(genes, group_nums):
                if num.strip() == '-1':
                    continue
                if gene in gene_to_group:
                    groups_dict[num.strip()].append(gene)

            # 生成输出内容
            output_lines = []
            for num, gene_list in groups_dict.items():
                # 按基因编号排序
                sorted_genes = sorted(gene_list, key=get_gene_key)
                
                # 生成新分组名称（去重后排序）
                unique_groups = sorted({gene_to_group[gene] for gene in sorted_genes})
                new_group_name = '-'.join(unique_groups)
                
                # 生成第三列group顺序
                group_sequence = [gene_to_group[gene] for gene in sorted_genes]
                
                # 构建输出行
                output_line = f"{new_group_name}\t{','.join(sorted_genes)}\t{','.join(group_sequence)}"
                output_lines.append(output_line)

            # 分流输出
            if output_lines:
                out1.write('\n'.join(output_lines) + '\n')
            else:
                out2.write(f"{original_line}\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py input1.txt input2.txt output1.txt output2.txt")
        sys.exit(1)
    
    input1_path = sys.argv[1]
    input2_path = sys.argv[2]
    output1_path = sys.argv[3]
    output2_path = sys.argv[4]
    
    process_files(input1_path, input2_path, output1_path, output2_path)
