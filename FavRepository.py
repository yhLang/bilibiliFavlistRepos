import requests

import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

class FavRepository:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = "bili_repos"

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 清晰度映射
        self.quality_map = {
            120: "超清 4K",
            116: "高清 1080P60",
            112: "高清 1080P+",
            80: "高清 1080P",
            74: "高清 720P60",
            64: "高清 720P",
            32: "清晰 480P",
            16: "流畅 360P"
        }

    def get_favorite_info(self, fid):
        """获取收藏夹基本信息"""
        url = f"https://api.bilibili.com/x/v3/fav/folder/info"
        params = {'media_id': fid}

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if data['code'] != 0:
                return None

            info = data['data']
            return {
                'id': info['id'],
                'title': self.clean_filename(info['title']),
                'media_count': info['media_count'],
                'upper': info['upper']['name'] if info['upper'] else 'Unknown'
            }
        except Exception as e:
            print(f"获取收藏夹信息失败: {e}")
            return None

    def get_favorite_videos(self, fid):
        """获取收藏夹中的视频列表"""
        videos = []
        page = 1

        while True:
            url = f"https://api.bilibili.com/x/v3/fav/resource/list"
            params = {
                'media_id': fid,
                'pn': page,
                'ps': 20,
                'keyword': '',
                'order': 'mtime',
                'type': 0,
                'tid': 0,
                'platform': 'web'
            }

            try:
                response = self.session.get(url, params=params)
                data = response.json()

                if data['code'] != 0:
                    print(f"获取收藏夹失败: {data.get('message', '未知错误')}")
                    if data['code'] == -403:
                        print("收藏夹可能是私密的或需要登录访问")
                    break

                medias = data['data']['medias']
                if not medias:
                    break

                for media in medias:
                    if media['type'] == 2:  # 视频类型
                        videos.append({
                            'bvid': media['bvid'],
                            'title': self.clean_filename(media['title']),
                            'upper': media['upper']['name'],
                            'duration': media['duration'],
                            'pubdate': media['pubtime']
                        })

                print(f"已获取第 {page} 页，共 {len(medias)} 个视频")
                page += 1
                time.sleep(0.5)  # 避免请求过快

            except Exception as e:
                print(f"获取收藏夹出错: {e}")
                break

        return videos

    def get_video_info(self, bvid):
        """获取视频详细信息"""
        url = f"https://api.bilibili.com/x/web-interface/view"
        params = {'bvid': bvid}

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if data['code'] != 0:
                return None

            return data['data']
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None

    def get_video_download_url(self, bvid, cid, quality=80):
        """获取视频下载链接"""
        url = "https://api.bilibili.com/x/player/playurl"
        params = {
            'bvid': bvid,
            'cid': cid,
            'qn': quality,
            'fnval': 16,
            'fourk': 1
        }

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if data['code'] != 0:
                return None, None

            play_info = data['data']
            if 'dash' in play_info:
                # DASH格式
                video_url = play_info['dash']['video'][0]['baseUrl'] if play_info['dash']['video'] else None
                audio_url = play_info['dash']['audio'][0]['baseUrl'] if play_info['dash']['audio'] else None
                actual_quality = play_info['quality']
                return {'video': video_url, 'audio': audio_url}, actual_quality
            else:
                # 传统格式
                video_url = play_info['durl'][0]['url']
                return {'video': video_url, 'audio': None}, play_info['quality']

        except Exception as e:
            print(f"获取下载链接失败: {e}")
            return None, None

    def download_file(self, url, filepath):
        """下载文件"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r下载进度: {percent:.1f}%", end='', flush=True)

            print()  # 换行
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False

    def merge_video_audio(self, video_path, audio_path, output_path):
        """合并视频和音频"""
        cmd = [
            'ffmpeg', '-i', video_path, '-i', audio_path,
            '-c', 'copy', '-y', output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"合并失败: {e}")
            return False

    def extract_audio(self, video_path, audio_path):
        """提取音频"""
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'copy', '-y', audio_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"提取音频失败: {e}")
            return False

    def clean_filename(self, filename):
        """清理文件名"""
        # 移除或替换不合法的字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip()
        return filename[:100]  # 限制长度

    def parse_favorite_url(self, url):
        """解析收藏夹URL，提取fid"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if 'fid' in query_params:
            return query_params['fid'][0]

        return None

    def get_repo_path(self, repo_name):
        """获取仓库路径"""
        return self.base_dir / repo_name

    def get_repo_config_path(self, repo_name):
        """获取仓库配置文件路径"""
        return self.get_repo_path(repo_name) / ".bili_repo.json"

    def get_next_repo_id(self):
        """获取下一个可用的仓库ID"""
        existing_ids = set()
        for item in self.base_dir.iterdir():
            if item.is_dir():
                config = self.load_repo_config(item.name)
                if config and 'repo_id' in config:
                    existing_ids.add(config['repo_id'])

        # 找到最小的未使用ID
        repo_id = 1
        while repo_id in existing_ids:
            repo_id += 1
        return repo_id

    def find_repo_by_id(self, repo_id):
        """通过ID查找仓库"""
        for item in self.base_dir.iterdir():
            if item.is_dir():
                config = self.load_repo_config(item.name)
                if config and config.get('repo_id') == repo_id:
                    return item.name
        return None

    def init_repo(self, fid, repo_name=None, quality=80, audio_only=True):
        """初始化仓库（类似git init）"""
        print(f"正在初始化收藏夹仓库...")

        # 获取收藏夹信息
        fav_info = self.get_favorite_info(fid)
        if not fav_info:
            print("无法获取收藏夹信息")
            return False

        # 如果没有指定仓库名，使用收藏夹标题
        if not repo_name:
            repo_name = fav_info['title']

        repo_path = self.get_repo_path(repo_name)
        config_path = self.get_repo_config_path(repo_name)

        # 检查仓库是否已存在
        if config_path.exists():
            print(f"仓库 '{repo_name}' 已存在")
            return False

        # 创建仓库目录
        repo_path.mkdir(exist_ok=True)

        # 获取新的仓库ID
        repo_id = self.get_next_repo_id()

        # 创建配置文件
        config = {
            'repo_id': repo_id,
            'fid': fid,
            'repo_name': repo_name,
            'fav_title': fav_info['title'],
            'fav_upper': fav_info['upper'],
            'quality': quality,
            'audio_only': audio_only,
            'created_time': datetime.now().isoformat(),
            'last_sync': None,
            'video_list': {}
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"✓ 仓库已初始化: {repo_path}")
        print(f"  仓库ID: {repo_id}")
        print(f"  收藏夹: {fav_info['title']}")
        print(f"  UP主: {fav_info['upper']}")
        print(f"  视频数量: {fav_info['media_count']}")
        print(f"  下载模式: {'仅音频' if audio_only else '视频'}")
        quality_desc = self.quality_map.get(quality, f"未知({quality})")
        print(f"  清晰度: {quality_desc}")

        # 自动进行首次同步
        print(f"\n开始首次同步...")
        success = self.pull_repo(repo_name)

        return success

    def load_repo_config(self, repo_name):
        """加载仓库配置"""
        config_path = self.get_repo_config_path(repo_name)
        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载仓库配置失败: {e}")
            return None

    def save_repo_config(self, repo_name, config):
        """保存仓库配置"""
        config_path = self.get_repo_config_path(repo_name)
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存仓库配置失败: {e}")
            return False

    def download_video(self, video_info, repo_path, quality=80, audio_only=True):
        """下载单个视频"""
        bvid = video_info['bvid']
        title = video_info['title']

        print(f"正在下载: {title}")

        # 获取视频详细信息
        detail = self.get_video_info(bvid)
        if not detail:
            print("获取视频详细信息失败")
            return False

        # 获取第一个分P的cid
        cid = detail['pages'][0]['cid']

        # 获取下载链接
        urls, actual_quality = self.get_video_download_url(bvid, cid, quality)
        if not urls:
            print("获取下载链接失败")
            return False

        quality_desc = self.quality_map.get(actual_quality, f"未知({actual_quality})")
        print(f"实际清晰度: {quality_desc}")

        if audio_only:
            # 仅下载音频
            if urls['audio']:
                audio_file = repo_path / f"{title}.m4a"
                print("下载音频...")
                if self.download_file(urls['audio'], audio_file):
                    print(f"✓ 音频下载完成")
                    return True
            else:
                # 如果没有单独音频流，下载视频后提取音频
                video_file = repo_path / f"{title}_temp.mp4"
                audio_file = repo_path / f"{title}.m4a"

                print("下载视频...")
                if self.download_file(urls['video'], video_file):
                    print("提取音频...")
                    if self.extract_audio(video_file, audio_file):
                        os.remove(video_file)  # 删除临时视频文件
                        print(f"✓ 音频提取完成")
                        return True
                    else:
                        os.remove(video_file)
        else:
            # 下载视频
            if urls['audio'] and urls['video']:
                # DASH格式，需要分别下载视频和音频后合并
                video_temp = repo_path / f"{title}_video.mp4"
                audio_temp = repo_path / f"{title}_audio.m4a"
                final_file = repo_path / f"{title}.mp4"

                print("下载视频流...")
                if not self.download_file(urls['video'], video_temp):
                    return False

                print("下载音频流...")
                if not self.download_file(urls['audio'], audio_temp):
                    os.remove(video_temp)
                    return False

                print("合并视频和音频...")
                if self.merge_video_audio(video_temp, audio_temp, final_file):
                    os.remove(video_temp)
                    os.remove(audio_temp)
                    print(f"✓ 视频下载完成")
                    return True
                else:
                    os.remove(video_temp)
                    os.remove(audio_temp)
            else:
                # 传统格式，直接下载
                video_file = repo_path / f"{title}.mp4"
                print("下载视频...")
                if self.download_file(urls['video'], video_file):
                    print(f"✓ 视频下载完成")
                    return True

        return False

    def pull_repo(self, repo_name):
        """同步仓库（类似git pull）"""
        config = self.load_repo_config(repo_name)
        if not config:
            print(f"仓库 '{repo_name}' 不存在，请先使用 init 命令初始化")
            return False

        print(f"正在同步仓库: {repo_name}")
        print(f"收藏夹: {config['fav_title']}")

        fid = config['fid']
        repo_path = self.get_repo_path(repo_name)

        # 获取当前收藏夹视频列表
        current_videos = self.get_favorite_videos(fid)
        if not current_videos:
            print("获取收藏夹视频列表失败")
            return False

        # 创建当前视频的bvid集合
        current_bvids = {video['bvid'] for video in current_videos}
        local_bvids = set(config['video_list'].keys())

        # 找出需要删除的视频（本地有但云端没有）
        to_delete = local_bvids - current_bvids
        # 找出需要下载的视频（云端有但本地没有）
        to_download = current_bvids - local_bvids

        print(f"本地视频: {len(local_bvids)} 个")
        print(f"云端视频: {len(current_bvids)} 个")
        print(f"需要删除: {len(to_delete)} 个")
        print(f"需要下载: {len(to_download)} 个")

        # 删除本地多余的文件
        deleted_count = 0
        for bvid in to_delete:
            video_info = config['video_list'][bvid]
            title = video_info['title']

            # 确定文件扩展名
            extension = '.m4a' if config['audio_only'] else '.mp4'
            file_path = repo_path / f"{title}{extension}"

            if file_path.exists():
                try:
                    os.remove(file_path)
                    print(f"✗ 已删除: {title}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除失败 {title}: {e}")

            # 从配置中移除
            del config['video_list'][bvid]

        # 下载新视频
        downloaded_count = 0
        videos_to_download = [v for v in current_videos if v['bvid'] in to_download]

        for i, video in enumerate(videos_to_download, 1):
            print(f"\n[{i}/{len(videos_to_download)}] ", end='')

            if self.download_video(video, repo_path, config['quality'], config['audio_only']):
                # 添加到配置
                config['video_list'][video['bvid']] = {
                    'title': video['title'],
                    'upper': video['upper'],
                    'duration': video['duration'],
                    'pubdate': video['pubdate'],
                    'download_time': datetime.now().isoformat()
                }
                downloaded_count += 1
            else:
                print("✗ 下载失败")

            # 休息一下避免请求过快
            time.sleep(1)

        # 更新配置
        config['last_sync'] = datetime.now().isoformat()
        self.save_repo_config(repo_name, config)

        print(f"\n同步完成！")
        print(f"✓ 下载: {downloaded_count} 个")
        print(f"✗ 删除: {deleted_count} 个")
        print(f"📁 当前仓库共有: {len(config['video_list'])} 个文件")

        return True

    def update_repo_config(self, repo_name, quality=None, audio_only=None):
        """更新仓库配置"""
        config = self.load_repo_config(repo_name)
        if not config:
            print(f"仓库 '{repo_name}' 不存在")
            return False

        repo_path = self.get_repo_path(repo_name)
        old_audio_only = config['audio_only']
        old_quality = config['quality']

        # 更新配置
        if quality is not None:
            config['quality'] = quality
        if audio_only is not None:
            config['audio_only'] = audio_only

        # 保存配置
        if not self.save_repo_config(repo_name, config):
            return False

        print(f"✓ 仓库配置已更新")
        if quality is not None and quality != old_quality:
            quality_desc = self.quality_map.get(quality, f"未知({quality})")
            print(f"  清晰度: {self.quality_map.get(old_quality, f'未知({old_quality})')} → {quality_desc}")

        if audio_only is not None and audio_only != old_audio_only:
            old_mode = '仅音频' if old_audio_only else '视频'
            new_mode = '仅音频' if audio_only else '视频'
            print(f"  下载模式: {old_mode} → {new_mode}")

        # 如果下载模式发生变化，提示用户
        if audio_only is not None and audio_only != old_audio_only:
            print(f"\n注意: 下载模式已改变，建议:")
            if audio_only:
                print("- 删除现有视频文件，重新下载音频")
                print("- 或保留视频文件，新视频将下载为音频")
            else:
                print("- 删除现有音频文件，重新下载视频")
                print("- 或保留音频文件，新视频将下载为视频")

            choice = input("是否重新下载所有文件? (y/n, 默认n): ").strip().lower()
            if choice == 'y':
                # 清空本地文件和记录
                print("正在清理旧文件...")
                for file_path in repo_path.iterdir():
                    if file_path.suffix in ['.mp4', '.m4a', '.mp3'] and file_path.name != '.bili_repo.json':
                        try:
                            os.remove(file_path)
                            print(f"已删除: {file_path.name}")
                        except Exception as e:
                            print(f"删除失败 {file_path.name}: {e}")

                # 清空视频列表，强制重新下载
                config['video_list'] = {}
                self.save_repo_config(repo_name, config)

                print("开始重新下载...")
                return self.pull_repo(repo_name)

        return True

    def parse_repo_input(self, user_input):
        """解析用户输入的仓库标识（ID或名称）"""
        user_input = user_input.strip()

        # 尝试解析为数字ID
        try:
            repo_id = int(user_input)
            repo_name = self.find_repo_by_id(repo_id)
            if repo_name:
                return repo_name
            else:
                print(f"未找到ID为 {repo_id} 的仓库")
                return None
        except ValueError:
            # 不是数字，当作仓库名处理
            if self.load_repo_config(user_input):
                return user_input
            else:
                print(f"未找到名为 '{user_input}' 的仓库")
                return None

    def list_repos(self):
        """列出所有仓库"""
        repos = []
        for item in self.base_dir.iterdir():
            if item.is_dir():
                config_path = item / ".bili_repo.json"
                if config_path.exists():
                    config = self.load_repo_config(item.name)
                    if config:
                        repos.append({
                            'name': item.name,
                            'config': config
                        })

        if not repos:
            print("没有找到任何仓库")
            return

        print("现有仓库列表:")
        print("=" * 80)
        for repo in repos:
            config = repo['config']
            repo_id = config.get('repo_id', '未知')
            print(f"📁 [{repo_id}] {repo['name']}")
            print(f"   收藏夹: {config['fav_title']}")
            print(f"   UP主: {config['fav_upper']}")
            print(f"   模式: {'仅音频' if config['audio_only'] else '视频'}")
            quality_desc = self.quality_map.get(config['quality'], f"未知({config['quality']})")
            print(f"   清晰度: {quality_desc}")
            print(f"   视频数量: {len(config['video_list'])}")
            print(f"   最后同步: {config['last_sync'] or '从未同步'}")
            print()