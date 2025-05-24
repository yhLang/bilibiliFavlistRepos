#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站收藏夹批量下载器 - Git风格仓库管理版
支持下载视频或仅提取音频，可选择清晰度
类似Git的仓库管理：init初始化，pull同步更新
"""

import json
import subprocess
from pathlib import Path

from FavRepository import FavRepository

def get_base_dir():
    """获取或设置基础目录"""
    config_file = Path("bili_config.json")
    
    # 如果配置文件存在，读取已保存的路径
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                base_dir = config.get('base_dir', 'bili_repos')
                if Path(base_dir).exists() or input(f"使用已配置的仓库目录 '{base_dir}'? (y/n, 默认y): ").strip().lower() != 'n':
                    return base_dir
        except Exception:
            pass
    
    # 首次运行或用户选择重新配置
    print("请设置仓库存储目录:")
    print("这个目录将用于存储所有B站收藏夹的下载内容")
    
    while True:
        base_dir = input("请输入目录路径 (默认: bili_repos): ").strip()
        if not base_dir:
            base_dir = "bili_repos"
        
        base_path = Path(base_dir)
        
        # 检查路径是否有效
        try:
            base_path = base_path.resolve()
            # 尝试创建目录
            base_path.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            config = {'base_dir': str(base_path)}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 仓库目录已设置为: {base_path}")
            return str(base_path)
            
        except Exception as e:
            print(f"✗ 目录创建失败: {e}")
            print("请输入一个有效的目录路径")

def main():
    print("bilibili Favlist Repository")
    print("=" * 50)
    
    # 获取基础目录
    base_dir = get_base_dir()
    repo = FavRepository(base_dir)
    
    print()
    print("命令说明:")
    print("  init   - 初始化新仓库")
    print("  pull   - 同步指定仓库 (支持ID或名称)")
    print("  list   - 列出所有仓库")
    print("  config - 重新配置仓库目录")
    print("  update - 更新仓库属性 (清晰度/下载模式)")
    print("  exit   - 退出程序")
    print()
    
    while True:
        command = input("请输入命令: ").strip().lower()
        
        if command == 'exit':
            print("再见！")
            break
        
        elif command == 'init':
            print("\n=== 初始化新仓库 ===")
            url = input("请输入收藏夹链接: ").strip()
            
            fid = repo.parse_favorite_url(url)
            if not fid:
                print("无效的收藏夹链接")
                continue
            
            repo_name = input("请输入仓库名（留空使用收藏夹标题）: ").strip() or None
            
            print("\n可选清晰度:")
            for qn, desc in repo.quality_map.items():
                print(f"{qn}: {desc}")
            
            try:
                quality = int(input("\n请选择清晰度 (默认80-高清1080P): ") or "80")
            except ValueError:
                quality = 80
            
            mode = input("\n下载模式 (1: 视频, 2: 仅音频, 默认2): ").strip() or "2"
            audio_only = mode == "2"
            
            repo.init_repo(fid, repo_name, quality, audio_only)
        
        elif command == 'pull':
            print("\n=== 同步仓库 ===")
            repo.list_repos()
            user_input = input("请输入仓库ID或名称: ").strip()
            
            repo_name = repo.parse_repo_input(user_input)
            if repo_name:
                repo.pull_repo(repo_name)
        
        elif command == 'update':
            print("\n=== 更新仓库属性 ===")
            repo.list_repos()
            user_input = input("请输入要更新的仓库ID或名称: ").strip()
            
            repo_name = repo.parse_repo_input(user_input)
            if not repo_name:
                continue
            
            config = repo.load_repo_config(repo_name)
            print(f"\n当前配置:")
            print(f"  仓库: [{config.get('repo_id', '未知')}] {repo_name}")
            print(f"  模式: {'仅音频' if config['audio_only'] else '视频'}")
            quality_desc = repo.quality_map.get(config['quality'], f"未知({config['quality']})")
            print(f"  清晰度: {quality_desc}")
            
            print(f"\n可修改项:")
            print(f"1. 下载模式")
            print(f"2. 清晰度")
            print(f"3. 两者都修改")
            
            choice = input("请选择 (1/2/3): ").strip()
            
            new_quality = config['quality']
            new_audio_only = config['audio_only']
            
            if choice in ['1', '3']:
                print(f"\n下载模式:")
                print(f"1. 仅音频")
                print(f"2. 视频")
                mode = input("请选择 (1/2): ").strip()
                if mode == '1':
                    new_audio_only = True
                elif mode == '2':
                    new_audio_only = False
                else:
                    print("无效选择")
                    continue
            
            if choice in ['2', '3']:
                print(f"\n可选清晰度:")
                for qn, desc in repo.quality_map.items():
                    print(f"{qn}: {desc}")
                
                try:
                    new_quality = int(input(f"\n请选择清晰度 (当前{config['quality']}): ") or str(config['quality']))
                except ValueError:
                    print("无效的清晰度")
                    continue
            
            if choice in ['1', '2', '3']:
                repo.update_repo_config(repo_name, new_quality, new_audio_only)
        
        elif command == 'config':
            print("\n=== 重新配置仓库目录 ===")
            base_dir = get_base_dir()
            repo = FavRepository(base_dir)
            print("配置已更新")
        
        elif command == 'list':
            print()
            repo.list_repos()
        
        else:
            print("未知命令，请输入 init、pull、list、config、update 或 exit")
        
        print()

if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("请先安装 requests: pip install requests")
        exit(1)
    
    # 检查ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("请先安装 ffmpeg")
        exit(1)
    
    main()