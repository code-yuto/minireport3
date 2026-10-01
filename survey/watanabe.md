# サーベイ論文まとめ（watanabe）

## 論文の情報
- 分野：②画像分類・物体認識
- タイトル：Deep transfer learning for image classification: a survey
- 著者・年：Jo Plested, Musa Phiri, Tom Gedeon（2026）
- 掲載：Artificial Intelligence Review, Vol. 59, Issue 3, Article 100（2026年1月29日公開）
- URL / DOI：https://link.springer.com/article/10.1007/s10462-026-11491-z / https://doi.org/10.1007/s10462-026-11491-z
- ライセンス：Open Access（CC BY 4.0）

## 1. 論文の要約
- **問題**：画像分類の深層学習（CNN・Transformer）は、ラベル付きデータが大量にあるときに一番性能が出る。しかし現実にはデータを大量に集められない場面が多い。
- **解決策**：転移学習。大きなデータセット（ソース）で事前学習したモデルを、目的のデータセット（ターゲット）でファインチューニングする。
- **この論文の主張**：転移学習がうまくいくかどうかは、次の2つで大きく決まる。
  1. ターゲットデータセットの**大きさ**（小：約1万枚 〜 大：100万枚以上）
  2. ソースとターゲットの**似ている度合い**（類似度）
- **新しい分類（タクソノミー）**：手法を次の5つに分けて整理している。
  - インスタンスベース：どのデータで事前学習するか
  - 特徴ベース：ソースとターゲットの特徴空間をそろえる
  - パラメータベース：PETL、正則化、正規化、アンサンブル
  - ベストプラクティス：事前学習データの選び方、ハイパーパラメータ、転移しやすさの指標
  - （ドメイン側の分類に「大きさ」と「類似度」の軸を追加）
- **負の転移**：事前学習したせいで、かえって性能が下がること。次の3つがそろうと起きやすい。
  - ターゲットが、ゼロから学習できるくらい大きい
  - ソースとターゲットが似ていない
  - 重みを事前学習の値から十分に動かせない設定になっている
- **結論**：「全部転移する / しない」の二択ではなく、「どの層を・どれくらい転移するか」を連続的に考えれば、負の転移はなくせる。
- **実験例**：Big Transfer（BiT）の推奨設定は、ImageNet に似た CIFAR・Pets ではよく効く。一方、似ていない Stanford Cars・FGVC Aircraft では最適から遠い。

## 2. 歴史・流れ
- **2009年**：Pan & Yang が転移学習の用語と定義を整理する（今も使われている基本の定義）。同じ年に ImageNet が登場する（Deng et al. 2009）。
- **2012年〜**：AlexNet などの CNN が ImageNet で成功する。「ImageNet で事前学習 → 小さいデータでファインチューニング」が定番になる。
- **2014年**：Yosinski et al. が次のことを示し、その後の転移学習のやり方に大きな影響を与える。
  - 下の層ほど汎用的な特徴、上の層ほどタスク固有の特徴を学ぶ
  - 層を凍結するより、ファインチューニングしたほうがよい
- **2017〜2020年**：事前学習データの大規模化が進む。
  - JFT-300M（3億枚）、Instagram Hashtag（35億枚）
  - Big Transfer（2020）：データが多いほど、ターゲットの性能も上がる
- **2018〜2021年**：転移学習専用の手法が多く提案される。
  - 正則化：L2-SP、DELTA、BSS
  - 正規化：Stochastic Normalization
  - アンサンブル：SpotTune、MultiTune
  - ただし多くは「ソースとターゲットが似ている」ときにしか効かない
- **2020年〜**：Vision Transformer（ViT）が登場する。パラメータが桁違いに多いので、事前学習データの大きさがさらに重要になる。
- **2020年〜**：自己教師あり学習（ラベルなしで事前学習）が伸びる。
  - 対照学習
  - マスク予測（MAE：画像の75%を隠して復元する。2022年）
  - ターゲット自身で事前学習する「self-training」
- **2022年〜現在**：基盤モデル（巨大なビジョンモデル・ビジョン言語モデル）の時代。全部をファインチューニングすると重いので、一部だけ学習する **PETL** が中心になる。
  - Prompt（VPT）
  - Adapter
  - 一部パラメータだけ更新（bias だけ、LayerNorm だけ）
  - LoRA のような低ランクの差分学習

## 3. 社会的課題とのつながり
データを大量に集められないことが、そのまま社会の課題になっている分野がある。転移学習はその解決に必須の技術。
- **医療画像**
  - データが少ない（希少疾患、プライバシー）
  - 一般の写真とは見た目が大きく違うので、近いソースデータがない
  - 病院の撮影機器や患者層が違うだけで精度が落ちる
- **ロボット**
  - 実機は高価で、データ集めに時間がかかる
  - シミュレーションで大量に学習し、少ない実データでファインチューニングする
- **自動運転**
  - 普段の運転データは多いが、緊急時の場面はまれ（ロングテール分布）
- **環境・防災**
  - 例：衛星画像から、山火事が自分で気象を作る「火災積乱雲（PyroCb）」になるかを予測する
  - 衛星画像は大量にあるが、目的の現象はまれで、ラベル付きデータがほとんどない
- **農業**
  - 作物の分類、収量予測、害虫の発見
  - 特定の害虫のラベル付き画像はとても少ない
- **環境負荷**
  - 大きいモデルをゼロから学習すると、計算資源と電力を大量に使う
  - 転移学習なら、それを減らせる
- **ミニ研究につながりそうな問い**
  - 食事の写真のように、身近だけれどラベル付きデータが少ないタスクで、ImageNet と似ていないデータにどう転移すると精度が上がるか
  - 例：資料 p.6 の「食事記録や健康管理の手間をどう減らせるか？」

