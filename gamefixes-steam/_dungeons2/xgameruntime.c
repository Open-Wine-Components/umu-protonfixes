/* Local Gaming Services stand-in for Proton.
 * Implements the xgameruntime exports and the XAsync/XTaskQueue ABI that
 * Minecraft Dungeons II calls. Does not mint Xbox Live tokens. */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#define E_NOTIMPL_      ((HRESULT)0x80004001)
#define E_NOINTERFACE_  ((HRESULT)0x80004002)
#define E_POINTER_      ((HRESULT)0x80004003)
#define E_ABORT_        ((HRESULT)0x80004004)
#define E_FAIL_         ((HRESULT)0x80004005)
#define E_PENDING_      ((HRESULT)0x8000000A)
#define E_INVALIDARG_   ((HRESULT)0x80070057)
#define E_INSUFFICIENT_ ((HRESULT)0x8007007A)

#define TITLE_ID 0x6B9DE498u
#define ASYNC_MAGIC 0x31524758u /* XRG1 */
#define ASYNC_DONE  0x32454758u /* XGE2 */
#define MODE_MANUAL 0
#define MODE_THREADPOOL 1
#define MODE_SERIAL 2
#define MODE_IMMEDIATE 3
#define PORT_WORK 0
#define PORT_COMP 1
#define OP_BEGIN 0
#define OP_DOWORK 1
#define OP_GETRESULT 2
#define OP_CANCEL 3
#define OP_CLEANUP 4

typedef struct queue_obj queue_obj;

typedef struct XAsyncBlock {
    queue_obj *queue;
    void *context;
    void (__stdcall *callback)(struct XAsyncBlock *);
    unsigned char internal[32];
} XAsyncBlock;

_Static_assert(sizeof(XAsyncBlock) == 56, "XAsyncBlock must match the GDK x64 layout");

typedef struct XAsyncProviderData {
    XAsyncBlock *async;
    SIZE_T bufferSize;
    void *buffer;
    void *context;
} XAsyncProviderData;

typedef HRESULT (__stdcall *XAsyncProvider)(UINT32 op, const XAsyncProviderData *data);
typedef HRESULT (__stdcall *XAsyncWork)(XAsyncBlock *async);
typedef void (__stdcall *XTaskQueueCallback)(void *context, BOOLEAN canceled);

typedef struct task_item {
    struct task_item *next;
    ULONGLONG ready;
    int kind; /* 0 = user callback, 1 = async dowork, 2 = async completion */
    void *context;
    XTaskQueueCallback callback;
    struct async_state *state;
} task_item;

typedef struct port_obj {
    queue_obj *q;
    int which;
} port_obj;

#define QUEUE_MAGIC 0x51554555u

struct queue_obj {
    UINT32 magic;
    const void *vtbl_unused;
    LONG refs;
    int work_mode;
    int comp_mode;
    int terminated;
    int closing;
    int composite;
    queue_obj *work_delegate;
    queue_obj *comp_delegate;
    task_item *work_head, *work_tail;
    task_item *comp_head, *comp_tail;
    port_obj work_port;
    port_obj comp_port;
    CRITICAL_SECTION lock;
    HANDLE work_event;
    HANDLE comp_event;
    HANDLE thread;
    DWORD thread_id;
    int nmon;
    void *mon_ctx[4];
    void (__stdcall *mon_cb[4])(void *ctx, struct queue_obj *queue, unsigned port);
    UINT64 mon_token[4];
};

typedef struct async_state {
    UINT32 magic;
    XAsyncBlock *block;
    void *context;
    const void *identity;
    XAsyncProvider provider;
    HRESULT result;
    SIZE_T required;
    int complete;
    int canceled;
    int cleaned;
    int completion_queued;
    void *payload;
    char name[48];
} async_state;

static CRITICAL_SECTION g_lock;
static int g_lock_ready;
static queue_obj *g_process_queue;
static DWORD g_tls = TLS_OUT_OF_INDEXES;
static int g_inited;

static char g_pls_parent[MAX_PATH];
static char g_pls_path[MAX_PATH];

/* The prefix's own user directory: steamuser under Proton, crossover under CrossOver. */
static const char *pls_path_str(void)
{
    char base[MAX_PATH];
    DWORD n;
    if (g_pls_path[0]) return g_pls_path;
    n = GetEnvironmentVariableA("LOCALAPPDATA", base, sizeof base);
    if (!n || n >= sizeof base) snprintf(base, sizeof base, "C:\\users\\steamuser\\AppData\\Local");
    snprintf(g_pls_parent, sizeof g_pls_parent, "%s\\Dungeons2", base);
    snprintf(g_pls_path, sizeof g_pls_path, "%s\\PLS", g_pls_parent);
    return g_pls_path;
}

