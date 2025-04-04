#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\minime.py
import sys
import ctypes
import ctypes.wintypes
import blue
import geo2
import time
import logmodule
try:
    import trinity
except (ImportError, RuntimeError):
    pass

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int)

def LOWORD(dword):
    return dword & 65535


def HIWORD(dword):
    return dword >> 16


hwnd = None
wndclass = None
OnKeyDown = None
OnKeyUp = None
OnChar = None
OnMouse = None
blueArgs = blue.pyos.GetArg()[1:]

def GetMousePosition(lparam):
    x = LOWORD(lparam)
    y = HIWORD(lparam)
    return (x, y)


def PostOnMouse(event, wParam, lParam):
    try:
        if OnMouse is not None and callable(OnMouse):
            x, y = GetMousePosition(lParam)
            if event == 'MOUSE_WHEEL':
                OnMouse(event, (x, y, HIWORD(wParam)))
            else:
                OnMouse(event, (x, y))
    except:
        import traceback
        traceback.print_exc()


class Camera(object):

    def __init__(self, fov, front, back, asp):
        self.minZoomDistance = 0.05
        self.maxZoomDistance = 100000.0
        self.parentPos = (0.0, 0.0, 0.0)
        self.localViewMatrix = geo2.MatrixIdentity()
        self.view = trinity.TriView()
        self.view.transform = geo2.MatrixIdentity()
        self.projection = trinity.TriProjection()
        self.SetPerspective(fov, front, back, asp)
        self.SetPosition((0.0, 50.0, -100.0))
        self.Focus((0.0, 0.0, 0.0))

    def _SetViewMatrix(self, value):
        self.view.transform = value

    def _GetViewMatrix(self):
        return self.view.transform

    viewMatrix = property(_GetViewMatrix, _SetViewMatrix)

    def _GetProjectionMatrix(self):
        return self.projection.transform

    projectionMatrix = property(_GetProjectionMatrix)

    def SetPerspective(self, fov, front, back, asp):
        self.fieldOfView = fov
        self.frontClip = front
        self.backClip = back
        self.aspectRatio = asp
        self.projection.PerspectiveFov(self.fieldOfView, self.aspectRatio, self.frontClip, self.backClip)

    def Update(self):
        parentMat = geo2.MatrixTranslation(*self.parentPos)
        viewInv = geo2.MatrixInverse(self.localViewMatrix)
        newT = geo2.MatrixMultiply(viewInv, parentMat)
        self.viewMatrix = geo2.MatrixInverse(newT)
        trinity.SetViewTransform(self.viewMatrix)
        trinity.SetPerspectiveProjection(self.fieldOfView, self.frontClip, self.backClip, self.aspectRatio)
        self.projection.PerspectiveFov(self.fieldOfView, self.aspectRatio, self.frontClip, self.backClip)

    def SetParentPos(self, pos):
        self.parentPos = pos

    def Zoom(self, val):
        dev = trinity.device
        pos = self.GetPosition()
        target = self.GetPointOfInterest()
        view = geo2.Vec3Normalize(geo2.Subtract(pos, target))
        length = geo2.Vec3Length(geo2.Subtract(pos, target))
        nextPos = geo2.Vec3Add(pos, geo2.Vec3Scale(view, length * val))
        nextLength = geo2.Vec3Length(geo2.Vec3Subtract(nextPos, target))
        if nextLength < self.minZoomDistance:
            nextPos = geo2.Vec3Add(target, geo2.Vec3Scale(view, self.minZoomDistance))
        elif nextLength > self.maxZoomDistance:
            nextPos = geo2.Vec3Add(target, geo2.Vec3Scale(view, self.maxZoomDistance))
        self.SetPosition(nextPos)

    def Orbit(self, yaw, pitch):
        dev = trinity.device
        self.Focus(self.pointOfInterest)
        up = geo2.Vector(0.0, 1.0, 0.0)
        t = geo2.Vector(self.localViewMatrix[1][0], self.localViewMatrix[1][1], self.localViewMatrix[1][2])
        if geo2.Vec3Dot(t, up) <= 0.0:
            pitch = -pitch
            yaw = -yaw
        pos = self.GetPosition()
        target = self.pointOfInterest
        view = geo2.Subtract(pos, target)
        view = geo2.Vec3Normalize(view)
        right = geo2.Vec3Cross(view, up)
        mat = self.localViewMatrix
        ipmat = geo2.MatrixTranslation(-target[0], -target[1], -target[2])
        pmat = geo2.MatrixTranslation(target[0], target[1], target[2])
        mat = geo2.MatrixInverse(mat)
        yrotMat = geo2.MatrixRotationAxis(up, yaw)
        rrotMat = geo2.MatrixRotationAxis(right, pitch)
        yrotMat = geo2.MatrixMultiply(yrotMat, rrotMat)
        mat = geo2.MatrixMultiply(mat, ipmat)
        mat = geo2.MatrixMultiply(mat, yrotMat)
        mat = geo2.MatrixMultiply(mat, pmat)
        self._position = geo2.MatrixDecompose(mat)[2]
        mat = geo2.MatrixInverse(mat)
        self.localViewMatrix = mat

    def Focus(self, point, dist = -1.0):
        dev = trinity.device
        pos = self.GetPosition()
        up = (0.0, 1.0, 0.0)
        t = (self.localViewMatrix[1][0], self.localViewMatrix[1][1], self.localViewMatrix[1][2])
        if geo2.Vec3Dot(t, up) <= 0.0:
            up = (0.0, -1.0, 0.0)
        self.pointOfInterest = point
        self.localViewMatrix = geo2.MatrixLookAtRH(pos, point, up)
        if dist > 0.0:
            view = geo2.Vec3Subtract(pos, point)
            view = geo2.Vec3Normalize(view)
            self.SetPosition(geo2.Vec3Add(point, geo2.Vec3Scale(view, dist)))

    def Pan(self, diff):
        pos = self.GetPosition()
        self.SetPosition(geo2.Vec3Add(pos, diff))
        self.pointOfInterest = geo2.Vec3Add(self.pointOfInterest, diff)

    def SetPosition(self, pos):
        mat = geo2.MatrixInverse(self.localViewMatrix)
        mat = (mat[0],
         mat[1],
         mat[2],
         (pos[0],
          pos[1],
          pos[2],
          mat[3][3]))
        self.localViewMatrix = geo2.MatrixInverse(mat)
        self._position = pos

    def GetPosition(self):
        return self._position

    def GetPointOfInterest(self):
        return self.pointOfInterest


