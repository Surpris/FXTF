# 機械学習の利用の検討
機械学習（ML）や遺伝的アルゴリズム（GA）などの最適化・予測アルゴリズムでは、説明変数 $\vec{x}(t) = (x_1(t), \dots, x_N(t))$ と
事象 $y = y(\vec{x})$ があって、これらの間に次の関係があるものとして、最適な重み $\vec{w}$ を見つける：
$$
y = g(\vec{w}\cdot \vec{x}(t) + \theta) \cdots (\triangle)
$$
ここで $g(a)$ は適当な関数で、入力 $a$ を分類するように値を返す。   
例えば２クラス分類であれば、 $g$ はとして &pm;1をとるステップ関数や $\tanh$ 関数が用いられる。   

単純なモデルとして、時刻 $t_0$ からさかのぼって $t_0 - (N-1)\tau_1$ までのレート $r(t)$ を説明変数とする：
$$
\vec{x}(t) = (r(t_0), \dots, r(t_0 - (N-1)\tau_1))
$$
そして $y$ としては、時刻 $t_0 + \tau_0$ でのレートの増分を与える。つまり
$$
y(t_0;\tau_0) = \Delta r(t; \tau_0) \equiv r(t + \tau_0) - r(t_0)
$$
そして $y$ を $N_c$ 個のクラスに分類する問題を考え、そのための分類関数 $g$ を用意する（多クラス分類関数）。これらによって先ほどの式 $(\triangle)$ が成り立つような重み $\vec{w}(t_0. \tau_0)$ を計算する。   

