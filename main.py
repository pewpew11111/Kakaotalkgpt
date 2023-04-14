import PyautoPywin as winAuto
import openaiAPI as turbo
import os

import openai

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

window_name = '' # 창 이름 정확히 입력
my_name = '' # 자신의 카카오톡 이름명
language = 'korean' # result 언어 설정

promptText = "this is ongoiong dialgue of chat between two people. provice a next sentance of ", my_name,"'s perspective in ",language,", also exclude [name], [time], from result"

if __name__ == '__main__':
    
    cText = winAuto.CtrlAC(window_name) # ctrl + A, ctrl + C ( 채팅창 내용 가져오기 )
    print("복사된 내용 : \n" + cText)	# 내용 확인
    
    gText = turbo.chat_generate_text(prompt= cText + str(promptText), model='gpt-3.5-turbo', system_prompt='You are a AI that texts like actual person.', temperature=0.4, max_tokens=128, n=1, stop=None, presence_penalty=0.1, frequency_penalty=0.1) # gpt-3.5-turbo
    
    print(gText) # gpt-3.5-turbo 결과 확인
    
    if input('전송하시겠습니까? (y/n)') == 'y':
        print(winAuto.sendText(window_name,gText)) # 텍스트 전송
        print(str(gText) + " 전송완료")
    else:
        print('취소되었습니다.')
        exit()
    
    
    