static void xlog(const char *fmt, ...)
{
    char buf[640];
    va_list ap;
    DWORD wrote;
    HANDLE h;
    int n;

    va_start(ap, fmt);
    n = vsnprintf(buf, sizeof(buf) - 2, fmt, ap);
    va_end(ap);
    if (n < 0) return;
    if (n > (int)sizeof(buf) - 2) n = (int)sizeof(buf) - 2;
    if (n == 0 || buf[n - 1] != '\n') buf[n++] = '\n';
    buf[n] = 0;
    h = CreateFileA("C:\\xgr.log", FILE_APPEND_DATA,
                    FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS,
                    FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return;
    WriteFile(h, buf, (DWORD)n, &wrote, NULL);
    CloseHandle(h);
}

static const char *g_seen[160];
static int g_seen_n;

static void log_once(const char *s)
{
    int i;
    if (!g_lock_ready) { xlog("%s", s); return; }
    EnterCriticalSection(&g_lock);
    for (i = 0; i < g_seen_n; i++) {
        if (g_seen[i] == s) { LeaveCriticalSection(&g_lock); return; }
    }
    if (g_seen_n < (int)(sizeof(g_seen) / sizeof(g_seen[0])))
        g_seen[g_seen_n++] = s;
    LeaveCriticalSection(&g_lock);
    xlog("%s", s);
}

static int guid_eq(const GUID *a, const GUID *b)
{
    return memcmp(a, b, sizeof(GUID)) == 0;
}

static void log_guid(const char *tag, const GUID *g)
{
    xlog("%s %08lX-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X",
         tag, g->Data1, g->Data2, g->Data3,
         g->Data4[0], g->Data4[1], g->Data4[2], g->Data4[3],
         g->Data4[4], g->Data4[5], g->Data4[6], g->Data4[7]);
}

#define G(name, d1, d2, d3, a, b, c, d, e, f, g, h) \
    static const GUID name = { d1, d2, d3, { a, b, c, d, e, f, g, h } };

G(IID_IUnknown_, 0x00000000, 0x0000, 0x0000, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46)
G(IID_Threading, 0x073b7dcb, 0x1fcf, 0x4030, 0x94, 0xbe, 0xe3, 0xc9, 0xeb, 0x62, 0x34, 0x28)
G(IID_Feature,   0x8836fe87, 0xedb9, 0x4fe3, 0x8d, 0xad, 0x05, 0xf0, 0xd2, 0xcd, 0x5b, 0x40)
G(IID_User,      0x01acd177, 0x91f9, 0x4763, 0xa3, 0x8e, 0xcc, 0xbb, 0x55, 0xce, 0x32, 0xe0)
G(IID_User2,     0xeb9bf948, 0x18dc, 0x4d82, 0xbb, 0xcc, 0x40, 0xe0, 0xa8, 0x09, 0xc4, 0xc0)
G(IID_User3,     0x1bf2f8c5, 0xd507, 0x4e52, 0xbb, 0x05, 0xf7, 0x26, 0xd0, 0xe7, 0x11, 0x61)
G(IID_User4,     0x079415e3, 0x6727, 0x437f, 0x8e, 0x9d, 0x8f, 0x8f, 0x9b, 0x24, 0x39, 0xf7)
G(IID_User5,     0x26f3c674, 0xa2fe, 0x44fa, 0xb6, 0xc4, 0xa3, 0x23, 0xbc, 0x94, 0xff, 0x53)
G(IID_User6,     0x5131d685, 0x4394, 0x4ee6, 0x8c, 0x18, 0xbf, 0xb5, 0xd4, 0xae, 0xf1, 0xff)
G(IID_Gamertag,  0xcef4fac0, 0x7676, 0x4a94, 0xa1, 0x19, 0x4c, 0x43, 0xf9, 0xeb, 0x5b, 0x74)
G(IID_Game,      0x973a344e, 0x24bf, 0x4d0f, 0x84, 0x57, 0x56, 0xc5, 0x34, 0x89, 0x2b, 0x29)
G(IID_Game2,     0x50849859, 0x0ad8, 0x4f81, 0x80, 0xe4, 0x5b, 0xc7, 0x86, 0x26, 0xf8, 0x52)
G(IID_Game3,     0x2549f142, 0x6419, 0x4a06, 0x97, 0xb5, 0x93, 0x1a, 0xab, 0x7c, 0x2f, 0x34)
G(IID_System,    0xe349bd1a, 0xfc20, 0x4e40, 0xb9, 0x9c, 0x41, 0x78, 0xcc, 0x6b, 0x40, 0x9f)
G(IID_System2,   0x6fd71f09, 0x7513, 0x49f0, 0x89, 0xbc, 0xbf, 0xaf, 0x5d, 0xf6, 0xf8, 0x52)
G(IID_System3,   0x67ce4bfc, 0xb1d1, 0x4ac7, 0xbc, 0x3a, 0xcb, 0x92, 0x19, 0xa9, 0x7a, 0x85)
G(IID_System4,   0xdadc2895, 0x34b0, 0x4ef5, 0xa8, 0x3e, 0x45, 0x11, 0x4d, 0x62, 0x9b, 0x80)
G(IID_System5,   0x1861cf2e, 0xe18b, 0x4834, 0xa9, 0xf5, 0xb4, 0xa4, 0xe6, 0xef, 0xb4, 0xcf)
G(IID_Analytics, 0xb884675d, 0xb738, 0x4a9c, 0x81, 0x5d, 0x9a, 0x9a, 0x1e, 0x0c, 0x6c, 0x9b)
G(IID_PLS,       0xf4faf4d4, 0x2d04, 0x4fce, 0xb3, 0xe0, 0x47, 0x4a, 0x71, 0x3a, 0x3e, 0x84)
G(IID_PLS2,      0xd29411df, 0x0794, 0x4553, 0x8b, 0x27, 0x95, 0xfc, 0x02, 0xd0, 0xf7, 0x5d)
G(IID_PLS3,      0x41a4e10c, 0x5a7e, 0x41d9, 0x8c, 0x37, 0x37, 0xbd, 0xe6, 0x2a, 0x07, 0xd6)
G(IID_Error,     0x8ca467f7, 0x22e8, 0x4096, 0x84, 0x56, 0xbb, 0x8a, 0xa1, 0x3f, 0x79, 0xd8)
G(IID_Protocol,  0x026b010c, 0x06c3, 0x4cdd, 0xbb, 0xcb, 0x43, 0xf2, 0x29, 0xdb, 0x1c, 0xff)
G(CLSID_Protocol,0x95fd18d2, 0x74dd, 0x4d7c, 0xaa, 0x1b, 0x0b, 0x51, 0x82, 0x76, 0x65, 0xd6)
G(IID_Net,       0x37e56907, 0x2f10, 0x41e8, 0xb7, 0x2f, 0x36, 0xed, 0xb1, 0x85, 0x33, 0x1a)
G(IID_Net2,      0xbf2346b2, 0x39af, 0x4658, 0xb5, 0xea, 0x44, 0x71, 0x3c, 0x7e, 0x83, 0xb3)

typedef struct com_obj { const void *vtbl; } com_obj;

static HRESULT WINAPI gen_qi(com_obj *self, const GUID *iid, void **out, const GUID *const *ok, int n)
{
    int i;
    if (!out) return E_POINTER_;
    *out = NULL;
    if (!iid) return E_INVALIDARG_;
    if (guid_eq(iid, &IID_IUnknown_)) { *out = self; return S_OK; }
    for (i = 0; i < n; i++) {
        if (guid_eq(iid, ok[i])) { *out = self; return S_OK; }
    }
    return E_NOINTERFACE_;
}

static ULONG WINAPI gen_addref(com_obj *self) { (void)self; return 2; }
static ULONG WINAPI gen_release(com_obj *self) { (void)self; return 1; }

static HRESULT WINAPI stub_notimpl(void *self)
{
    (void)self;
    log_once("stub_notimpl");
    return E_NOTIMPL_;
}

/* ---------- async / task queue ---------- */

static async_state *state_of(XAsyncBlock *b)
{
    async_state *s;
    UINT32 magic;
    if (!b) return NULL;
    memcpy(&s, b->internal, sizeof(s));
    memcpy(&magic, b->internal + sizeof(s), sizeof(magic));
    if (magic != ASYNC_MAGIC || !s || s->magic != ASYNC_MAGIC || s->block != b)
        return NULL;
    return s;
}

static void state_bind(XAsyncBlock *b, async_state *s)
{
    UINT32 magic = ASYNC_MAGIC;
    memset(b->internal, 0, sizeof(b->internal));
    memcpy(b->internal, &s, sizeof(s));
    memcpy(b->internal + sizeof(s), &magic, sizeof(magic));
}

static void state_unbind(XAsyncBlock *b)
{
    if (b) memset(b->internal, 0, sizeof(b->internal));
}

static void state_mark_done(XAsyncBlock *b, HRESULT hr, SIZE_T required)
{
    UINT32 magic = ASYNC_DONE;
    memset(b->internal, 0, sizeof(b->internal));
    memcpy(b->internal + 8, &magic, sizeof(magic));
    memcpy(b->internal + 12, &hr, sizeof(hr));
    memcpy(b->internal + 16, &required, sizeof(required));
}

static int read_done(XAsyncBlock *b, HRESULT *hr, SIZE_T *required)
{
    UINT32 magic;
    if (!b) return 0;
    memcpy(&magic, b->internal + 8, sizeof(magic));
    if (magic != ASYNC_DONE) return 0;
    if (hr) memcpy(hr, b->internal + 12, sizeof(*hr));
    if (required) memcpy(required, b->internal + 16, sizeof(*required));
    return 1;
}

static queue_obj *target_queue(queue_obj *q, int port)
{
    if (!q) return NULL;
    if (port == PORT_WORK && q->work_delegate) return q->work_delegate;
    if (port == PORT_COMP && q->comp_delegate) return q->comp_delegate;
    return q;
}

static int mode_of(queue_obj *q, int port)
{
    queue_obj *t = target_queue(q, port);
    if (!t) return MODE_THREADPOOL;
    return port == PORT_WORK ? t->work_mode : t->comp_mode;
}

static task_item *pop_ready(task_item **head, task_item **tail)
{
    task_item *prev = NULL, *it = *head;
    ULONGLONG now = GetTickCount64();
    while (it) {
        if (it->ready <= now) {
            if (prev) prev->next = it->next;
            else *head = it->next;
            if (*tail == it) *tail = prev;
            it->next = NULL;
            return it;
        }
        prev = it;
        it = it->next;
    }
    return NULL;
}

static void cleanup_state(async_state *st)
{
    XAsyncProvider provider;
    XAsyncBlock *block;
    void *context;
    XAsyncProviderData data;

    if (!st) return;
    EnterCriticalSection(&g_lock);
    if (st->cleaned) { LeaveCriticalSection(&g_lock); return; }
    st->cleaned = 1;
    provider = st->provider;
    block = st->block;
    context = st->context;
    if (block) {
        if (st->complete) state_mark_done(block, st->result, st->required);
        else state_unbind(block);
    }
    LeaveCriticalSection(&g_lock);

    if (provider) {
        memset(&data, 0, sizeof(data));
        data.async = block;
        data.context = context;
        provider(OP_CLEANUP, &data);
    }
    st->magic = 0;
    free(st);
}

static void run_dowork(async_state *st)
{
    XAsyncProviderData data;
    if (!st || st->cleaned || st->canceled || st->complete || !st->provider) return;
    memset(&data, 0, sizeof(data));
    data.async = st->block;
    data.context = st->context;
    st->provider(OP_DOWORK, &data);
}

static void run_completion(async_state *st)
{
    XAsyncBlock *block;
    if (!st || st->cleaned) return;
    block = st->block;
    if (block && block->callback) block->callback(block);
    cleanup_state(st);
}

static void run_item(task_item *it)
{
    if (it->kind == 0) {
        if (it->callback) it->callback(it->context, FALSE);
    } else if (it->kind == 1) {
        run_dowork(it->state);
    } else if (it->kind == 2) {
        run_completion(it->state);
    }
    free(it);
}

static int dispatch_one(queue_obj *q, int port)
{
    task_item *it;
    task_item **head, **tail;
    q = target_queue(q, port);
    if (!q) return 0;
    EnterCriticalSection(&q->lock);
    if (port == PORT_WORK) { head = &q->work_head; tail = &q->work_tail; }
    else { head = &q->comp_head; tail = &q->comp_tail; }
    it = pop_ready(head, tail);
    LeaveCriticalSection(&q->lock);
    if (!it) return 0;
    run_item(it);
    return 1;
}

static int port_is_auto(int mode)
{
    return mode != MODE_MANUAL;
}

static DWORD WINAPI queue_thread(LPVOID param)
{
    queue_obj *q = param;
    for (;;) {
        HANDLE waits[2];
        DWORD n = 0;
        int did;
        do {
            int drain_manual = q->work_mode == MODE_MANUAL && q->comp_mode == MODE_MANUAL && q->nmon == 0;
            did = 0;
            if (port_is_auto(q->work_mode) || drain_manual) did |= dispatch_one(q, PORT_WORK);
            if (port_is_auto(q->comp_mode) || drain_manual) did |= dispatch_one(q, PORT_COMP);
        } while (did);
        if (q->terminated) break;
        if (port_is_auto(q->work_mode) && q->work_event) waits[n++] = q->work_event;
        if (port_is_auto(q->comp_mode) && q->comp_event) waits[n++] = q->comp_event;
        if (n == 0) { Sleep(40); continue; }
        WaitForMultipleObjects(n, waits, FALSE, 30);
    }
    return 0;
}

static int queue_live(queue_obj *q)
{
    return q && q->magic == QUEUE_MAGIC;
}

static queue_obj *process_queue(void);

static void WINAPI thr_Close(void *self, queue_obj *q);

static queue_obj *queue_new(int work_mode, int comp_mode)
{
    queue_obj *q = calloc(1, sizeof(*q));
    if (!q) return NULL;
    q->refs = 1;
    q->work_mode = work_mode;
    q->comp_mode = comp_mode;
    q->work_port.q = q;
    q->work_port.which = PORT_WORK;
    q->comp_port.q = q;
    q->comp_port.which = PORT_COMP;
    InitializeCriticalSection(&q->lock);
    q->work_event = CreateEventA(NULL, FALSE, FALSE, NULL);
    q->comp_event = CreateEventA(NULL, FALSE, FALSE, NULL);
    q->magic = QUEUE_MAGIC;
    q->thread = CreateThread(NULL, 0, queue_thread, q, 0, &q->thread_id);
    return q;
}

static void fire_monitors(queue_obj *q, unsigned port)
{
    void (__stdcall *cbs[4])(void *, queue_obj *, unsigned);
    void *ctxs[4];
    int n = 0, i;
    if (!q || !g_lock_ready) return;
    EnterCriticalSection(&g_lock);
    if (queue_live(q)) {
        n = q->nmon;
        if (n > 4) n = 4;
        for (i = 0; i < n; i++) { cbs[i] = q->mon_cb[i]; ctxs[i] = q->mon_ctx[i]; }
    }
    LeaveCriticalSection(&g_lock);
    for (i = 0; i < n; i++) if (cbs[i]) cbs[i](ctxs[i], q, port);
}

static void enqueue(queue_obj *q, int port, task_item *it)
{
    HANDLE ev;
    queue_obj *orig = q;
    int manual;
    if (!g_lock_ready) { free(it); return; }
    EnterCriticalSection(&g_lock);
    q = target_queue(q, port);
    if (!queue_live(q)) {
        q = process_queue();
        orig = q;
    }
    if (!queue_live(q)) {
        LeaveCriticalSection(&g_lock);
        free(it);
        return;
    }
    EnterCriticalSection(&q->lock);
    LeaveCriticalSection(&g_lock);
    if (q->terminated) {
        LeaveCriticalSection(&q->lock);
        free(it);
        return;
    }
    it->next = NULL;
    if (port == PORT_WORK) {
        if (q->work_tail) q->work_tail->next = it;
        else q->work_head = it;
        q->work_tail = it;
        ev = q->work_event;
    } else {
        if (q->comp_tail) q->comp_tail->next = it;
        else q->comp_head = it;
        q->comp_tail = it;
        ev = q->comp_event;
    }
    manual = (port == PORT_WORK) ? q->work_mode == MODE_MANUAL : q->comp_mode == MODE_MANUAL;
    if (ev) SetEvent(ev);
    LeaveCriticalSection(&q->lock);
    if (manual) {
        fire_monitors(q, (unsigned)port);
        if (orig && orig != q) fire_monitors(orig, (unsigned)port);
    }
}

static queue_obj *process_queue(void)
{
    if (!g_process_queue)
        g_process_queue = queue_new(MODE_THREADPOOL, MODE_THREADPOOL);
    return g_process_queue;
}

static void complete_async(XAsyncBlock *block, HRESULT result, SIZE_T required)
{
    async_state *st = state_of(block);
    queue_obj *q;
    int mode;
    task_item *it;
    static int logs;

    if (!st || st->cleaned) return;
    EnterCriticalSection(&g_lock);
    if (st->complete) { LeaveCriticalSection(&g_lock); return; }
    st->complete = 1;
    st->result = result;
    st->required = required;
    LeaveCriticalSection(&g_lock);
    if (logs++ < 48) xlog("complete %s hr=%08lX", st->name, (unsigned long)result);

    if (!block->callback) return;
    q = block->queue ? block->queue : process_queue();
    mode = mode_of(q, PORT_COMP);
    EnterCriticalSection(&g_lock);
    if (st->completion_queued || st->cleaned) { LeaveCriticalSection(&g_lock); return; }
    st->completion_queued = 1;
    LeaveCriticalSection(&g_lock);

    if (mode == MODE_IMMEDIATE) {
        run_completion(st);
        return;
    }
    it = calloc(1, sizeof(*it));
    if (!it) { run_completion(st); return; }
    it->kind = 2;
    it->state = st;
    it->ready = GetTickCount64();
    enqueue(q, PORT_COMP, it);
}

static HRESULT schedule_async(XAsyncBlock *block, UINT32 delay)
{
    async_state *st = state_of(block);
    queue_obj *q;
    int mode;
    task_item *it;
    static int logs;

    if (!st || st->cleaned) return E_INVALIDARG_;
    if (st->complete) return S_OK;
    q = block->queue ? block->queue : process_queue();
    mode = mode_of(q, PORT_WORK);
    if (logs++ < 48) xlog("schedule %s delay=%lu mode=%d", st->name, (unsigned long)delay, mode);
    if (mode == MODE_IMMEDIATE && delay == 0) {
        run_dowork(st);
        return S_OK;
    }
    it = calloc(1, sizeof(*it));
    if (!it) return E_FAIL_;
    it->kind = 1;
    it->state = st;
    it->ready = GetTickCount64() + delay;
    enqueue(q, PORT_WORK, it);
    return S_OK;
}

static HRESULT WINAPI run_provider(UINT32 op, const XAsyncProviderData *data)
{
    XAsyncWork work;
    HRESULT hr;
    if (op != OP_DOWORK) return S_OK;
    work = (XAsyncWork)data->context;
    hr = work ? work(data->async) : E_FAIL_;
    complete_async(data->async, hr, 0);
    return S_OK;
}

static HRESULT WINAPI user_add_provider(UINT32 op, const XAsyncProviderData *data)
{
    async_state *st;
    if (op != OP_DOWORK) return S_OK;
    st = state_of(data->async);
    if (st) st->payload = (void*)(uintptr_t)1; /* filled by caller via global user */
    complete_async(data->async, S_OK, sizeof(void *));
    return S_OK;
}

/* threading methods */

static HRESULT WINAPI thr_GetStatus(void *self, XAsyncBlock *async, BOOLEAN wait)
{
    async_state *st;
    HRESULT hr;
    unsigned spins = 0;
    static unsigned calls;
    (void)self;
    if ((++calls % 20000u) == 1u)
        xlog("GetStatus calls=%u", calls);
    for (;;) {
        st = state_of(async);
        if (!st) {
            if (read_done(async, &hr, NULL)) return hr;
            return E_PENDING_;
        }
        if (st->complete) return st->result;
        if (!wait) return E_PENDING_;
        if (async->queue) {
            dispatch_one(async->queue, PORT_WORK);
            dispatch_one(async->queue, PORT_COMP);
        } else if (g_process_queue) {
            dispatch_one(g_process_queue, PORT_WORK);
            dispatch_one(g_process_queue, PORT_COMP);
        }
        if (++spins > 4000) {
            st = state_of(async);
            hr = (st && st->complete) ? st->result : E_PENDING_;
            xlog("GetStatus giveup %s", st ? st->name : "?");
            return hr;
        }
        Sleep(1);
    }
}

static HRESULT WINAPI thr_GetResultSize(void *self, XAsyncBlock *async, SIZE_T *bufferSize)
{
    async_state *st = state_of(async);
    (void)self;
    if (!bufferSize) return E_POINTER_;
    if (!st || !st->complete) {
        SIZE_T n;
        HRESULT hr;
        if (read_done(async, &hr, &n)) { *bufferSize = n; return FAILED(hr) ? hr : S_OK; }
        return E_PENDING_;
    }
    *bufferSize = st->required;
    return S_OK;
}

static void WINAPI thr_Cancel(void *self, XAsyncBlock *async)
{
    async_state *st = state_of(async);
    XAsyncProviderData data;
    (void)self;
    if (!st || st->cleaned || st->complete) return;
    st->canceled = 1;
    if (st->provider) {
        memset(&data, 0, sizeof(data));
        data.async = async;
        data.context = st->context;
        st->provider(OP_CANCEL, &data);
    }
    complete_async(async, E_ABORT_, 0);
}

static HRESULT WINAPI thr_Run(void *self, XAsyncBlock *async, XAsyncWork work)
{
    HRESULT hr;
    (void)self;
    if (!async || !work) return E_INVALIDARG_;
    hr = 0;
    {
        async_state *st = calloc(1, sizeof(*st));
        XAsyncProviderData data;
        if (!st) return E_FAIL_;
        st->magic = ASYNC_MAGIC;
        st->block = async;
        st->context = (void *)work;
        st->provider = run_provider;
        snprintf(st->name, sizeof(st->name), "XAsyncRun");
        state_bind(async, st);
        memset(&data, 0, sizeof(data));
        data.async = async;
        data.context = (void *)work;
        hr = run_provider(OP_BEGIN, &data);
        if (FAILED(hr)) { cleanup_state(st); return hr; }
    }
    return schedule_async(async, 0);
}

static HRESULT WINAPI thr_Begin(void *self, XAsyncBlock *async, void *context, const void *identity,
                                const char *identityName, XAsyncProvider provider)
{
    async_state *st;
    XAsyncProviderData data;
    HRESULT hr;
    (void)self;
    if (!async || !provider) return E_INVALIDARG_;
    if (state_of(async)) return E_INVALIDARG_;
    st = calloc(1, sizeof(*st));
    if (!st) return E_FAIL_;
    st->magic = ASYNC_MAGIC;
    st->block = async;
    st->context = context;
    st->identity = identity;
    st->provider = provider;
    snprintf(st->name, sizeof(st->name), "%s", identityName ? identityName : "?");
    state_bind(async, st);
    log_once(identityName ? identityName : "XAsyncBegin");
    memset(&data, 0, sizeof(data));
    data.async = async;
    data.context = context;
    hr = provider(OP_BEGIN, &data);
    if (FAILED(hr)) {
        xlog("begin failed %s %08lX", st->name, (unsigned long)hr);
        cleanup_state(st);
        return hr;
    }
    return S_OK;
}

static HRESULT WINAPI thr_Pad(void *self)
{
    (void)self;
    log_once("threading padding");
    return E_NOTIMPL_;
}

static HRESULT WINAPI thr_Schedule(void *self, XAsyncBlock *async, UINT32 delay)
{
    (void)self;
    return schedule_async(async, delay);
}

static void WINAPI thr_Complete(void *self, XAsyncBlock *async, HRESULT result, SIZE_T required)
{
    (void)self;
    complete_async(async, result, required);
}

static HRESULT WINAPI thr_GetResult(void *self, XAsyncBlock *async, const void *identity,
                                    SIZE_T bufferSize, void *buffer, SIZE_T *bufferUsed)
{
    async_state *st = state_of(async);
    XAsyncProviderData data;
    HRESULT hr;
    (void)self;
    if (!st) return E_INVALIDARG_;
    if (!st->complete) return E_PENDING_;
    if (identity && st->identity && identity != st->identity) return E_INVALIDARG_;
    if (bufferSize < st->required) return E_INSUFFICIENT_;
    memset(&data, 0, sizeof(data));
    data.async = async;
    data.bufferSize = bufferSize;
    data.buffer = buffer;
    data.context = st->context;
    hr = st->provider ? st->provider(OP_GETRESULT, &data) : S_OK;
    if (bufferUsed) *bufferUsed = st->required;
    cleanup_state(st);
    return hr;
}

static HRESULT WINAPI thr_QueueCreate(void *self, UINT32 workMode, UINT32 compMode, queue_obj **out)
{
    (void)self;
    if (!out) return E_POINTER_;
    *out = queue_new((int)workMode, (int)compMode);
    xlog("QueueCreate %p work=%lu comp=%lu", (void *)*out, (unsigned long)workMode, (unsigned long)compMode);
    return *out ? S_OK : E_FAIL_;
}

static HRESULT WINAPI thr_QueueCreateComposite(void *self, port_obj *work, port_obj *comp, queue_obj **out)
{
    queue_obj *q;
    (void)self;
    log_once("QueueCreateComposite");
    if (!out || !work || !comp || !work->q || !comp->q) return E_INVALIDARG_;
    q = calloc(1, sizeof(*q));
    if (!q) return E_FAIL_;
    if (!g_lock_ready) { free(q); return E_FAIL_; }
    EnterCriticalSection(&g_lock);
    if (!queue_live(work->q) || !queue_live(comp->q)) {
        LeaveCriticalSection(&g_lock);
        free(q);
        return E_INVALIDARG_;
    }
    InterlockedIncrement(&work->q->refs);
    InterlockedIncrement(&comp->q->refs);
    LeaveCriticalSection(&g_lock);
    q->refs = 1;
    q->composite = 1;
    q->work_delegate = work->q;
    q->comp_delegate = comp->q;
    q->work_mode = work->q->work_mode;
    q->comp_mode = comp->q->comp_mode;
    q->work_port.q = q;
    q->work_port.which = PORT_WORK;
    q->comp_port.q = q;
    q->comp_port.which = PORT_COMP;
    InitializeCriticalSection(&q->lock);
    q->magic = QUEUE_MAGIC;
    *out = q;
    return S_OK;
}

static HRESULT WINAPI thr_GetPort(void *self, queue_obj *q, UINT32 port, port_obj **out)
{
    (void)self;
    if (!q || !out) return E_INVALIDARG_;
    *out = (port == PORT_COMP) ? &q->comp_port : &q->work_port;
    return S_OK;
}

static HRESULT WINAPI thr_Duplicate(void *self, queue_obj *q, queue_obj **out)
{
    (void)self;
    if (!q || !out) return E_INVALIDARG_;
    if (!q->composite) InterlockedIncrement(&q->refs);
    *out = q;
    return S_OK;
}

static BOOLEAN WINAPI thr_Dispatch(void *self, queue_obj *q, UINT32 port, UINT32 timeout)
{
    ULONGLONG start;
    BOOLEAN hit = FALSE;
    (void)self;
    if (!q) q = process_queue();
    if (!q || !g_lock_ready) return FALSE;
    EnterCriticalSection(&g_lock);
    if (!queue_live(q)) {
        LeaveCriticalSection(&g_lock);
        return FALSE;
    }
    InterlockedIncrement(&q->refs);
    LeaveCriticalSection(&g_lock);
    if (timeout != 0) {
        static int disp_logs;
        if (disp_logs++ < 12)
            xlog("Dispatch q=%p port=%lu timeout=%lu", (void *)q, (unsigned long)port, (unsigned long)timeout);
    }
    start = GetTickCount64();
    for (;;) {
        if (dispatch_one(q, (int)port)) { hit = TRUE; break; }
        if (timeout == 0) break;
        if (timeout != 0xFFFFFFFFu && GetTickCount64() - start >= timeout) break;
        {
            queue_obj *t = target_queue(q, (int)port);
            DWORD slice = 15;
            if (timeout != 0xFFFFFFFFu) {
                ULONGLONG left = timeout - (GetTickCount64() - start);
                if (left < slice) slice = (DWORD)left;
            }
            if (t && queue_live(t)) {
                HANDLE ev = ((int)port == PORT_COMP) ? t->comp_event : t->work_event;
                if (ev) WaitForSingleObject(ev, slice);
                else Sleep(slice);
            } else Sleep(slice);
        }
    }
    thr_Close(NULL, q);
    return hit;
}

static void queue_destroy(queue_obj *q)
{
    queue_obj *w = NULL, *c = NULL;
    int composite;
    task_item *it;
    if (!q || !g_lock_ready) return;
    EnterCriticalSection(&g_lock);
    if (q->magic != QUEUE_MAGIC) {
        LeaveCriticalSection(&g_lock);
        return;
    }
    composite = q->composite;
    q->magic = 0;
    q->terminated = 1;
    if (composite) {
        w = q->work_delegate;
        c = q->comp_delegate;
        q->work_delegate = q->comp_delegate = NULL;
    }
    LeaveCriticalSection(&g_lock);
    if (composite) {
        free(q);
        if (w) thr_Close(NULL, w);
        if (c) thr_Close(NULL, c);
        return;
    }
    if (q->work_event) SetEvent(q->work_event);
    if (q->comp_event) SetEvent(q->comp_event);
    if (q->thread && q->thread_id != GetCurrentThreadId()) {
        WaitForSingleObject(q->thread, 5000);
        CloseHandle(q->thread);
        q->thread = NULL;
    }
    EnterCriticalSection(&q->lock);
    while ((it = q->work_head)) { q->work_head = it->next; free(it); }
    while ((it = q->comp_head)) { q->comp_head = it->next; free(it); }
    q->work_head = q->work_tail = q->comp_head = q->comp_tail = NULL;
    if (q->work_event) CloseHandle(q->work_event);
    if (q->comp_event) CloseHandle(q->comp_event);
    q->work_event = q->comp_event = NULL;
    LeaveCriticalSection(&q->lock);
    DeleteCriticalSection(&q->lock);
    free(q);
}

static void WINAPI thr_Close(void *self, queue_obj *q)
{
    LONG left;
    (void)self;
    if (!q || !g_lock_ready) return;
    EnterCriticalSection(&g_lock);
    if (q->magic != QUEUE_MAGIC) {
        LeaveCriticalSection(&g_lock);
        return;
    }
    if (q == g_process_queue) {
        LeaveCriticalSection(&g_lock);
        return;
    }
    left = InterlockedDecrement(&q->refs);
    LeaveCriticalSection(&g_lock);
    if (left <= 0) queue_destroy(q);
}

static HRESULT WINAPI thr_Submit(void *self, queue_obj *q, UINT32 port, void *context, XTaskQueueCallback cb)
{
    task_item *it;
    int mode;
    (void)self;
    if (!cb) return E_INVALIDARG_;
    if (!q) q = process_queue();
    if (q->closing) return E_ABORT_;
    mode = mode_of(q, (int)port);
    if (mode == MODE_IMMEDIATE) { cb(context, FALSE); return S_OK; }
    it = calloc(1, sizeof(*it));
    if (!it) return E_FAIL_;
    it->kind = 0;
    it->context = context;
    it->callback = cb;
    it->ready = GetTickCount64();
    enqueue(q, (int)port, it);
    return S_OK;
}

static HRESULT WINAPI thr_SubmitDelayed(void *self, queue_obj *q, UINT32 port, UINT32 delay, void *context, XTaskQueueCallback cb)
{
    task_item *it;
    (void)self;
    if (!cb) return E_INVALIDARG_;
    if (!q) q = process_queue();
    if (q->closing) return E_ABORT_;
    if (delay == 0 && mode_of(q, (int)port) == MODE_IMMEDIATE) { cb(context, FALSE); return S_OK; }
    it = calloc(1, sizeof(*it));
    if (!it) return E_FAIL_;
    it->kind = 0;
    it->context = context;
    it->callback = cb;
    it->ready = GetTickCount64() + delay;
    enqueue(q, (int)port, it);
    return S_OK;
}

static HRESULT WINAPI thr_RegWaiter(void *self, queue_obj *q, UINT32 port, HANDLE h, void *ctx, XTaskQueueCallback cb, void *token)
{
    (void)self; (void)q; (void)port; (void)h; (void)ctx; (void)cb; (void)token;
    log_once("XTaskQueueRegisterWaiter");
    return E_NOTIMPL_;
}
static void WINAPI thr_UnregWaiter(void *self, queue_obj *q, UINT64 token)
{
    (void)self; (void)q; (void)token;
}
struct term_note { void (__stdcall *cb)(void *); void *ctx; };
static void __stdcall term_marker(void *ctx, BOOLEAN canceled)
{
    struct term_note *n = ctx;
    (void)canceled;
    if (n && n->cb) n->cb(n->ctx);
    free(n);
}

static HRESULT WINAPI thr_Terminate(void *self, queue_obj *q, BOOLEAN wait, void *ctx, void (__stdcall *cb)(void *))
{
    int guard = 0;
    struct term_note *n;
    task_item *it;
    (void)self;
    xlog("XTaskQueueTerminate q=%p wait=%u", (void *)q, (unsigned)wait);
    if (!q || !g_lock_ready) {
        if (cb) cb(ctx);
        return S_OK;
    }
    EnterCriticalSection(&g_lock);
    if (!queue_live(q)) {
        LeaveCriticalSection(&g_lock);
        if (cb) cb(ctx);
        return S_OK;
    }
    InterlockedIncrement(&q->refs);
    LeaveCriticalSection(&g_lock);
    if (wait && q) {
        while (guard++ < 1000 && (dispatch_one(q, PORT_WORK) || dispatch_one(q, PORT_COMP)))
            ;
        if (cb) cb(ctx);
    } else if (q) {
        /* Let a thread blocked in Dispatch(completion) observe termination. */
        n = calloc(1, sizeof(*n));
        it = n ? calloc(1, sizeof(*it)) : NULL;
        if (n && it) {
            n->cb = cb;
            n->ctx = ctx;
            it->kind = 0;
            it->callback = term_marker;
            it->context = n;
            it->ready = GetTickCount64();
            enqueue(q, PORT_COMP, it);
        } else if (cb) {
            cb(ctx);
        }
    } else if (cb) {
        cb(ctx);
    }
    if (q) {
        queue_obj *tw = target_queue(q, PORT_WORK);
        queue_obj *tc = target_queue(q, PORT_COMP);
        q->closing = 1;
        if (tw && tw != q) tw->closing = 1;
        if (tc && tc != q && tc != tw) tc->closing = 1;
        if (tw && tw->work_event) SetEvent(tw->work_event);
        if (tw && tw->comp_event) SetEvent(tw->comp_event);
        if (tc && tc != tw && tc->comp_event) SetEvent(tc->comp_event);
    }
    thr_Close(NULL, q);
    xlog("XTaskQueueTerminate done");
    return S_OK;
}
static HRESULT WINAPI thr_RegMon(void *self, queue_obj *q, void *ctx, void *cb, UINT64 *token)
{
    static UINT64 next_token = 1;
    (void)self;
    xlog("XTaskQueueRegisterMonitor q=%p", (void *)q);
    if (!q) q = process_queue();
    if (!g_lock_ready || !cb) return E_INVALIDARG_;
    EnterCriticalSection(&g_lock);
    if (!queue_live(q) || q->nmon >= 4) {
        LeaveCriticalSection(&g_lock);
        return E_FAIL_;
    }
    q->mon_ctx[q->nmon] = ctx;
    q->mon_cb[q->nmon] = cb;
    q->mon_token[q->nmon] = next_token++;
    if (token) *token = q->mon_token[q->nmon];
    q->nmon++;
    LeaveCriticalSection(&g_lock);
    return S_OK;
}
static void WINAPI thr_UnregMon(void *self, queue_obj *q, UINT64 token)
{
    int i;
    (void)self;
    if (!q || !g_lock_ready) return;
    EnterCriticalSection(&g_lock);
    for (i = 0; i < q->nmon; i++) {
        if (q->mon_token[i] != token) continue;
        q->nmon--;
        q->mon_ctx[i] = q->mon_ctx[q->nmon];
        q->mon_cb[i] = q->mon_cb[q->nmon];
        q->mon_token[i] = q->mon_token[q->nmon];
        break;
    }
    LeaveCriticalSection(&g_lock);
}
static BOOLEAN WINAPI thr_GetProcessQueue(void *self, queue_obj **out)
{
    (void)self;
    if (!out) return FALSE;
    *out = process_queue();
    return *out ? TRUE : FALSE;
}
static void WINAPI thr_SetProcessQueue(void *self, queue_obj *q)
{
    (void)self;
    log_once("SetProcessQueue");
    if (q) g_process_queue = q;
}
static HRESULT WINAPI thr_SetTimeSens(void *self, BOOLEAN on)
{
    (void)self;
    if (g_tls != TLS_OUT_OF_INDEXES) TlsSetValue(g_tls, (void *)(uintptr_t)(on ? 1 : 0));
    return S_OK;
}
static HRESULT WINAPI thr_Pad2(void *self) { (void)self; return E_NOTIMPL_; }
static void WINAPI thr_AssertNot(void *self) { (void)self; }
static BOOLEAN WINAPI thr_IsTimeSens(void *self)
{
    (void)self;
    if (g_tls == TLS_OUT_OF_INDEXES) return FALSE;
    return TlsGetValue(g_tls) ? TRUE : FALSE;
}

static void *threading_vtbl[] = {
    gen_qi, gen_addref, gen_release,
    thr_GetStatus, thr_GetResultSize, thr_Cancel, thr_Run, thr_Begin, thr_Pad,
    thr_Schedule, thr_Complete, thr_GetResult,
    thr_QueueCreate, thr_QueueCreateComposite, thr_GetPort, thr_Duplicate, thr_Dispatch, thr_Close,
    thr_Submit, thr_SubmitDelayed, thr_RegWaiter, thr_UnregWaiter, thr_Terminate,
    thr_RegMon, thr_UnregMon, thr_GetProcessQueue, thr_SetProcessQueue,
    thr_SetTimeSens, thr_Pad2, thr_AssertNot, thr_IsTimeSens
};
static com_obj threading_obj = { threading_vtbl };

/* The generic QI above ignores the accepted-iid list because the vtable
 * slot is gen_qi, whose signature doesn't match. Wrap it. */
static HRESULT WINAPI threading_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Threading };
    return gen_qi(self, iid, out, ok, 1);
}

