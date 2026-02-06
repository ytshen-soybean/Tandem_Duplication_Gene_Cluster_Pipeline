import sys

def split_files(input_file, output_with_hyphen, output_without_hyphen):
    with open(input_file, 'r') as f_in, \
         open(output_with_hyphen, 'w') as f_hyphen, \
         open(output_without_hyphen, 'w') as f_no_hyphen:
        
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) != 3:
                continue  # 跳过不符合格式的行
            
            group_id = parts[0]
            if '-' in group_id:
                f_hyphen.write(line + '\n')
            else:
                f_no_hyphen.write(line + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input_file output_with_hyphen_file output_without_hyphen_file")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_with_hyphen = sys.argv[2]
    output_without_hyphen = sys.argv[3]
    
    split_files(input_file, output_with_hyphen, output_without_hyphen)
