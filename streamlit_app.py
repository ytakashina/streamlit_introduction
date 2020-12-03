import pandas as pd
import streamlit as st
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

TITLE = "データ分析アプリのラピッドプロトタイピングパッケージ「Streamlit」"
BODY = """
by ytakashina for DSN アドベントカレンダー day 3

# はじめに
機械学習や数理最適化といった、データ分析に関係する仕事をする際、
Jupyter でデータの加工や可視化を行っている方は多いと思います。
実際、私もよく使っています。

開発者にとっては、Jupyter は使いやすいツールですが、
一方で、開発者ではない一般ユーザーには、敷居が高い面もあります。
生のソースコードがそのまま見えていますし、Python の実行環境の用意も必要です。
したがって、**データ分析プログラムを実業務に適用する段階では、多くの場合、
より使いやすいユーザーインターフェース（UI）に移行する必要**があります。

そんな UI を実現する 1 つ目の手段として、**Tableau 等の BI ツール**があります。
特に、データの可視化が主な目的であれば、BI ツールは強力な選択肢です。
しかし、機械学習による予測や、数理最適化による計画立案など、
**数値計算の比重が大きくなると、BI ツールでは対応が難しい**と個人的には感じています。

> ※もちろん「外部で行った計算をファイル出力し、BI ツールで読み込む」等の対応は可能です。
しかし、「入力は Excel、計算は EXE ファイル、可視化は Tableau」とツールが分散・複雑化し、属人性に繋がります。

> そもそも、ユーザーと議論しながら頻繁にアップデートを行う場合、ネイティブアプリとして開発すると
「バージョンアップのたびに最新版をダウンロードしてもらう」手間が発生します。更新に手間がかかると、それだけ改善スピードも落ちます。

UI を作成するもう 1 つの手段として、**Django 等を利用してスクラッチで Web アプリを作る**、というものがあります。
Web アプリとして作ってしまえば、データの前後処理や数値計算といった処理も、Web アプリの機能として自然に盛り込むことができます。
また、自由度が極めて高く、望んだ機能が大抵は実現できるでしょう（コストを度外視すれば）。
ユーザーから見ても、いつも同じページにアクセスすれば済むため、更新時のダウンロード・インストールの手間が省けます。

しかし、**スクラッチで Web アプリを作成するということは、開発に手間がかかる**ということでもあります。
それだけの手間と時間をかけてでも開発したいプロダクトであれば、スクラッチ開発もありかもしれません。
しかし、社内向けでユーザーも数人程度の場合は、もっと短期間に手軽に作りたいことが多いです。


# そんなあなたの願いを叶えるのが、Streamlit です。
Streamlit は、BI ツールのような使いやすい UI と、スクラッチ Web アプリに近い柔軟性を、
Jupyter のような手軽さで実現できる Python パッケージです。
百聞は一見に如かず。ここからは、実際に Streamlit を使ってみます。

例えば、以下のように、2 つの商品の月ごとの需要を表すようなデータがあったとします（商品と数字は適当）。

```python
demand = pd.DataFrame({
    "にんじん": [100, 200, 200, 150],
    "じゃがいも": [50, 20, 20, 300],
}, index=["April", "May", "June", "July"])
```
"""

BOTTOM = """
# 終わりに
お気づきかと思いますが、この記事は Streamlit を使って作成しています。
Web アプリ開発の経験がなくとも、普段から Jupyter を使っている人であれば、
このような見栄えの良いダッシュボードを気軽に作成できる、というのは非常に魅力的ではないでしょうか。

最後になりますが、褒めてばかりではフェアではないと思いますので、
Streamlit を触ってみて（まだ）不便だなと感じる点をいくつか書いておきます。

## データフレームが編集できない
Streamlit は、ウィジェットのスライダーやテキストフィールドで入力を取ることはできるのですが、
**Excel やスプレッドシートのような表形式の入力を行うことはできません**。
したがって、たくさんのデータの入力を一度に行いたい場合や、Excel からコピペしたい場合は、
現状では別の入力手段を用意する必要があります。

この点については、以下の issue でも議論が行われており、開発陣も必要性は認識しているようです。
当面は別の入力手段を使いつつ、気長に待つしかないかな、と思います。

https://github.com/streamlit/streamlit/issues/455
https://github.com/streamlit/streamlit/issues/271
https://github.com/streamlit/streamlit/issues/1345

## ユーザー認証等の機能は未実装
AWS Cognito 等と組み合わせることである程度解決可能だとは思いますが、
同じダッシュボード作成ツールの Plotly Dash 等と異なり、ユーザー認証機能はついていないようです。

ただし、これも現在開発中の Enterprise 版である「Streamlit for Teams」では実装される予定のようなので、
気長に待ちたいと思います。


## 細かいレイアウトの調整には不向き
あくまでプロトタイピング用なので、凝ったレイアウトを作るのには向かない気がしています。
このような用途の場合は、同じくダッシュボード作成ツールの Plotly Dash の方が良いかもしれません。
こちらは、作成は Streamlit より複雑で面倒ですが、レイアウトのカスタマイズ性が高く、本格的な製品の開発向きだと思います。



"""