/* ---------- feature / game / system / pls / error / user ---------- */

static BOOLEAN WINAPI feat_avail(void *self, UINT32 feature)
{
    BOOLEAN yes;
    static uint64_t logged;
    (void)self;
    /* XAsync, XAsyncProvider, XGame, XPersistentLocalStorage, XSystem, XTaskQueue, XThread, XUser, XError. */
    /* 2 XAsync, 3 XAsyncProvider, 5 XGame, 10 XNetworking, 12 PLS,
       15 XSystem, 16 XTaskQueue, 17 XThread, 18 XUser, 19 XError. */
    yes = (feature == 2 || feature == 3 || feature == 5 || feature == 10 ||
           feature == 12 || feature == 15 || feature == 16 || feature == 17 ||
           feature == 18 || feature == 19);
    if (feature < 64 && (logged & (1ull << feature)) == 0) {
        logged |= 1ull << feature;
        xlog("feature %lu -> %u", (unsigned long)feature, (unsigned)yes);
    }
    return yes;
}
static void *feature_vtbl[] = { gen_qi, gen_addref, gen_release, feat_avail };
static com_obj feature_obj = { feature_vtbl };
static HRESULT WINAPI feature_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Feature };
    return gen_qi(self, iid, out, ok, 1);
}

static HRESULT WINAPI game_title(void *self, UINT32 *titleId)
{
    (void)self;
    if (!titleId) return E_POINTER_;
    *titleId = TITLE_ID;
    log_once("XGameGetXboxTitleId");
    return S_OK;
}
static void WINAPI game_launch(void *self, const char *exe, const char *args, void *user)
{
    (void)self; (void)user;
    xlog("XLaunchNewGame %s %s", exe ? exe : "", args ? args : "");
}
static HRESULT WINAPI game_restart(void *self, const char *args, UINT32 reserved)
{
    (void)self; (void)reserved;
    xlog("XLaunchRestartOnCrash %s", args ? args : "");
    return S_OK;
}
static void *game_vtbl[] = {
    gen_qi, gen_addref, gen_release, game_title, game_launch, game_restart
};
static com_obj game_obj = { game_vtbl };
static HRESULT WINAPI game_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Game, &IID_Game2, &IID_Game3 };
    return gen_qi(self, iid, out, ok, 3);
}

