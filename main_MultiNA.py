import FreeSimpleGUI as sg
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import itertools

sg.theme('LightBlue3')

layout_left = [
                [sg.Text('近い(bp)/(nt)値が無い試料を表示', pad = (15, 5))],
                [sg.Table(values = [ 'None' ], headings=[ 'ウェル名', 'サイズ(bp)/(nt)' ], \
                    col_widths = [ 10, 24 ], justification = 'left', auto_size_columns = False, \
                    text_color = '#000000',background_color = '#cccccc',\
                    alternating_row_color = '#ffffff', header_text_color = '#FFFFFF', \
                    header_background_color = '#080e47', num_rows = 20, key = '-TABLE_ALONE-', \
                    pad = (15, 5))]
              ]


layout_right = [
                [sg.Text('(bp)/(nt)値が近いと思われる試料を表示', pad = (5,5))],
                [sg.Table(values = [ 'None' ],headings = [ 'ウェル名' ], col_widths = [ 38 ], \
                    justification = 'left', text_color = '#000000', background_color = '#cccccc', \
                    alternating_row_color = '#ffffff', header_text_color = '#FFFFFF',\
                    header_background_color = '#080e47', auto_size_columns = False, num_rows = 8, \
                    key = '-TABLE_COMB_LIST-', enable_events = True, \
                    select_mode = sg.TABLE_SELECT_MODE_BROWSE, pad = (5,5))], \
                [sg.Table(values = [ 'None' ], headings = [ 'ウェル名', 'サイズ(bp)/(nt)' ], \
                    col_widths = [ 10,28 ],justification='left',text_color='#000000', \
                    background_color = '#cccccc', alternating_row_color='#ffffff', \
                    header_text_color = '#FFFFFF', header_background_color = '#080e47', \
                    auto_size_columns = False, num_rows = 10, key = '-TABLE_COMB_EVENT-', \
                    enable_events = True, pad = (5,5))]
               ]


# レイアウトの定義
layout = [
          [sg.Frame( 'Input' , [
            [sg.Text('csvデータのファイルを選んでください', pad = (15, 5)), \
                sg.Button('選 択', key = '-CSV_CHOOSE-')],
            [sg.Text('選択されたファイル', pad = (15, 5)), \
                sg.Input(key = '-AMOUNT-', size = (61,1))],
            [sg.Text("しきい値を入力してください（1〜30の整数を入力） :", pad = (15, 0)), \
                sg.InputText(default_text="20", key = "-INPUT-", size = (5,1), enable_events = True), \
                sg.Button("OK", key = '-LIMIT_SET-', disabled = True)],
            [sg.Button('Input  Data', key = '-SUBMIT_EXE-', disabled = True, pad = (15, 15))]
            ], font = (None, 18))
          ],
          [sg.Frame( 'Preview' , [
            [sg.Column(layout_left, vertical_alignment = 'top', expand_y = True),\
                sg.Column(layout_right, vertical_alignment = 'top', expand_y = True)]
            ], font = (None, 18))
          ],
          [sg.Push(),sg.Button('リセット', key='-SUBMIT_RESET-', disabled = True, pad = (15, 15)), \
                sg.Button('終 了',key='-SUBMIT_EXIT-', pad = (15, 15))]
         ]


# ウインドウの作成
window = sg.Window('電気泳動結果の判定補助アプリ  ver.1.1', layout, size = (1100, 850), \
    font = (None, 15))

