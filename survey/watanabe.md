# サーベイ論文まとめ（watanabe）

## 論文の情報
- 分野：②画像分類・物体認識
- 論文1：Deep transfer learning for image classification: a survey
  - 著者・年：Jo Plested, Musa Phiri, Tom Gedeon（2026）/ Artificial Intelligence Review 59, 100
  - URL / DOI：https://doi.org/10.1007/s10462-026-11491-z
- 論文2：Vision Transformers for Image Classification: A Comparative Survey
  - 著者・年：Yaoli Wang, Yaojun Deng, Yuanjin Zheng, Pratik Chattopadhyay, Lipo Wang（2025）/ Technologies 13(1), 32
  - URL / DOI：https://doi.org/10.3390/technologies13010032
- 2本の関係：「画像分類でデータが少ないときどうするか」を、論文1は**学習のさせ方（転移学習）**、論文2は**モデル（Vision Transformer）**の側から扱っている。

## 1. 論文の要約
- **論文1**：大きいデータで事前学習したモデルを、目的の小さいデータで学習し直す「転移学習」を体系的に整理したサーベイ。
  - 主張：転移学習の成否は「ターゲットデータの大きさ」と「事前学習データとの似ている度合い」の2つでほぼ決まる。
  - 似ていないデータに転移すると、かえって精度が下がる「負の転移」が起きる。「全部転移するかしないか」ではなく「どれくらい転移するか」を調整すれば防げる。
  - 手法を、インスタンス / 特徴 / パラメータ（PETL・正則化など）/ ベストプラクティスに分類し直した。
- **論文2**：文章用のモデル Transformer を画像に使った ViT と、その改良版を、CNN と数字で比較したサーベイ。
  - ViT は画像全体の関係を一度に見られるが、データを大量に必要とする。ImageNet（130万枚）だけでは CNN と同程度で、3億枚で事前学習すると CNN を上回る。
  - 改良の方向：データ効率（DeiT）、CNN との組み合わせ（CvT）、軽量化（LeViT・CCT）、深層化（CaiT）。
  - 例：ImageNet だけで学習すると ViT-L（76.5%）が ViT-B（77.9%）より低い。データ不足だと大きいモデルを活かせない。

## 2. 歴史・流れ
- 2009年：転移学習の定義が整理され、ImageNet が登場。
- 2012年〜：CNN が主流に。「ImageNet で事前学習 → 小さいデータで学習し直す」が定番になる。
- 2017〜2020年：事前学習データが巨大化（3億枚〜35億枚）。2017年に文章用の Transformer が登場。
- 2020年：ViT が登場。畳み込みを使わずに画像分類に成功。
- 2021年〜：ViT の改良（DeiT・CvT・LeViT など）と、ラベルなしで事前学習する自己教師あり学習（MAE など）が進む。
- 2022年〜現在：巨大な基盤モデルの一部だけを学習し直す PETL や、画像と文章をセットで学習する CLIP が中心に。

## 3. 社会的課題とのつながり
- 医療画像：データが少なく（希少疾患・プライバシー）、一般の写真とも見た目が違うため、転移学習が欠かせない。ViT のデータ不足の弱点も問題になる。
- 防災・農業：衛星画像や作物画像は大量にあるが、山火事の急拡大や特定の害虫のような目的の現象のラベル付きデータはごくわずか。
- 自動運転・ロボット：緊急時の場面はめったに起きず、実機でのデータ集めは高価。シミュレーションで学習し、少ない実データで仕上げる。
- 電力・機器：軽量な ViT（LeViT・CCT）なら、高性能なサーバーがなくても動き、電力も減らせる。

## 4. よく使われる信頼性のあるデータセット
論文の中で実際に使われているものを書く。

| データセット名 | 中身 | 規模 | 論文での使われ方 | 入手先（URL） |
| --- | --- | --- | --- | --- |
| ImageNet-1K | 身の回りの物・動物 | 約130万枚、1,000クラス | 事前学習の標準。論文2の比較の基準 | https://www.image-net.org/ |
| CIFAR-10 / 100 | 一般物体（小さい画像） | 6万枚、10 / 100クラス | ImageNet に似ている転移先の代表（両方の論文） | https://www.cs.toronto.edu/~kriz/cifar.html |
| Oxford-IIIT Pets | 犬・猫の品種 | 7,349枚、37クラス | 転移が効く例。精度 83.2% → 94.5%（論文1） | https://www.robots.ox.ac.uk/~vgg/data/pets/ |
| Oxford 102 Flowers | 花の種類 | 8,189枚、102クラス | 転移先の評価（両方の論文） | https://www.robots.ox.ac.uk/~vgg/data/flowers/102/ |
| Stanford Cars | 車の車種 | 16,185枚、196クラス | ImageNet に似ておらず転移が効きにくい例（両方の論文） | https://huggingface.co/datasets/tanganke/stanford_cars |
| FGVC Aircraft | 飛行機の機種 | 10,000枚、100クラス | Cars と同じく転移が効きにくい例（論文1） | https://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/ |
| Food-101 | 料理の種類 | 101,000枚、101クラス | 細かい分類の転移先（論文1） | https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/ |