## いろいろサイトを見ていて
株価やFXはランダムウォークであるという考えが大多数のようである。瞬間的にはそう見えるかもしれないが、しかし長期的に見ればなにかしらの傾向（履歴）があると考えられる。   
そうでなければゴールデンクロスやら三田法やらで見られるような買い目・売り目が一度や二度ではなく何度も現れるわけがない。   
「そんなのは後付けである」という意見あるだろうが、それは「これから先にそういう傾向が現れるかどうかが不確かである」だけであって「傾向がある」ことへの反論ではない。   
多くのトレーダーはその傾向をつかみたいがために新旧のテクニックを利用している（はず）。   
莫大な数のトレーダーが取引しているのだから、秒単位での瞬間的な変化というのは予測不可能と考えてよいだろう。この辺りはQiitaなどで報告されている、機械学習を用いた実験からも分かる。   
一方で「[機械学習で為替予測 Deep Learning 編](https://kuune.org/text/2017/04/09/market-prediction-with-deep-learning/)」や「[人工知能を使った小さな開発会社の小さな作品](http://ai-deep.hatenablog.com/entry/2016/04/18/134446)」には、数分、数十分の単位でみると予測確率または期待値が大きく上がるという記述がある。これは先ほど述べたように長期的には上昇・下降の傾向が現れるということと違わない話である。こういう話を聞くと、数十分先に勝っているかどうかを予想しようという試みは、それほど分が悪いものではないと考える（傍から見ればばかげているかもしれないが）。   
なお、彼らが用いている指標は、前者はOHLCとVolume（出来高）と時間のみ、後者は様々なテクニカル指標である。   

## データの規格化
何を特徴量（入力データ）にするにしても、そのデータの規格化の方法でパフォーマンスが変わるのは、経験的にも理論的にもよく知られている。   
このことは[Impact of Data Normalization on Stock Index Forecasting ](http://mirlabs.net/ijcisim/regular_papers_2014/IJCISIM_24.pdf)にも報告されている。   
この論文で掲載されている規格化の方法は次のとおりである。      

|Method|Definition|
|:---:|:---:|
|Min-Max|$\hat{a} = low + \frac{(high-low)}{\max(A) - \min(A)}(a - \min(A))$|
|Decimal|$\hat{a} = a/10^d, \max(\hat{a})< 1$|
|Z-Score|$\hat{a} = (a - \mu(a))/\sigma(a)$|
|Median|$\hat{a} = a/median(a)$|
|Sigmoid|$\hat{a} = \frac{1}{1+e^a}$|
|Median and Median Absolute Deviation|$\hat{a} = \frac{a - median(A)}{MAD(a)}$, $MAD \equiv median(abs(\{a_k\})-median(A)))$|
|Tanh|$\hat{a} = 0.5\left[\tanh\left(\frac{0.01(a-\mu)}{\sigma}\right)+1\right]$|

<br/>

## 参考サイト
* [機械学習で為替予測 Deep Learning 編](https://kuune.org/text/2017/04/09/market-prediction-with-deep-learning/)
* [人工知能を使った小さな開発会社の小さな作品](http://ai-deep.hatenablog.com/entry/2016/04/18/134446)
* [Qiita->FX(tag)](http://qiita.com/tags/FX)
    + [ここ](http://qiita.com/ryo_grid/items/7746528f8cae8026b936)に割とまとまっている
* [Impact of Data Normalization on Stock Index Forecasting ](http://mirlabs.net/ijcisim/regular_papers_2014/IJCISIM_24.pdf)

### 機械学習のパッケージの公式サイト
* [Tensorflow](https://www.tensorflow.org/)
* [Keras](https://keras.io/ja/)
* [scikit-learn](http://scikit-learn.org/stable/)

# 機械学習に関するメモ
* Kerasでの訓練データは、`model.fit`のパラメータ`shuffle`が`True`だと内部でシャッフルされる。
* Kerasでの各エポックでの学習結果は`hist.history`で確認できる。
* エポック数とは、一つのデータセットを繰り返して学習させる回数を指す。
    + 繰り返し過ぎると過学習する。
    + 下図のように、識別精度（訓練データに対する精度）と予測精度（テストデータに対する精度）の差が小さくなるように設定する。   
    ![](../images/20170117165040.png)   
* [こちらのサイト](http://ai-programming.hatenablog.jp/entry/2016/04/14/230122)によれば、中間層の最適数に関しては、これが最適という意見は今のところ（2016/04/14）ない。
    + 中間層の素子数は入力する特徴量の数より大きくとり、一層ずつ増やしていって精度の変化を見るのが良い？
    + 「あらゆる連続な非線形関数は3層ニューラルネットワークで近似できるということが証明されている」らしいが、どの論文？

## 参考サイト
* [中間層はどのぐらいが良いのか...？ - AI-Programming](http://ai-programming.hatenablog.jp/entry/2016/04/14/230122)
* [日経平均が日中どのくらい変動するかをTensorFlowで予測する （今までのまとめ） - 今日も窓辺でプログラム](http://www.madopro.net/entry/2016/09/20/120259)
* [【機械学習】ニューラルネットワークにおける効率的なパラメータ調整方法についてまとめてみた - Qiita](http://qiita.com/To_Murakami/items/e8b7bfe66750fb3f2050)

# 今後の方針
2017/05/28 (Sun.) 時点でKeras/Tensorflowを用いた深層学習モデルの構築方法の基本を身につけた。   
次に検討したいことを以下に並べる。   

* モデルパラメータの最適化
* 特徴量の選択と規格化
* リアルタイム予測のためのシステム構築

## モデルパラメータの最適化
これは特徴量によって変わってくるのだろうが、最適化の手順だけでも

## 特徴量の選択と規格化
特徴量が大事で、OHLCと取引時間帯という基本パラメータ、SMAなどのテクニカル指標、これらの組み合わせでどれが使えそうかをよく検討する必要がある。   
2017/05/30 (Tue.) 時点でテストして判明していることを記す。   

* 高確率で予測される部分を取り出せば勝率は上がる。
* 特徴量の組と勝率の関係は次の通り：close単体 < SMA < SMA+HL。

## リアルタイム予測のためのシステム構築
### バックテストのシステム
2017/05/30 (Tue.) の時点で、SMA+HLを特徴量に用いることで勝率が高くなることを確認した。   
作成したモデルを用いて一度バックテストをやっておきたいという思いがあり、特徴量とモデルの選択を休憩してバックテストのシステムを構築する。   
バックテストのシステムの要件を以下に挙げる。

* SQLDBに登録されたレコードを順に取得して予測にかける。
* モデルが「勝てる」と予測する確率を与え、それを超えたときに注文する。
* まずは注文してから $\tau$ 分後に決済する方針をとる。
    + 時間 $\tau$ はモデルの訓練に用いた時間差とする。
    + 損切りや途中決済は後々実装する。
* 決済するまでは新しい注文を出さない。
* スプレッドを与えられるようにする。
    + もしくは取得されたデータを用いてスプレッドを計算・更新する。
* スタートの値を与えられるようにする。

### オンラインテストのシステム
オンラインテストでは、取得されたデータをため込みつつ予測を開始する。モデルの時間足に合わせて、予測するタイミングを調整する。   
そのほかの要件はバックテストとほぼ変わらない（と思う）が、リアルタイムで相場や予測を見える化するようにしたい。

## 2017/06/01 (Thu.) の週にわかったことと、残りで進めること
2017/06/01 (Thu.) の時点で、オフラインにて次のことを一通り実施した状態にある。   

* データの取得と保存（オンライン込み）
* 各時間足でのOHLCの計算
* テクニカル指標であるSMAの計算
* モデルの生成・訓練
* バックテストの実施とレポート

2017/06/02 (Fri.) の週の残りは、次を進めたい。   
* オフラインについては、
    + モデルの生成・訓練部分の調整
    + バックテストクラスの調整
    + レポートやログを残すよう調整
    + 全体用のSQLDBの準備
    + SQLAnaforFXに関して、週末や欠損値であるかどうかのフラグの追加
        * これに際して、timestampの飛びをなくす
    + 週末にモデル更新を行う
* オンラインについては、
    + 取得されたデータをDBにリアルタイムで書き込むよう調整
    + OHLC、SMAなどの計算を行うよう調整
    + リアルタイムで予測し、注文・決済を行うシステムの構築

そうして時間が許せば、モデルや特徴量の検討を進める。具体的には次を調査する。   

* エポック数などのハイパーパラメータを変えたときのlossやaccuracyの変化
* 特徴量の規格化方法を変えたときのlossやaccuracyの変化
* 決済をするタイミング $\tau$ を変えたときのlossやaccuracyの変化
* 複数のタイミング $\tau$ に対して訓練されたモデルの一連を利用したシステムの構築とその性能の評価
* 注文してからさらに注文を入れたときのゲインの変化
* 決済するタイミングを途中の予測に基づき変更したときのゲインの変化
* モデルの構造を変えたときのlossやaccuracyの変化
    + LSTMの利用を検討する

### モデルの生成・訓練部分の調整
いま実装しているmodelの生成部分、訓練部分、出力部分などを一つのクラスにする。   
初期化の引数として訓練データの型、層の数などを検討する。   
訓練部分は、エポック数を何かしらの条件で決められるようにしたいが、、   
エポックを変えつつ、最も良いものを選択するか。（ここでの選択基準は高確率？それとも全体？）   
訓練中のaccuracyやlossを記録に残せるようにしたい。   
データの保存形式はzipやtarにするか？

### バックテストクラスの調整
レポート（グラフ、始値、終値、ドローダウン、最大）やログ（資産の変動、確率、etc.）を出力できるようにする。   
また、結果を保存できるようにするか。

### 全体用のSQLDBの準備
これは比較的簡単で、SQLAnaforFXの引数にフォルダを指定する文字列のリストを与えられるように調整すればよい。

### 週末や欠損値であるかどうかのフラグの追加
SQLDBそのものの構造を変えることにするが、タイムスタンプは"yyyyMMDD 00:00:00"をスタートとして時間足を用意する。   
これにしたがって、１か月だと１分足で1440&times;30=43200レコードにおよぶOHCLやテクニカル指標が存在する。   
その中でおよそ８日分は休日である。   
フラグとして、週末の値に０、欠損値にー１、そのほか（つまり有効なデータ）に１を与える。

### モデル更新
上記調整が終了した時点で、エポック数を調整しつつモデルを更新する。   
その段階で最も良いモデルのいくつかをリアルタイムテストにかけてみる。   

### DBにリアルタイムで書き込むよう調整
Jupyter notebook上でDBを呼び出し、そのDBに書き込んでいく。   
とりあえず来週は裏で回して様子を見ることにして、うまくいけば本回しにする。   
というかバックテストをすればよいか。

### OHLC、SMAなどの計算を行うよう調整
先に述べたが、時間足は"yyyyMMDD 00:00:00"を基準にして用意する。   
そこでデータを取得した時刻が次の時間足のタイミングになったときに、前の時間足のOHLCやSMAを計算するように組む。

### リアルタイムで予測し、注文・決済を行うシステムの構築
これはバックテストとかぶる部分がある。   
時間足を基に予測を行うシステムの場合、予測を行うタイミングはその時間足データの計算以後となる。   
注文した時刻を覚えておき、そこから $\tau$ 分後に決済する。   
決済した時刻の次に取得したデータを決済時のレートとする。

### 2017/06/05 (Mon.) に考えていた内容
```
About FX system
KerasModelsForFX
This class is not only for FX but also stocks.
Some functions are to implemented.
For example,
• return the trained models,
• select effective models by some criteria,
• return or plot histories of accuracy and loss of each model,
• predict high and low of FX (or stocks) and return the list of probabilities which are used by FXTrader,
• save / load trained models by using KerasModelAdapter.
KerasModelAdapter
This class serves some functions about save / load of Keras models.
FXTrader
This class deals with trades of FX.
This inherits TraderBase and serves the following functions:
• order / settle a trade,
• load models,
• plot history of trades, etc.
FXSystem
This is a GUI class.
This class offers the followings:
• plot trend graph of funding and others, probability map,
• manual order / settlement,
• show information on global affairs,
• send messages of e-mails about the current status.
Currently Keras is used, but in the future CNTK, Cognitive Toolkits provided by MS, will be used for its transportability to other Windows systems.
```
