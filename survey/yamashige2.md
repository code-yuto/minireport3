# サーベイ論文まとめ（yamashige）

## 論文の情報
- 分野：⑤時系列・異常検知
- タイトル：Deep Learning for Time Series Anomaly Detection: A Survey
- 著者・年：Zahra Zamanzadeh Darban, Geoffrey I. Webb, Shirui Pan, Charu C. Aggarwal, Mahsa Salehi (2022年) 
- URL / DOI：https://doi.org/10.48550/arXiv.2211.05244 / arXiv:2211.05244

## 1. 論文の要約
- 概要：製造、医療、ITインフラなど多岐にわたる分野で必須となる「時系列データの異常検知」において、近年のディープラーニング技術を用いた手法を包括的に整理・体系化したサーベイ論文。
 取り上げられている手法：
1. 予測ベース（Forecasting-based）：RNN/LSTM/GRU, TCN(CNN), GNN, HTM, Transformer
2. 再構築ベース（Reconstruction-based）：Autoencoder (AE), VAE, GAN, Transformer
3. ハイブリッド（Hybrid）：両者を統合したモデル
本論文の強み・主張：1次元（単変量）および多次元（多変量）時系列における異常の定義（点・文脈・トレンド・相関異常など）を数学的に分類し、最新モデルの構造・強み・限界、さらには48個のベンチマークデータセットと12の応用分野までを徹底的に網羅している点。

## 2. 歴史・流れ
- 1. 1960年代〜（古典的統計手法・外れ値検知の黎明期）
 統計的な移動平均や境界値に基づく手法（Grubbsテストなど）が中心。
2. 2000年代〜2010年代前半（機械学習モデルの導入）
 One-Class SVMやIsolation Forest、PCA（主成分分析）を用いた外れ値検出。時系列の複雑な時間変化を捉えるには限界があった。
3. 2015年頃〜（RNN/LSTMによる「予測ベース」の台頭）
 LSTMやGRUなどの再帰型ニューラルネットワークを用いて「次の値を予測し、予測誤差で異常を測る」手法（LSTM-ADなど）が一般化。
4. 2018年頃〜（Autoencoder / VAE / GANによる「再構築ベース」の普及）
 変動が激しく予測が困難な時系列に対し、波形全体を潜在空間に落とし込んで復元するAutoencoderやVAE（Donut, OmniAnomaly等）、GAN（BeatGAN, MAD-GAN等）が成果を上げる。
5. 2020年以降（GNN・Transformer・ハイブリッド時代）
 センサー間の「空間的相関（関係性）」を捉えるGNN（グラフAI）（GDN等）や、長期間の依存関係を捉えるTransformer（Anomaly Transformer, TranAD等）が融合し、複雑な多変量時系列システムに適用される現在に至る。

## 3. 社会的課題とのつながり
-  インフラ・プラントのダウンタイム回避：スマートファクトリー、水処理プラント、電力網（スマートグリッド）における突然の設備故障やサイバー攻撃を未然に防ぎ、巨大な経済損失を防止する。
 医療リスクの早期発見：心電図（ECG）や脳波（EEG）などの生体時系列データから、不整脈やてんかん発作、アルツハイマー病の前兆などの微細な異常パターンを自動検知して生存率を向上させる。
 IT・クラウド障害の即時検知：大規模なWebサービスやクラウドサーバー（AWS、Azure、Uber等）のKPIやリソース使用率を監視し、サーバーダウンやサービス遅延の根本原因（障害部位）を即座に特定する。

## 4. よく使われる信頼性のあるデータセット
論文の中で実際に使われているものを書く。
| データセット名 | 中身 | 規模 | 論文での使われ方 | 入手先（URL） |
| --- | --- | --- | --- | --- |
| SMD (Server Machine Dataset) | 大規模IT企業のサーバーマシンのリソース利用状況（CPU・メモリ等）[cite: 67]。 | 1,416,825サンプル / 28エンティティ / 38次元[cite: 67] | 多変量サーバー障害検出における最頻出のデファクトスタンダード[cite: 67]。 | https://github.com/NetManAIOps/OmniAnomaly |
| MSL (Mars Science Laboratory) | NASAの火星探査機のテレメトリデータ[cite: 67]。 | 132,046サンプル / 27エンティティ / 55次元[cite: 67] | 宇宙・航空分野における多変量時系列異常検知の標準ベンチマーク[cite: 67]。 | https://github.com/khundman/telemanom |
| SMAP (Soil Moisture Active Passive) | NASAの土壌水分観測衛星のテレメトリデータ[cite: 67]。 | 562,800サンプル / 55エンティティ / 25次元[cite: 67] | 宇宙・環境モニタリングデータの異常検知モデルの評価[cite: 67]。 | https://github.com/khundman/telemanom |
| SWAT (Secure Water Treatment) | 水処理プラントの物理テストベッドデータ[cite: 67]。 | 946,719サンプル / 1エンティティ / 51次元[cite: 67] | 産業制御システム（ICS）やインフラへのサイバー攻撃・障害検知[cite: 67]。 | https://itrust.sutd.edu.sg/testbeds/secure-water-treatment-swat/ |
| WADI (Water Distribution) | 配水システムの超多次元IoTテストベッドデータ[cite: 67]。 | 957,372サンプル / 1エンティティ / 127次元[cite: 67] | 超多次元なセンサーネットワークにおける高難易度異常検知の検証[cite: 67]。 | https://itrust.sutd.edu.sg/testbeds/water-distribution-wadi/ |
| PSM (Pooled Server Metrics) | eBayの多数のサーバーから収集された内部リソースメトリクス[cite: 67]。 | 132,480サンプル / 1エンティティ / 24次元[cite: 67] | 大規模ECサーバー群の障害・異常検知アルゴリズムの評価[cite: 67]。 | https://github.com/ebay/RANSynCoders |
| Yahoo (S5 Dataset) | Yahoo!が公開したWebトラフィック（A1〜A4データセット）[cite: 67]。 | 572,966サンプル / 367エンティティ / 1次元[cite: 67] | 単変量時系列異常検知における最も代表的な標準ベンチマーク[cite: 67]。 | https://webscope.sandbox.yahoo.com/ |
| NAB (Numenta Anomaly Benchmark) | 実世界および合成データを含むストリーミング異常検知用ベンチマーク[cite: 67]。 | 複数データセット（計数十万サンプル）[cite: 67] | リアルタイム・ストリーミングデータに対する異常検知精度の評価[cite: 67]。 | https://github.com/numenta/NAB |
| MIT-BIH Arrhythmia (ECG) | 標準的な心電図（ECG）不整脈データベース[cite: 67]。 | 28,600,000サンプル / 48エンティティ / 2次元[cite: 67] | 医療・ヘルスケア分野における心拍異常・不整脈検知のデファクトスタンダード[cite: 67]。 | https://www.physionet.org/content/mitdb/ |
| Credit Card Fraud Detection | クレジットカードの取引履歴データ（PCA変換済み）[cite: 67]。 | 284,807サンプル / 1エンティティ / 31次元[cite: 67] | 金融分野における極端な不均衡データの不正・異常検知評価[cite: 67]。 | https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud |