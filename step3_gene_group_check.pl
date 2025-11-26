#!/usr/bin/perl
use strict;
use warnings;

my %last_chr;  # 保存各染色体最后处理的group信息：{ gene_num => ..., group => ... }

while (my $line = <>) {
    chomp $line;
    next if $line =~ /^\s*$/;  # 跳过空行

    my @fields = split ' ', $line;
    next if @fields < 2;       # 忽略无基因的group

    my ($group, $gene_id) = @fields[0,1];

    # 提取染色体编号和基因编号
    if ($gene_id =~ /(\d{2})G(\d{4})/) {
        my ($chr, $current_num) = ($1, $2);

        if (exists $last_chr{$chr}) {
            my $last_num = $last_chr{$chr}{gene_num};
            my $last_group = $last_chr{$chr}{group};

            # 比较当前基因编号是否小于等于上一个
            if ($current_num le $last_num) {
                print "$last_group $group\n";
            }
        }

        # 更新当前染色体记录（无论是否输出）
        $last_chr{$chr} = { gene_num => $current_num, group => $group };
    } else {
        warn "无法解析基因ID: $gene_id (Group: $group)\n";
    }
}
