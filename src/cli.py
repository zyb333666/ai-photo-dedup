"""
命令行入口模块
"""

import click
import os
from pathlib import Path

from .dedup import PhotoDeduplicator
from .report import ReportGenerator


@click.group()
def cli():
    """AI 智能清理重复照片工具"""
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--threshold', '-t', default=0.9, help='相似度阈值 (0-1)，默认 0.9')
@click.option('--action', '-a', type=click.Choice(['scan', 'move', 'delete']), 
              default='scan', help='执行操作: scan=仅扫描, move=移动到回收站, delete=永久删除')
@click.option('--output', '-o', help='报告输出路径')
@click.option('--use-ai', is_flag=True, help='使用 AI 特征辅助判断')
@click.option('--recursive/--no-recursive', default=True, help='递归扫描子目录')
@click.option('--yes', '-y', is_flag=True, help='跳过确认直接执行')
def scan(directory, threshold, action, output, use_ai, recursive, yes):
    """扫描目录查找重复图片"""
    
    click.echo(f"🔍 正在扫描: {directory}")
    click.echo(f"📊 相似度阈值: {threshold}")
    if use_ai:
        click.echo("🤖 AI 辅助: 已启用")
    
    # 初始化去重器
    dedup = PhotoDeduplicator(
        threshold=threshold,
        use_ai=use_ai,
    )
    
    # 扫描目录
    try:
        groups = dedup.scan_directory(directory, recursive=recursive)
    except Exception as e:
        click.echo(f"❌ 扫描失败: {e}", err=True)
        return
    
    if not groups:
        click.echo("✅ 未发现重复图片！")
        return
    
    # 显示结果
    total_duplicates = sum(len(g.duplicates) for g in groups)
    click.echo(f"\n📋 扫描结果:")
    click.echo(f"   重复组: {len(groups)}")
    click.echo(f"   重复文件: {total_duplicates}")
    
    # 生成报告
    if output:
        report_gen = ReportGenerator(groups)
        if output.endswith('.json'):
            report_gen.generate_json(output)
        else:
            if not output.endswith('.html'):
                output += '.html'
            report_gen.generate_html(output)
        click.echo(f"📄 报告已保存: {output}")
    
    # 执行操作
    if action == 'scan':
        click.echo("\n💡 使用 --action move 可移动重复文件到回收站")
        click.echo("💡 使用 --action delete 可永久删除重复文件（谨慎）")
    
    elif action in ('move', 'delete'):
        if not yes:
            click.confirm(f"\n⚠️ 将{'移动' if action == 'move' else '删除'} {total_duplicates} 个重复文件，是否继续？", 
                         abort=True)
        
        if action == 'move':
            moved = dedup.move_duplicates(groups, confirm=False)
            click.echo(f"✅ 已移动 {len(moved)} 个文件到回收站")
        else:
            deleted = dedup.delete_duplicates(groups, confirm=False)
            click.echo(f"✅ 已永久删除 {len(deleted)} 个文件")


def main():
    cli()


if __name__ == '__main__':
    main()