demand = pd.DataFrame({
    "にんじん": [1000, 2000, 2000, 1500],
    "じゃがいも": [500, 200, 200, 3000],
}, index=["April", "May", "June", "July"])

BUY_UC = pd.DataFrame({
    'VEG1': {1: 110, 2: 130, 3: 110, 4: 120, 5: 100, 6: 90},
    'VEG2': {1: 120, 2: 130, 3: 140, 4: 110, 5: 120, 6: 100},
    'OIL1': {1: 130, 2: 110, 3: 130, 4: 120, 5: 150, 6: 140},
    'OIL2': {1: 110, 2: 90, 3: 100, 4: 120, 5: 110, 6: 80},
    'OIL3': {1: 115, 2: 115, 3: 95, 4: 125, 5: 105, 6: 135}
})

TIME_IDX = [1, 2, 3, 4, 5, 6]
OILS = ['VEG1', 'VEG2', 'OIL1', 'OIL2', 'OIL3']
REF_LINES = ['VEG', 'NONVEG']
USED_OILS = {
    'VEG': ['VEG1', 'VEG2'],
    'NONVEG': ['OIL1', 'OIL2', 'OIL3']
}


def main():
    st.set_page_config(page_title=TITLE)
    st.title(TITLE)

    st.markdown(BODY)
    st.markdown("Streamlit では、これを `st.table(demand)` で表形式で表示したり、 ")
    st.table(demand)
    st.markdown("`st.bar_chart(demand)` で棒グラフで表示したり、")
    st.bar_chart(demand)
    st.markdown("`st.area_chart(demand)` で面グラフで表示したりできます。")
    st.area_chart(demand)
    st.markdown("また、セレクタを使用して、表示項目を操作することもできます（「表示する商品」を切り替えてみてください）。")
    selected = st.selectbox("表示する商品", demand.columns)
    st.area_chart(demand[selected])

    st.markdown("他にも[様々なグラフ](https://docs.streamlit.io/en/stable/api.html)が用意されています。")
    st.markdown("最も素晴らしいのは、上記の（操作可能なウィジェットを含む）UI を生み出すソースコードが、"
                "pandas の `DataFrame` 形式の `demand` をそのまま使い、全て 1-2 行で表現できてしまうことです。"
                "**つまり、Python を使ったことがある人であれば、まるで print 文を扱うような手軽さで、"
                "このように見栄えの良いダッシュボードを作成できてしまうのです。**")

    st.markdown("# 生産計画立案ツールの例")
    st.markdown("前節では、Streamlit のごく一部の機能を紹介しました。"
                "しかし、ダッシュボード機能だけなら、BI ツールで十分であり、Streamlit の良さが伝わらないかと思います。"
                "そこで、以降では、上記の機能を利用して、簡単な生産計画ツールを作ってみたいと思います。")
    st.markdown("今回は[こちらの Qiita の記事](https://qiita.com/ytakashina/items/0d2a01c66230e0dc6fe9)"
                "に掲載されている問題設定をそのまま使用します。食品の生産計画を扱ったものなのですが、"
                "簡単にまとめると「原料をなるべく安く買って、加工して販売する」という問題です（詳細が気になる方は元記事へどうぞ！）。")
    st.markdown("1 月から 6 月にかけて 5 つの原料が購入でき、原料の単価は以下のように与えられています。")
    st.table(BUY_UC.T)
    st.markdown("この単価を元に、一定の制約の下で利益を最大化するように最適化を行います。"
                "販売単価は、元記事では 150 で固定されていますが、今回は以下のスライダーで指定できるようにします。")
    sell_uc = st.slider("販売単価", min_value=0, max_value=300, value=150)
    st.markdown("販売単価を変化させながら、**以下のボタンで最適化を走らせる**と、"
                "「販売単価が安すぎると生産を行わない」というような結果が出てきます。"
                "このように、**ダッシュボード上で前提データを変化させながら、"
                "同じ画面で結果を確認できる**のが便利なところです。")

    if st.button("最適化実行"):
        objective_value, buy_value, use_value, produce_value, closing_stock_value = run_optimization(sell_uc=sell_uc)
        st.markdown(f"利益: {objective_value}")
        st.markdown("### 食品の生産量")
        st.bar_chart(produce_value)
        st.markdown("### 原料の月末在庫")
        st.bar_chart(closing_stock_value)
        st.markdown("### 原料の購入量")
        st.bar_chart(buy_value)

    st.markdown(BOTTOM)


