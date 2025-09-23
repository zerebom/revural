# AIエージェント プロフィール案 (9名)

## 命名規則
- 日本人名: 漢字表記 (例: 佐藤 彰)
- 外国人名: カタカナ表記 (例: リアム・オコナー)

---

### 日本人エージェント (4名)

#### 1. エンジニア (Engineer)
- **id**: `engineer`
- **名前**: 佐藤 彰 (Sato Akira)
- **役割ラベル**: エンジニアAI
- **Bio**: 技術的実現性、パフォーマンス、保守性の観点からレビューします。スケーラブルで堅牢なシステムを設計するお手伝いをします。
- **タグ**: `#システム設計`, `#パフォーマンス`, `#保守性`

#### 2. UXデザイナー (UX Designer)
- **id**: `ux_designer`
- **名前**: 鈴木 美緒 (Suzuki Mio)
- **役割ラベル**: UXデザイナーAI
- **Bio**: ユーザー中心設計に基づき、直感的で使いやすい体験を提案します。ユーザビリティとアクセシビリティを最大化することが私の役目です。
- **タグ**: `#ユーザー体験`, `#UIデザイン`, `#アクセシビリティ`

#### 3. データサイエンティスト (Data Scientist)
- **id**: `data_scientist`
- **名前**: 高橋 健太 (Takahashi Kenta)
- **役割ラベル**: データサイエンティストAI
- **Bio**: その仕様で本当に成果を測定できるかを検証します。ログ設計、KPIの計測可能性、A/Bテストの妥当性をレビューします。
- **タグ**: `#データ分析`, `#効果測定`, `#A/Bテスト`

#### 4. UXライター (UX Writer)
- **id**: `ux_writer`
- **名前**: 田中 結衣 (Tanaka Yui)
- **役割ラベル**: UXライターAI
- **Bio**: ブランドボイスを保ちながら、心に響く言葉を提案します。UIコピー、エラーメッセージ、行動を促すフレーズの改善を支援します。
- **タグ**: `#UXライティング`, `#マイクロコピー`, `#ブランドボイス`

---

### 海外エージェント (5名)

#### 5. QAテスター (QA Tester)
- **id**: `qa_tester`
- **名前**: リアム・オコナー
- **役割ラベル**: QAテスターAI
- **Bio**: ユーザーが遭遇しうるあらゆる問題を想定し、仕様の抜け漏れやエッジケースを洗い出します。最高の品質を一緒に目指しましょう。
- **タグ**: `#品質保証`, `#テストケース`, `#エッジケース`

#### 6. プロダクトマネージャー (Product Manager)
- **id**: `pm`
- **名前**: マリア・ガルシア
- **役割ラベル**: プロダクトマネージャーAI
- **Bio**: ビジネス目標とユーザー価値が両立しているかを確認します。仕様の明確性、優先順位、KPIの妥当性をレビューします。
- **タグ**: `#プロダクト戦略`, `#優先順位付け`, `#KPI設計`

#### 7. セキュリティスペシャリスト (Security Specialist)
- **id**: `security_specialist`
- **名前**: イヴァン・ペトロフ
- **役割ラベル**: セキュリティAI
- **Bio**: 想定される脅威からサービスとユーザーデータを守ります。脆弱性、認証認可、個人情報保護の観点からリスクを指摘します。
- **タグ**: `#セキュリティ`, `#脆弱性診断`, `#個人情報保護`

#### 8. マーケティングストラテジスト (Marketing Strategist)
- **id**: `marketing_strategist`
- **名前**: クロエ・デュポン
- **役割ラベル**: マーケティングAI
- **Bio**: プロダクトの価値が市場と顧客に正しく伝わるかを確認します。競合優位性、ターゲット顧客、市場投入戦略をレビューします。
- **タグ**: `#マーケティング戦略`, `#GTM`, `#競合分析`

#### 9. リーガルアドバイザー (Legal Advisor)
- **id**: `legal_advisor`
- **名前**: サミュエル・ジョーンズ
- **役割ラベル**: リーガルAI
- **Bio**: 法務・コンプライアンス上のリスクを特定し、あなたの事業を守ります。利用規約、プライバシーポリシー、関連法規への準拠を確認します。
- **タグ**: `#法務`, `#コンプライアンス`, `#利用規約`

---
---

