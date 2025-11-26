import sys

def extract_gene_number(gene_id):
    # 分割gene_id以获取G后面的部分，并提取前四位数字
    parts = gene_id.split('G')
    if len(parts) < 2:
        return None
    number_part = parts[1]
    # 提取前四位并转换为整数
    if len(number_part) < 4:
        return None
    four_digits = number_part[:4]
    try:
        return int(four_digits)
    except ValueError:
        return None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    cols = line.split('\t')
    if len(cols) < 2:
        continue
    gene1, gene2 = cols[0], cols[1]
    
    # 提取基因编号
    g1_num = extract_gene_number(gene1)
    g2_num = extract_gene_number(gene2)
    
    if g1_num is None or g2_num is None:
        continue  # 忽略无法解析的行
    
    diff = abs(g1_num - g2_num)
    if diff!=0 and diff <= 50:
        print(line)
