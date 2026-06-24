# AIスロップ回避チェックリスト（Webデザイン／AI生成の品質リファレンス）

> 立場: AI（Claude Design / v0 / Lovable / Bolt / Figma AI / ChatGPT 等）で自分が作る側
> 対象: ①ビジュアル ②コピー・文章 ③UX・構成
> 調査日: 2026-06-24（出典付き）／ deep-research による調査結果を統合
> 用途: Web/資料を AI で作るときの「いかにもAI」回避。doc-prompt-builder（Claude Design 用プロンプト生成）の素材としても流用可

---

## 結論

**AIスロップ＝「指示の不足」が生む統計的な平均値。** モデルは放っておくと学習データの中央値（みんなが使う無難な型）に収束する。対策は一つ ―「**作る順番を逆にする**」。いきなり生成させず、**先にブランド（色・書体・声・トークン）を定義して食わせ、避けたい定番を名指しで禁止する。** 全ツール共通の王道で、Anthropic・Vercel が自社ドキュメントで認めている。

---

## 1. なぜAIは「同じ顔」を作るのか（原因）

| 原因 | 中身 | 出典 |
|---|---|---|
| 統計的平均への回帰 | LLMはデザイナーではなく統計的パターンマッチャー。無指定だと学習データ（英語・西欧中心のチュートリアル）の中央値を出す | Anthropic cookbook／arXiv 2603.13036 |
| RLHFによるmode collapse | 事後学習で「典型性バイアス（流暢で馴染みあるものを高評価）」が働き出力の多様性が崩壊。入力が違っても似た出力 | Kirk et al., ICLR 2024 (arXiv 2310.06452) |
| ベンダー自身の証言 | Claudeは「明示しないと generic・conservative に寄る」。v0は「default shadcn/ui で訓練されカスタマイズに苦労しうる」 | claude-cookbooks／v0 docs |
| 紫グラデの正体 | Tailwind作者が約5年前に `bg-indigo-500` を既定化→テンプレ経由で学習データを支配。本人が2025-08にX公式謝罪 | Adam Wathan (X) |
| フィードバックループ | AI製の紫サイトが公開→再スクレイプ→次の学習へ、で偏りが増幅 | prg.sh |

→ **「いい感じにして」と頼むほど中央値が返る。**

---

## 2. 「AIっぽさ」シグナル一覧（検出チェックリスト）

### ① ビジュアル（最も確度が高い）
- [ ] 紫／インディゴ、青→紫グラデ（白・薄グレー背景に）― 最強のtell。Reddit 320万投稿の検証でも色tell第1位
- [ ] 多用フォント: Inter / Roboto / Arial / system-ui
- [ ] 3カラムのアイコン特徴カード（アイコン＋見出し＋短文）
- [ ] すべて角丸（一律16px前後）、淡い影（opacity 0.1前後）
- [ ] 大きな中央寄せsans-serif見出し、グラデ見出し
- [ ] 定型のセクション順: Hero → 特徴3点 → 証言 → 料金 → FAQ → footer
- [ ] padding・カード高が一律で階層感がない／プラスチック的なストック画像

### ② コピー・文章
**定型の枕詞・前置き**
- [ ] "In today's fast-paced/digital world", "In the ever-evolving landscape of..."（"In the ever-evolving" は人間比 11,000倍）
- [ ] "It's important to note", "Let's dive in / unpack", "Here's why"（中身のない助走）
- [ ] "In conclusion" / "Overall," / "In summary"（結論の出だし＋本文繰り返し）

**煽り・空疎な決まり文句**
- [ ] "Elevate your X", "Unlock the power of", "Take your X to the next level", "Look no further", "game-changer", "stay ahead of the curve"

**過剰バズワード（平易語に置換 or 削除）**
- [ ] seamless / robust / leverage / elevate / unlock / transformative / innovative / comprehensive / delve / tapestry（"vibrant tapestry" 17,000倍）/ testament（"a testament to" 4,000倍）/ utilize

**構文・記号・リズム**
- [ ] "It's not just X, it's Y" / "not X but Y"（左右対称構文）― 指摘が最多
- [ ] em-dash（—）の多用（※単独では誤判定リスク大。後述）
- [ ] 太字・箇条書き・絵文字（特に 🚀）の乱発
- [ ] 全段落・全見出しが同じ長さ／同じリズム（burstinessが低くなめらかで単調）
- [ ] 縮約・断片文・砕けた表現がゼロ＝完璧すぎる
- [ ] 弱いCTA: "Get Started" / "Learn More" / "Call us to learn more"