## 4. よく使われる信頼性のあるデータセット
論文の中で実際に使われているもの（論文の Table 4・5 と本文から）。

**事前学習（ソース）に使うデータセット**

| データセット名 | 中身 | 規模 | 論文での使われ方 | 入手先（URL） |
| --- | --- | --- | --- | --- |
| ImageNet（1K / 21K） | 一般物体 | 130万枚〜（1,000〜21,000クラス） | 標準のソース。BiT の実験では ImageNet-21K から転移 | https://www.image-net.org/ |
| JFT-300M | 一般物体（Google 社内） | 3億枚、18,291クラス | 大規模事前学習の例（非公開） | 非公開 |
| Instagram Hashtag | ハッシュタグ付き画像 | 35億枚、1,500クラス以上 | ゆるいラベルでも事前学習に効く例 | 非公開 |
| Places365 | 屋内・屋外のシーン | 180万〜800万枚、365クラス | 似ていないソースとして使われた例 | http://places2.csail.mit.edu/ |
| iNaturalist | 動植物 | 85.9万枚、5,000クラス以上 | 動植物系ターゲット向けのソース | https://github.com/visipedia/inat_comp |

**転移先（ターゲット）に使うデータセット**

| データセット名 | 中身 | 規模 | 論文での使われ方 | 入手先（URL） |
| --- | --- | --- | --- | --- |
| CIFAR-10 / 100 | 一般物体（小さい画像） | 5万枚、10 / 100クラス | ImageNet に似ている代表。BiT の推奨設定がよく効く | https://www.cs.toronto.edu/~kriz/cifar.html |
| Oxford-IIIT Pets | 犬・猫の品種 | 7,049枚、37クラス | 似ている側の代表。精度 83.2%（ゼロから）→ 94.5%（転移） | https://www.robots.ox.ac.uk/~vgg/data/pets/ |
| Oxford 102 Flowers | 花の種類 | 8,189枚、102クラス | BiT・Decathlon の評価 | https://www.robots.ox.ac.uk/~vgg/data/flowers/102/ |
| Stanford Cars | 車の車種 | 16,185枚、196クラス | 似ていない側の代表。ImageNet からの転移が効きにくい | https://huggingface.co/datasets/tanganke/stanford_cars |
| FGVC Aircraft | 飛行機の機種 | 10,000枚、100クラス | 似ていない側の代表。Cars と同じく転移が効きにくい | https://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/ |
| CUB-200-2011 | 鳥の種類 | 11,788枚、200クラス | Transferability Estimation Benchmark | https://www.vision.caltech.edu/datasets/cub_200_2011/ |
| Stanford Dogs | 犬の品種 | 20,580枚、120クラス | Transferability Estimation Benchmark | http://vision.stanford.edu/aditya86/ImageNetDogs/ |
| Food-101 | 料理の種類 | 101,000枚、101クラス | 食べ物の細かい分類のターゲット | https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/ |
| Caltech-101 / 256 | 一般物体 | 9,146枚、101 / 256クラス | Transferability Estimation Benchmark | https://data.caltech.edu/records/mzrjq-6wc02 |
| PASCAL VOC 2007 | 一般物体 | 9,963枚、20クラス | Transferability Estimation Benchmark | http://host.robots.ox.ac.uk/pascal/VOC/voc2007/ |
| SUN397 | シーン | 108,754枚、397クラス | シーン分類のターゲット | https://vision.princeton.edu/projects/2010/SUN/ |
| DTD | テクスチャ | 5,640枚、47クラス | Decathlon の1タスク | https://www.robots.ox.ac.uk/~vgg/data/dtd/ |
| German Traffic Signs（GTSRB） | 道路標識 | 39,209枚（学習用）、43クラス | Decathlon の1タスク | https://benchmark.ini.rub.de/ |
| SVHN | 街中の家の番号（数字） | 73,257枚（学習用）、10クラス | Decathlon の1タスク | http://ufldl.stanford.edu/housenumbers/ |
| COCO | 物体検出 | 32.8万枚、80クラス、150万個のバウンディングボックス | ImageNet で事前学習すると負の転移が起きた例 | https://cocodataset.org/ |

**ベンチマーク（複数のデータセットのセット）**
- **Transferability Estimation Benchmark**（Bolya et al. 2021）
  - ターゲット6つ：Caltech101, CIFAR10, Birds, CUB, Pets, Dogs
  - ソース8つ、モデル4つ
- **Visual Decathlon**（Rebuffi et al. 2017）：10タスクを同時に評価する
  - ImageNet, CIFAR-100, Aircraft, Daimler pedestrian, DTD, GTSRB, Omniglot, SVHN, UCF101, Flowers
- **Visual PETL Benchmark**（Xin et al. 2024）：PETL 手法の評価用、30データセット

**メモ**
- 論文の Table 5 では、データセットの数字にいくつか誤りがありそうなので、ここでは各データセットの公式の値を書いた。
  - Food-101：論文では「500クラス」→ 正しくは101クラス
  - PASCAL VOC 2007：論文では9,063枚 → 公式は9,963枚
  - DTD：論文では3,760枚 → 公式は5,640枚
- JFT と Instagram は非公開なので、ミニ研究では使えない。
- ミニ研究で実証するなら、**公開されていて小さめ**（数千〜数万枚）なものが扱いやすい。
  - 似ている例：Pets、Flowers
  - 似ていない例：Cars、Aircraft
  - 社会的課題に近い例：Food-101
  - これらを使えば、論文の「大きさ × 類似度」の主張を自分たちで確かめられる。