# イベントループ
while True:
    event, values = window.read()

    if event == '-CSV_CHOOSE-':
        # ファイル選択ダイアログを表示してファイルパスを取得
        fpath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if fpath:
            # print(f"選択されたファイル: {fpath}")
            
            # CSVファイルを読み込み（実際のファイル形式に合わせて引数を調整）
            df00 = pd.read_csv(fpath, header=0, encoding = 'shift_jis') 
            window['-AMOUNT-'].update(f'{fpath}')
            window['-LIMIT_SET-'].update(disabled = False)
        else:
            sg.popup("ファイル選択がキャンセルされました。", font = (None, 14), title="Caution!")

 
    if event == '-INPUT-':
        input_value = values['-INPUT-']
        try:
			# 入力値を整数に変換
            number = int(input_value)
            
            if 1 <= number <= 30:
                window['-LIMIT_SET-'].update(disabled = False)
            else:
                sg.popup_error("無効な入力です。1〜30の整数のみを入力してください。", font = (None, 14), \
                    title = "Caution!")
                window['-SUBMIT_EXE-'].update(disabled = True)
                window['-LIMIT_SET-'].update(disabled = True)
		
        except ValueError:
            # 変換できなかった場合はエラーメッセージを表示
            sg.popup_error("無効な入力です。1〜999の整数のみを入力してください。", font = (None, 14), \
                title = "Caution!")
            window['-SUBMIT_EXE-'].update(disabled = True)
            window['-LIMIT_SET-'].update(disabled = True)


    if event == '-LIMIT_SET-':
        window['-SUBMIT_EXE-'].update(disabled = False)


    if event == '-SUBMIT_EXE-':
        window['-CSV_CHOOSE-'].update(disabled = True)
        # サンプル名ごとにデータをフィルタリング
        # df01=ラダー削除、df02=LMとUM削除、df03=bp値をウェル名ごとにまとめる
        df01 = df00.loc[ ~df00['ウェル名'].str.contains('X') , ['ウェル名','サイズ(bp)/(nt)']]
        df02 = df01[df01['サイズ(bp)/(nt)'] != '-']
        df03 = df02.groupby('ウェル名')['サイズ(bp)/(nt)'].agg(list).reset_index()
        
        
        # 2列目のリスト内要素をフィルタリング（1500以下だけ残す）
        def filter_list(x):
            # xがリストであり、かつ中身がある場合のみフィルタリング
            if isinstance(x, list):
                filtered = []
                for i in x:
                    try:
                        # 文字列であっても数値に変換を試みる
                        val = float(i) 
                        if val <= 1500:
                             filtered.append(i) # 元の形式(str等)を維持したいならi、数値にしたいならval
                    except (ValueError, TypeError):
                        # 数値に変換できない文字列（例: "abc"）などは無視する
                        continue
                return filtered
            return []
        df03.iloc[:, 1] = df03.iloc[:, 1].apply(filter_list)   # iloc[:, 1print(df03)] で2列目を指定
        
        # リストが空になった行を削除する
        # map(len) で要素数が0より大きい行だけを残す
        df03 = df03[df03.iloc[:, 1].map(len) > 0].reset_index(drop=True)


        # bp値のみのデータフレームの作成
        df_3d = df03.loc[ : , [ 'サイズ(bp)/(nt)']]
        # データフレームをリストに変換
        list_3d = df_3d.to_numpy()
        
        # list_3dを二次元配列に変換
        list_2d = []
        for i in range(len(list_3d)):
            for j in range(len(list_3d[i])):
                mid_list = []
                for k in range(len(list_3d[i][j])):
                    mid_list.append(list_3d[i][j][k])
            list_2d.append(mid_list)
        
        # list_2dをint型に変換
        list_2dint = [[int(x) for x in y] for y in list_2d]
        
        """
        # list_2dintから1501以上の要素を削除
        new_data = [[x for x in sub if x <= 1500] for sub in list_2dint]
        list_2dint_f = [sub for sub in new_data if sub]
        
        print(list_2dint)
        print(list_2dint_f)
        """


        # bp値の差が指定のしきい値内に収まる組み合わせを探す関数
        def extract_comb(data):

            valid_combinations = []
            comb_list = []
            diff_limit = int(values['-INPUT-'])
   
            # 行のインデックスの組み合わせを生成
            row_indices = range(len(data))
            for i, j in itertools.combinations(row_indices, 2):
                row1 = data[i]
                row2 = data[j]
        
                # 列数が同じか確認
                if len(row1) != len(row2):
                    continue
            
                # 要素の差がdiff_limit以下か確認
                else:
                    for k in range(len(row1)):
                
                        all_within_limit = []
                
                        all_within_limit = all(abs(x - y) <= diff_limit for x, y in zip(row1, row2))
                                
                        if all_within_limit:
                            valid_combinations.append((df03.iat[i,0], df03.iat[j,0]))
                    
                        else:
                            break
            
            return valid_combinations
        
        # 関数の実行
        valid_comb = extract_comb(list_2dint)


        # extract_comb()で出来たリストのうち重複した要素を削除する関数
        seen = []
        comb_list = []
        def get_unique_list(seq):
            comb_list = [x for x in seq if x not in seen and not seen.append(x)]

            return comb_list

        # 関数の実行
        result = get_unique_list(valid_comb)


        # 組み合わせのリストの重複を纏める関数
        def merge_tuples_with_common_strings(data):
            # 各タプルを集合に変換してリスト化
            sets_list = [set(tup) for tup in data]
    
            merged = True
            while merged:
                merged = False
                temp_list = []
                while sets_list:
                    # リストから最初の集合を取り出す
                    current_set = sets_list.pop(0)
                    # 残りの集合と共通要素がないか確認
                    for other_set in sets_list:
                        # 共通要素がある場合、それらをマージ (和集合)
                        if current_set.intersection(other_set):
                            current_set.update(other_set)
                            # マージされた集合は元のリストから削除
                            sets_list.remove(other_set)
                            merged = True
                            break
                    # 共通要素とマージした後の集合を一時リストに追加
                    temp_list.append(current_set)
                # 次のイテレーションのためにリストを更新
                sets_list = temp_list
        
            # 結果をタプルのリストに戻して返す
            return [tuple(sorted(s)) for s in sets_list]

        # 関数の実行
        merged_tuple = merge_tuples_with_common_strings(result)


        # タプルとリストの二次元配列をリストの二次元配列に変換
        merged_list = [list(tpl) for tpl in merged_tuple]
        


        # 組合せTable表示用に各サブリストの要素を結合
        mmerged_list = [",".join(sublist) for sublist in merged_list]
        duplicated_list = [[item] for item in mmerged_list]
                
        window['-TABLE_COMB_LIST-'].update(values = duplicated_list)
        

        # 一覧表示用にデータフレームdf03をリストに変換
        table_all_list = df03.to_numpy().tolist()
        
        
        # ウェル名のみのデータフレームの作成
        df_well = df03.loc[ : , [ 'ウェル名']]
        # データフレームをリストに変換
        list_well = df_well.to_numpy().tolist()
        # 二次元リストから一次元リストへ
        list_well_1d = sum(list_well, [])
        merged_list_1d = sum(merged_list, [])

        # 重複しないものを抽出
        alone_list_1d = [i for i in list_well_1d if i not in merged_list_1d]


        def make_table_list(list_rows,list_all):
            # 一次元リストの各要素に対して処理
            table_list_rows = []
            for element in list_rows:
                # 二次元リストの各行に対して処理
                for row in list_all:
                    # 要素がその行に含まれているかチェック
                    if element in row:
                        # 含まれている行を結果リストに追加
                        table_list_rows.append(row)
                        # 同じ行に複数の要素がある場合でも重複して追加されないようにする
                        break # 該当する行が見つかったら、次の要素のチェックに移る
            return table_list_rows

        alone_list_rows = make_table_list(alone_list_1d, table_all_list)

        window['-TABLE_ALONE-'].update(values = alone_list_rows)
        
        window['-SUBMIT_RESET-'].update(disabled=False)
        
        window['-TABLE_COMB_EVENT-'].update(values = [ 'None' ])
        
                
    if event == '-TABLE_COMB_LIST-':
        selected_rows_indices = values['-TABLE_COMB_LIST-']

        if selected_rows_indices:
            selected_data = [merged_list[i] for i in selected_rows_indices]
            selected_data_1d = sum(selected_data, [])

            combi_list_rows = make_table_list(selected_data_1d, table_all_list)                        
        
            window['-TABLE_COMB_EVENT-'].update(values = combi_list_rows)
        

    
    if event == '-SUBMIT_RESET-':
        window['-TABLE_COMB_EVENT-'].update(values = [ 'None' ])
        window['-TABLE_ALONE-'].update(values = [ 'None' ])
        window['-TABLE_COMB_LIST-'].update(values = [ 'None' ])
        window['-INPUT-'].update(f'{20}')
        window['-AMOUNT-'].update(f'{''}')
        window['-LIMIT_SET-'].update(disabled = True)
        window['-SUBMIT_EXE-'].update(disabled = True)
        window['-SUBMIT_RESET-'].update(disabled = True)
        window['-CSV_CHOOSE-'].update(disabled = False)

    
    if event == '-SUBMIT_EXIT-':
        break
    
    if event == sg.WIN_CLOSED:
        break
    
window.close()