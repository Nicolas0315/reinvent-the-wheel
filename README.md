# reinvent-the-wheel

車輪の再発明、二重の意味で。

1. **Myers O(ND) diff** — Myers (1986) の論文アルゴリズムを difflib 不使用でフル再実装(`rewheel/__init__.py`)。unified diff 出力付き。
2. **Python wheel** — その成果物を setuptools / build / pip 一切なしで PEP 427 準拠の `.whl` に手組みパッケージング(`build_wheel.py`)。METADATA / WHEEL / RECORD(sha256)も手書き生成。

## 検証

```
python test_rewheel.py   # fuzz 2,008ケース: 復元オラクル + DP最小性オラクル
python build_wheel.py    # rewheel-0.1.0-py3-none-any.whl を生成
py -3 -m pip install --target ./_pip_check rewheel-0.1.0-py3-none-any.whl
```

- 復元: 編集スクリプト適用で a→b が完全再現
- 最小性: 編集距離 = n+m−2·LCS (独立実装のDPと全件一致)
- 本家 pip 26.1.2 が手組み wheel を正規品として受理・インストール成功
- 論文の例 `abcabba`→`cbabac` で D=5 (原論文と一致)
