## 日本語
### data_processor.py 
入力: 人が写った(街路空間の)画像   
出力: トリミングされた人の顔とそれに対応する人の特徴(年齢、性別、感情など)がcsv形式で出力されます。  

FaceAPIを使っているので、キーは各自で取得してください。
取得したキーは"key.txt"をdata_processor.py と同じディレクトリに作成して、その1行目に入力してください。
KEY = "????" の????を書き換える形でも構いません。   

直下にimgフォルダを作成して、実行をすると、outputフォルダーに顔画像を出力します。

## English
### data_processor.py  
Input: Images with pedestrians taken in street spaces  
Output: Cropped human face and corresponding human attributes (age, gender, emotion, etc.) in csv format.  

Since this tool is using the FaceAPI, please obtain the key by yourself.   
Create a file "key.txt" in the same directory as "data_processor.py" and enter the key in the first line of the file.   
You can also rewrite ???? in KEY = "????".  