CS_HREDRAW = 2
CS_VREDRAW = 1
NULL = 0
IDI_APPLICATION = 32512
IDC_ARROW = 32512
WHITE_BRUSH = 0
BLACK_BRUSH = 4
WS_OVERLAPPEDWINDOW = 13565952
CW_USEDEFAULT = -2147483648L
SW_SHOWNORMAL = 1
WM_PAINT = 15
DT_SINGLELINE = 32
DT_CENTER = 1
DT_VCENTER = 4
WM_DESTROY = 2
GWL_STYLE = -16
WS_POPUP = -2147483648L
WS_SYSMENU = 524288
WS_VISIBLE = 268435456
WS_MINIMIZEBOX = 131072
WS_CAPTION = 12582912
WM_CLOSE = 16
WM_QUIT = 18
WM_SIZE = 5
WM_SETCURSOR = 32
WM_MOUSEFIRST = 512
WM_MOUSEMOVE = 512
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_LBUTTONDBLCLK = 515
WM_RBUTTONDOWN = 516
WM_RBUTTONUP = 517
WM_RBUTTONDBLCLK = 518
WM_MBUTTONDOWN = 519
WM_MBUTTONUP = 520
WM_MBUTTONDBLCLK = 521
WM_MOUSEWHEEL = 522
WM_ACTIVATE = 6
WM_SYSCOMMAND = 274
WM_ERASEBKGND = 20
SC_KEYMENU = 61696
WA_ACTIVE = 1
WA_CLICKACTIVE = 2
WS_EX_TOPMOST = 8
WS_EX_COMPOSITED = 33554432
WM_KEYDOWN = 256
WM_KEYUP = 257
WM_CHAR = 258
WM_NCLBUTTONDOWN = 161
HTCAPTION = 2
WS_THICKFRAME = 262144
WS_SIZEBOX = WS_THICKFRAME
VK_RETURN = 13
VK_SHIFT = 16
VK_CONTROL = 17
VK_ESCAPE = 27
VK_SPACE = 32
VK_PRIOR = 33
VK_NEXT = 34
VK_END = 35
VK_HOME = 36
VK_LEFT = 37
VK_UP = 38
VK_RIGHT = 39
VK_DOWN = 40
VK_SELECT = 41
VK_PRINT = 42
VK_EXECUTE = 43
VK_SNAPSHOT = 44
VK_INSERT = 45
VK_DELETE = 46
VK_HELP = 47
SWP_NOSIZE = 1
SWP_NOMOVE = 2
SWP_NOZORDER = 4
WT_DEFAULT_FRAME = WS_OVERLAPPEDWINDOW
WT_FRAME_NO_X = WS_POPUP | WS_SIZEBOX
WT_NO_FRAME = WS_EX_TOPMOST | WS_POPUP
uilib = None