## 画像生成AI用プロンプト (9名分)

### ベースプロンプト構成
- **静的パート (BASE PROMPT):** 全員共通で、画風・品質・構図・ライティングを定義し、統一感を保証します。
- **動的パート (DYNAMIC PROFILE):** キャラクターごとに変更し、個性（特徴・服装・表情・小物）を表現します。
- **ネガティブプロンプト (NEGATIVE PROMPT):** 望ましくない要素を排除します。

---

### 1. 佐藤 彰 (エンジニア)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a Japanese man in his early 30s, Akira Sato.
He has short, neat black hair and is wearing glasses.
Dressed in a clean, dark grey turtleneck sweater.
He has a confident, focused expression, looking directly at the viewer.
In the background, the soft glow of a computer monitor with code is subtly visible.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 2. 鈴木 美緒 (UXデザイナー)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a Japanese woman in her late 20s, Mio Suzuki.
She has long dark hair tied neatly in a ponytail.
Dressed in a simple yet elegant white blouse.
She has an empathetic and creative expression, looking slightly away as if deep in thought, with a gentle smile.
A digital stylus pen is held lightly in her hand.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 3. 高橋 健太 (データサイエンティスト)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a Japanese man in his 30s, Kenta Takahashi.
He has slightly messy but stylish black hair.
Dressed in a casual but smart plaid button-down shirt.
He has an analytical and curious expression, with a slight smirk as if he has just discovered an insight.
A faint, glowing holographic chart is subtly overlaid in the foreground.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 4. 田中 結衣 (UXライター)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a Japanese woman in her late 20s, Yui Tanaka.
She has shoulder-length brown hair with soft waves.
Dressed in a comfortable, light-beige knit sweater.
She has a warm and thoughtful expression, as if listening intently to someone's story.
She is holding a classic fountain pen and a small notebook.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 5. リアム・オコナー (QAテスター)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of an Irish man in his early 30s, Liam O'Connor.
He has short, reddish-brown hair.
Dressed in a practical, dark green polo shirt.
He has a meticulous and sharp-eyed expression, looking very closely as if inspecting for details.
A subtle magnifying glass icon is integrated into the background's geometric shape.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 6. マリア・ガルシア (プロダクトマネージャー)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a Spanish woman in her late 30s, Maria Garcia.
Her dark hair is tied back in a professional bun.
Dressed in a crisp, light blue business blouse.
She has a determined and strategic expression, looking forward with clear vision.
A faint roadmap or timeline graphic is visible in the background.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 7. イヴァン・ペトロフ (セキュリティスペシャリスト)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of an Eastern European man in his 40s, Ivan Petrov.
He has a shaved head and a well-defined jawline.
Dressed in a modern, black collared shirt.
He has a serious, vigilant, and protective expression. His gaze is steady and unwavering.
A subtle, stylized shield icon is integrated into the background.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 8. クロエ・デュポン (マーケティングストラテジスト)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a French woman in her mid-30s, Chloé Dupont.
She has a stylish, chin-length blonde bob hairstyle.
Dressed in a smart, navy blue blazer.
She has a friendly and engaging smile, with a sharp, intelligent gaze that shows confidence.
A tablet device displaying a simple upward-trending growth chart is held lightly in one hand.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```

### 9. サミュエル・ジョーンズ (リーガルアドバイザー)
```text
## BASE PROMPT -- DO NOT CHANGE --
professional UI avatar illustration, bust-shot portrait, character facing slightly towards the camera, face is the main focus.
minimalist style, clean vector art with subtle gradients, soft shadows.
simple abstract background with a single brand color geometric shape.
extremely high detail, 8k, sharp focus.

## DYNAMIC PROFILE -- REPLACE PER CHARACTER --
A professional portrait of a British man in his 50s, Samuel Jones.
He has neatly combed, graying hair at the temples and a well-groomed beard.
Dressed in a classic, dark brown tweed jacket over a collared shirt.
He has a calm, wise, and authoritative expression.
A subtle scales of justice icon is integrated into the background's geometric shape.

## NEGATIVE PROMPT -- DO NOT CHANGE --
- photorealistic, photography, 3D render
- blurry, noisy, deformed, disfigured, ugly
- extra limbs, bad hands
- text, signature, watermark
- childish, cartoonish
- full body shot
```
