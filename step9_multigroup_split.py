import sys
from collections import defaultdict, OrderedDict

def get_unique_ordered(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def process_line(line):
    parts = line.strip().split('\t')
    if len(parts) != 3:
        return []
    
    original_group, genes_str, groups_str = parts
    genes = genes_str.split(',')
    groups = groups_str.split(',')
    
    # Step 1: Remove single-occurrence groups
    counts = defaultdict(int)
    for g in groups:
        counts[g] += 1
    
    new_groups = []
    new_genes = []
    for g, gene in zip(groups, genes):
        if counts[g] > 1:
            new_groups.append(g)
            new_genes.append(gene)
    
    if len(new_groups) < 2:
        return []
    
    # Step 2: New splitting logic
    output = []
    current_groups = new_groups.copy()
    current_genes = new_genes.copy()
    
    # Find unique groups in order
    unique_groups = get_unique_ordered(current_groups)
    
    for group in unique_groups:
        # Get all indices of this group
        indices = [i for i, g in enumerate(current_groups) if g == group]
        
        # Check if indices form a single continuous block
        if indices != list(range(indices[0], indices[0]+len(indices))):
            continue
        
        # Check if block is at start or end
        is_start = (indices[0] == 0)
        is_end = (indices[-1] == len(current_groups)-1)
        
        if not (is_start or is_end):
            continue
        
        # Extract the continuous block
        block_groups = current_groups[indices[0]:indices[-1]+1]
        block_genes = current_genes[indices[0]:indices[-1]+1]
        
        # Create new entry
        output.append(f"{group}\t{','.join(block_genes)}\t{','.join(block_groups)}")
        
        # Update current data
        current_groups = current_groups[:indices[0]] + current_groups[indices[-1]+1:]
        current_genes = current_genes[:indices[0]] + current_genes[indices[-1]+1:]
        
        # Update unique groups as the list has changed
        unique_groups = get_unique_ordered(current_groups)
        
    # Add remaining data if valid
    if len(current_genes) >= 3:
        remaining_group = '-'.join(get_unique_ordered(current_groups))
        output.append(f"{remaining_group}\t{','.join(current_genes)}\t{','.join(current_groups)}")
    
    return output

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            line = line.rstrip('\n')
            if not line:
                continue
            processed = process_line(line)
            if processed:
                f_out.write('\n'.join(processed) + '\n')

if __name__ == "__main__":
    main()