### ③ UX・構成
- [ ] 上記の定型セクション順をそのまま踏襲
- [ ] 見出しが空疎（"Build the future of work" 系で具体性ゼロ）
- [ ] コンポーネント配置が均一でメリハリ・導線設計がない

> ⚠ これらは**組み合わせで初めてAI臭**になる相関シグナル。決定的証拠ではない（人間がInter＋紫を使うこともある）。単一シグナルで断定しない。

---

## 3. 脱却の実践手法

### 原則：作る順番を逆転する
最初の仕事は**ビジュアル生成ではなくブランドキャプチャ**。既存ソース（ロゴ・配色・書体・既存サイト・資料）から、色・タイポ・モチーフ・見出しパターン・声を1枚の「ブランドシート」に抽出してから生成に入る。学術側も "productive friction（生産的な摩擦）" をあえて挟むことを推奨（cookbook／arXiv 2603.13036）。

### A. プロンプト術（Anthropic検証済みの3本柱）
1. **デザイン次元を個別に指定** ―「いい感じに」でなく、タイポ／色／モーション／背景を別々に指示
2. **参照で錨を打つ（過剰指定はしない）** ―「Linearの視覚スタイルで」「IDEテーマの〇〇風」など固有名で方向づけ
3. **定番を名指しで禁止** ―「Inter/Roboto/Arial を使うな」「紫グラデ禁止」「型通りにするな（think outside the box）」

補足の効く指示:
- hex＋意味的名称で色を渡す（色名だけだと既定で埋められる）
- 書体は重み＋取得元まで（例: "Syne 600/700 from Google Fonts"、`@import`で重み込みロード）
- spacingの基準単位とborder-radiusを明示（AIが最も既定に戻しやすい2つ。pill/16px角丸を殺す）
- 曖昧な形容詞を避ける（「モダンで洗練された」はモデルが既定で穴埋めする隙になる）

### B. コピーを人間に戻す
- 禁止語リスト（anti-vocabulary）を明示：「'innovative','comprehensive','transformative','tapestry' は使うな。コーヒー片手に賢い友人が話すような平易な英語で」
- 立場（POV）を先に与える：「一般論の〇〇は実は間違いで、なぜなら…。その視点で書け」
- 自分の文章サンプルを食わせてスタイルガイド化させ以後それを適用
- 文長をばらつかせろと指示（短い断定文＋長い説明文を混ぜる＝burstinessを上げる）
- 編集側：一般論を具体（数字・固有名詞・一次情報）に置換（「saves time」→「two hours every day」）、前置きを削る、声に出して読む

### C. デザインシステム/トークンを注入する
個別コンポーネントを手で書き換えるより、トークン層（CSS変数）を一度直す方が全体に伝播し構造的にブランドに合う。各ツールの「ネイティブに読む経路」で渡す（→次節）。

### D. 反復と人間のキュレーション
生成後の調整機能（v0 Design mode／ChatGPT Canvas／Lovable edit-mode）で初稿のgenericさを削る。複数案を出させて選ぶ。最後は独自フォント・spacing・自社アセットで人間が仕上げる。

---

## 4. ツール別の癖と対処