static HRESULT copy_out(const char *src, INT32 cap, char *dst, SIZE_T *used)
{
    SIZE_T n = strlen(src) + 1;
    if (used) *used = n;
    if (!dst || cap < (INT32)n) return E_INSUFFICIENT_;
    memcpy(dst, src, n);
    return S_OK;
}
static HRESULT WINAPI sys_console(void *self, INT32 cap, char *dst, SIZE_T *used)
{
    (void)self;
    log_once("XSystemGetConsoleId");
    return copy_out("0000000000000001", cap, dst, used);
}
static HRESULT WINAPI sys_sandbox(void *self, INT32 cap, char *dst, SIZE_T *used)
{
    (void)self;
    log_once("XSystemGetXboxLiveSandboxId");
    return copy_out("RETAIL", cap, dst, used);
}
static HRESULT WINAPI sys_device(void *self, INT32 cap, char *dst, SIZE_T *used)
{
    (void)self;
    log_once("XSystemGetAppSpecificDeviceId");
    return copy_out("d2d2d2d2-d2d2-4d2d-8d2d-d2d2d2d2d2d2", cap, dst, used);
}
static HRESULT WINAPI sys_track(void *self, void *cb, void *ctx)
{
    (void)self; (void)cb; (void)ctx;
    log_once("XSystemHandleTrack");
    return S_OK;
}
static BOOLEAN WINAPI sys_valid(void *self, void *handle)
{
    (void)self;
    return handle ? TRUE : FALSE;
}
static void WINAPI sys_bandwidth(void *self, BOOLEAN enable)
{
    (void)self; (void)enable;
}
static void *system_vtbl[] = {
    gen_qi, gen_addref, gen_release,
    sys_console, sys_sandbox, sys_device, sys_track, sys_valid, sys_bandwidth
};
static com_obj system_obj = { system_vtbl };
static HRESULT WINAPI system_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_System, &IID_System2, &IID_System3, &IID_System4, &IID_System5 };
    return gen_qi(self, iid, out, ok, 5);
}

typedef struct analytics_info {
    UINT16 os_maj, os_min, os_bld, os_rev;
    UINT16 host_maj, host_min, host_bld, host_rev;
    char family[64];
    char form[64];
} analytics_info;

static analytics_info *WINAPI analytics_get(void *self, analytics_info *ret)
{
    (void)self;
    log_once("XSystemGetAnalyticsInfo");
    if (!ret) return NULL;
    memset(ret, 0, sizeof(*ret));
    ret->os_maj = 10;
    ret->os_bld = 26100;
    ret->host_maj = 10;
    ret->host_bld = 26100;
    memcpy(ret->family, "Windows.Desktop", 16);
    memcpy(ret->form, "Desktop", 8);
    return ret;
}
static void *analytics_vtbl[] = { gen_qi, gen_addref, gen_release, analytics_get };
static com_obj analytics_obj = { analytics_vtbl };
static HRESULT WINAPI analytics_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Analytics };
    return gen_qi(self, iid, out, ok, 1);
}

static HRESULT WINAPI pls_size(void *self, SIZE_T *pathSize)
{
    (void)self;
    if (!pathSize) return E_POINTER_;
    *pathSize = strlen(pls_path_str()) + 1;
    return S_OK;
}
static HRESULT WINAPI pls_path(void *self, SIZE_T pathSize, char *path, SIZE_T *used)
{
    const char *pls = pls_path_str();
    SIZE_T n = strlen(pls) + 1;
    (void)self;
    log_once("XPersistentLocalStorageGetPath");
    CreateDirectoryA(g_pls_parent, NULL);
    CreateDirectoryA(pls, NULL);
    if (used) *used = n;
    if (!path || pathSize < n) return E_INSUFFICIENT_;
    memcpy(path, pls, n);
    return S_OK;
}
static HRESULT WINAPI pls_space(void *self, UINT64 *info)
{
    (void)self;
    if (!info) return E_POINTER_;
    info[0] = 32ull << 30;
    info[1] = 32ull << 30;
    info[2] = 0;
    info[3] = 64ull << 30;
    return S_OK;
}
static HRESULT WINAPI pls_prompt(void *self, UINT64 bytes, XAsyncBlock *async)
{
    (void)self; (void)bytes;
    log_once("PLS prompt");
    if (!async) return E_INVALIDARG_;
    complete_async(async, S_OK, 0);
    return S_OK;
}
static HRESULT WINAPI pls_prompt_result(void *self, XAsyncBlock *async)
{
    async_state *st = state_of(async);
    (void)self;
    if (!st) return S_OK;
    return st->complete ? st->result : E_PENDING_;
}
static HRESULT WINAPI pls_mount(void *self, const char *pkg, void **mount)
{
    (void)self; (void)mount;
    xlog("PLS mount %s", pkg ? pkg : "");
    return E_NOTIMPL_;
}
static void *pls_vtbl[] = {
    gen_qi, gen_addref, gen_release,
    pls_size, pls_path, pls_space, pls_prompt, pls_prompt_result, pls_mount
};
static com_obj pls_obj = { pls_vtbl };
static HRESULT WINAPI pls_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_PLS, &IID_PLS2, &IID_PLS3 };
    return gen_qi(self, iid, out, ok, 3);
}

