# サーベイ論文まとめ（yamashige）

## 論文の情報
- 分野：⑤時系列・異常検知
- タイトル：A Survey of Machine Learning and Deep Learning for Financial Fraud Detection
- 著者・年：Spiros Thivaios, Georgios Kostopoulos, Antonia Stefani, Sotiris Kotsiantis (2026年)
- URL / DOI：https://www.mdpi.com/1999-4893/19/5/354

## 1. 論文の要約
- 概要：金融取引のデジタル化に伴い増加・複雑化する「金融不正（クレジットカード詐欺・不正送金・粉飾決算等）」に対し、機械学習（ML）および深層学習（DL）を用いた検知手法を体系的に網羅した包括的サーベイ論文。   
取り上げられている手法：従来の教師あり学習、異常検知から、グラフニューラルネットワーク（GNN）、時系列Transformer、マルチモーダル統合、コスト考慮型学習、強化学習、連合学習（Federated Learning）、大規模言語モデル（LLM）の活用まで多岐にわたる[cite: 1, 3]。
本論文の強み・主張：単なるモデル精度の比較にとどまらず、極端なクラス不均衡（不正データの少なさ）、コンセプトドリフト（詐欺手法の変化）、リアルタイム判定の遅延制約、データプライバシー、運用コストといった「実社会（現場）へのデプロイにおける課題」を踏まえた評価手法・設計指針を提案している点[cite: 1, 3]。

## 2. 歴史・流れ
- 1990年代（ルールベース・手動監査の時代）[cite: 8]

「1回100万円以上でフラグ」のような固定ルールや手動チェックが中心[cite: 2, 8]。変化する不正手法への適応力や拡張性に限界が生じた[cite: 2]。

2000年代（初期のデータマイニング・統計モデル）[cite: 8]

統計的手法やデータマイニング（決定木、SVM、ロジスティック回帰など）を導入し、自動化と精度の向上が図られた[cite: 2, 8]。

2010年代（アンサンブル学習とクラス不均衡対策）[cite: 8]

ランダムフォレストやXGBoost/LightGBMなどのアンサンブル学習が主流に[cite: 6, 8]。不均衡データ処理（SMOTEなど）と組み合わせて表形式データの検知精度が大幅に向上[cite: 6, 8, 26]。

2018年頃〜（ディープラーニング・時系列・GANの台頭）[cite: 8]

CNN/LSTMを用いた取引履歴（時系列パターン）のモデリングや、オートエンコーダ・GANによる異常検知・データ生成が活発化[cite: 2, 8, 14, 15]。

2020年代以降（グラフAI・マルチモーダル・連合学習・LLM時代）[cite: 8]

複数アカウント・端末・加盟店の関係性をネットワークとして捉える「グラフニューラルネットワーク（GNN）」、テキストと数値データを統合するマルチモーダルAI、プライバシーを保護しつつ協調学習する「連合学習」、アナリスト業務を補助する「LLM」などが統合された最新環境へ進化[cite: 1, 2, 8, 19]。

## 3. 社会的課題とのつながり
- 被害額の巨大化と手口の高度化：オンライン決済や暗号資産の普及に伴い、資金洗浄（マネーロンダリング）や組織的な口座乗っ取りなど手口が広域化・自動化しており、従来の固定ルールでは防ぎきれない[cite: 1, 2]。

誤検知（False Positive）による顧客体験の低下と調査コスト：誤って正常なカード利用を止めてしまうと顧客満足度が低下するだけでなく、現場調査員の確認コスト（人件費）が膨れ上がる。単なる正解率ではなく「ビジネス上の損失・運用コスト」を最小化するAIが求められている[cite: 21, 22, 27]。

データプライバシーの壁（GDPR等）：複数金融機関で連携して不正を防ぎたいが、個人情報保護の法規制により顧客データを容易に一括共有できない。これを解決する「連合学習」や「説明可能AI（XAI）」による監査可能性の担保が急務となっている[cite: 1, 2, 29]。

## 4. よく使われる信頼性のあるデータセット
論文の中で実際に使われているものを書く。


| データセット名 | 中身 | 規模 | 論文での使われ方 | 入手先（URL） |
| --- | --- | --- | --- | --- |
| Fraud Dataset Benchmark (FDB) | カード不正・悪意あるWebトラフィック・ボット検知・ローンデフォルトなどを集約した標準化ベンチマーク[cite: 10]。 | 複数データセットの集合[cite: 11] | データローダーや評価プロトコルが統一されており、タスクを跨いだMLモデルの体系的な比較評価に使用[cite: 10]。| GitHub (FDB)[cite: 37]https://github.com/amazon-science/fraud-dataset-benchmark|
| ULB Credit Card Fraud | 2013年9月に欧州のカード保持者が利用した取引データ（PCA変換済）[cite: 10]。| 284,807件(不正率 0.172%)[cite: 11]| 極端なクラス不均衡下における異常検知や不均衡分類モデルの評価用標準ベンチマーク[cite: 10]。| Kaggle (ULB)[cite: 10, 37][https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)<br> |
| IEEE-CIS Fraud Detection | Vesta社提供の実EC取引データ（数値・カテゴリ・端末ID属性等）。 | 590,540件(不正率 〜3.5%)| 豊富な文脈情報を含むため、ディープラーニングやアンサンブル学習、特徴量エンジニアリングの評価に使用。 | [[https://www.kaggle.com/competitions/ieee-fraud-detection/data](https://www.kaggle.com/competitions/ieee-fraud-detection/data)<br> ](https://www.kaggle.com/competitions/ieee-fraud-detection/data)|
| PaySim | モバイルマネーサービスの実際の実績をベースにした合成（シミュレーション）取引データ。 | 6,362,620件(不正率 〜0.129%)| 大規模取引環境におけるスケーラビリティや強化学習・コスト考慮型モデルのシミュレーション評価で使用。| [https://www.kaggle.com/datasets/ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1)|
| Credit Card Fraud Detection 2023 | 2023年の欧州クレジットカード取引データ（バランス調整済みの実験をサポート）。
 | 568,630件(不正率 50%)
 | 最新の取引パターンに対するアンサンブル学習やディープニューラルネットワークの評価に使用。
 | [https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023](https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023)<br> |
| Elliptic Bitcoin Dataset | ビットコインの取引ネットワーク（ノード＝取引、エッジ＝BTCの流れていく関係）。
 | 203,769ノード(不正率 〜2.05%)
 | 取引の「グラフ構造（ネットワーク関係）」を活かしたGNNや暗号資産の不正追跡モデルの検証に使用。
 | [https://www.kaggle.com/datasets/ellipticco/elliptic-data-set](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set)<br> |
