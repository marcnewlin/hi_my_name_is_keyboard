from enum import Enum
from .helpers import log

class Mod(Enum):
    LeftControl = 0x01
    LeftShift = 0x02
    LeftAlt = 0x04
    LeftMeta = 0x08
    RightControl = 0x10
    RightShift = 0x20
    RightAlt = 0x40
    RightMeta = 0x80

class Key(Enum):
    NONE = 0x00
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0a
    H = 0x0b
    I = 0x0c
    J = 0x0d
    K = 0x0e
    L = 0x0f
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1a
    X = 0x1b
    Y = 0x1c
    Z = 0x1d
    _1 = 0x1e
    _2 = 0x1f
    _3 = 0x20
    _4 = 0x21
    _5 = 0x22
    _6 = 0x23
    _7 = 0x24
    _8 = 0x25
    _9 = 0x26
    _0 = 0x27
    Enter = 0x28
    Escape = 0x29
    BackSpace = 0x2a
    Tab = 0x2b
    Space = 0x2c
    Minus = 0x2d
    Equal = 0x2e
    LeftBrace = 0x2f
    RightBrace = 0x30
    BackSlash = 0x31
    Semicolon = 0x33
    Quote = 0x34
    Backtick = 0x35
    Comma = 0x36
    Dot = 0x37
    Slash = 0x38
    CapsLock = 0x39
    F1 = 0x3a
    F2 = 0x3b
    F3 = 0x3c
    F4 = 0x3d
    F5 = 0x3e
    F6 = 0x3f
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45
    PrintScreen = 0x46
    ScrollLock = 0x47
    Pause = 0x48
    Insert = 0x49
    Home = 0x4a
    PageUp = 0x4b
    Delete = 0x4c
    End = 0x4d
    PageDown = 0x4e
    Right = 0x4f
    Left = 0x50
    Down = 0x51
    Up = 0x52
    NumLock = 0x53
    KeyPadSlash = 0x54
    KeyPadAsterisk = 0x55
    KeyPadMinus = 0x56
    KeyPadPlus = 0x57
    KeyPadEnter = 0x58
    KeyPad1 = 0x59
    KeyPad2 = 0x5a
    KeyPad3 = 0x5b
    KeyPad4 = 0x5c
    KeyPad5 = 0x5d
    KeyPad6 = 0x5e
    KeyPad7 = 0x5f
    KeyPad8 = 0x60
    KeyPad9 = 0x61
    KeyPad0 = 0x62
    KeyPadDelete = 0x63
    KeyPadCompose = 0x65
    KeyPadPower = 0x66
    KeyPadEqual = 0x67
    F13 = 0x68
    F14 = 0x69
    F15 = 0x6a
    F16 = 0x6b
    F17 = 0x6c
    F18 = 0x6d
    F19 = 0x6e
    F20 = 0x6f
    F21 = 0x70
    F22 = 0x71
    F23 = 0x72
    F24 = 0x73
    Open = 0x74
    Help = 0x75
    Props = 0x76
    Front = 0x77
    Stop = 0x78
    Again = 0x79
    Undo = 0x7a
    Cut = 0x7b
    Copy = 0x7c
    Paste = 0x7d
    Find = 0x7e
    Mute = 0x7f
    VolumeUp = 0x80
    VolumeDown = 0x81
    LeftControl = 0xe0
    LeftShift = 0xe1
    LeftAlt = 0xe2
    LeftMeta = 0xe3
    RightControl = 0xe4
    RightShift = 0xe5
    RightAlt = 0xe6
    RightMeta = 0xe7
    MediaPlayPause = 0xe8
    MediaStopCD = 0xe9
    MediaPrev = 0xea
    MediaNext = 0xeb
    MediaEjectCD = 0xec
    MediaVolumeUp = 0xed
    MediaVolumeDown = 0xee
    MediaMute = 0xef
    MediaWebBrowser = 0xf0
    MediaBack = 0xf1
    MediaForward = 0xf2
    MediaStop = 0xf3
    MediaFind = 0xf4
    MediaScrollUp = 0xf5
    MediaScrollDown = 0xf6
    MediaEdit = 0xf7
    MediaSleep = 0xf8
    MediaCoffee = 0xf9
    MediaRefresh = 0xfa
    MediaCalc = 0xfb

def ascii_to_hid(c):
  if c >= 'a' and c <= 'z':
    return (Key(ord(c)-ord('a')+0x04),)
  elif c >= 'A' and c <= 'Z':
    return (Key(ord(c)-ord('A')+0x04), Key.LeftShift, Mod.LeftShift)
  elif c >= '1' and c <= '9':
    return (Key(ord(c)-ord('1')+0x1e),)
  elif c == '0':
    return (Key._0,)
  elif c == ',':
    return (Key.Comma,)
  elif c == '?':
    return (Key.Slash, Key.LeftShift, Mod.LeftShift)
  elif c == ' ':
    return (Key.Space,)
  elif c == '.':
    return (Key.Dot,)
  elif c == ':':
    return (Key.Semicolon, Key.LeftShift, Mod.LeftShift)
  elif c == '/':
    return (Key.Slash,)
  elif c == '=':
    return (Key.Equal,)
  elif c == '"':
    return (Key.Quote, Key.LeftShift, Mod.LeftShift)
  elif c == '\'':
    return (Key.Quote,)
  elif c == '-':
    return (Key.Minus,)
  elif c == '+':
    return (Key.Equal, Key.LeftShift, Mod.LeftShift)
  elif c in ['\r', '\n']:
    return (Key.Enter,)
  else:
    log.error("UNKNOWN '%s'" % c)

def keyboard_report(*args):
  keycodes = []
  flags = 0
  for a in args:
    if isinstance(a, Key):
      keycodes.append(a.value)
    elif isinstance(a, Mod):
      flags |= a.value
  assert(len(keycodes) <= 7)
  keycodes += [0] * (7 - len(keycodes))
  report = bytes([0xa1, 0x01, flags, 0x00] + keycodes)
  return report
