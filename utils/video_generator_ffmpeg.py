import os
import platform
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
from utils.voicevox import VoiceVoxAPI


class VideoGeneratorFFmpeg:
    """Pillow + FFmpegで動画生成（高速・高品質）"""

    # 縦書き時に回転が必要な文字
    VERTICAL_ROTATE_CHARS = {'ー', '〜', '～', '－', '-', '―', '‐', '–', '—', '=', '＝', '+', '＋', '<', '>', '＜', '＞'}

    # 小書き文字（右に寄せる）
    SMALL_CHARS = {'っ', 'ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ', 'ゃ', 'ゅ', 'ょ', 'ゎ',
                   'ッ', 'ァ', 'ィ', 'ゥ', 'ェ', 'ォ', 'ャ', 'ュ', 'ョ', 'ヮ', 'ヶ', 'ヵ'}

    def __init__(self, background_color=(0, 255, 0), voicevox_url="http://localhost:50021"):
        self.background_color = background_color
        self.voicevox = VoiceVoxAPI(voicevox_url)

    def _create_checker_background(self, width: int, height: int, cell_size: int = 20) -> Image.Image:
        """チェッカーパターン背景を作成（Photoshop風透過表示）"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        color1 = (200, 200, 200)  # 明るいグレー
        color2 = (150, 150, 150)  # 暗いグレー

        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                # 市松模様
                if (x // cell_size + y // cell_size) % 2 == 0:
                    color = color1
                else:
                    color = color2
                draw.rectangle([x, y, x + cell_size, y + cell_size], fill=color)

        return img

    def _create_text_image(self, text: str, width: int, height: int, font_size: int = 100, transparent: bool = False, checker: bool = False) -> Image.Image:
        """縦書きテキスト画像を生成"""
        # OS別にフォントを読み込み
        font = None
        if platform.system() == "Darwin":
            # macOS → ヒラギノ角ゴシック
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/ヒラギノ角ゴ ProN W6.otf",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
            ]
        elif platform.system() == "Linux":
            # Linux (Streamlit Cloud等) → Noto Sans CJK
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
                "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
            ]
        else:
            # Windows → 游ゴシック
            font_paths = [
                "C:/Windows/Fonts/YuGothB.ttc",  # 游ゴシック Bold
                "C:/Windows/Fonts/YuGothM.ttc",  # 游ゴシック Medium
                "C:/Windows/Fonts/meiryo.ttc",   # メイリオ（フォールバック）
            ]
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()

        # 固定の文字送り（通常）
        char_pitch = font_size

        # 文字情報を収集
        char_info = []
        for char in text:
            needs_rotation = char in self.VERTICAL_ROTATE_CHARS
            is_small = char in self.SMALL_CHARS
            char_info.append((char, needs_rotation, is_small))

        # 高さ計算（全文字同じ間隔）
        total_height = char_pitch * len(char_info)
        max_width = font_size

        # 背景サイズ
        rect_width = max_width + 60
        rect_height = total_height + 60

        # 画像を作成（透過、チェッカー、または緑背景）
        if transparent:
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        elif checker:
            img = self._create_checker_background(width, height)
        else:
            img = Image.new('RGB', (width, height), self.background_color)
        draw = ImageDraw.Draw(img)

        # 白い長方形を描画（Y=288）
        rect_x = (width - rect_width) // 2
        rect_y = 288
        draw.rectangle(
            [(rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height)],
            fill=(255, 255, 255)
        )

        # 縦書きテキスト描画（白背景はそのまま、文字のみ25px上）
        y_offset = rect_y + 5
        x_center = width // 2

        for i, (char, needs_rotation, is_small) in enumerate(char_info):
            if needs_rotation:
                # 長音記号を90度回転（中央配置）
                # 回転用の画像サイズ
                img_size = font_size * 2
                char_img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
                char_draw = ImageDraw.Draw(char_img)

                # 文字を画像の中央に描画
                char_draw.text((img_size // 2, img_size // 2), char, font=font, fill=(0, 0, 0, 255), anchor="mm")

                # 90度回転
                char_img = char_img.rotate(90, expand=False, resample=Image.BICUBIC)

                # 回転後の文字位置を取得
                rotated_bbox = char_img.getbbox()
                if rotated_bbox:
                    # x_centerに文字の中心が来るように配置
                    rotated_center_x = (rotated_bbox[0] + rotated_bbox[2]) // 2
                    paste_x = x_center - rotated_center_x
                    # 文字の上端をy_offsetに合わせる
                    paste_y = y_offset - rotated_bbox[1]
                else:
                    paste_x = x_center - img_size // 2
                    paste_y = y_offset

                img.paste(char_img, (paste_x, paste_y), char_img)
                y_offset += char_pitch
            elif is_small:
                # 小書き文字は右に寄せ、前の文字に重ねる
                # 前の文字が小書き文字かどうかで重なり量を変える
                prev_is_small = i > 0 and char_info[i-1][2]
                overlap = 10 if prev_is_small else 20  # 2文字目以降は10px、1文字目は20px

                bbox = draw.textbbox((0, 0), char, font=font)
                char_w = bbox[2] - bbox[0]
                # 通常文字と同じ中央揃えから10px右にオフセット
                x = x_center - char_w // 2 + 10
                y = y_offset - overlap
                draw.text((x, y), char, font=font, fill=(0, 0, 0))
                y_offset += char_pitch - overlap
            else:
                # 通常の文字
                bbox = draw.textbbox((0, 0), char, font=font)
                char_w = bbox[2] - bbox[0]
                x = x_center - char_w // 2
                y = y_offset
                draw.text((x, y), char, font=font, fill=(0, 0, 0))
                y_offset += char_pitch

        return img

    def count_clips(self, text: str) -> int:
        """テキストから生成されるクリップ数を計算"""
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        return len(lines)

    def create_green_screen_video(
        self,
        audio_text: str,
        display_text: str,
        speaker_id: int,
        speed: float = 1.0,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        transparent: bool = False,
        progress_callback=None
    ) -> tuple:
        """FFmpegで動画を生成

        Args:
            audio_text: 音声生成用テキスト（改行区切り）
            display_text: 表示用テキスト（改行区切り）
            progress_callback: 進捗コールバック関数 (current, total, message) を受け取る

        Returns:
            tuple: (透過動画bytes, プレビュー動画bytes) - 透過モード時
                   (動画bytes, None) - 非透過モード時
        """
        # 音声用テキストを行ごとに分割
        audio_lines = [line.strip() for line in audio_text.strip().split('\n') if line.strip()]

        # 表示用テキストを行ごとに分割し、句読点を削除
        display_lines = []
        for line in display_text.strip().split('\n'):
            line = line.strip()
            if line:
                clean_line = line.replace('、', '').replace('。', '').replace('，', '').replace('．', '')
                display_lines.append(clean_line)

        # 行数が異なる場合は警告し、短い方に合わせる
        if len(audio_lines) != len(display_lines):
            print(f"警告: 音声用テキスト({len(audio_lines)}行)と表示用テキスト({len(display_lines)}行)の行数が異なります")
            min_len = min(len(audio_lines), len(display_lines))
            audio_lines = audio_lines[:min_len]
            display_lines = display_lines[:min_len]

        # (音声用, 表示用) のペアを作成
        lines = list(zip(audio_lines, display_lines))

        if not lines:
            raise ValueError("テキストが空です")

        total_clips = len(lines)

        temp_dir = tempfile.mkdtemp()
        temp_files = []
        segment_videos_transparent = []
        segment_videos_preview = []

        try:
            # 各行の動画セグメントを作成
            for i, (audio_line, display_line) in enumerate(lines):
                clip_num = i + 1
                print(f"セグメント {clip_num}/{total_clips} を作成中: {display_line[:20]}...")

                # 進捗コールバック
                if progress_callback:
                    progress_callback(clip_num, total_clips, f"クリップ {clip_num}/{total_clips} を生成中...")

                # 1. 音声生成
                audio_data = self.voicevox.generate_voice(audio_line, speaker_id, speed)
                if not audio_data:
                    raise Exception(f"行 {i+1} の音声生成に失敗しました")

                audio_path = os.path.join(temp_dir, f"audio_{i}.wav")
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                temp_files.append(audio_path)

                # 2. 音声の長さを取得
                duration = self._get_audio_duration(audio_path)

                if transparent:
                    # 透過モード：透過画像とチェッカー画像の両方を生成
                    # 透過画像
                    img_transparent = self._create_text_image(display_line, width, height, transparent=True)
                    img_transparent_path = os.path.join(temp_dir, f"frame_transparent_{i}.png")
                    img_transparent.save(img_transparent_path)
                    temp_files.append(img_transparent_path)

                    # チェッカー背景画像（プレビュー用）
                    img_preview = self._create_text_image(display_line, width, height, checker=True)
                    img_preview_path = os.path.join(temp_dir, f"frame_preview_{i}.png")
                    img_preview.save(img_preview_path)
                    temp_files.append(img_preview_path)

                    # 透過動画セグメント
                    video_transparent_path = os.path.join(temp_dir, f"segment_transparent_{i}.mov")
                    self._create_video_segment(img_transparent_path, audio_path, video_transparent_path, duration, fps, transparent=True)
                    segment_videos_transparent.append(video_transparent_path)
                    temp_files.append(video_transparent_path)

                    # プレビュー動画セグメント（MP4）
                    video_preview_path = os.path.join(temp_dir, f"segment_preview_{i}.mp4")
                    self._create_video_segment(img_preview_path, audio_path, video_preview_path, duration, fps, transparent=False)
                    segment_videos_preview.append(video_preview_path)
                    temp_files.append(video_preview_path)
                else:
                    # 非透過モード：グリーンバック動画のみ
                    img = self._create_text_image(display_line, width, height, transparent=False)
                    img_path = os.path.join(temp_dir, f"frame_{i}.png")
                    img.save(img_path)
                    temp_files.append(img_path)

                    video_path = os.path.join(temp_dir, f"segment_{i}.mp4")
                    self._create_video_segment(img_path, audio_path, video_path, duration, fps, transparent=False)
                    segment_videos_transparent.append(video_path)
                    temp_files.append(video_path)

            # 全セグメントを連結
            print(f"全 {len(segment_videos_transparent)} セグメントを連結中...")

            if transparent:
                # 透過動画（MOV）
                output_transparent_path = os.path.join(temp_dir, "output_transparent.mov")
                self._concat_videos(segment_videos_transparent, output_transparent_path, transparent=True)
                temp_files.append(output_transparent_path)

                # プレビュー動画（MP4）
                output_preview_path = os.path.join(temp_dir, "output_preview.mp4")
                self._concat_videos(segment_videos_preview, output_preview_path, transparent=False)
                temp_files.append(output_preview_path)

                with open(output_transparent_path, 'rb') as f:
                    video_transparent = f.read()
                with open(output_preview_path, 'rb') as f:
                    video_preview = f.read()

                print("動画生成完了！（透過 + プレビュー）")
                return (video_transparent, video_preview)
            else:
                # 非透過動画（MP4のみ）
                output_path = os.path.join(temp_dir, "output.mp4")
                self._concat_videos(segment_videos_transparent, output_path, transparent=False)
                temp_files.append(output_path)

                with open(output_path, 'rb') as f:
                    video_data = f.read()

                print("動画生成完了！")
                return (video_data, None)

        finally:
            # クリーンアップ
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def _get_audio_duration(self, audio_path: str) -> float:
        """音声ファイルの長さを取得"""
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())

    def _create_video_segment(self, img_path: str, audio_path: str, output_path: str, duration: float, fps: int, transparent: bool = False):
        """1つのセグメント動画を作成（音声と映像を同期）"""
        if transparent:
            # ProRes 4444（アルファチャンネル対応）
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-framerate', str(fps),
                '-t', str(duration),
                '-i', img_path,
                '-i', audio_path,
                '-c:v', 'prores_ks',
                '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le',
                '-c:a', 'pcm_s16le',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-vsync', 'cfr',
                output_path
            ], capture_output=True, check=True)
        else:
            # 通常のMP4
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-framerate', str(fps),
                '-t', str(duration),
                '-i', img_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-vsync', 'cfr',
                output_path
            ], capture_output=True, check=True)

    def _concat_videos(self, video_paths: list, output_path: str, transparent: bool = False):
        """複数の動画を連結（音声同期を維持）"""
        # 連結リストファイルを作成
        list_path = output_path + '.txt'
        with open(list_path, 'w') as f:
            for vp in video_paths:
                f.write(f"file '{vp}'\n")

        if transparent:
            # ProRes 4444を維持（音声同期オプション付き）
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_path,
                '-c:v', 'prores_ks',
                '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le',
                '-c:a', 'pcm_s16le',
                '-vsync', 'cfr',
                '-af', 'aresample=async=1',
                output_path
            ], capture_output=True, check=True)
        else:
            # MP4（再エンコードで同期を確保）
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '18',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-vsync', 'cfr',
                '-af', 'aresample=async=1',
                output_path
            ], capture_output=True, check=True)

        os.unlink(list_path)

    def create_video_with_audio_segments(
        self,
        display_text: str,
        audio_segments: list,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        transparent: bool = False,
        progress_callback=None
    ) -> tuple:
        """既に生成された音声セグメントを使用して動画を生成

        Args:
            display_text: 表示用テキスト（改行区切り）
            audio_segments: 行ごとの音声データ（bytesのリスト）
            progress_callback: 進捗コールバック関数 (current, total, message) を受け取る

        Returns:
            tuple: (透過動画bytes, プレビュー動画bytes) - 透過モード時
                   (動画bytes, None) - 非透過モード時
        """
        # 表示用テキストを行ごとに分割し、句読点を削除
        display_lines = []
        for line in display_text.strip().split('\n'):
            line = line.strip()
            if line:
                clean_line = line.replace('、', '').replace('。', '').replace('！', '').replace('？', '')
                display_lines.append(clean_line)

        # 行数と音声セグメント数が一致するか確認
        if len(display_lines) != len(audio_segments):
            print(f"警告: 表示用テキスト({len(display_lines)}行)と音声セグメント({len(audio_segments)}個)の数が異なります")
            min_len = min(len(display_lines), len(audio_segments))
            display_lines = display_lines[:min_len]
            audio_segments = audio_segments[:min_len]

        if not display_lines:
            raise ValueError("テキストが空です")

        total_clips = len(display_lines)

        temp_dir = tempfile.mkdtemp()
        temp_files = []
        segment_videos_transparent = []
        segment_videos_preview = []

        try:
            # 各行の動画セグメントを作成
            for i, (display_line, audio_data) in enumerate(zip(display_lines, audio_segments)):
                clip_num = i + 1
                print(f"セグメント {clip_num}/{total_clips} を作成中: {display_line[:20]}...")

                # 進捗コールバック
                if progress_callback:
                    progress_callback(clip_num, total_clips, f"クリップ {clip_num}/{total_clips} を生成中...")

                # 1. 音声を一時ファイルに保存
                audio_path = os.path.join(temp_dir, f"audio_{i}.wav")
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                temp_files.append(audio_path)

                # 2. 音声の長さを取得
                duration = self._get_audio_duration(audio_path)

                if transparent:
                    # 透過モード：透過画像とチェッカー画像の両方を生成
                    # 透過画像
                    img_transparent = self._create_text_image(display_line, width, height, transparent=True)
                    img_transparent_path = os.path.join(temp_dir, f"frame_transparent_{i}.png")
                    img_transparent.save(img_transparent_path)
                    temp_files.append(img_transparent_path)

                    # チェッカー背景画像（プレビュー用）
                    img_preview = self._create_text_image(display_line, width, height, checker=True)
                    img_preview_path = os.path.join(temp_dir, f"frame_preview_{i}.png")
                    img_preview.save(img_preview_path)
                    temp_files.append(img_preview_path)

                    # 透過動画セグメント
                    video_transparent_path = os.path.join(temp_dir, f"segment_transparent_{i}.mov")
                    self._create_video_segment(img_transparent_path, audio_path, video_transparent_path, duration, fps, transparent=True)
                    segment_videos_transparent.append(video_transparent_path)
                    temp_files.append(video_transparent_path)

                    # プレビュー動画セグメント（MP4）
                    video_preview_path = os.path.join(temp_dir, f"segment_preview_{i}.mp4")
                    self._create_video_segment(img_preview_path, audio_path, video_preview_path, duration, fps, transparent=False)
                    segment_videos_preview.append(video_preview_path)
                    temp_files.append(video_preview_path)
                else:
                    # 非透過モード：グリーンバック動画のみ
                    img = self._create_text_image(display_line, width, height, transparent=False)
                    img_path = os.path.join(temp_dir, f"frame_{i}.png")
                    img.save(img_path)
                    temp_files.append(img_path)

                    video_path = os.path.join(temp_dir, f"segment_{i}.mp4")
                    self._create_video_segment(img_path, audio_path, video_path, duration, fps, transparent=False)
                    segment_videos_transparent.append(video_path)
                    temp_files.append(video_path)

            # 全セグメントを連結
            print(f"全 {len(segment_videos_transparent)} セグメントを連結中...")

            if transparent:
                # 透過動画（MOV）
                output_transparent_path = os.path.join(temp_dir, "output_transparent.mov")
                self._concat_videos(segment_videos_transparent, output_transparent_path, transparent=True)
                temp_files.append(output_transparent_path)

                # プレビュー動画（MP4）
                output_preview_path = os.path.join(temp_dir, "output_preview.mp4")
                self._concat_videos(segment_videos_preview, output_preview_path, transparent=False)
                temp_files.append(output_preview_path)

                with open(output_transparent_path, 'rb') as f:
                    video_transparent = f.read()
                with open(output_preview_path, 'rb') as f:
                    video_preview = f.read()

                print("動画生成完了！（透過 + プレビュー）")
                return (video_transparent, video_preview)
            else:
                # 非透過動画（MP4のみ）
                output_path = os.path.join(temp_dir, "output.mp4")
                self._concat_videos(segment_videos_transparent, output_path, transparent=False)
                temp_files.append(output_path)

                with open(output_path, 'rb') as f:
                    video_data = f.read()

                print("動画生成完了！")
                return (video_data, None)

        finally:
            # クリーンアップ
            for f in temp_files:
                if os.path.exists(f):
                    os.unlink(f)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def create_video_from_timestamped_segments(
        self,
        audio_path: str,
        segments: list,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        transparent: bool = True,
        progress_callback=None,
        audio_margin: float = 0.0
    ) -> tuple:
        """タイムスタンプ付きセグメントから動画を生成（音声を切らない方式）

        Args:
            audio_path: 元の音声ファイルパス
            segments: [{"start": 0.0, "end": 1.5, "text": "テキスト"}, ...]
            progress_callback: 進捗コールバック関数
            audio_margin: 未使用（互換性のため残す）

        Returns:
            tuple: (透過動画bytes, プレビュー動画bytes)
        """
        if not segments:
            raise ValueError("セグメントがありません")

        total_clips = len(segments)
        total_audio_duration = self._get_audio_duration(audio_path)

        temp_dir = tempfile.mkdtemp()
        temp_files = []
        segment_videos_transparent = []
        segment_videos_preview = []

        try:
            # 各セグメントの映像のみを作成（音声なし）
            for i, seg in enumerate(segments):
                clip_num = i + 1
                text = seg["text"].strip()
                start_time = seg["start"]

                # 終了時間：次のセグメントの開始時間、または最後なら音声全体の長さ
                if i < total_clips - 1:
                    end_time = segments[i + 1]["start"]
                else:
                    end_time = total_audio_duration

                duration = end_time - start_time
                # 負の値や極端に短い値を防止（最小0.1秒）
                if duration < 0.1:
                    duration = 0.1
                    print(f"警告: セグメント {i} の時間が短すぎます。0.1秒に設定します。")

                display_text = text.replace('、', '').replace('。', '').replace('，', '').replace('．', '')

                print(f"セグメント {clip_num}/{total_clips}: {display_text[:20]}... ({start_time:.2f}s - {end_time:.2f}s, duration={duration:.2f}s)")

                if progress_callback:
                    progress_callback(clip_num, total_clips, f"クリップ {clip_num}/{total_clips} を生成中...")

                if transparent:
                    img_transparent = self._create_text_image(display_text, width, height, transparent=True)
                    img_transparent_path = os.path.join(temp_dir, f"frame_transparent_{i}.png")
                    img_transparent.save(img_transparent_path)
                    temp_files.append(img_transparent_path)

                    img_preview = self._create_text_image(display_text, width, height, checker=True)
                    img_preview_path = os.path.join(temp_dir, f"frame_preview_{i}.png")
                    img_preview.save(img_preview_path)
                    temp_files.append(img_preview_path)

                    # 映像のみのセグメント（音声なし）
                    video_transparent_path = os.path.join(temp_dir, f"segment_transparent_{i}.mov")
                    self._create_video_only_segment(img_transparent_path, video_transparent_path, duration, fps, transparent=True)
                    segment_videos_transparent.append(video_transparent_path)
                    temp_files.append(video_transparent_path)

                    video_preview_path = os.path.join(temp_dir, f"segment_preview_{i}.mp4")
                    self._create_video_only_segment(img_preview_path, video_preview_path, duration, fps, transparent=False)
                    segment_videos_preview.append(video_preview_path)
                    temp_files.append(video_preview_path)
                else:
                    img = self._create_text_image(display_text, width, height, transparent=False)
                    img_path = os.path.join(temp_dir, f"frame_{i}.png")
                    img.save(img_path)
                    temp_files.append(img_path)

                    video_path = os.path.join(temp_dir, f"segment_{i}.mp4")
                    self._create_video_only_segment(img_path, video_path, duration, fps, transparent=False)
                    segment_videos_transparent.append(video_path)
                    temp_files.append(video_path)

            print(f"全 {len(segment_videos_transparent)} セグメントを連結中...")

            if transparent:
                # 映像のみを連結
                video_only_transparent_path = os.path.join(temp_dir, "video_only_transparent.mov")
                self._concat_videos_no_audio(segment_videos_transparent, video_only_transparent_path, transparent=True)
                temp_files.append(video_only_transparent_path)

                video_only_preview_path = os.path.join(temp_dir, "video_only_preview.mp4")
                self._concat_videos_no_audio(segment_videos_preview, video_only_preview_path, transparent=False)
                temp_files.append(video_only_preview_path)

                # 元の音声とマージ
                output_transparent_path = os.path.join(temp_dir, "output_transparent.mov")
                self._mux_video_audio(video_only_transparent_path, audio_path, output_transparent_path, transparent=True)
                temp_files.append(output_transparent_path)

                output_preview_path = os.path.join(temp_dir, "output_preview.mp4")
                self._mux_video_audio(video_only_preview_path, audio_path, output_preview_path, transparent=False)
                temp_files.append(output_preview_path)

                with open(output_transparent_path, 'rb') as f:
                    video_transparent = f.read()
                with open(output_preview_path, 'rb') as f:
                    video_preview = f.read()

                print("動画生成完了！（透過 + プレビュー）")
                return (video_transparent, video_preview)
            else:
                # 映像のみを連結
                video_only_path = os.path.join(temp_dir, "video_only.mp4")
                self._concat_videos_no_audio(segment_videos_transparent, video_only_path, transparent=False)
                temp_files.append(video_only_path)

                # 元の音声とマージ
                output_path = os.path.join(temp_dir, "output.mp4")
                self._mux_video_audio(video_only_path, audio_path, output_path, transparent=False)
                temp_files.append(output_path)

                with open(output_path, 'rb') as f:
                    video_data = f.read()

                print("動画生成完了！")
                return (video_data, None)

        finally:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_audio_segment(self, input_path: str, output_path: str, start_time: float, duration: float):
        """音声ファイルから指定区間を切り出し"""
        subprocess.run([
            'ffmpeg', '-y',
            '-i', input_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:a', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            output_path
        ], capture_output=True, check=True)

    def _create_video_only_segment(self, img_path: str, output_path: str, duration: float, fps: int, transparent: bool = False):
        """音声なしの映像セグメントを作成"""
        if transparent:
            # ProRes 4444（アルファチャンネル対応）
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-framerate', str(fps),
                '-i', img_path,
                '-t', str(duration),
                '-c:v', 'prores_ks',
                '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le',
                '-an',
                output_path
            ], capture_output=True, check=True)
        else:
            # 通常のMP4（音声なし）
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-framerate', str(fps),
                '-i', img_path,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-pix_fmt', 'yuv420p',
                '-an',
                output_path
            ], capture_output=True, check=True)

    def _concat_videos_no_audio(self, video_paths: list, output_path: str, transparent: bool = False):
        """音声なしの動画を連結"""
        list_path = output_path + '.txt'
        with open(list_path, 'w') as f:
            for vp in video_paths:
                f.write(f"file '{vp}'\n")

        if transparent:
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_path,
                '-c:v', 'prores_ks',
                '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le',
                '-an',
                output_path
            ], capture_output=True, check=True)
        else:
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '18',
                '-an',
                output_path
            ], capture_output=True, check=True)

        os.unlink(list_path)

    def _mux_video_audio(self, video_path: str, audio_path: str, output_path: str, transparent: bool = False):
        """映像と音声を結合（元の音声をそのまま使用）"""
        if transparent:
            subprocess.run([
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'pcm_s16le',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ], capture_output=True, check=True)
        else:
            subprocess.run([
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ], capture_output=True, check=True)
