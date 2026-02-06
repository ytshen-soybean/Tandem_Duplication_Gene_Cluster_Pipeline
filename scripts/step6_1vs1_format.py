import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)
    
    gene_dict = {}
    input_file = sys.argv[1]
    
    # 读取文件并构建基因字典
    with open(input_file, 'r') as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                print(f"Warning: Line {line_number} has no genes.", file=sys.stderr)
                continue
            
            group = parts[0]
            genes = parts[1:]
            
            for gene in genes:
                if gene in gene_dict:
                    gene_dict[gene].add(group)  # 使用集合去重
                else:
                    gene_dict[gene] = {group}   # 初始化集合
    
    # 检查重复的group
    duplicates = {gene: groups for gene, groups in gene_dict.items() if len(groups) > 1}
    
    # 输出结果或错误信息
    if duplicates:
        print("Error: Genes found in multiple groups:", file=sys.stderr)
        for gene, groups in sorted(duplicates.items()):
            groups_list = sorted(groups)
            print(f"{gene}\t" + ", ".join(groups_list), file=sys.stderr)
        sys.exit(1)
    else:
        for gene, groups in sorted(gene_dict.items()):
            print(f"{gene}\t{groups.pop()}")

if __name__ == "__main__":
    main()