def SetWindowSize(w, h):
    dev = trinity.device
    hwnd = dev.GetWindow()
    ctypes.windll.user32.SetWindowPos(ctypes.c_int(hwnd), 0, 0, 0, w, h, SWP_NOZORDER | SWP_NOMOVE)


def SetWindowPos(x, y):
    dev = trinity.device
    hwnd = dev.GetWindow()
    ctypes.windll.user32.SetWindowPos(ctypes.c_int(hwnd), 0, x, y, 0, 0, SWP_NOZORDER | SWP_NOSIZE)


def StartUI():
    global uilib
    from carbonui.uilib import Uilib
    uilib = Uilib()


class WNDCLASS(ctypes.Structure):
    _fields_ = [('style', ctypes.c_uint),
     ('lpfnWndProc', WNDPROC),
     ('cbClsExtra', ctypes.c_int),
     ('cbWndExtra', ctypes.c_int),
     ('hInstance', ctypes.wintypes.HINSTANCE),
     ('hIcon', ctypes.wintypes.HICON),
     ('hCursor', ctypes.wintypes.HICON),
     ('hbrBackground', ctypes.wintypes.HBRUSH),
     ('lpszMenuName', ctypes.wintypes.LPCSTR),
     ('lpszClassName', ctypes.wintypes.LPCSTR)]


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
     ('top', ctypes.c_long),
     ('right', ctypes.c_long),
     ('bottom', ctypes.c_long)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [('hdc', ctypes.c_int),
     ('fErase', ctypes.c_int),
     ('rcPaint', RECT),
     ('fRestore', ctypes.c_int),
     ('fIncUpdate', ctypes.c_int),
     ('rgbReserved', ctypes.c_char * 32)]


class MARGINS(ctypes.Structure):
    _fields_ = [('cxLeftWidth', ctypes.c_long),
     ('cxRightWidth', ctypes.c_long),
     ('cyTopHeight', ctypes.c_long),
     ('cyBottomHeight', ctypes.c_long)]


class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]


class MSG(ctypes.Structure):
    _fields_ = [('hwnd', ctypes.c_int),
     ('message', ctypes.c_uint),
     ('wParam', ctypes.c_int),
     ('lParam', ctypes.c_int),
     ('time', ctypes.c_int),
     ('pt', POINT)]


def ErrorIfZero(handle):
    if handle == 0:
        raise ctypes.WinError()
    else:
        return handle


def SetConstantYawRotation(rad_per_sec):
    global START_TIME
    START_TIME = time.clock()

    def render_cb():
        global START_TIME
        current = time.clock()
        m = geo2.MatrixRotationY((current - START_TIME) * rad_per_sec)
        trinity.SetViewTransform(geo2.MatrixMultiply(m, trinity.GetViewTransform()))
        START_TIME = current

    rj = trinity.CreateRenderJob('ConstantYawRotation')
    rj.PythonCB(render_cb)
    rj.ScheduleRecurring()


