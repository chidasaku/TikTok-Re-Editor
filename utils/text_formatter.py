import google.generativeai as genai
from typing import Optional


class GeminiFormatter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def format_text(self, text: str) -> Optional[str]:
        """
        テキストを14文字/行に整形
        重要: 元の発言内容は1文字も変えず、句読点と改行のみを調整
        """
        prompt = f"""あなたは厳格な校正者です。以下のテキストを整形してください。

【絶対厳守のルール】
1. 元のテキストの内容（単語、表現）を1文字も変更してはいけません
2. 1行は14文字以内にしてください
3. **重要**: 各行は必ず句点（。）または読点（、）で終わらせてください。句読点がない行は絶対に作らないでください
4. 文の途中で改行する場合は、必ず読点（、）を追加してください
5. 文の終わりで改行する場合は、必ず句点（。）を追加してください
6. 意味のまとまりや自然な区切りで改行してください
7. 読みやすい位置で改行してください（途中で単語が切れないように）
8. 要約や言い換えは絶対に禁止です

【良い例】
職場の嫌な奴は、← 読点で終わる
こう扱えば大丈夫。← 句点で終わる
職場に嫌いな人は、← 読点で終わる
一人はいますよね。← 句点で終わる
そんな人の対処法を、← 読点を追加
5つ紹介します。← 句点で終わる
この動画はもう二度と、← 読点を追加
おすすめに表示されませんので、← 読点で終わる
忘れないよう、← 読点で終わる
いいねと保存を、← 読点を追加
お願いします。← 句点で終わる

【悪い例（絶対NG）】
そんな人の対処法を ← ×句読点がない
この動画はもう ← ×句読点がない

【入力テキスト】
{text}

【出力】
整形後のテキストのみを出力してください。説明や追加コメントは不要です。
全ての行が句点（。）または読点（、）で終わることを確認してください。
"""

        try:
            print(f"Gemini APIリクエスト中... (テキスト長: {len(text)}文字)")
            response = self.model.generate_content(prompt)
            print(f"Gemini APIレスポンス受信完了")

            # レスポンスの内容を確認
            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"整形結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                # prompt_feedbackを確認
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"テキスト整形エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_filename(self, formatted_text: str) -> Optional[str]:
        """
        整形済みテキストの1〜3行目から、20文字以内の適切なファイル名を生成
        """
        lines = formatted_text.split('\n')
        first_lines = '\n'.join(lines[:3])

        prompt = f"""以下のテキストから、適切なファイル名を生成してください。

【ルール】
1. 20文字以内
2. 内容を端的に表すタイトル
3. ファイル名として使える文字のみ（記号は使用しない）
4. 日本語でOK

【テキスト】
{first_lines}

【出力】
ファイル名のみを出力してください。説明や追加コメントは不要です。
拡張子（.txtや.wav）は付けないでください。
"""

        try:
            print(f"Gemini APIでファイル名生成中...")
            response = self.model.generate_content(prompt)
            print(f"ファイル名生成レスポンス受信完了")

            if hasattr(response, 'text'):
                filename = response.text.strip()
                # 不適切な文字を削除
                filename = filename.replace('/', '').replace('\\', '').replace(':', '').replace('*', '')
                filename = filename.replace('?', '').replace('"', '').replace('<', '').replace('>', '')
                filename = filename.replace('|', '').replace('\n', '').replace('\r', '')
                result = filename[:20]  # 20文字制限
                print(f"生成されたファイル名: {result}")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"ファイル名生成エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_metadata(self, text: str) -> Optional[str]:
        """
        テキストからタイトル案、紹介文案、ハッシュタグを生成

        Returns:
            フォーマット済みのメタデータ文字列
        """
        prompt = f"""以下のテキストから、TikTok/SNS投稿用のタイトル、紹介文、ハッシュタグを生成してください。

【ルール】
1. タイトル案：3つ提案（各30字以内、【見出し】本文 の形式）
2. 紹介文案：3つ提案（各100字前後）
3. ハッシュタグ：5つ提案

【入力テキスト】
{text}

【出力フォーマット（このフォーマット厳守）】
【タイトル案（『【見出し】本文』／各30字以内）】

1）……

2）……

3）……

【紹介文案（各100字前後）】

1）……

2）……

3）……

【ハッシュタグ（5つ）】

#〇〇 #〇〇 #〇〇 #〇〇 #〇〇

上記のフォーマットに従って、テキストの内容に基づいた魅力的なメタデータを生成してください。
説明や追加コメントは不要です。フォーマット通りに出力してください。
"""

        try:
            print(f"Gemini APIでメタデータ生成中... (テキスト長: {len(text)}文字)")
            response = self.model.generate_content(prompt)
            print(f"メタデータ生成レスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"生成されたメタデータ: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"メタデータ生成エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
