import google.generativeai as genai
from typing import Optional


class GeminiFormatter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # 2026年1月時点の無料モデル
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')

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

    def rephrase_text(self, text: str, politeness: str = None, emotion: str = None, style: str = None) -> Optional[str]:
        """
        テキストのニュアンスを変更

        Args:
            text: 整形済みテキスト
            politeness: 丁寧度（casual/polite/formal）
            emotion: 感情（gentle/strong/cool）
            style: 話し方（explanatory/conversational/narrative）

        Returns:
            ニュアンス変更後のテキスト
        """
        # ニュアンス指示を構築
        nuance_instructions = []

        if politeness:
            politeness_map = {
                "casual": "カジュアルで親しみやすい口調（タメ口、くだけた表現）",
                "polite": "丁寧で礼儀正しい口調（です・ます調）",
                "formal": "フォーマルで格式高い口調（敬語、ビジネス調）"
            }
            nuance_instructions.append(f"【丁寧度】{politeness_map.get(politeness, '')}")

        if emotion:
            emotion_map = {
                "gentle": "優しく穏やかな雰囲気（柔らかい表現、共感的）",
                "strong": "力強く情熱的な雰囲気（断定的、エネルギッシュ）",
                "cool": "クールで落ち着いた雰囲気（淡々と、客観的）"
            }
            nuance_instructions.append(f"【感情】{emotion_map.get(emotion, '')}")

        if style:
            style_map = {
                "explanatory": "説明的な話し方（論理的、順序立てて）",
                "conversational": "会話的な話し方（語りかける、問いかける）",
                "narrative": "物語的な話し方（ストーリー調、引き込む）"
            }
            nuance_instructions.append(f"【話し方】{style_map.get(style, '')}")

        nuance_text = "\n".join(nuance_instructions)

        prompt = f"""あなたは文章のニュアンス調整の専門家です。以下のテキストを指定されたニュアンスに変更してください。

{nuance_text}

【絶対厳守のルール】
1. 内容・意味は変えずに、ニュアンス（トーン・雰囲気）だけを変更してください
2. 1行は最大14文字、できるだけ14文字に近づけてください
3. 各行は必ず句点（。）または読点（、）で終わらせてください
4. **重要**: 読点（、）は最低限にしてください。不要な読点は入れないでください
5. 文の途中で改行する場合のみ読点（、）を追加してください
6. 文の終わりは句点（。）で終わらせてください
7. 読み方がおかしくならない自然な位置で改行してください
8. 行数は元のテキストと同じか近い数を維持してください

【良い例】
職場の嫌な奴は、← 14文字に近い、文の途中なので読点
こう扱えば大丈夫。← 文の終わりなので句点
そんな人の対処法を、← 14文字に近い
5つ紹介します。← 句点で終わる

【悪い例】
職場の、← 短すぎる、不要な読点
嫌な奴は、← 短すぎる
こう、← 不要な読点が多い

【入力テキスト】
{text}

【出力】
ニュアンス変更後のテキストのみを出力してください。説明や追加コメントは不要です。
"""

        try:
            nuance_desc = f"丁寧度={politeness}, 感情={emotion}, 話し方={style}"
            print(f"Gemini APIでニュアンス変更中... ({nuance_desc})")
            response = self.model.generate_content(prompt)
            print(f"ニュアンス変更レスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"ニュアンス変更結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"ニュアンス変更エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def convert_to_hiragana(self, text: str) -> Optional[str]:
        """
        テキストをひらがなに変換（音声生成用）
        漢字、カタカナ、数字を全てひらがなの読みに変換

        Args:
            text: 整形済みテキスト

        Returns:
            ひらがな変換後のテキスト
        """
        prompt = f"""あなたは日本語の読み方の専門家です。以下のテキストを音声合成（TTS）用にひらがなに変換してください。

【絶対厳守のルール】
1. 漢字 → ひらがなの読みに変換
2. カタカナ → ひらがなに変換
3. 数字 → 日本語の読み（ひらがな）に変換
   例: 1 → いち、10 → じゅう、100 → ひゃく、2026 → にせんにじゅうろく
4. 年号の読み方:
   例: 2026年 → にせんにじゅうろくねん
5. アルファベット → カタカナ読みをひらがなに
   例: TikTok → てぃっくとっく、AI → えーあい
6. 改行はそのまま維持（行数を変えない）

【句読点のルール - 重要】
音声合成で自然なイントネーションを得るため、1行に1つだけ読点（、）を追加してください。
- 元の句読点（。、）は維持
- 追加する読点は1行につき最大1つ
- 行の前半（最初の意味のまとまりの後）に入れる
- 短い行（8文字以下）には追加不要

【良い例】
入力: 今回は2026年に、
出力: こんかいは、にせんにじゅうろくねんに、

入力: 給料が上がらない職種を、
出力: きゅうりょうが、あがらないしょくしゅを、

入力: ランキング形式で紹介します。
出力: らんきんぐけいしきで、しょうかいします。

入力: 早めの行動が必要です。
出力: はやめのこうどうが、ひつようです。

入力: こう扱えば大丈夫。
出力: こうあつかえば、だいじょうぶ。

【悪い例】
× こんかいはにせんにじゅうろくねんに（読点なし）
× こんかいは、にせん、にじゅうろくねんに、（読点多すぎ）
× きゅうりょうが、あがらない、しょくしゅを、（読点多すぎ）

【注意】
- 文脈に応じて正しい読み方を選んでください
- 例: 「今日」→「きょう」、「1日」→「いちにち」または「ついたち」（文脈による）
- 例: 「5つ」→「いつつ」、「5人」→「ごにん」

【入力テキスト】
{text}

【出力】
ひらがな変換後のテキストのみを出力してください。
行数と改行位置は入力テキストと完全に同じにしてください。
説明や追加コメントは不要です。
"""

        try:
            print(f"Gemini APIでひらがな変換中... (テキスト長: {len(text)}文字)")
            response = self.model.generate_content(prompt)
            print(f"ひらがな変換レスポンス受信完了")

            if hasattr(response, 'text'):
                result = response.text.strip()
                print(f"ひらがな変換結果: {len(result)}文字")
                return result
            else:
                print(f"レスポンスにtextが含まれていません: {response}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"Prompt feedback: {response.prompt_feedback}")
                return None

        except Exception as e:
            print(f"ひらがな変換エラー: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