@st.cache
def run_optimization(sell_uc=150):
    # 集合の定義

    # パラメータの設定
    stock_init = 500
    stock_final_lb = 500
    stock_uc = 5
    stock_ub = 1000
    prod_ub = {'VEG': 200, 'NONVEG': 250}
    hardness_lb = 3
    hardness_ub = 6
    hardness = {'VEG1': 8.8, 'VEG2': 6.1, 'OIL1': 2.0, 'OIL2': 4.2, 'OIL3': 5.0}
    buy_uc = {
        'VEG1': {1: 110, 2: 130, 3: 110, 4: 120, 5: 100, 6: 90},
        'VEG2': {1: 120, 2: 130, 3: 140, 4: 110, 5: 120, 6: 100},
        'OIL1': {1: 130, 2: 110, 3: 130, 4: 120, 5: 150, 6: 140},
        'OIL2': {1: 110, 2: 90, 3: 100, 4: 120, 5: 110, 6: 80},
        'OIL3': {1: 115, 2: 115, 3: 95, 4: 125, 5: 105, 6: 135}
    }

    # 変数の定義
    buy = LpVariable.dicts("buy", (OILS, TIME_IDX), lowBound=0)
    use = LpVariable.dicts("use", (OILS, TIME_IDX), lowBound=0)
    produce = LpVariable.dicts("produce", TIME_IDX, lowBound=0)
    opening_stock = LpVariable.dicts("opening_stock", (OILS, TIME_IDX), lowBound=0, upBound=stock_ub)
    closing_stock = LpVariable.dicts("closing_stock", (OILS, TIME_IDX), lowBound=0, upBound=stock_ub)

    # 目的関数の計算
    total_sales = lpSum(produce[t] * sell_uc for t in TIME_IDX)
    total_buy_cost = lpSum(buy[oil][t] * buy_uc[oil][t] for t in TIME_IDX for oil in OILS)
    total_stock_cost = lpSum(closing_stock[oil][t] * stock_uc for t in TIME_IDX for oil in OILS)
    total_cost = total_buy_cost + total_stock_cost
    total_profit = total_sales - total_cost

    # モデルの定義と目的関数の設定
    model = LpProblem("Food manufacture 1", LpMaximize)
    model += total_profit

    # 制約式
    # 初期在庫、最終在庫
    for oil in OILS:
        model += opening_stock[oil][TIME_IDX[0]] == stock_init
        model += closing_stock[oil][TIME_IDX[-1]] >= stock_final_lb

    # 各月に関して
    for t in TIME_IDX:
        # 在庫バランス
        for oil in OILS:
            if t != TIME_IDX[0]:
                model += opening_stock[oil][t] == closing_stock[oil][t - 1]
            model += closing_stock[oil][t] == opening_stock[oil][t] + buy[oil][t] - use[oil][t]

        # 販売量バランス
        model += produce[t] == lpSum(use[oil][t] for oil in OILS)

        # 硬度
        total_hardness = lpSum(hardness[oil] * use[oil][t] for oil in OILS)
        model += total_hardness <= hardness_ub * produce[t]
        model += total_hardness >= hardness_lb * produce[t]

        # 精製量上限
        for line in REF_LINES:
            total_prod_amount = lpSum(use[oil][t] for oil in USED_OILS[line])
            model += total_prod_amount <= prod_ub[line]

    model.solve()
    objective_value = model.objective.value()
    buy_value = pd.DataFrame(buy, index=TIME_IDX, columns=OILS).applymap(lambda x: x.value())
    use_value = pd.DataFrame(use, index=TIME_IDX, columns=OILS).applymap(lambda x: x.value())
    produce_value = pd.Series(produce, index=TIME_IDX, name="Value").apply(lambda x: x.value())
    closing_stock_value = pd.DataFrame(closing_stock, index=TIME_IDX, columns=OILS).applymap(lambda x: x.value())
    return objective_value, buy_value, use_value, produce_value, closing_stock_value


if __name__ == "__main__":
    main()