def CreateWindow(fullscreen = False, size = None, windowType = WT_DEFAULT_FRAME, showWindow = True):
    global hwnd
    global wndclass
    CreateWindowEx = ctypes.windll.user32.CreateWindowExA
    CreateWindowEx.argtypes = [ctypes.wintypes.DWORD,
     ctypes.wintypes.LPCSTR,
     ctypes.wintypes.LPCSTR,
     ctypes.wintypes.DWORD,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.c_int,
     ctypes.wintypes.HWND,
     ctypes.wintypes.HMENU,
     ctypes.wintypes.HINSTANCE,
     ctypes.wintypes.LPVOID]
    CreateWindowEx.restype = ErrorIfZero
    wndclass = WNDCLASS()
    wndclass.style = CS_HREDRAW | CS_VREDRAW
    wndclass.lpfnWndProc = WNDPROC(WndProc)
    wndclass.cbClsExtra = wndclass.cbWndExtra = 0
    wndclass.hInstance = ctypes.windll.kernel32.GetModuleHandleA(ctypes.c_char_p(NULL))
    wndclass.hIcon = ctypes.windll.user32.LoadImageA(ctypes.c_void_p(NULL), ctypes.c_char_p(IDI_APPLICATION), ctypes.c_uint(1), ctypes.c_int64(10), ctypes.c_int64(10), ctypes.c_uint64(0))
    wndclass.hCursor = ctypes.windll.user32.LoadImageA(ctypes.c_void_p(NULL), ctypes.c_char_p(IDC_ARROW), ctypes.c_uint(2), ctypes.c_int64(10), ctypes.c_int64(10), ctypes.c_uint64(0))
    wndclass.hbrBackground = ctypes.windll.gdi32.GetStockObject(ctypes.c_int(BLACK_BRUSH))
    wndclass.lpszMenuName = None
    wndclass.lpszClassName = 'MainWin'
    if not ctypes.windll.user32.RegisterClassA(ctypes.byref(wndclass)):
        raise ctypes.WinError()
    if '/fullscreen' in blueArgs:
        fullscreen = True
    if fullscreen:
        dspmode = trinity.adapters.GetCurrentDisplayMode(trinity.adapters.DEFAULT_ADAPTER)
        if size is None:
            width = dspmode.width
            height = dspmode.height
        else:
            width, height = size
        hwnd = CreateWindowEx(0, wndclass.lpszClassName, 'MINI ME', WS_EX_TOPMOST | WS_POPUP, 0, 0, width, height, NULL, NULL, wndclass.hInstance, NULL)
    else:
        if size is None:
            width = CW_USEDEFAULT
            height = CW_USEDEFAULT
        else:
            width, height = size
        hwnd = CreateWindowEx(WS_EX_COMPOSITED, wndclass.lpszClassName, 'MINI ME', windowType, CW_USEDEFAULT, CW_USEDEFAULT, width, height, NULL, NULL, wndclass.hInstance, NULL)
    if showWindow:
        ctypes.windll.user32.ShowWindow(ctypes.c_int(hwnd), ctypes.c_int(SW_SHOWNORMAL))
        ctypes.windll.user32.UpdateWindow(ctypes.c_int(hwnd))
    return hwnd


def GetWindowSize(hwnd):
    rect = RECT()
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
    return (rect.right, rect.bottom)


def CreateDevice(hwnd, fullscreen = False):
    if '/fullscreen' in blueArgs:
        fullscreen = True
    w, h = GetWindowSize(hwnd)
    if fullscreen:
        trinity.device.CreateFullScreenDevice(hwnd, w, h)
    else:
        trinity.device.CreateWindowedDevice(hwnd, w, h)


def RunTestScript():
    try:
        for each in blueArgs:
            if each.startswith('/test_script'):
                path = each.split('=')[1]
                execfile(path, globals())

    except Exception as e:
        import traceback
        traceback.print_exc()
        logmodule.LogException()
        sys.exc_clear()


def Main(postCreateCallback = None, fullscreen = False, size = None, windowType = WT_DEFAULT_FRAME):
    hwnd = CreateWindow(fullscreen, size, windowType)
    CreateDevice(hwnd, fullscreen)
    w, h = GetWindowSize(hwnd)
    asp = float(w) / float(h)
    trinity.SetPerspectiveProjection(1.57, 1.0, 1000.0, asp)
    if postCreateCallback and callable(postCreateCallback):
        postCreateCallback()
    MinimeMainLoop()