| ツール | デフォルトの寄り方 | 上書きする「ネイティブ経路」 |
|---|---|---|
| Claude（Design/Code） | 公式に「generic・conservative」。Inter/Roboto/Arial・紫グラデを回避対象に | cookbookの4軸指定＋デフォルト禁止／DESIGN.md をプロンプト先頭に貼る（毎セッション。保持しない）／Claude Designの Design System 機能でコード・スクショ・資料から抽出 |
| v0（Vercel） | default shadcn/ui で訓練→slate/zinc等の標準に回帰（公式明記） | Themes（自然言語でテーマ生成・トークン編集・生成ごと切替）／Registry でデザインシステムを渡す／`tokens.css`で色・`layout.tsx`でフォント／Figmaは1フレーム=1コンポ。※コンポ内部の手書き換えは品質低下。トークン経由が正解 |
| Lovable | React+Vite+Tailwind+shadcn/ui+Supabaseで雛形化→shadcnルック | Knowledge（Workspace=全PJ共通、Project=PJ単位、各1万字、競合はProject優先）／`index.css`＋`tailwind.config.ts`のトークン編集／`AGENTS.md`/`CLAUDE.md`自動読込／Figmaインポート（Builder.io経由、※インタラクション非保持） |
| Bolt（bolt.new） | エンジンはClaude Sonnet。Vite+React+Tailwind+shadcn。動くコード優先で見た目後回し→Inter/青グレー/定型グリッド | `.bolt/prompt`ファイルに全体規約（全ページ＋チャットに注入）／UIの Project/Global System Prompt／Enhance prompt／Figmaは"Screenshot"インポート推奨／Lock fileで手調整を保護 |
| Figma AI（Make/First Draft） | ライブラリ未接続だとgeneric（2024年に天気アプリがApple酷似で一時停止） | Team library接続が必須／コンポを正確な名前で指定（`Button/Primary`）＋変数（トークン）参照／Code Connect＋Figma MCP で実装の実体を渡す |
| ChatGPT/GPT | 自社ブランド非内蔵。Tailwind名前付き色（slate/indigo/emerald）＋全面Inter＋定型構成に平均化。"purple problem" | Custom Instructions で役割・必須パターン固定／デザイントークンを構造化して貼る／Canvas で局所反復編集 |

**横断の鉄則**: ①やめさせたい定番を名指し禁止 → ②トークンを「ツールがネイティブに読む層」で注入 → ③hex・書体取得元・spacing・radiusを明示 → ④参照で錨打ち → ⑤Figma連携はフレーム粒度・スクショ重視 → ⑥生成後に反復で削る。

---

## 5. すぐ使える「貼り付け用」テンプレ

**ネガティブ指定ブロック（プロンプト末尾に固定）**
```
避けること（重要・型通りにするな）:
- フォント: Inter / Roboto / Arial / system-ui は使わない
- 色: 紫・インディゴ、青→紫グラデを背景/CTA/見出しに使わない
- レイアウト: Hero→特徴3カード→証言→料金→footer の定型に逃げない
- 装飾: 一律16pxの角丸、opacity0.1の淡い影を全要素に付けない
- コピー: "Elevate/Unlock/seamless/robust", "In today's...", "not just X but Y",
  em-dash多用、空疎な美辞麗句、"Get Started/Learn More" の定型CTAを禁止
指定すること:
- 色は hex＋意味的名称で / 書体は重み＋取得元まで / spacing基準単位とborder-radiusを明示
- タイポ・色・モーション・背景を個別に設計せよ / 参照: 〇〇（固有名）の視覚スタイル
```

**コピー提出前チェック**: 禁止フレーズを検索して潰す → 一般論を数字・固有名詞に置換 → 文長をばらつかせる → 結論が繰り返しでないか → CTAが商品固有か → 声に出して読む。

---

## 6. 注意点（確度と限界）

- 証拠が強い: ビジュアルのシグナルとモデル機構（Anthropic公式＋査読論文）、v0/shadcnのツール挙動（公式docs）
- 証拠が中程度: コピーのtellはブログ＋検出ツール中心（Pangram の倍率データ・Tailwind作者の一次証言で補強）。`Elevate your`等の一部は定量裏取りが弱い
- 誤判定リスク: em-dash単独や「Inter使用」だけでAI判定するのは危険（Washington Post も論争として報道）。検出ツール（GPTZero等）はスクリーニングであって最終根拠にしない
- 鮮度: v0 Themes/registry、Claude Design、Figma AI は変化が速い。重要機能は使う直前に公式docsで再確認
- 要確認: LovableのGUIテーマ機能の有無、Boltの`.bolt/prompt`とUI Promptの関係、ChatGPTのスクショ→UI複製手順は一次裏付けが未取得

---

## 主な出典
- Anthropic claude-cookbooks「prompting_for_frontend_aesthetics」（一次）
- Kirk et al., ICLR 2024「RLHF と mode collapse」arXiv 2310.06452（査読）
- arXiv 2603.13036「Design Homogenization / productive friction」（UW+MS, preprint）
- Adam Wathan (Tailwind) Xポスト（indigo起源・一次）
- v0 docs（design-systems）／Vercel changelog（v0 Themes）（一次）
- Pangram Labs「Walking Through AI Phrases」「Spotting AI Writing Patterns」
- 1up.ai／REFUGE Marketing（コピー矯正・ブランドボイス）／GPTZero（検出原理）
- 925studios／prg.sh／JCarterJohnson vibecoded-design-tells（視覚シグナル）
