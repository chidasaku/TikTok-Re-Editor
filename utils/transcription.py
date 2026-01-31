import requests
import time
from typing import Optional


class GladiaAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.gladia.io/v2"
        self.headers = {
            "x-gladia-key": api_key,
            "Content-Type": "application/json"
        }

    def upload_file(self, file_path: str) -> Optional[str]:
        """動画ファイルをアップロードしてURLを取得"""
        try:
            import os
            import mimetypes

            filename = os.path.basename(file_path)
            # ファイルタイプを自動判定
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            print(f"ファイルアップロード中: {filename} ({mime_type})")

            with open(file_path, "rb") as f:
                # ファイル名とMIMEタイプを明示的に指定
                files = {"audio": (filename, f, mime_type)}
                response = requests.post(
                    f"{self.base_url}/upload",
                    headers={"x-gladia-key": self.api_key},
                    files=files
                )

                print(f"アップロードレスポンス: {response.status_code}")
                response.raise_for_status()

                result = response.json()
                audio_url = result.get("audio_url")
                print(f"アップロード成功: {audio_url}")
                return audio_url

        except Exception as e:
            print(f"ファイルアップロードエラー: {e}")
            if 'response' in locals():
                print(f"ステータスコード: {response.status_code}")
                print(f"詳細: {response.text}")
            return None

    def transcribe(self, audio_url: str, language: str = "ja") -> Optional[str]:
        """音声ファイルを文字起こし"""
        try:
            # 文字起こしリクエストを送信
            payload = {
                "audio_url": audio_url,
                "language_config": {
                    "languages": [language]
                }
            }

            response = requests.post(
                f"{self.base_url}/pre-recorded",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # 結果IDを取得
            result_id = result.get("id")
            if not result_id:
                print(f"結果IDが取得できませんでした: {result}")
                return None

            # 結果を取得（ポーリング）
            return self._poll_result(result_id)

        except Exception as e:
            print(f"文字起こしエラー: {e}")
            print(f"詳細: {response.text if 'response' in locals() else '不明'}")
            return None

    def _poll_result(self, result_id: str, max_attempts: int = 60) -> Optional[str]:
        """文字起こし結果をポーリングして取得"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.base_url}/pre-recorded/{result_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                status = result.get("status")
                print(f"ポーリング {attempt + 1}/{max_attempts}: ステータス = {status}")

                if status == "done":
                    # テキストを抽出
                    transcription = result.get("result", {}).get("transcription", {})
                    full_transcript = transcription.get("full_transcript", "")
                    return full_transcript
                elif status == "error":
                    error_msg = result.get("error", "不明なエラー")
                    print(f"文字起こしエラー: {error_msg}")
                    return None

                # 処理中の場合は待機
                time.sleep(3)

            except Exception as e:
                print(f"結果取得エラー (リトライ {attempt + 1}/{max_attempts}): {e}")
                if 'response' in locals():
                    print(f"詳細: {response.text}")
                time.sleep(3)
                continue

        print("タイムアウト: 文字起こしが完了しませんでした")
        return None

    def transcribe_from_file(self, file_path: str, language: str = "ja") -> Optional[str]:
        """ファイルから直接文字起こし（便利メソッド）"""
        audio_url = self.upload_file(file_path)
        if audio_url:
            return self.transcribe(audio_url, language)
        return None

    def transcribe_with_timestamps(self, audio_url: str, language: str = "ja") -> Optional[dict]:
        """音声ファイルを文字起こしし、タイムスタンプ付きセグメントと単語を返す

        Returns:
            dict: {
                "segments": [{"start": 0.0, "end": 1.5, "text": "...", "words": [...]}],
                "words": [{"word": "...", "start": 0.0, "end": 0.3}, ...]
            }
        """
        try:
            payload = {
                "audio_url": audio_url,
                "language_config": {
                    "languages": [language]
                }
            }

            response = requests.post(
                f"{self.base_url}/pre-recorded",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            result_id = result.get("id")
            if not result_id:
                print(f"結果IDが取得できませんでした: {result}")
                return None

            return self._poll_result_with_timestamps(result_id)

        except Exception as e:
            print(f"文字起こしエラー: {e}")
            return None

    def _poll_result_with_timestamps(self, result_id: str, max_attempts: int = 60) -> Optional[dict]:
        """タイムスタンプ付き文字起こし結果をポーリングして取得

        Returns:
            dict: {
                "segments": [{"start": 0.0, "end": 1.5, "text": "...", "words": [...]}],
                "words": [{"word": "...", "start": 0.0, "end": 0.3}, ...]
            }
        """
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"{self.base_url}/pre-recorded/{result_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                status = result.get("status")
                print(f"ポーリング {attempt + 1}/{max_attempts}: ステータス = {status}")

                if status == "done":
                    transcription = result.get("result", {}).get("transcription", {})
                    utterances = transcription.get("utterances", [])

                    # セグメントリストを作成（各セグメント内のwordsも含む）
                    segments = []
                    all_words = []

                    for utt in utterances:
                        # utterance内のwordsを取得
                        utt_words = utt.get("words", [])
                        words_list = []
                        for w in utt_words:
                            word_data = {
                                "word": w.get("word", ""),
                                "start": w.get("start", 0),
                                "end": w.get("end", 0)
                            }
                            words_list.append(word_data)
                            all_words.append(word_data)

                        segments.append({
                            "start": utt.get("start", 0),
                            "end": utt.get("end", 0),
                            "text": utt.get("text", "").strip(),
                            "words": words_list
                        })

                    print(f"文字起こし完了: {len(segments)} セグメント, {len(all_words)} 単語")
                    return {
                        "segments": segments,
                        "words": all_words
                    }

                elif status == "error":
                    error_msg = result.get("error", "不明なエラー")
                    print(f"文字起こしエラー: {error_msg}")
                    return None

                time.sleep(3)

            except Exception as e:
                print(f"結果取得エラー (リトライ {attempt + 1}/{max_attempts}): {e}")
                time.sleep(3)
                continue

        print("タイムアウト: 文字起こしが完了しませんでした")
        return None

    def transcribe_from_file_with_timestamps(self, file_path: str, language: str = "ja") -> Optional[dict]:
        """ファイルから直接タイムスタンプ付き文字起こし

        Returns:
            dict: {
                "segments": [{"start": 0.0, "end": 1.5, "text": "...", "words": [...]}],
                "words": [{"word": "...", "start": 0.0, "end": 0.3}, ...]
            }
        """
        audio_url = self.upload_file(file_path)
        if audio_url:
            return self.transcribe_with_timestamps(audio_url, language)
        return None
