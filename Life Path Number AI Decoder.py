import gradio as gr
import openai

# 設定 OpenAI API 金鑰
openai.api_key = "your_openai_api_key_here"  # 替換為您的 API 金鑰

# 星座對應數字
ZODIAC_MAP = {
    "牡羊座": 1, "金牛座": 2, "雙子座": 3, "巨蟹座": 4,
    "獅子座": 5, "處女座": 6, "天秤座": 7, "天蠍座": 8,
    "射手座": 9, "摩羯座": [10, 1], "水瓶座": [11, 2], "雙魚座": [12, 3]
}

# 血型對應數字
BLOOD_TYPE_MAP = {"A": 1, "B": 2, "AB": 3, "O": 6}


def reduce_to_single_digit(number):
    """
    將數字化約至個位數，返回最終結果
    """
    while number >= 10:
        number = sum(int(digit) for digit in str(number))
    return number


def calculate_numbers(name, year, month, day, zodiac, blood_type):
    """
    計算主命數與天賦數，並生成回應
    """
    try:
        # 確保年份、月份和日期為整數
        year = int(year)
        month = int(month)
        day = int(day)

        # 計算主命數
        digits = [int(d) for d in f"{year}{month:02d}{day:02d}"]
        main_number = reduce_to_single_digit(sum(digits))

        # 呼叫 OpenAI API，生成主命數特質分析
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是生命靈數的專家，請為主命數分析特質、性格、未來方向、事業、財運、人際關係、戀愛。"},
                    {"role": "user", "content": f"請分析主命數為 {main_number} 的特質。"}
                ]
            )
            analysis = response['choices'][0]['message']['content']
        except openai.error.AuthenticationError:
            analysis = "API 測試失敗：金鑰驗證失敗，請檢查您的 API 金鑰是否正確。"
            print("API 測試失敗：金鑰驗證失敗，請檢查您的 API 金鑰是否正確。")
        except openai.error.RateLimitError:
            analysis = "API 測試失敗：達到使用限制，請稍後重試或升級計劃。"
            print("API 測試失敗：達到使用限制，請稍後重試或升級計劃。")
        except openai.error.OpenAIError as e:
            if "exceeded your current quota" in str(e):
                analysis = "API 測試失敗：超出當前配額。請檢查您的帳戶使用量，或升級至付費計劃以繼續使用。"
                print("API 測試失敗：超出當前配額。請檢查您的帳戶使用量，或升級至付費計劃以繼續使用。")
            else:
                analysis = f"API 測試失敗，發生錯誤：{e}"
                print(f"API 測試失敗，發生錯誤：{e}")
        except Exception as e:
            analysis = f"API 測試失敗，發生未知錯誤：{e}"
            print(f"API 測試失敗，發生未知錯誤：{e}")

        return (
            f"姓名：{name}",
            f"主命數：{main_number}",
            analysis
        )
    except ValueError as e:
        return "Error", "Error", f"輸入的年份、月份或日期有誤：{str(e)}"
    except Exception as e:
        return "Error", "Error", f"發生錯誤：{str(e)}"


# 使用 Gradio 構建網頁應用介面
with gr.Blocks(
        css=".gradio-container {background-image: url('https://www.pixelstalk.net/wp-content/uploads/2016/08/Cool-green-wallpaper-hd.jpg'); font-family: Arial;}") as app:
    with gr.Row():
        gr.Markdown(
            """
            <h1 style="text-align: center; font-weight: bold; color: black;">生命靈數分析工具</h1>
            <p style="text-align: center; font-size: 20px;">
            生命靈數為來自古希臘的占數術，約西元兩千五百年前古希臘 數學家畢達格拉斯所倡導，
            再傳達給當時的知識份子研究，他們認為數字是宇宙的真理；畢達哥拉斯利用數學的公式與統計學發明
            「原數力量開運術」，發現每個人都有一組生命數字隱藏在身體裡，每個數字都蘊含著為人不知的命運密碼，
            每個數字從１到９，都有它形而上的特殊意義；從單純的數字，瞭解自己和他人、使人與人之間互動更為和諧、
            天生性格、未來方向、戀愛、財運等，答案都能從簡單的數字得知。
            </p>
            """
        )

    with gr.Row():
        with gr.Column(scale=1):
            name = gr.Textbox(label="姓名", placeholder="請輸入您的姓名")
            year = gr.Dropdown(label="西元出生年", choices=[str(y) for y in range(1900, 2025)], value="1982")
            month = gr.Dropdown(label="出生月份", choices=[f"{m:02d}" for m in range(1, 13)], value="05")
            day = gr.Dropdown(label="出生日期", choices=[f"{d:02d}" for d in range(1, 32)], value="16")
            zodiac = gr.Dropdown(
                label="星座",
                choices=["牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座",
                         "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"],
            )
            blood_type = gr.Dropdown(
                label="血型",
                choices=["A", "B", "AB", "O"],
            )
            calculate_button = gr.Button("計算")

        with gr.Column(scale=2):
            output_name = gr.Textbox(label="姓名")
            output_main_number = gr.Textbox(label="主命數")
            output_analysis = gr.Textbox(label="主命數特質分析", lines=10)

        # 設定按鈕的操作
        calculate_button.click(
            fn=calculate_numbers,
            inputs=[name, year, month, day, zodiac, blood_type],
            outputs=[output_name, output_main_number, output_analysis],
        )

# 啟動應用程式
app.launch()
