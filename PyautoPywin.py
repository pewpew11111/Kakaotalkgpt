import time, win32con, win32api, win32gui, ctypes
from pywinauto import clipboard

PBYTE256 = ctypes.c_ubyte * 256
_user32 = ctypes.WinDLL("user32")
GetKeyboardState = _user32.GetKeyboardState
SetKeyboardState = _user32.SetKeyboardState
PostMessage = win32api.PostMessage
SendMessage = win32gui.SendMessage
FindWindow = win32gui.FindWindow
IsWindow = win32gui.IsWindow
GetCurrentThreadId = win32api.GetCurrentThreadId
GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
AttachThreadInput = _user32.AttachThreadInput

MapVirtualKeyA = _user32.MapVirtualKeyA
MapVirtualKeyW = _user32.MapVirtualKeyW

MakeLong = win32api.MAKELONG
w = win32con

# 조합키 쓰기 위해
def PostKeyEx(hwnd, key, shift, specialkey): # hwnd - 핸들, key - 키코드, shift - 조합키, specialkey - 특수키 여부
    if IsWindow(hwnd): # 윈도우가 살아있을 경우

        ThreadId = GetWindowThreadProcessId(hwnd, None) # 쓰레드 아이디

        lparam = MakeLong(0, MapVirtualKeyA(key, 0)) # lParam 생성
        msg_down = w.WM_KEYDOWN # 키다운 메시지
        msg_up = w.WM_KEYUP # 키업 메시지

        if specialkey: # 특수키일 경우
            lparam = lparam | 0x1000000 # extended key

        if len(shift) > 0: # 조합키가 있을 경우
            pKeyBuffers = PBYTE256() # 조합키를 누르기 위한 버퍼
            pKeyBuffers_old = PBYTE256() # 조합키를 누르기 전의 버퍼

            SendMessage(hwnd, w.WM_ACTIVATE, w.WA_ACTIVE, 0) # 활성화
            AttachThreadInput(GetCurrentThreadId(), ThreadId, True) # 쓰레드 연결
            GetKeyboardState(ctypes.byref(pKeyBuffers_old)) # 조합키를 누르기 전의 버퍼를 가져옴

            for modkey in shift: # 조합키를 누르기 위한 버퍼를 생성
                if modkey == w.VK_MENU: # alt
                    lparam = lparam | 0x20000000 # context code : 1 (right) 0 (left)    # alt 누르기
                    msg_down = w.WM_SYSKEYDOWN # alt 누르기
                    msg_up = w.WM_SYSKEYUP # alt 떼기
                pKeyBuffers[modkey] |= 128 # 조합키를 누르기 위한 버퍼 생성

            SetKeyboardState(ctypes.byref(pKeyBuffers)) # 조합키를 누르기 위한 버퍼를 적용
            time.sleep(0.01)
            PostMessage(hwnd, msg_down, key, lparam) # 키다운 메시지 전송 ( 조합키 + 키 ) 
            time.sleep(0.01)
            PostMessage(hwnd, msg_up, key, lparam | 0xC0000000) # 키업 메시지 전송 ( 조합키 + 키 )
            time.sleep(0.01)
            SetKeyboardState(ctypes.byref(pKeyBuffers_old)) # 조합키를 누르기 전의 버퍼를 적용
            time.sleep(0.01)
            AttachThreadInput(GetCurrentThreadId(), ThreadId, False) # 쓰레드 연결 해제

        else: # 조합키가 없을 경우
            SendMessage(hwnd, msg_down, key, lparam) # 키다운 메시지 전송 ( 키 )
            SendMessage(hwnd, msg_up, key, lparam | 0xC0000000) # 키업 메시지 전송 ( 키 )

def CtrlAC(window_name): # ctrl + A, ctrl + C ( 채팅창 내용 가져오기 )
    # # 핸들 _ 채팅방
    hwndMain = win32gui.FindWindow( None, window_name) # 핸들 가져오기
    hwndListControl = win32gui.FindWindowEx(hwndMain, None, "EVA_VH_ListControl_Dblclk", None) # 핸들 가져오기

    # #조합키, 본문을 클립보드에 복사 ( ctl + A , C )
    PostKeyEx(hwndListControl, ord('A'), [w.VK_CONTROL], False) # ctrl + A
    time.sleep(1)
    PostKeyEx(hwndListControl, ord('C'), [w.VK_CONTROL], False) # ctrl + C
    ctext = clipboard.GetData() # 클립보드 내용 가져오기
    return ctext

def SendReturn(hwnd):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    
def sendText(window_name,Text):
    hwndMain = win32gui.FindWindow( None, window_name)
    hwndEdit = win32gui.FindWindowEx( hwndMain, None, "RichEdit50W", None)
    hwndListControl = win32gui.FindWindowEx( hwndMain, None, "EVA_VH_ListControl_Dblclk", None)

    Text = str(Text)
    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, Text)
    SendReturn(hwndEdit)
    
    