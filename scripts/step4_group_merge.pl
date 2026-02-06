#!/usr/bin/perl
use strict;
use warnings;

my @groups;

# 读取并解析所有group数据
while (my $line = <>) {
    chomp $line;
    my @cols = split /\t/, $line;
    next unless @cols >= 2;  # 跳过空行或无效行
    
    my $group_name = shift @cols;
    my @genes = @cols;
    
    # 提取起始和终止基因编号
    my ($chr) = $genes[0] =~ /(\d{2})G/ or die "Invalid gene format: $genes[0]";
    my ($start) = $genes[0] =~ /G(\d{6})/ or die "Invalid gene format: $genes[0]";
    my ($end) = $genes[-1] =~ /G(\d{6})/ or die "Invalid gene format: $genes[-1]";
    
    push @groups, {
        chr => $chr,
        name => $group_name,
        start => $start,
        end => $end,
        genes => \@genes,
    };
}

# 合并重叠的group
my @result;
if (@groups) {
    my $current = shift @groups;
    my ($chr, $name, $start, $end, $genes) = @{$current}{qw/chr name start end genes/};
    
    for my $group (@groups) {
        if ($group->{start} <= $end and  $chr == $group->{chr}) {
            # 合并group
            $end = $group->{end} if $group->{end} > $end;
            $name .= "_$group->{name}";
            push @$genes, @{$group->{genes}};
        } else {
            # 保存当前合并结果
            push @result, { name => $name, genes => $genes };
            # 重置为新的group
            ($chr, $name, $start, $end, $genes) = @{$group}{qw/chr name start end genes/};
        }
    }
    
    # 添加最后一个合并结果
    push @result, { name => $name, genes => $genes };
}

# 输出结果
for my $entry (@result) {
    print join("\t", $entry->{name}, @{$entry->{genes}}), "\n";
}
