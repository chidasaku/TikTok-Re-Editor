import requests
import json
import io
import wave
from typing import List, Dict, Optional, Callable


class VoiceVoxAPI:
    def __init__(self, base_url: str = "http://localhost:50021"):
        self.base_url = base_url

    def get_speakers(self) -> List[Dict]:
        """VOICEVOXのスピーカー一覧を取得"""
        try:
            response = requests.get(f"{self.base_url}/speakers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"スピーカー取得エラー: {e}")
            return []

    def get_speaker_styles(self, speakers: List[Dict]) -> Dict[str, List[Dict]]:
        """スピーカーとスタイルの辞書を作成"""
        speaker_styles = {}
        for speaker in speakers:
            speaker_name = speaker.get("name", "")
            styles = speaker.get("styles", [])
            speaker_styles[speaker_name] = styles
        return speaker_styles

    def find_speaker_id(self, speakers: List[Dict], speaker_name: str, style_name: str = "ノーマル") -> Optional[int]:
        """指定されたスピーカー名とスタイル名からスピーカーIDを取得"""
        for speaker in speakers:
            if speaker.get("name") == speaker_name:
                for style in speaker.get("styles", []):
                    if style.get("name") == style_name:
                        return style.get("id")
        return None

    def generate_audio_query(self, text: str, speaker_id: int) -> Optional[Dict]:
        """テキストから音声クエリを生成"""
        try:
            response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"音声クエリ生成エラー: {e}")
            return None

    def synthesize_voice(self, audio_query: Dict, speaker_id: int, speed: float = 1.2, pause_length: float = 1.0) -> Optional[bytes]:
        """音声クエリから音声を合成"""
        try:
            # 話速を設定
            audio_query["speedScale"] = speed
            # 間の長さを設定（0.0〜2.0、デフォルト1.0）
            audio_query["pauseLengthScale"] = pause_length
            # ステレオ出力を有効化
            audio_query["outputStereo"] = True

            response = requests.post(
                f"{self.base_url}/synthesis",
                params={"speaker": speaker_id},
                headers={"Content-Type": "application/json"},
                data=json.dumps(audio_query)
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"音声合成エラー: {e}")
            return None

    def generate_voice(self, text: str, speaker_id: int, speed: float = 1.2, pause_length: float = 1.0) -> Optional[bytes]:
        """テキストから直接音声を生成（便利メソッド）"""
        audio_query = self.generate_audio_query(text, speaker_id)
        if audio_query:
            return self.synthesize_voice(audio_query, speaker_id, speed, pause_length)
        return None

    def generate_voice_with_progress(
        self,
        text: str,
        speaker_id: int,
        speed: float = 1.2,
        pause_length: float = 1.0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        return_segments: bool = False
    ) -> Optional[bytes]:
        """テキストを行ごとに生成し、進捗を報告しながら音声を合成

        Args:
            return_segments: Trueの場合、(結合音声, 個別音声リスト)のタプルを返す
        """
        # テキストを行に分割
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

        if not lines:
            return None

        total_lines = len(lines)
        audio_segments = []

        for i, line in enumerate(lines):
            # 進捗コールバック
            if progress_callback:
                progress_callback(i + 1, total_lines, f"行 {i + 1}/{total_lines} を生成中...")

            # 音声生成
            audio_data = self.generate_voice(line, speaker_id, speed, pause_length)
            if audio_data:
                audio_segments.append(audio_data)
            else:
                print(f"行 {i + 1} の音声生成に失敗しました: {line[:20]}...")

        if not audio_segments:
            return None

        # WAVファイルを結合
        combined = self._concat_wav_files(audio_segments)

        if return_segments:
            return (combined, audio_segments)
        return combined

    def _concat_wav_files(self, wav_data_list: List[bytes]) -> Optional[bytes]:
        """複数のWAVデータを結合"""
        if not wav_data_list:
            return None

        if len(wav_data_list) == 1:
            return wav_data_list[0]

        try:
            # 最初のファイルからパラメータを取得
            with wave.open(io.BytesIO(wav_data_list[0]), 'rb') as first_wav:
                params = first_wav.getparams()
                frames = [first_wav.readframes(first_wav.getnframes())]

            # 残りのファイルのフレームを追加
            for wav_data in wav_data_list[1:]:
                with wave.open(io.BytesIO(wav_data), 'rb') as wav_file:
                    frames.append(wav_file.readframes(wav_file.getnframes()))

            # 結合したWAVを作成
            output = io.BytesIO()
            with wave.open(output, 'wb') as out_wav:
                out_wav.setparams(params)
                for frame in frames:
                    out_wav.writeframes(frame)

            return output.getvalue()
        except Exception as e:
            print(f"WAV結合エラー: {e}")
            return None

    def generate_sample_voice(self, speaker_id: int) -> Optional[bytes]:
        """キャラクター試聴用のサンプル音声を生成"""
        sample_text = "こんにちは、VOICEVOXです。よろしくお願いします。"
        return self.generate_voice(sample_text, speaker_id, speed=1.0)
