#!/bin/bash

file_name_list={{params.file_name_list}}

project_id={{params.project_id}}
bucket={{params.bucket}}
folder_name={{params.folder_name}}
for file_name in ${file_name_list[@]}; do

    # iconv: utf8へ文字コード変換
    # tr: ヌル文字削除
    # cut: 全てデータが空のカラムを削除
    gsutil cp "gs://${project_id}-${bucket}/${folder_name}/${file_name}.csv" /tmp/${file_name}.csv
    iconv -c -f CP932 -t utf8 /tmp/${file_name}.csv | tr -d '\000' > /tmp/${file_name}_fix.csv
    gsutil cp /tmp/${file_name}_fix.csv "gs://${project_id}-${bucket}/${folder_name}/${file_name}.csv"
done