def MinimeMainLoop():
    msg = MSG()
    pMsg = ctypes.pointer(msg)
    running = True
    TranslateMessage = ctypes.windll.user32.TranslateMessage
    DispatchMessageA = ctypes.windll.user32.DispatchMessageA
    PeekMessageA = ctypes.windll.user32.PeekMessageA
    while running:
        while PeekMessageA(pMsg, NULL, 0, 0, 1):
            if msg.message == WM_QUIT:
                running = False
                break
            TranslateMessage(pMsg)
            DispatchMessageA(pMsg)

        blue.os.Pump()

    ctypes.windll.user32.PostQuitMessage(0)
    return msg.wParam


def WndProc(hwnd, message, wParam, lParam):
    dev = trinity.device
    if message == WM_DESTROY:
        blue.os.Terminate()
        return 0
    elif message == WM_CLOSE:
        blue.os.Terminate()
        return 0
    if message == WM_SIZE:
        if dev.GetWindow():
            rect = RECT()
            ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
            viewTrans = trinity.GetViewTransform()
            fov = trinity.GetFieldOfView()
            front = trinity.GetFrontClip()
            back = trinity.GetBackClip()
            w, h = rect.right, rect.bottom
            defaultBackBuffer = trinity.device.GetRenderContext().GetDefaultBackBuffer()
            if w == defaultBackBuffer.width and h == defaultBackBuffer.height:
                return 0
            asp = float(w) / float(h)
            dev.ChangeBackBufferSize(w, h)
            trinity.SetPerspectiveProjection(fov, front, back, asp)
            trinity.SetViewTransform(viewTrans)
    elif message == WM_LBUTTONDOWN:
        rect = RECT()
        ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
        offset = POINT()
        ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(offset))
        ctypes.windll.user32.OffsetRect(ctypes.byref(rect), offset.x, offset.y)
        ctypes.windll.user32.ClipCursor(ctypes.byref(rect))
        PostOnMouse('LEFT_BUTTON_DOWN', wParam, lParam)
    elif message == WM_LBUTTONUP:
        ctypes.windll.user32.ClipCursor(0)
        PostOnMouse('LEFT_BUTTON_UP', wParam, lParam)
    elif message == WM_LBUTTONDBLCLK:
        PostOnMouse('LEFT_BUTTON_DBLCLK', wParam, lParam)
    elif message == WM_RBUTTONUP:
        PostOnMouse('RIGHT_BUTTON_UP', wParam, lParam)
    elif message == WM_RBUTTONDOWN:
        PostOnMouse('RIGHT_BUTTON_DOWN', wParam, lParam)
    elif message == WM_RBUTTONDBLCLK:
        PostOnMouse('RIGHT_BUTTON_DBLCLK', wParam, lParam)
    elif message == WM_MBUTTONUP:
        PostOnMouse('MIDDLE_BUTTON_UP', wParam, lParam)
    elif message == WM_MBUTTONDOWN:
        PostOnMouse('MIDDLE_BUTTON_DOWN', wParam, lParam)
    elif message == WM_MBUTTONDBLCLK:
        PostOnMouse('MIDDLE_BUTTON_DBLCLK', wParam, lParam)
    elif message == WM_MOUSEMOVE:
        PostOnMouse('MOUSE_MOVE', wParam, lParam)
    elif message == WM_MOUSEWHEEL:
        PostOnMouse('MOUSE_WHEEL', wParam, lParam)
    elif message == WM_ACTIVATE:
        if not (wParam == WA_ACTIVE and wParam == WA_CLICKACTIVE):
            ctypes.windll.user32.ClipCursor(0)
    elif message == WM_SYSCOMMAND:
        if wParam == SC_KEYMENU:
            return 0
    else:
        if message == WM_ERASEBKGND:
            return 0
        if message == WM_KEYDOWN:
            if OnKeyDown is not None and callable(OnKeyDown):
                OnKeyDown(wParam)
        elif message == WM_KEYUP:
            if OnKeyUp is not None and callable(OnKeyUp):
                OnKeyUp(wParam)
        elif message == WM_CHAR:
            if OnChar is not None and callable(OnChar):
                OnChar(wParam)
    if uilib is not None:
        return 0
    else:
        return ctypes.windll.user32.DefWindowProcA(ctypes.c_int(hwnd), ctypes.c_int(message), ctypes.c_int(wParam), ctypes.c_int(lParam))
