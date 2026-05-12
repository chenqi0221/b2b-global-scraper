"""Windows 11 毛玻璃效果模块

使用 Windows API (DWM) 实现真实的毛玻璃效果
支持：Acrylic (亚克力) 和 Mica (云母) 效果
"""

import ctypes
import ctypes.wintypes
from ctypes import windll, c_int, c_bool, POINTER, Structure, sizeof
from typing import Optional
import tkinter as tk


# Windows API 常量
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
DWMWA_MICA_EFFECT = 1029
DWMWA_SYSTEMBACKDROP_TYPE = 38

# 系统背景类型
DWMSBT_AUTO = 0
DWMSBT_NONE = 1
DWMSBT_MAINWINDOW = 2  # Mica
DWMSBT_TRANSIENTWINDOW = 3  # Acrylic
DWMSBT_TABBEDWINDOW = 4  # Tabbed


class OSVERSIONINFOEXW(Structure):
    """Windows 版本信息结构体"""
    _fields_ = [
        ("dwOSVersionInfoSize", ctypes.c_ulong),
        ("dwMajorVersion", ctypes.c_ulong),
        ("dwMinorVersion", ctypes.c_ulong),
        ("dwBuildNumber", ctypes.c_ulong),
        ("dwPlatformId", ctypes.c_ulong),
        ("szCSDVersion", ctypes.c_wchar * 128),
        ("wServicePackMajor", ctypes.c_ushort),
        ("wServicePackMinor", ctypes.c_ushort),
        ("wSuiteMask", ctypes.c_ushort),
        ("wProductType", ctypes.c_ubyte),
        ("wReserved", ctypes.c_ubyte),
    ]


class DWM_BLURBEHIND(Structure):
    """DWM 模糊效果结构体"""
    _fields_ = [
        ("dwFlags", ctypes.wintypes.DWORD),
        ("fEnable", c_bool),
        ("hRgnBlur", ctypes.wintypes.HRGN),
        ("fTransitionOnMaximized", c_bool),
    ]


class ACCENT_POLICY(Structure):
    """强调色策略结构体 (用于 Acrylic 效果)"""
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint),
    ]


class WINDOW_COMPOSITION_ATTRIBUTE_DATA(Structure):
    """窗口合成属性数据结构体"""
    _fields_ = [
        ("Attribute", ctypes.c_uint),
        ("Data", POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t),
    ]


# 强调色状态
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # Windows 10 1803+