static void (__stdcall *g_err_cb)(HRESULT, const char *, void *);
static void *g_err_ctx;

static HRESULT WINAPI err_pad(void *self) { (void)self; return E_NOTIMPL_; }
static void WINAPI err_setcb(void *self, void (__stdcall *cb)(HRESULT, const char *, void *), void *ctx)
{
    (void)self;
    g_err_cb = cb;
    g_err_ctx = ctx;
    log_once("XErrorSetCallback");
}
static void WINAPI err_setopts(void *self, UINT32 a, UINT32 b)
{
    (void)self;
    xlog("XErrorSetOptions %lu %lu", (unsigned long)a, (unsigned long)b);
}
static void *error_vtbl[] = { gen_qi, gen_addref, gen_release, err_pad, err_setcb, err_setopts };
static com_obj error_obj = { error_vtbl };
static HRESULT WINAPI error_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Error };
    return gen_qi(self, iid, out, ok, 1);
}

/* user */

static com_obj user_obj;
static com_obj gamertag_obj;

static char g_gamertag[96];
static char g_xbox_token[12000];
static char g_mc_token[12000];
static char g_playfab_token[12000];
static char g_msa_token[8000];
static unsigned long long g_xuid;
static long long g_token_exp;
static int g_auth_loaded;

static void auth_apply_line(char *line)
{
    char *eq = strchr(line, '=');
    if (!eq) return;
    *eq = 0;
    char *val = eq + 1;
    if (!strcmp(line, "exp")) g_token_exp = atoll(val);
    else if (!strcmp(line, "xuid")) g_xuid = strtoull(val, NULL, 10);
    else if (!strcmp(line, "gamertag")) snprintf(g_gamertag, sizeof g_gamertag, "%s", val);
    else if (!strcmp(line, "xbox")) snprintf(g_xbox_token, sizeof g_xbox_token, "%s", val);
    else if (!strcmp(line, "mc")) snprintf(g_mc_token, sizeof g_mc_token, "%s", val);
    else if (!strcmp(line, "playfab")) snprintf(g_playfab_token, sizeof g_playfab_token, "%s", val);
    else if (!strcmp(line, "msa")) snprintf(g_msa_token, sizeof g_msa_token, "%s", val);
}

static char g_compat_unix[360];
static char g_token_z[420];
static char g_code_z[420];
static char g_err_z[420];
static char g_xauth_unix[420];

static void compat_paths(void)
{
    const char *home = getenv("HOME");
    const char *user;
    char homebuf[240];
    char wine[400];
    size_t i, j;
    if (g_xauth_unix[0]) return;
    /* Wine passes the host's HOME to Windows processes as WINE_HOST_HOME. */
    if (!home || home[0] != '/') home = getenv("WINE_HOST_HOME");
    if (!home || home[0] != '/') {
        user = getenv("USER");
        if (!user || !user[0]) user = getenv("LOGNAME");
        if (!user || !user[0]) {
            xlog("HOME is unset; cannot find ~/.local/share/dungeons2-compat");
            user = "steamuser";
        }
        snprintf(homebuf, sizeof homebuf, "/home/%s", user);
        home = homebuf;
    }
    snprintf(g_compat_unix, sizeof g_compat_unix, "%s/.local/share/dungeons2-compat", home);
    j = 0;
    wine[j++] = 'Z';
    wine[j++] = ':';
    for (i = 0; g_compat_unix[i] && j + 1 < sizeof wine; i++)
        wine[j++] = (g_compat_unix[i] == '/') ? '\\' : g_compat_unix[i];
    wine[j] = 0;
    snprintf(g_token_z, sizeof g_token_z, "%s\\tokens.txt", wine);
    snprintf(g_code_z, sizeof g_code_z, "%s\\login-code.txt", wine);
    snprintf(g_err_z, sizeof g_err_z, "%s\\login-error.txt", wine);
    snprintf(g_xauth_unix, sizeof g_xauth_unix, "%s/xauth.py", g_compat_unix);
}

static int auth_read_file(void)
{
    const char *paths[2];
    FILE *f = NULL;
    char line[16000];
    int i;
    compat_paths();
    paths[0] = "C:\\users\\steamuser\\AppData\\Local\\Dungeons2\\tokens.txt";
    paths[1] = g_token_z;
    for (i = 0; i < 2 && !f; i++) f = fopen(paths[i], "r");
    if (!f) {
        log_once("auth file missing");
        return 0;
    }
    g_xbox_token[0] = g_mc_token[0] = g_playfab_token[0] = g_msa_token[0] = g_gamertag[0] = 0;
    g_xuid = 0;
    g_token_exp = 0;
    while (fgets(line, sizeof line, f)) {
        size_t n = strlen(line);
        while (n && (line[n - 1] == '\n' || line[n - 1] == '\r')) line[--n] = 0;
        auth_apply_line(line);
    }
    fclose(f);
    /* a cache from before the PlayFab token existed must be renewed */
    g_auth_loaded = g_xbox_token[0] && g_playfab_token[0] && g_token_exp > (long long)time(NULL) + 30;
    if (g_auth_loaded) log_once("auth file loaded");
    else log_once("auth file unusable");
    return g_auth_loaded;
}

static DWORD WINAPI auth_prompt(void *unused)
{
    FILE *f;
    char url[256], code[64], msg[400];
    (void)unused;
    compat_paths();
    f = fopen(g_code_z, "r");
    url[0] = code[0] = 0;
    if (f) {
        fgets(url, sizeof url, f);
        fgets(code, sizeof code, f);
        fclose(f);
    }
    snprintf(msg, sizeof msg, "Sign in with your Microsoft account.\n\n%s\nCode: %s", url, code);
    xlog("microsoft login code %s", code);
    MessageBoxA(NULL, msg, "Minecraft Dungeons II sign-in", MB_OK | MB_SETFOREGROUND);
    return 0;
}

static int auth_ensure(void)
{
    char *argv[6];
    LONG (WINAPI *spawn)(char *const *, int);
    LONG status;
    int i, prompted = 0;
    compat_paths();
    if (auth_read_file()) return 1;
    DeleteFileA(g_err_z);
    DeleteFileA(g_code_z);
    xlog("starting Microsoft sign-in");
    /* start.exe /unix hands an extensionless Unix binary to ShellExecuteEx, which finds no
     * association for it and puts up an error box; spawn it the way winebrowser does. */
    /* Wine runs under Rosetta on Apple silicon, so a universal binary it starts runs as x86_64,
     * and /usr/bin/python3 then cannot load xcrun. arch starts the native slice first. */
    if (GetFileAttributesA("Z:\\System\\Library\\CoreServices\\SystemVersion.plist") != INVALID_FILE_ATTRIBUTES) {
        argv[0] = (char *)"/usr/bin/arch";
        argv[1] = (char *)"-arm64";
        argv[2] = (char *)"-x86_64";
        argv[3] = (char *)"/usr/bin/python3";
        argv[4] = g_xauth_unix;
        argv[5] = NULL;
    } else {
        argv[0] = (char *)"/usr/bin/python3";
        argv[1] = g_xauth_unix;
        argv[2] = NULL;
    }
    spawn = (void *)GetProcAddress(GetModuleHandleA("ntdll.dll"), "__wine_unix_spawnvp");
    status = spawn ? spawn(argv, 0) : -1;
    if (status) {
        xlog("login spawn failed %#lx", (unsigned long)status);
        return 0;
    }
    for (i = 0; i < 240; i++) {
        FILE *err;
        if (auth_read_file()) {
            xlog("microsoft sign-in ok xuid=%llu", g_xuid);
            return 1;
        }
        err = fopen(g_err_z, "r");
        if (err) {
            char buf[300];
            if (!fgets(buf, sizeof buf, err)) buf[0] = 0;
            fclose(err);
            xlog("microsoft sign-in failed %s", buf);
            return 0;
        }
        if (!prompted && GetFileAttributesA(g_code_z) != INVALID_FILE_ATTRIBUTES) {
            prompted = 1;
            CreateThread(NULL, 0, auth_prompt, NULL, 0, NULL);
        }
        Sleep(1000);
    }
    xlog("microsoft sign-in timed out");
    return 0;
}

static const char *auth_token_for(const char *url)
{
    /* PlayFab only accepts tokens for its own relying party */
    if (url && strstr(url, "playfabapi.com") && g_playfab_token[0]) return g_playfab_token;
    if (url && (strstr(url, "minecraft") || strstr(url, "Minecraft"))) {
        if (g_mc_token[0]) return g_mc_token;
    }
    return g_xbox_token;
}

static const char *gamertag_for(UINT32 component)
{
    if (component == 2) return "";
    auth_read_file();
    if (g_gamertag[0]) return g_gamertag;
    return "Player";
}

