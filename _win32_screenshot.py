import ctypes
from ctypes import wintypes
import win32gui
import win32ui
import win32con
from PIL import Image
import os

# Find SafeShrink window
hwnd = win32gui.FindWindow(None, "SafeShrink - 文档工具箱")
print(f'hwnd = {hwnd}')

if not hwnd:
    # Try partial match
    win32gui.EnumWindows(lambda h, results: results.append(h) if 'SafeShrink' in win32gui.GetWindowText(h) else None, [])
    print('Searching...')
    
print(f'Final hwnd = {hwnd}')

if hwnd:
    # Get window rect
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    print(f'Window: {width}x{height} at ({left},{top})')
    
    # Create DC
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    # Create bitmap
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    
    # PrintWindow
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    print(f'PrintWindow result = {result}')
    
    # Save
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    img.save(r'C:\Users\26112\Desktop\SafeShrink\_ss_arrows.png')
    print('Saved _ss_arrows.png')
    
    # Cleanup
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