class GlassmorphismEffect:
    """毛玻璃效果管理器"""
    
    def __init__(self):
        self.dwmapi = windll.dwmapi
        self.user32 = windll.user32
        self._is_windows_11 = self._check_windows_11()
    
    def _check_windows_11(self) -> bool:
        """检查是否为 Windows 11"""
        try:
            version = OSVERSIONINFOEXW()
            version.dwOSVersionInfoSize = sizeof(version)
            if hasattr(ctypes.windll.ntdll, 'RtlGetVersion'):
                ctypes.windll.ntdll.RtlGetVersion(ctypes.byref(version))
                # Windows 11 是 10.0.22000+
                is_win11 = (version.dwMajorVersion == 10 and 
                        version.dwMinorVersion == 0 and 
                        version.dwBuildNumber >= 22000)
                if is_win11:
                    print(f"检测到 Windows 11 (Build {version.dwBuildNumber})")
                else:
                    print(f"检测到 Windows {version.dwMajorVersion}.{version.dwMinorVersion} (Build {version.dwBuildNumber})")
                return is_win11
        except Exception as e:
            print(f"版本检测失败: {e}")
        return False
    
    def apply_mica_effect(self, hwnd: int, dark_mode: bool = True) -> bool:
        """
        应用 Mica (云母) 效果 - Windows 11 原生效果
        
        Args:
            hwnd: 窗口句柄
            dark_mode: 是否使用深色模式
            
        Returns:
            是否成功应用
        """
        if not self._is_windows_11:
            return False
        
        try:
            # 设置深色模式
            if dark_mode:
                self._set_window_attribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.c_int(1)
                )
            
            # 应用 Mica 效果
            self._set_window_attribute(
                hwnd, DWMWA_SYSTEMBACKDROP_TYPE, ctypes.c_int(DWMSBT_MAINWINDOW)
            )
            return True
        except Exception as e:
            print(f"应用 Mica 效果失败: {e}")
            return False
    
    def apply_acrylic_effect(self, hwnd: int, dark_mode: bool = True) -> bool:
        """
        应用 Acrylic (亚克力) 效果 - 半透明模糊
        
        Args:
            hwnd: 窗口句柄
            dark_mode: 是否使用深色模式
            
        Returns:
            是否成功应用
        """
        if not self._is_windows_11:
            return self._apply_legacy_acrylic(hwnd)
        
        try:
            # 设置深色模式
            if dark_mode:
                self._set_window_attribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.c_int(1)
                )
            
            # 应用 Acrylic 效果
            self._set_window_attribute(
                hwnd, DWMWA_SYSTEMBACKDROP_TYPE, ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
            )
            return True
        except Exception as e:
            print(f"应用 Acrylic 效果失败: {e}")
            return False
    
    def _apply_legacy_acrylic(self, hwnd: int) -> bool:
        """
        为 Windows 10 应用传统的 Acrylic 效果
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            是否成功应用
        """
        try:
            # 使用 SetWindowCompositionAttribute (undocumented API)
            SetWindowCompositionAttribute = self.user32.SetWindowCompositionAttribute
            SetWindowCompositionAttribute.argtypes = [
                ctypes.wintypes.HWND, POINTER(WINDOW_COMPOSITION_ATTRIBUTE_DATA)
            ]
            SetWindowCompositionAttribute.restype = ctypes.c_int
            
            accent = ACCENT_POLICY()
            accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
            accent.AccentFlags = 2  # 绘制左/上/右/下边框
            # 深色半透明背景色 (ARGB: 0xD0000000)
            accent.GradientColor = 0xD0000000
            accent.AnimationId = 0
            
            data = WINDOW_COMPOSITION_ATTRIBUTE_DATA()
            data.Attribute = 19  # WCA_ACCENT_POLICY
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = sizeof(accent)
            
            result = SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
            return result != 0
        except Exception as e:
            print(f"应用传统 Acrylic 效果失败: {e}")
            return False
    
    def _set_window_attribute(self, hwnd: int, attr: int, value: ctypes.c_int) -> bool:
        """设置窗口属性"""
        try:
            self.dwmapi.DwmSetWindowAttribute(
                ctypes.wintypes.HWND(hwnd),
                ctypes.wintypes.DWORD(attr),
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
            return True
        except Exception:
            return False
    
    def remove_effect(self, hwnd: int) -> bool:
        """
        移除毛玻璃效果
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            是否成功移除
        """
        try:
            self._set_window_attribute(
                hwnd, DWMWA_SYSTEMBACKDROP_TYPE, ctypes.c_int(DWMSBT_NONE)
            )
            return True
        except Exception:
            return False


# 全局效果实例
glass_effect = GlassmorphismEffect()


def _ensure_window_visible(window: tk.Tk) -> bool:
    """确保窗口已经显示并获取有效的 HWND"""
    try:
        window.update_idletasks()
        window.update()
        hwnd = window.winfo_id()
        return hwnd != 0
    except Exception:
        return False


def apply_mica_to_window(window: tk.Tk, dark_mode: bool = True) -> bool:
    """
    为 tkinter 窗口应用 Mica 效果
    
    Args:
        window: tkinter 窗口
        dark_mode: 是否使用深色模式
        
    Returns:
        是否成功应用
    """
    if not _ensure_window_visible(window):
        print("窗口未准备好，无法应用 Mica 效果")
        return False
    
    hwnd = window.winfo_id()
    result = glass_effect.apply_mica_effect(hwnd, dark_mode)
    if result:
        print("✓ Mica 毛玻璃效果已应用")
    else:
        print("✗ Mica 效果应用失败（可能不是 Windows 11）")
    return result


def apply_acrylic_to_window(window: tk.Tk, dark_mode: bool = True) -> bool:
    """
    为 tkinter 窗口应用 Acrylic 效果
    
    Args:
        window: tkinter 窗口
        dark_mode: 是否使用深色模式
        
    Returns:
        是否成功应用
    """
    if not _ensure_window_visible(window):
        print("窗口未准备好，无法应用 Acrylic 效果")
        return False
    
    hwnd = window.winfo_id()
    result = glass_effect.apply_acrylic_effect(hwnd, dark_mode)
    if result:
        print("✓ Acrylic 毛玻璃效果已应用")
    else:
        print("✗ Acrylic 效果应用失败")
    return result


def remove_glass_effect(window: tk.Tk) -> bool:
    """
    移除窗口的毛玻璃效果
    
    Args:
        window: tkinter 窗口
        
    Returns:
        是否成功移除
    """
    hwnd = window.winfo_id()
    return glass_effect.remove_effect(hwnd)


# 圆角窗口常量
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_DEFAULT = 0
DWMWCP_DONOTROUND = 1
DWMWCP_ROUND = 2
DWMWCP_ROUNDSMALL = 3


def apply_rounded_corners(window: tk.Tk, radius: int = 12) -> bool:
    """
    为窗口应用圆角效果 (Windows 11)
    
    Args:
        window: tkinter 窗口
        radius: 圆角半径 (仅用于兼容性，Windows API 使用固定枚举值)
        
    Returns:
        是否成功应用
    """
    if not _ensure_window_visible(window):
        print("窗口未准备好，无法应用圆角效果")
        return False
    
    hwnd = window.winfo_id()
    try:
        # Windows 11 圆角偏好设置
        # DWMWCP_ROUND = 2 是标准圆角，DWMWCP_ROUNDSMALL = 3 是小圆角
        corner_pref = ctypes.c_int(DWMWCP_ROUND if radius >= 8 else DWMWCP_ROUNDSMALL)
        glass_effect._set_window_attribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, corner_pref)
        print("✓ 圆角窗口效果已应用")
        return True
    except Exception as e:
        print(f"应用圆角效果失败: {e}")
        return False


def remove_rounded_corners(window: tk.Tk) -> bool:
    """
    移除窗口圆角效果
    
    Args:
        window: tkinter 窗口
        
    Returns:
        是否成功移除
    """
    hwnd = window.winfo_id()
    try:
        corner_pref = ctypes.c_int(DWMWCP_DONOTROUND)
        glass_effect._set_window_attribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, corner_pref)
        return True
    except Exception:
        return False