static HRESULT WINAPI user_dup(void *self, void *user, void **out)
{
    (void)self;
    if (!out) return E_POINTER_;
    *out = user ? user : (void *)&user_obj;
    return S_OK;
}
static void WINAPI user_close(void *self, void *user) { (void)self; (void)user; }
static INT32 WINAPI user_cmp(void *self, void *a, void *b)
{
    (void)self;
    if (a == b) return 0;
    return (a < b) ? -1 : 1;
}
static HRESULT WINAPI user_max(void *self, UINT32 *max)
{
    (void)self;
    if (!max) return E_POINTER_;
    *max = 4;
    return S_OK;
}
static HRESULT WINAPI user_add_async(void *self, UINT32 options, XAsyncBlock *async)
{
    async_state *st;
    XAsyncProviderData data;
    HRESULT hr;
    (void)self;
    xlog("XUserAddAsync opts=%lu", (unsigned long)options);
    if (!async) return E_INVALIDARG_;
    st = calloc(1, sizeof(*st));
    if (!st) return E_FAIL_;
    st->magic = ASYNC_MAGIC;
    st->block = async;
    st->provider = user_add_provider;
    st->payload = &user_obj;
    snprintf(st->name, sizeof(st->name), "XUserAdd");
    state_bind(async, st);
    memset(&data, 0, sizeof(data));
    data.async = async;
    hr = user_add_provider(OP_BEGIN, &data);
    if (FAILED(hr)) { cleanup_state(st); return hr; }
    return schedule_async(async, 0);
}
static HRESULT WINAPI user_add_result(void *self, XAsyncBlock *async, void **newUser)
{
    async_state *st = state_of(async);
    (void)self;
    if (!newUser) return E_POINTER_;
    if (!st) return E_INVALIDARG_;
    if (!st->complete) return E_PENDING_;
    if (FAILED(st->result)) return st->result;
    *newUser = &user_obj;
    log_once("XUserAddResult");
    return S_OK;
}
static HRESULT WINAPI user_local_id(void *self, void *user, UINT64 *id)
{
    (void)self; (void)user;
    if (!id) return E_POINTER_;
    *id = 1;
    return S_OK;
}
static HRESULT WINAPI user_find_local(void *self, UINT64 id, void **handle)
{
    (void)self;
    if (!handle) return E_POINTER_;
    if (id != 1) return E_FAIL_;
    *handle = &user_obj;
    return S_OK;
}
static HRESULT WINAPI user_get_id(void *self, void *user, UINT64 *id)
{
    (void)self; (void)user;
    log_once("XUserGetId");
    if (!id) return E_POINTER_;
    auth_read_file();
    *id = g_xuid ? g_xuid : 1;
    xlog("XUserGetId value %llu", (unsigned long long)*id);
    return S_OK;
}
static HRESULT WINAPI user_find_id(void *self, UINT64 id, void **handle)
{
    (void)self;
    if (!handle) return E_POINTER_;
    auth_read_file();
    if (id != 1 && id != g_xuid) {
        xlog("XUserFindUserById miss %llu", (unsigned long long)id);
        return E_FAIL_;
    }
    *handle = &user_obj;
    return S_OK;
}
static HRESULT WINAPI user_guest(void *self, void *user, BOOLEAN *guest)
{
    (void)self; (void)user;
    if (!guest) return E_POINTER_;
    *guest = FALSE;
    return S_OK;
}
static HRESULT WINAPI user_state(void *self, void *user, UINT32 *state)
{
    (void)self; (void)user;
    log_once("XUserGetState");
    if (!state) return E_POINTER_;
    *state = 0; /* SignedIn */
    return S_OK;
}
static HRESULT WINAPI user_pic_async(void *self, void *user, UINT32 size, XAsyncBlock *async)
{
    (void)self; (void)user; (void)size; (void)async;
    log_once("XUserGetGamerPictureAsync");
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_pic_size(void *self, XAsyncBlock *async, SIZE_T *sz)
{
    (void)self; (void)async; (void)sz;
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_pic_result(void *self, XAsyncBlock *async, SIZE_T sz, void *buf, SIZE_T *used)
{
    (void)self; (void)async; (void)sz; (void)buf; (void)used;
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_age(void *self, void *user, UINT32 *age)
{
    (void)self; (void)user;
    if (!age) return E_POINTER_;
    *age = 3; /* Adult */
    return S_OK;
}
static HRESULT WINAPI user_priv(void *self, void *user, UINT32 opts, UINT32 priv, BOOLEAN *has, UINT32 *reason)
{
    static uint64_t seen[4];
    (void)self; (void)user; (void)opts;
    if ((priv >> 6) < 4 && (seen[priv >> 6] & (1ull << (priv & 63))) == 0) {
        seen[priv >> 6] |= 1ull << (priv & 63);
        xlog("privilege %lu", (unsigned long)priv);
    }
    if (has) *has = TRUE;
    if (reason) *reason = 0;
    return S_OK;
}
static HRESULT WINAPI user_resolve_priv_async(void *self, void *user, UINT32 opts, UINT32 priv, XAsyncBlock *async)
{
    (void)self; (void)user; (void)opts; (void)priv; (void)async;
    log_once("XUserResolvePrivilegeWithUiAsync");
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_resolve_priv_result(void *self, XAsyncBlock *async)
{
    (void)self; (void)async;
    return E_NOTIMPL_;
}
typedef struct token_blob {
    SIZE_T tokenSize;
    SIZE_T signatureSize;
    const char *token;
    const char *signature;
} token_blob;

static HRESULT WINAPI token_provider(UINT32 op, const XAsyncProviderData *data)
{
    async_state *st;
    const char *url;
    const char *tok;
    if (op == OP_CLEANUP) {
        free(data->context);
        return S_OK;
    }
    if (op == OP_GETRESULT) {
        st = state_of(data->async);
        tok = (st && st->payload) ? (const char *)st->payload : "";
        if (data->buffer && data->bufferSize >= sizeof(token_blob) + strlen(tok) + 2) {
            token_blob *blob = data->buffer;
            char *dst = (char *)(blob + 1);
            memcpy(dst, tok, strlen(tok) + 1);
            dst[strlen(tok) + 1] = 0;
            blob->tokenSize = strlen(tok) + 1;
            blob->signatureSize = 1;
            blob->token = dst;
            blob->signature = dst + blob->tokenSize;
        }
        return S_OK;
    }
    if (op != OP_DOWORK) return S_OK;
    st = state_of(data->async);
    url = st ? (const char *)st->context : NULL;
    if (!auth_ensure()) {
        complete_async(data->async, E_FAIL_, 0);
        return S_OK;
    }
    tok = auth_token_for(url);
    if (st) st->payload = (void *)tok;
    complete_async(data->async, S_OK, sizeof(token_blob) + strlen(tok) + 2);
    return S_OK;
}

static HRESULT start_token_async(XAsyncBlock *async, const char *url, const char *name)
{
    async_state *st;
    XAsyncProviderData data;
    HRESULT hr;
    if (!async) return E_INVALIDARG_;
    st = calloc(1, sizeof(*st));
    if (!st) return E_FAIL_;
    st->magic = ASYNC_MAGIC;
    st->block = async;
    st->context = (url && url[0]) ? strdup(url) : NULL;
    st->provider = token_provider;
    snprintf(st->name, sizeof st->name, "%s", name);
    state_bind(async, st);
    memset(&data, 0, sizeof data);
    data.async = async;
    data.context = st->context;
    hr = token_provider(OP_BEGIN, &data);
    if (FAILED(hr)) { cleanup_state(st); return hr; }
    return schedule_async(async, 0);
}

static HRESULT WINAPI user_token_async(void *self, void *user, UINT32 opts, const char *method, const char *url,
                                       SIZE_T headerCount, const void *headers, SIZE_T bodySize, const void *body, XAsyncBlock *async)
{
    (void)self; (void)user; (void)opts; (void)headerCount; (void)headers; (void)bodySize; (void)body;
    xlog("token %s %s", method ? method : "?", url ? url : "");
    return start_token_async(async, url, "XUserToken");
}
static HRESULT WINAPI user_token_size(void *self, XAsyncBlock *async, SIZE_T *sz)
{
    async_state *st = state_of(async);
    (void)self;
    if (!sz) return E_POINTER_;
    if (!st || !st->complete) return E_PENDING_;
    if (FAILED(st->result)) return st->result;
    *sz = st->required;
    return S_OK;
}
static HRESULT WINAPI user_token_result(void *self, XAsyncBlock *async, SIZE_T sz, void *buf, void *ptr, SIZE_T *used)
{
    async_state *st = state_of(async);
    token_blob *blob;
    const char *tok;
    char *dst;
    SIZE_T need;
    (void)self;
    if (!st || !st->complete) return E_PENDING_;
    if (FAILED(st->result)) return st->result;
    tok = st->payload ? (const char *)st->payload : "";
    need = sizeof(token_blob) + strlen(tok) + 2;
    if (!buf || sz < need) return E_INSUFFICIENT_;
    blob = buf;
    dst = (char *)(blob + 1);
    memcpy(dst, tok, strlen(tok) + 1);
    dst[strlen(tok) + 1] = 0;
    blob->tokenSize = strlen(tok) + 1;
    blob->signatureSize = 1;
    blob->token = dst;
    blob->signature = dst + blob->tokenSize;
    if (ptr) *(void **)ptr = blob;
    if (used) *used = need;
    return S_OK;
}
static HRESULT WINAPI user_token16_async(void *self, void *user, UINT32 opts, const WCHAR *method, const WCHAR *url,
                                         SIZE_T headerCount, const void *headers, SIZE_T bodySize, const void *body, XAsyncBlock *async)
{
    char url8[512];
    (void)self; (void)user; (void)opts; (void)method; (void)headerCount; (void)headers; (void)bodySize; (void)body;
    url8[0] = 0;
    if (url) WideCharToMultiByte(CP_UTF8, 0, url, -1, url8, sizeof url8, NULL, NULL);
    xlog("token utf16 %s", url8);
    return start_token_async(async, url8[0] ? url8 : NULL, "XUserToken16");
}
static HRESULT WINAPI user_issue_async(void *self, void *user, const char *url, XAsyncBlock *async)
{
    (void)self; (void)user; (void)async;
    xlog("resolve issue %s", url ? url : "");
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_issue_result(void *self, XAsyncBlock *async)
{
    (void)self; (void)async;
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_issue16_async(void *self, void *user, const WCHAR *url, XAsyncBlock *async)
{
    (void)self; (void)user; (void)url; (void)async;
    log_once("resolve issue utf16");
    return E_NOTIMPL_;
}
typedef void (__stdcall *user_change_fn)(void *context, UINT64 localId, UINT32 event);
static user_change_fn g_change_cb;
static void *g_change_ctx;
static void __stdcall deliver_user_change(void *ctx, BOOLEAN canceled)
{
    (void)ctx; (void)canceled;
    xlog("deliver user change");
    if (g_change_cb) g_change_cb(g_change_ctx, 1, 0);
}
static HRESULT WINAPI user_reg_change(void *self, void *q, void *ctx, void *cb, UINT64 *token)
{
    (void)self;
    g_change_cb = (user_change_fn)cb;
    g_change_ctx = ctx;
    xlog("XUserRegisterForChangeEvent q=%p", q);
    if (token) *token = 1;
    if (cb) thr_Submit(NULL, (queue_obj *)q, PORT_COMP, NULL, deliver_user_change);
    return S_OK;
}
static BOOLEAN WINAPI user_unreg_change(void *self, UINT64 token, BOOLEAN wait)
{
    (void)self; (void)token; (void)wait;
    return TRUE;
}
static HRESULT WINAPI user_deferral(void *self, void **out)
{
    (void)self;
    if (!out) return E_POINTER_;
    *out = &user_obj;
    return S_OK;
}
static void WINAPI user_close_deferral(void *self, void *d) { (void)self; (void)d; }
static HRESULT WINAPI user_add_by_id(void *self, UINT64 id, XAsyncBlock *async)
{
    xlog("XUserAddByIdWithUiAsync id=%llu", (unsigned long long)id);
    return user_add_async(self, 0, async);
}
static HRESULT WINAPI user_add_by_id_result(void *self, XAsyncBlock *async, void **user)
{
    return user_add_result(self, async, user);
}
static HRESULT WINAPI msa_provider(UINT32 op, const XAsyncProviderData *data)
{
    async_state *st;
    if (op == OP_GETRESULT) {
        st = state_of(data->async);
        const char *src = (st && st->payload) ? (const char *)st->payload : "";
        SIZE_T n = strlen(src) + 1;
        if (data->buffer && data->bufferSize >= n) memcpy(data->buffer, src, n);
        return S_OK;
    }
    if (op != OP_DOWORK) return S_OK;
    st = state_of(data->async);
    if (!auth_ensure()) {
        complete_async(data->async, E_FAIL_, 0);
        return S_OK;
    }
    if (st) st->payload = g_msa_token;
    complete_async(data->async, S_OK, strlen(g_msa_token) + 1);
    return S_OK;
}
static HRESULT WINAPI user_msa_async(void *self, void *user, UINT32 opts, const char *scope, XAsyncBlock *async)
{
    async_state *st;
    XAsyncProviderData data;
    HRESULT hr;
    (void)self; (void)user; (void)opts;
    xlog("msa token %s", scope ? scope : "");
    if (!async) return E_INVALIDARG_;
    st = calloc(1, sizeof(*st));
    if (!st) return E_FAIL_;
    st->magic = ASYNC_MAGIC;
    st->block = async;
    st->provider = msa_provider;
    snprintf(st->name, sizeof st->name, "XUserMsa");
    state_bind(async, st);
    memset(&data, 0, sizeof data);
    data.async = async;
    hr = msa_provider(OP_BEGIN, &data);
    if (FAILED(hr)) { cleanup_state(st); return hr; }
    return schedule_async(async, 0);
}
static HRESULT WINAPI user_msa_result(void *self, XAsyncBlock *async, SIZE_T cap, char *tok, SIZE_T *used)
{
    async_state *st = state_of(async);
    const char *src;
    SIZE_T n;
    (void)self;
    if (!st || !st->complete) return E_PENDING_;
    if (FAILED(st->result)) return st->result;
    src = st->payload ? (const char *)st->payload : "";
    n = strlen(src) + 1;
    if (used) *used = n;
    if (!tok || cap < n) return E_INSUFFICIENT_;
    memcpy(tok, src, n);
    return S_OK;
}
static HRESULT WINAPI user_msa_size(void *self, XAsyncBlock *async, SIZE_T *sz)
{
    async_state *st = state_of(async);
    (void)self;
    if (!sz) return E_POINTER_;
    if (!st || !st->complete) return E_PENDING_;
    if (FAILED(st->result)) return st->result;
    *sz = st->required;
    return S_OK;
}
static BOOLEAN WINAPI user_is_store(void *self, void *user)
{
    (void)self; (void)user;
    log_once("XUserIsStoreUser");
    return FALSE;
}
static HRESULT WINAPI user_remote_set(void *self, void *q, void *handlers)
{
    (void)self; (void)q; (void)handlers;
    log_once("remote connect handlers");
    return S_OK;
}
static HRESULT WINAPI user_remote_cancel(void *self, void *op)
{
    (void)self; (void)op;
    return S_OK;
}
static HRESULT WINAPI user_spop_set(void *self, void *q, void *handler, void *ctx)
{
    (void)self; (void)q; (void)handler; (void)ctx;
    log_once("spop handlers");
    return S_OK;
}
static HRESULT WINAPI user_spop_complete(void *self, void *op, UINT32 result)
{
    (void)self; (void)op; (void)result;
    return S_OK;
}
static BOOLEAN WINAPI user_signout_present(void *self)
{
    (void)self;
    return FALSE;
}
static HRESULT WINAPI user_signout_async(void *self, void *user, XAsyncBlock *async)
{
    (void)self; (void)user; (void)async;
    log_once("XUserSignOutAsync");
    return E_NOTIMPL_;
}
static HRESULT WINAPI user_signout_result(void *self, XAsyncBlock *async)
{
    (void)self; (void)async;
    return E_NOTIMPL_;
}

static void *user_vtbl[] = {
    gen_qi, gen_addref, gen_release,
    user_dup, user_close, user_cmp, user_max, user_add_async, user_add_result,
    user_local_id, user_find_local, user_get_id, user_find_id, user_guest, user_state,
    stub_notimpl,
    user_pic_async, user_pic_size, user_pic_result, user_age, user_priv,
    user_resolve_priv_async, user_resolve_priv_result,
    user_token_async, user_token_size, user_token_result,
    user_token16_async, user_token_size, user_token_result,
    user_issue_async, user_issue_result, user_issue16_async, user_issue_result,
    user_reg_change, user_unreg_change, user_deferral, user_close_deferral,
    user_add_by_id, user_add_by_id_result,
    user_msa_async, user_msa_result, user_msa_size,
    user_is_store,
    user_remote_set, user_remote_cancel, user_spop_set, user_spop_complete,
    user_signout_present, user_signout_async, user_signout_result
};
static HRESULT WINAPI user_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_User, &IID_User2, &IID_User3, &IID_User4, &IID_User5, &IID_User6 };
    if (iid && guid_eq(iid, &IID_Gamertag)) {
        if (out) *out = &gamertag_obj;
        return S_OK;
    }
    return gen_qi(self, iid, out, ok, 6);
}

static HRESULT WINAPI tag_get(void *self, void *user, UINT32 component, SIZE_T cap, char *buf, SIZE_T *used)
{
    const char *s = gamertag_for(component);
    SIZE_T n = strlen(s) + 1;
    (void)self; (void)user;
    xlog("gamertag component %lu", (unsigned long)component);
    if (used) *used = n;
    if (!buf || cap < n) return E_INSUFFICIENT_;
    memcpy(buf, s, n);
    return S_OK;
}
static void *gamertag_vtbl[] = { gen_qi, gen_addref, gen_release, tag_get };
static HRESULT WINAPI gamertag_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Gamertag };
    if (iid && (guid_eq(iid, &IID_User) || guid_eq(iid, &IID_User6))) {
        if (out) *out = &user_obj;
        return S_OK;
    }
    return gen_qi(self, iid, out, ok, 1);
}

/* Fix QI slots now that wrappers exist. user_obj/gamertag_obj defined above. */
static HRESULT WINAPI proto_reg(void *self, void *queue, void *context, void *callback, UINT64 *token)
{
    (void)self; (void)queue; (void)context; (void)callback;
    log_once("XGameProtocolRegisterForActivation");
    if (token) *token = 1;
    return S_OK;
}
static BOOLEAN WINAPI proto_unreg(void *self, UINT64 token, BOOLEAN wait)
{
    (void)self; (void)token; (void)wait;
    return TRUE;
}
static HRESULT WINAPI net_port(void *self, UINT16 *port)
{
    (void)self;
    log_once("XNetworkingQueryPreferredLocalUdpMultiplayerPort");
    if (!port) return E_POINTER_;
    *port = 3074;
    return S_OK;
}
static HRESULT WINAPI net_port_async(void *self, XAsyncBlock *async)
{
    (void)self; (void)async;
    log_once("udp port async");
    return E_NOTIMPL_;
}
static HRESULT WINAPI net_port_result(void *self, XAsyncBlock *async, UINT16 *port)
{
    (void)self; (void)async;
    if (!port) return E_POINTER_;
    *port = 3074;
    return S_OK;
}
static HRESULT WINAPI net_reg_port(void *self, void *q, void *ctx, void *cb, UINT64 *token)
{
    (void)self; (void)q; (void)ctx; (void)cb;
    log_once("reg udp port");
    if (token) *token = 1;
    return S_OK;
}
static BOOLEAN WINAPI net_unreg_port(void *self, UINT64 token, BOOLEAN wait)
{
    (void)self; (void)token; (void)wait;
    return TRUE;
}
typedef struct net_sec_info {
    UINT32 flags;
    SIZE_T count;
    void *prints;
} net_sec_info;

/* XCurl passes this dword straight to WINHTTP_OPTION_SECURE_PROTOCOLS.
 * Those are WinHTTP bits: TLS1.2 = 0x800, TLS1.3 = 0x2000. The value 0xC
 * makes schannel fail the handshake before any request is sent. */
#define WINHTTP_TLS12 0x800u
#define WINHTTP_TLS13 0x2000u
#define WINHTTP_OPT_PROTOCOLS 84u
#define WINHTTP_OPT_IPV6_FAST_FALLBACK 140u
#define WINHTTP_OPT_DECOMPRESSION 118u
#define WINHTTP_ERR_INVALID_OPTION 12009u

static BOOL (WINAPI *real_set_option)(void *, DWORD, void *, DWORD);
static void *(WINAPI *real_connect)(void *, const WCHAR *, unsigned short, DWORD);
static void *(WINAPI *real_open_request)(void *, const WCHAR *, const WCHAR *, const WCHAR *, const WCHAR *, const WCHAR **, DWORD);
static BOOL (WINAPI *real_send)(void *, const WCHAR *, DWORD, void *, DWORD, DWORD, DWORD_PTR);
static BOOL (WINAPI *real_recv)(void *, void *);
static BOOL (WINAPI *real_query)(void *, DWORD, const WCHAR *, void *, DWORD *, DWORD *);
static BOOL (WINAPI *real_read)(void *, void *, DWORD, DWORD *);

static void *http_handles[24];
static int http_codes[24];
static int http_next;
static int http_status_of(void *req)
{
    int i;
    for (i = 0; i < 24; i++) if (http_handles[i] == req) return http_codes[i];
    return 0;
}
static void http_status_set(void *req, int code)
{
    int i;
    for (i = 0; i < 24; i++) if (http_handles[i] == req) { http_codes[i] = code; return; }
    http_handles[http_next % 24] = req;
    http_codes[http_next % 24] = code;
    http_next++;
}

static BOOL WINAPI hook_set_option(void *handle, DWORD option, void *buffer, DWORD length)
{
    DWORD fixed;
    BOOL ok;
    if (option == WINHTTP_OPT_IPV6_FAST_FALLBACK)
        return TRUE; /* wine returns 12009; XCurl treats that as fatal and never connects */
    if (option == WINHTTP_OPT_PROTOCOLS && buffer && length >= sizeof(DWORD)) {
        if ((*(DWORD *)buffer & WINHTTP_TLS12) == 0) {
            fixed = WINHTTP_TLS12 | WINHTTP_TLS13;
            return real_set_option(handle, option, &fixed, sizeof fixed);
        }
    }
    ok = real_set_option(handle, option, buffer, length);
    /* CrossOver's WinHTTP (Wine 11.0) has no decompression option either and fails it with
     * 12009, and XCurl abandons the request. XCurl sends no Accept-Encoding of its own, so
     * accepting it only means the reply arrives uncompressed. */
    if (!ok && option == WINHTTP_OPT_DECOMPRESSION && GetLastError() == WINHTTP_ERR_INVALID_OPTION)
        return TRUE;
    return ok;
}
static void *WINAPI hook_connect(void *session, const WCHAR *host, unsigned short port, DWORD reserved)
{
    char host8[200];
    host8[0] = 0;
    if (host) WideCharToMultiByte(CP_UTF8, 0, host, -1, host8, sizeof host8, NULL, NULL);
    if (!strstr(host8, "events.data.microsoft.com"))
        xlog("http connect %s:%u", host8, (unsigned)port);
    return real_connect(session, host, port, reserved);
}
static void *WINAPI hook_open_request(void *connect, const WCHAR *verb, const WCHAR *object, const WCHAR *version,
                                      const WCHAR *referrer, const WCHAR **accept, DWORD flags)
{
    char path[240];
    static int logged;
    path[0] = 0;
    if (object) WideCharToMultiByte(CP_UTF8, 0, object, -1, path, sizeof path, NULL, NULL);
    if (logged < 40 && path[0] && !strstr(path, "OneCollector")) {
        logged++;
        xlog("http %s", path);
    }
    return real_open_request(connect, verb, object, version, referrer, accept, flags);
}
static BOOL WINAPI hook_send(void *request, const WCHAR *headers, DWORD headers_len, void *optional, DWORD optional_len, DWORD total, DWORD_PTR ctx)
{
    BOOL ok = real_send(request, headers, headers_len, optional, optional_len, total, ctx);
    if (!ok) xlog("http send failed %lu", (unsigned long)GetLastError());
    return ok;
}
static BOOL WINAPI hook_recv(void *request, void *reserved)
{
    BOOL ok = real_recv(request, reserved);
    DWORD code = 0, sz = sizeof code;
    if (ok && real_query(request, 19 | 0x20000000, NULL, &code, &sz, NULL)) {
        static int logged;
        http_status_set(request, (int)code);
        if (logged < 40) { logged++; xlog("http status %lu", (unsigned long)code); }
    } else if (!ok) {
        xlog("http recv failed %lu", (unsigned long)GetLastError());
    }
    return ok;
}
static BOOL WINAPI hook_read(void *request, void *buffer, DWORD cap, DWORD *read)
{
    BOOL ok = real_read(request, buffer, cap, read);
    int status = http_status_of(request);
    if (ok && read && *read && status >= 400) {
        static int logged;
        char tmp[180];
        DWORD n = *read;
        if (n > sizeof tmp - 1) n = sizeof tmp - 1;
        memcpy(tmp, buffer, n);
        tmp[n] = 0;
        for (DWORD i = 0; i < n; i++) if (tmp[i] == '\n' || tmp[i] == '\r') tmp[i] = ' ';
        if (logged < 8 && !strstr(tmp, "eyJ") && !strstr(tmp, "XBL3")) {
            logged++;
            xlog("http error body %s", tmp);
        }
    }
    return ok;
}

static void **winhttp_slot(HMODULE mod, const char *name)
{
    unsigned char *base = (unsigned char *)mod;
    IMAGE_NT_HEADERS *nt = (IMAGE_NT_HEADERS *)(base + ((IMAGE_DOS_HEADER *)base)->e_lfanew);
    IMAGE_DATA_DIRECTORY *dir = &nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    IMAGE_IMPORT_DESCRIPTOR *imp;
    if (!dir->VirtualAddress) return NULL;
    for (imp = (IMAGE_IMPORT_DESCRIPTOR *)(base + dir->VirtualAddress); imp->Name; imp++) {
        IMAGE_THUNK_DATA *names, *slots;
        if (_stricmp((const char *)(base + imp->Name), "WINHTTP.dll")) continue;
        names = (IMAGE_THUNK_DATA *)(base + (imp->OriginalFirstThunk ? imp->OriginalFirstThunk : imp->FirstThunk));
        slots = (IMAGE_THUNK_DATA *)(base + imp->FirstThunk);
        for (; names->u1.AddressOfData; names++, slots++) {
            if (IMAGE_SNAP_BY_ORDINAL(names->u1.Ordinal)) continue;
            if (!strcmp((const char *)((IMAGE_IMPORT_BY_NAME *)(base + names->u1.AddressOfData))->Name, name))
                return (void **)&slots->u1.Function;
        }
    }
    return NULL;
}

static void patch_slot(void **slot, void *hook, void **saved)
{
    DWORD old;
    if (!VirtualProtect(slot, sizeof *slot, PAGE_READWRITE, &old)) return;
    *saved = *slot;
    *slot = hook;
    VirtualProtect(slot, sizeof *slot, old, &old);
}
static void hook_xcurl_winhttp(void)
{
    HMODULE mod;
    void **set_option, **connect, **open_request, **send, **recv, **query, **read;
    if (real_set_option) return;
    mod = GetModuleHandleW(L"XCurl.dll");
    if (!mod) return;
    /* By name rather than by RVA, so a game update that moves XCurl's IAT does not
     * have these write over whatever sits at the old addresses. */
    set_option = winhttp_slot(mod, "WinHttpSetOption");
    connect = winhttp_slot(mod, "WinHttpConnect");
    open_request = winhttp_slot(mod, "WinHttpOpenRequest");
    send = winhttp_slot(mod, "WinHttpSendRequest");
    recv = winhttp_slot(mod, "WinHttpReceiveResponse");
    query = winhttp_slot(mod, "WinHttpQueryHeaders");
    read = winhttp_slot(mod, "WinHttpReadData");
    if (!set_option || !connect || !open_request || !send || !recv || !query || !read) {
        xlog("XCurl.dll does not import the WinHTTP calls this expects; not hooking");
        return;
    }
    real_query = *query;
    patch_slot(set_option, (void *)hook_set_option, (void **)&real_set_option);
    patch_slot(connect, (void *)hook_connect, (void **)&real_connect);
    patch_slot(open_request, (void *)hook_open_request, (void **)&real_open_request);
    patch_slot(send, (void *)hook_send, (void **)&real_send);
    patch_slot(recv, (void *)hook_recv, (void **)&real_recv);
    patch_slot(read, (void *)hook_read, (void **)&real_read);
    xlog("hooked XCurl WinHTTP");
}

static void fill_sec(net_sec_info *out)
{
    out->flags = WINHTTP_TLS12 | WINHTTP_TLS13;
    out->count = 0;
    out->prints = NULL;
}
static HRESULT WINAPI sec_provider(UINT32 op, const XAsyncProviderData *data)
{
    if (op == OP_DOWORK) complete_async(data->async, S_OK, sizeof(net_sec_info));
    if (op == OP_GETRESULT && data->buffer && data->bufferSize >= sizeof(net_sec_info)) {
        fill_sec(data->buffer);
        log_once("security result tls");
    }
    return S_OK;
}
static HRESULT start_sec_async(XAsyncBlock *async, const char *url)
{
    async_state *st;
    XAsyncProviderData data;
    HRESULT hr;
    xlog("security for %s", url ? url : "");
    hook_xcurl_winhttp();
    if (!async) return E_INVALIDARG_;
    st = calloc(1, sizeof(*st));
    if (!st) return E_FAIL_;
    st->magic = ASYNC_MAGIC;
    st->block = async;
    st->provider = sec_provider;
    snprintf(st->name, sizeof st->name, "XNetSecurity");
    state_bind(async, st);
    memset(&data, 0, sizeof data);
    data.async = async;
    hr = sec_provider(OP_BEGIN, &data);
    if (FAILED(hr)) { cleanup_state(st); return hr; }
    return schedule_async(async, 0);
}
static HRESULT WINAPI net_sec_async(void *self, const char *url, XAsyncBlock *async)
{
    (void)self;
    return start_sec_async(async, url);
}
static HRESULT WINAPI net_sec_size(void *self, XAsyncBlock *async, SIZE_T *n)
{
    async_state *st = state_of(async);
    (void)self;
    if (!n) return E_POINTER_;
    if (!st || !st->complete) return E_PENDING_;
    *n = sizeof(net_sec_info);
    return S_OK;
}
static HRESULT WINAPI net_sec_result(void *self, XAsyncBlock *async, SIZE_T cap, SIZE_T *used, void *buf, void *info)
{
    net_sec_info *out;
    (void)self; (void)async;
    if (!buf || cap < sizeof(net_sec_info)) return E_INSUFFICIENT_;
    out = buf;
    fill_sec(out);
    log_once("security result tls");
    if (info) *(void **)info = out;
    if (used) *used = sizeof(net_sec_info);
    return S_OK;
}
static HRESULT WINAPI net_sec16_async(void *self, const WCHAR *url, XAsyncBlock *async)
{
    char url8[512];
    (void)self;
    url8[0] = 0;
    if (url) WideCharToMultiByte(CP_UTF8, 0, url, -1, url8, sizeof url8, NULL, NULL);
    return start_sec_async(async, url8);
}
static HRESULT WINAPI net_verify(void *self, void *req, const void *info)
{
    (void)self; (void)req; (void)info;
    log_once("verify cert");
    return S_OK;
}
static void fill_hint(unsigned char *p)
{
    memset(p, 0, 16);
    ((UINT32 *)p)[0] = 3; /* InternetAccess */
    ((UINT32 *)p)[1] = 1; /* Unrestricted */
    ((UINT32 *)p)[2] = 6; /* ethernet */
    p[12] = 1;            /* networkInitialized */
}
static HRESULT WINAPI net_hint(void *self, void *hint)
{
    (void)self;
    log_once("XNetworkingGetConnectivityHint");
    if (!hint) return E_POINTER_;
    fill_hint(hint);
    return S_OK;
}
static void *g_net_cb, *g_net_ctx;
static void __stdcall deliver_net(void *ctx, BOOLEAN canceled)
{
    unsigned char hint[16];
    (void)ctx; (void)canceled;
    fill_hint(hint);
    if (g_net_cb) ((void (__stdcall *)(void *, const void *))g_net_cb)(g_net_ctx, hint);
}
static HRESULT WINAPI net_reg_hint(void *self, void *q, void *ctx, void *cb, UINT64 *token)
{
    (void)self;
    g_net_cb = cb;
    g_net_ctx = ctx;
    log_once("reg connectivity");
    if (token) *token = 1;
    if (cb) thr_Submit(NULL, (queue_obj *)q, PORT_COMP, NULL, deliver_net);
    return S_OK;
}
static BOOLEAN WINAPI net_unreg_hint(void *self, UINT64 token, BOOLEAN wait)
{
    (void)self; (void)token; (void)wait;
    return TRUE;
}
static HRESULT WINAPI net_get_cfg(void *self, UINT32 setting, UINT64 *value)
{
    (void)self;
    xlog("net cfg %lu", (unsigned long)setting);
    if (!value) return E_POINTER_;
    *value = 4ull << 20;
    return S_OK;
}
static HRESULT WINAPI net_set_cfg(void *self, UINT32 setting, UINT64 value)
{
    (void)self;
    xlog("net set cfg %lu %llu", (unsigned long)setting, (unsigned long long)value);
    return S_OK;
}
static HRESULT WINAPI net_stats(void *self, UINT32 type, void *buf)
{
    (void)self; (void)type;
    if (!buf) return E_POINTER_;
    memset(buf, 0, 40);
    return S_OK;
}
static void *net_vtbl[] = {
    gen_qi, gen_addref, gen_release,
    net_port, net_port_async, net_port_result, net_reg_port, net_unreg_port,
    net_sec_async, net_sec_size, net_sec_result,
    net_sec16_async, net_sec_size, net_sec_result,
    net_verify, net_hint, net_reg_hint, net_unreg_hint,
    net_get_cfg, net_set_cfg, net_stats
};
static com_obj net_obj = { net_vtbl };
static HRESULT WINAPI net_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Net, &IID_Net2 };
    return gen_qi(self, iid, out, ok, 2);
}

