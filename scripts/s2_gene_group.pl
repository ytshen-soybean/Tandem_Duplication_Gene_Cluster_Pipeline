#!/usr/bin/perl
use strict;
use warnings;

# 高效同源基因分组脚本
# 输入：包含基因对的TSV文件
# 输出：分组结果的TSV文件

my ($input_file, $output_file) = @ARGV;
die "使用方法：$0 输入文件 输出文件\n" unless $output_file;

my %adj;        # 邻接表（哈希结构提高查询效率）
my %visited;    # 访问标记
my @groups;     # 存储分组结果

# 1. 构建邻接表（自动去重）
open my $in_fh, '<', $input_file or die "无法打开输入文件：$!";
while (my $line = <$in_fh>) {
    next if $line =~ /^\s*$/;  # 跳过空行
    my ($g1, $g2) = split /\s+/, $line;
    $adj{$g1}{$g2} = 1;  # 哈希的哈希实现快速去重
    $adj{$g2}{$g1} = 1;
}
close $in_fh;

# 2. BFS遍历找连通分量
foreach my $gene (keys %adj) {
    next if $visited{$gene};
    
    my @group;
    my @queue = ($gene);
    $visited{$gene} = 1;
    
    while (@queue) {
        my $current = shift @queue;
        push @group, $current;
        
        # 直接遍历哈希键避免重复检查
        foreach my $neighbor (keys %{$adj{$current}}) {
            unless ($visited{$neighbor}) {
                $visited{$neighbor} = 1;
                push @queue, $neighbor;
            }
        }
    }
    
    push @groups, [sort @group] if @group;
}

# 3. 输出结果到文件（按分组大小排序）
open my $out_fh, '>', $output_file or die "无法创建输出文件：$!";
my $group_num = 1;
foreach my $group (sort { @$b <=> @$a } @groups) {
    print $out_fh join("\t", "group$group_num", @$group), "\n";
    $group_num++;
}
close $out_fh;

print "处理完成！共找到".@groups."个同源组\n";
