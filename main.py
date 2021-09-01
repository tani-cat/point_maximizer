import csv
import os
from collections import deque


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, 'goods_source.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'result.csv')

FILE_ENCODE = 'shift_jis'
INPUT_COLS = ('id', 'goods_name', 'price')


def import_csv():
    """入力データの読み込み

    """
    try:
        data_l = list()
        with open(INPUT_PATH, mode='r', encoding=FILE_ENCODE, newline='') as csvf:
            reader = csv.DictReader(csvf)
            for dic in reader:
                dic['id'] = int(dic['id'])
                dic['price'] = int(dic['price'])
                data_l.append(dic)

        for col in INPUT_COLS:
            if col not in data_l[0]:
                raise IndexError(col)

        return data_l

    except FileNotFoundError:
        print('goods_source.csvがありません')
        return list()
    except IndexError as e:
        print('列が不足しています: ' + str(e))
        return list()


def func(init, old_que, threshold=50):
    keep = dict()
    new_que = deque(list())
    while old_que:
        last = old_que.pop()
        if init['mod'] + last['mod'] >= threshold:
            if keep:
                new_que.appendleft(keep)
            keep = last
        else:
            new_que.appendleft(last)
            break

    return init, keep, old_que, new_que


def calculate(data_l):
    """アルゴリズム
    1. 50未満の中でペアにできるものを探す
    1-1. queの末端でペアを作れる場合、左端を固定し和が50以上で最小になるように右を選んでペアにする
    1-2. queの末端でペアを作れない場合、末端2つを取り出した上で3個以上の組み合わせで消化する
    1-2-1. 右末端で和が50以上なら右から左に探索して和が50以上になる最小値を得る->組にして除外
    1-2-2. 右末端でも和が50にならないなら右末端をして1-2に戻る
    -> 全部を消化しても50にならないならそのまま全部を足してしまう
    2. 1と同じことを全体かつ閾値150で行う
    """
    # 50未満のものだけ和を取る処理に入れる
    under_que = list()
    over_que = list()
    for i in range(len(data_l)):
        _mod = data_l[i]['price'] % 100
        data_l[i]['set'] = 0
        dic = {
            'id': [i],
            'mod': _mod,
        }
        if _mod < 50:
            under_que.append(dic)
        else:
            over_que.append(dic)

    under_que.sort(key=lambda x: x['mod'])
    under_que = deque(under_que)
    while under_que:
        init = under_que.popleft()
        while under_que:
            init, keep, under_que, last_que = func(init, under_que)
            # この時点でlast_queは要素1以上
            if not keep:
                keep = last_que.pop()

            init = {
                'id': init['id'] + keep['id'],
                'mod': init['mod'] + keep['mod'],
            }
            if last_que:
                over_que.append(init)
                under_que.extend(last_que)
                break
        else:
            over_que.append(init)
            break

    # 50以上の項目のうち、合計が150以上になる項目同士を足す
    # (これにより購入回数を最小にする)
    # final_que: 最終的な組み合わせ
    over_que = deque(sorted(over_que, key=lambda x: x['mod']))
    final_que = list()
    while over_que:
        init = over_que.popleft()
        init, keep, over_que, last_que = func(init, over_que, 150)
        if keep:
            init = {
                'id': init['id'] + keep['id'],
                'mod': (init['mod'] + keep['mod']) % 100,
            }
            over_que.appendleft(init)
        else:
            final_que.append(init)
        over_que.extend(last_que)


    sum_p = 0
    # 計算結果の出力
    for cnt, que in enumerate(final_que):
        point = 0
        for id in que['id']:
            data_l[id]['set'] = cnt + 1
            point += data_l[id]['price']

        print(f'set{cnt + 1} {round(point / 100)} P')
        sum_p += round(point / 100)

    print(f'total: {sum_p} P')
    return data_l


def main():
    # ファイルの読み込み
    data_l = import_csv()
    if not data_l:
        print('処理を中止します')
        return False

    # 計算処理
    data_l = calculate(data_l)

    # 結果をファイルに出力
    data_l.sort(key=lambda x: (x['set'], x['id']))
    with open(OUTPUT_PATH, mode='w', encoding=FILE_ENCODE, newline='') as csvf:
        writer = csv.DictWriter(csvf, data_l[0].keys())
        writer.writeheader()
        writer.writerows(data_l)
    print('Done')


if __name__ == '__main__':
    main()