static void *protocol_vtbl[] = { gen_qi, gen_addref, gen_release, proto_reg, proto_unreg };
static com_obj protocol_obj = { protocol_vtbl };
static HRESULT WINAPI protocol_qi(com_obj *self, const GUID *iid, void **out)
{
    const GUID *ok[] = { &IID_Protocol };
    return gen_qi(self, iid, out, ok, 1);
}

static void fix_vtbls(void)
{
    ((void **)threading_vtbl)[0] = threading_qi;
    ((void **)feature_vtbl)[0] = feature_qi;
    ((void **)game_vtbl)[0] = game_qi;
    ((void **)system_vtbl)[0] = system_qi;
    ((void **)analytics_vtbl)[0] = analytics_qi;
    ((void **)pls_vtbl)[0] = pls_qi;
    ((void **)error_vtbl)[0] = error_qi;
    ((void **)protocol_vtbl)[0] = protocol_qi;
    ((void **)net_vtbl)[0] = net_qi;
    ((void **)user_vtbl)[0] = user_qi;
    ((void **)gamertag_vtbl)[0] = gamertag_qi;
    user_obj.vtbl = user_vtbl;
    gamertag_obj.vtbl = gamertag_vtbl;
}

static int known_and_qi(const GUID *id, const GUID *iid, void **out)
{
    if (guid_eq(id, &IID_Threading)) return threading_qi(&threading_obj, iid, out);
    if (guid_eq(id, &IID_Feature)) return feature_qi(&feature_obj, iid, out);
    if (guid_eq(id, &IID_User) || guid_eq(id, &IID_User2) || guid_eq(id, &IID_User3) ||
        guid_eq(id, &IID_User4) || guid_eq(id, &IID_User5) || guid_eq(id, &IID_User6) ||
        guid_eq(id, &IID_Gamertag))
        return user_qi(&user_obj, iid ? iid : id, out);
    if (guid_eq(id, &IID_Game) || guid_eq(id, &IID_Game2) || guid_eq(id, &IID_Game3))
        return game_qi(&game_obj, iid, out);
    if (guid_eq(id, &IID_System) || guid_eq(id, &IID_System2) || guid_eq(id, &IID_System3) ||
        guid_eq(id, &IID_System4) || guid_eq(id, &IID_System5))
        return system_qi(&system_obj, iid, out);
    if (guid_eq(id, &IID_Analytics)) return analytics_qi(&analytics_obj, iid, out);
    if (guid_eq(id, &IID_PLS) || guid_eq(id, &IID_PLS2) || guid_eq(id, &IID_PLS3))
        return pls_qi(&pls_obj, iid, out);
    if (guid_eq(id, &IID_Error)) return error_qi(&error_obj, iid, out);
    if (guid_eq(id, &IID_Protocol) || guid_eq(id, &CLSID_Protocol))
        return protocol_qi(&protocol_obj, iid, out);
    if (guid_eq(id, &IID_Net) || guid_eq(id, &IID_Net2))
        return net_qi(&net_obj, iid, out);
    return 1; /* not ours */
}

/* ---------- exports ---------- */

__declspec(dllexport) HRESULT WINAPI InitializeApiImplEx2(UINT64 gdk, UINT64 gs, UINT32 mode, const void *options)
{
    char exe[260];
    if (!g_inited) {
        g_inited = 1;
        fix_vtbls();
        process_queue();
        GetModuleFileNameA(NULL, exe, sizeof(exe));
        xlog("init gdk=%llx gs=%llx mode=%lu exe=%s",
             (unsigned long long)gdk, (unsigned long long)gs, (unsigned long)mode, exe);
    }
    (void)options;
    return S_OK;
}

__declspec(dllexport) HRESULT WINAPI InitializeApiImplEx(UINT64 gdk, UINT64 gs, UINT32 mode)
{
    return InitializeApiImplEx2(gdk, gs, mode, NULL);
}

__declspec(dllexport) HRESULT WINAPI InitializeApiImpl(UINT64 gdk, UINT64 gs)
{
    return InitializeApiImplEx2(gdk, gs, 0, NULL);
}

__declspec(dllexport) HRESULT WINAPI UninitializeApiImpl(void)
{
    log_once("uninit");
    return S_OK;
}

__declspec(dllexport) HRESULT WINAPI XErrorReport(HRESULT hr, const char *msg)
{
    xlog("XErrorReport %08lX %s", (unsigned long)hr, msg ? msg : "");
    if (g_err_cb) g_err_cb(hr, msg, g_err_ctx);
    return S_OK;
}

static GUID g_unknown[48];
static int g_unknown_n;
static int g_unknown_total;

__declspec(dllexport) HRESULT WINAPI QueryApiImpl(const GUID *clsid, const GUID *iid, void **out)
{
    int i, rc;
    if (!out) return E_POINTER_;
    *out = NULL;
    if (!clsid) return E_INVALIDARG_;
    if (!g_inited) InitializeApiImplEx2(0, 0, 0, NULL);
    rc = known_and_qi(clsid, iid ? iid : clsid, out);
    if (rc != 1) return rc;
    if (iid) {
        rc = known_and_qi(iid, iid, out);
        if (rc != 1) return rc;
    }
    g_unknown_total++;
    for (i = 0; i < g_unknown_n; i++) {
        if (guid_eq(&g_unknown[i], clsid)) return E_NOINTERFACE_;
    }
    if (g_unknown_n < (int)(sizeof(g_unknown) / sizeof(g_unknown[0])))
        g_unknown[g_unknown_n++] = *clsid;
    log_guid("unknown", clsid);
    if (iid && !guid_eq(iid, clsid)) log_guid(" unknown-iid", iid);
    if ((g_unknown_total % 500) == 0)
        xlog("unknown total %d", g_unknown_total);
    return E_NOINTERFACE_;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, void *reserved)
{
    (void)inst; (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        g_tls = TlsAlloc();
        InitializeCriticalSection(&g_lock);
        g_lock_ready = 1;
    } else if (reason == DLL_PROCESS_DETACH) {
        if (g_tls != TLS_OUT_OF_INDEXES) TlsFree(g_tls);
    }
    return TRUE;
}
