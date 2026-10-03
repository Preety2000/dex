
// index.js,  Main JavaScript Library, Copyright © 2026 Kautilya, Version: Nt.0.5
!function (e, t) { "use strict"; "object" == typeof module && "object" == typeof module.exports ? module.exports = t(e, !0) : t(e) }("undefined" != typeof window ? window : this, function (t, n) {
    "use strict";
    if (!t.document)
        throw Error("jQuery requires a window with a document");
    const T = (a, b) => typeof a == b
        , C = (a, b) => a?.constructor?.name == b
        , gt = (t, a, b) => (F(a) ? t[a.name] = a : t[a] = b, t)
        , gf = (t, a, b) => (a.forEach(i => t[i] = b[i]), t)
        , gk = (t, a) => (Object.entries(a).forEach(([k, v]) => gt(t, k, v)), t)
        , ga = function ga(a, b = []) { for (const value of a.split(U[0])) b.push(value.toLocaleLowerCase()); return b; }
        , is = value => typeof value != "undefined"
        , set = (t, n, v) => {
            if (typeof t === "boolean") return;
            if (typeof n === "function") v = n, n = n.name;
            t[n] = v;
        }
        , mt = () => {
            let b = history.state;
            if (!b?.__key) {
                b = { ...b, __key: crypto.randomUUID() };
                history.replaceState(b, "", t.location.href);
            }
            return b.__key;
        }
    const U = "/&/ ", D = ga("DIV/SECTION/ARTICLE/HEADER/FOOTER/NAV/MAIN/ASIDE"), G = ga("P/SPAN/H1/H2/H3/H4/H5/H6/BLOCKQUOTE/PRE/HR/BR"), H = ga("STRONG/EM/B/I/MARK/SMALL/ABBR/CITE/CODE/SUB/SUP/TIME/Q"), P = ga("IMG/VIDEO/AUDIO/SOURCE/TRACK/PICTURE/CANVAS/SVG/MAP/AREA/FIGCAPTION/FIGURE"), J = ga("A/NAV/LINK"), K = ga("UL/OL/LI/DL/DT/DD"), L = ga("FORM/INPUT/TEXTAREA/SELECT/OPTION/LABEL/BUTTON/FIELDSET/LEGEND/DATALIST/OPTGROUP/OUTPUT"), M = ga("TABLE/THEAD/TBODY/TFOOT/TR/TH/TD/CAPTION/COLGROUP/COL"), Q = ga("SCRIPT/STYLE/META/TITLE/BASE/NOSCRIPT/TEMPLATE/SLOT/IFRAME/INS"), X = ga("STYLE/IFRAME/SCRIPT/LINK/VIDEO"), Y = ga("DIV/SPAN/P/A/BUTTON/INPUT/TEXTAREA/LABEL/FORM/LIST/IMG/LI/UL/H1/H2/HR/ICON"), Z = ga('CLICK/DBLCLICK/MOUSEDOWN/MOUSEENTER/MOUSEOVER/MOUSELEAVE/MOUSEUP/MOUSEMOVE/KEYDOWN/KEYUP/INPUT/CHANGE/FOCUSIN/FOCUSOUT/SCROLL/SUBMIT/LOAD'),
        E = a => a?.tagName,
        A = a => C(a, "Array"),
        S = a => T(a, "string"),
        N = a => T(a, "number"),
        O = a => T(a, "object"),
        B = a => C(a, "Object"),
        F = a => T(a, "function"),
        I = a => Math.floor(Date.now()) + (N(a) ? a : 0),
        ALT = [...D, ...G, ...H, ...P, ...J, ...K, ...L, ...M, ...Q],
        Is = a => { !S(a) && (a = JSON.stringify(a)); return a; },
        Ss = (a, b) => b.some(e => String(a).includes(e)),
        Gm = (q, a = { method: "post" }) => { B(q) && (a.type = json, a.body = q); return a; },
        Gd = () => { let a = location.hostname.split("."); return a.length == 3 ? (a.shift(), a.join(".")) : undefined };




    function proto(a, b) { F(a) && (b = a, a = a.name), this.__proto__[a] = b }

    class AUTH_TOKEN {
        static reversed(a) { let b = a.split("/"); return b.length == 2 ? b[1] : (b.unshift($.getKey(0)), b.join("/")) }
        static encode(a, b) { let c = btoa(unescape(encodeURIComponent(JSON.stringify(a)))).replace(/=+$/, ""); return b ? c : this.reversed(c) }
        static decode(a) { if (!a) return null; try { return a = this.reversed(a), JSON.parse(decodeURIComponent(escape(atob(a + "=".repeat((4 - a.length % 4) % 4))))) } catch (b) { return null } }
    };
    class MAPX {
        constructor(a = {}) {
            S(a) && (a = JSON.parse(a)); if (a && O(a))
                for (let [k, v] of Object.entries(a)) this[k] = v;
        }
        add(a, b) {
            return B(a)
                ? gk(this, a)
                : A(a) && typeof b == "object"
                    ? gf(this, a, b) : gt(this, a, b)
        }
        get(a, b = null) { return this.hasOwnProperty(a) ? this[a] : b }
        remove(a) { return this.hasOwnProperty(a) ? (delete this[a], this) : this }
    }

    function SEOPES(a) { let b = []; return new (class extends MAPX { push(a) { return b.push(a) } includes(a) { return b.includes(a) } })(a) }
    function mapx(a = {}) {
        let b = { ...a };
        set(b, "get", function (a) { return this[a] });
        set(b, "add", function (a, b) { return this[a] = b, this });
        set(b, "has", function (a) { return Object.hasOwn(this, a) });
        return b
    }
    function isExtend(a) {
        a = F(a) ? $(a, a) : a || $(function Session() { return this; });
        return {
            extend: (b, c) => (F(b) && (c = b, b = b.name), a.add(b, c)),
            export: b => { let c = a.export(b); return a.is(b) && c ? c : a.is(b) },
            bind: (b, c) => { let d = a.export(b); return d && F(c) ? c(d) : void 0 },
            session: a
        }
    }
    function urlParts(u, a) {
        a = new URL(u || t.location.href);
        a = a.pathname.split('/')
        a = a.filter(Boolean);

        return {
            res_: a[0] || null,
            sub_: a[1] || null,
            det_: a[2] || null
        };
    }
    function defProty(a, b) { F(a) && (b = a, a = a.name), Object.__proto__[a] = b }

    const FlEXMAP = (c = {}) => new MAPX(c);
    const Sl = t.location.origin + "/script/";
    const Cl = t.location.origin + "/static/css/";

    function script(p, c) {
        const i = btoa(p); p.includes("http") || (p = Sl + p);
        const b = $.getHtmlBody(); let s = $.weres(`[type="text/javascript"]`).find(e => e.id == i);
        if (!s) {
            s = b.create({ tagName: "script", type: "text/javascript", src: p, id: i });
            s._callbacks = []; s.onload = () => { s._loaded = 1; s._callbacks.forEach(f => f(s)); s._callbacks = [] };
        }
        F(c) && (s._loaded ? c(s) : s._callbacks.push(c)); return s;
    }

    function style(p, cb) {
        if (!p.includes(t.location.hostname)) p = Cl + p;
        if (!p.endsWith(".css")) p += ".css";


        let g = $.weres("link", false);
        if (g.filter(m => m.get("href") == p) <= 0) {
            const l = $.bindFunction(document.head).create({
                tagName: "link",
                rel: "stylesheet",
                type: "text/css",
                href: p
            });
            if (typeof cb === "function") l.onload = cb;
            return l;
        }
    }

    defProty("get", function getValue(name, value = null) {
        return this.hasOwnProperty(name) ? this[name] : value;
    });
    defProty("add", function getValue(name, value = null) {
        return B(name)
            ? gk(this, name)
            : A(name) && typeof value == "object"
                ? gf(this, name, value)
                : gt(this, name, value);
    });

    const LIST = []
        , characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        , oj = "&"
        , qd = "?"
        , json = "json"
        , specialCharsMap = {
            leftBracket: "[",
            rightBracket: "]",
            leftCurly: "{",
            rightCurly: "}",
            forwardSlash: "/",
            ampersand: "&",
            questionMark: "?",
            comma: ",",
            period: ".",
            hash: "#"
        };

    const ks = (e, s = (d) => e.insert(AUTH_TOKEN.encode(d)), r = v => v(AUTH_TOKEN.decode(e.get()) || {})) => ({
        set: (i, v) => r(d => (d[i] = v, s(d))),
        res: i => r(d => i && (delete d[i], s(d)) || e.remove()),
        get: i => r(d => i ? Object.prototype.hasOwnProperty.call(d, i) ? d[i] : null : d)
    })

    function makeid(a = 20) { let b = ""; for (; b.length < a;)b += characters[Math.floor(Math.random() * characters.length)]; return b }
    function getNewClassName(a) {
        const used = new Set([...document.querySelectorAll('*')].flatMap(el => [...el.classList]));
        let id;
        if (a) {
            for (const [n, m] of Object.entries(a)) {
                if (Number(m)) a[n] = `${m}px`;
            }
        }


        let g = Object.entries(this || {});
        if (g.length && O(this)) {
            const result = g.find(e => {
                if (A(e)) {
                    let [, value] = e;
                    return JSON.stringify(value) == JSON.stringify(a)
                }
            });
            if (result) { return result[0] }
        }
        do id = makeid(6);
        while (used.has(id));
        return id;
    };

    class Objects extends MAPX {
        constructor(data = {}) {
            super(data);
        }

        filter(functions, array = []) {
            for (const [name, value] of Object.entries(this)) {
                if (functions(name, value)) {
                    array.push(value)
                }
            }
            return array;
        }

        getter(name, a, b, c, d) {
            return this.hasOwnProperty(name) ? function (value) {
                return F(value)
                    ? typeof a == "undefined" ? value : value(a, b, c, d)
                    : value;
            }(this[name]) : null;
        }

        find(callBack) {
            for (const [key, value] of Object.entries(this)) {
                if (callBack(key, value)) return this[key]
            }
        }
        export(name, value = null) {
            return this.hasOwnProperty(name) ? this[name] : value;
        }

        is(id) {
            if (this.hasOwnProperty(id)) {
                return this[id];
            }

            for (const [key, value] of Object.entries(this)) {
                if (typeof value === 'object' && value !== null) {
                    const result = new Objects(value).is(id);
                    if (result) {
                        return result;
                    }
                }
            }
            return null;
        }

        [Symbol.iterator]() {
            let properties = Object.entries(this);
            let index = 0;
            return {
                next() {
                    if (index < properties.length) {
                        return { value: properties[index++], done: false };
                    } else {
                        return { done: true };
                    }
                }
            };
        }

        get json() {
            return JSON.stringify({ ...this });
        }

        get length() {
            return Object.keys(this).length;
        }
    }

    class URLState {

        constructor(a = true, u = location.href) {
            this.a = a; this.e = true; this.c = new Set; this.u = new URL(u);
            ['popstate', 'hashchange'].forEach(e => window.addEventListener(e, () => this.navigate(location.href)));
            this.check();
        }
        onChange(f) { typeof f == 'function' && this.c.add(f); return this; }
        check() {
            let o = this.o; this.p = new URLSearchParams(this.u.search); this.o = this.u.href;
            Object.assign(this, Object.fromEntries(['href', 'host', 'hostname', 'origin', 'pathname', 'port', 'search', 'protocol'].map(k => [k, this.u[k]])));
            this.e && o != this.o && this.change(); return this;
        }
        change() { this.c.forEach(f => f.call(this, this.u)); }
        push(x = true) { this.a && history.pushState({ u: this.href }, '', this.u); x && this.check(); return this; }
        navigate(u, x = true) { this.u = new URL(u, location.origin); this.p = new URLSearchParams(this.u.search); return this.push(x); }
        get(k) { return this.p.get(k); }
        set(k, v, x = true) { this.p.set(k, v); this.u.search = this.p; return this.push(x); }
        delete(k, x = true) { this.p.delete(k); this.u.search = this.p; return this.push(x); }
        clear(x) { this.p = new URLSearchParams; this.u.search = ''; return x && this.push(x); }
        back() { return history.back(); }
        reload() { return this.a && location.reload(); }

        offEvent(cb, o) { this.e = false; cb.call(this, this.u); this.e = true; o && this.check() }
        path(p) { this.u.pathname = p; return this.push(); }
        append(k, v, x = true) { this.p.append(k, v); this.u.search = this.p; return this.push(x); }
        deleteAll(x = true) { this.u.search = ""; this.p = new URLSearchParams(); return this.push(x); }
        isPath(p) { return this.pathname == p; }
    }

    class URLManager {
        constructor(opreter, url) {
            this.currentUrl = url || t.location.href;
            this.url = new URL(this.currentUrl);
            this.params = new URLSearchParams(this.url.search);
            this.opreter = typeof opreter === "boolean" ? opreter : true;
            this.eventCall = true
            this.functions = () => {
                if (typeof opreter === "undefined") {
                    return;
                }
                return typeof opreter === "function"
                    ? opreter(this)
                    : this.locationRun();
            };

            // Listen to native events
            t.addEventListener('popstate', () => this.check());
            t.addEventListener('hashchange', () => this.check());
            this.check();
        }

        onChange(callback) {
            if (!t.$) t.$ = {};
            if (!t.$.Request$Hooks) {
                t.$.Request$Hooks = [];
            }
            if (typeof callback === 'function') {
                t.$.Request$Hooks.push(callback);
            }
        }

        check() {

            if (this.opreter === false) {
                this.classUpdate();
                this.functions();
                return;
            }
            const newUrl = t.location.href;
            this.url = new URL(t.location.href);
            this.params = new URLSearchParams(this.url.search);

            this.classUpdate();
            this.functions();

            if (newUrl !== this.currentUrl && this.eventCall) {
                this.currentUrl = newUrl;
                for (const cb of t.$?.Request$Hooks || [])
                    cb.call(this, this.url);
            }
        }

        get(name) {
            return this.search.get(name);
        }

        back() {
            return t.history.back();
        }

        classUpdate() {
            const listKey = ["host", "hostname", "href", "origin", "pathname", "port", "protocol"];
            for (const e of listKey) {
                this[e] = this.url[e];
            }
            return this;
        }

        updateHistory(update = true) {
            this.fixHashInUrl();
            let j = this.requestTitle || null;
            let s = { idx: 0, url: this.href };
            update && this.check();

            if (this.opreter === false) return this;
            t.history.pushState(s, j, this.url.toString());

            // if (this.opreter === false) return this;
            // this.fixHashInUrl();
            // let j = this.requestTitle || null;
            // let s = { idx: 0, url: this.href };
            // t.history.pushState(s, j, this.url.toString());
            // update && this.check();
        }

        setPath(newPathname, title) {
            this.requestTitle = title;
            this.url.pathname = newPathname;
            this.updateHistory();
            return this.url;
        }

        isPathname(pathname) {
            return this.url.pathname === pathname;
        }

        setUrl(newUrl, action = true) {
            this.url = 0 <= newUrl.search('http')
                ? new URL(newUrl)
                : new URL(newUrl, t.location.origin)
            this.fixHashInUrl();
            this.params = new URLSearchParams(this.url.search);
            this.updateHistory(action);
            return this.url;
        }

        locationRun() {
            return this.opreter === true ? t.location.reload() : null;
        }

        fixHashInUrl() {
            let hashIndex = this.url.href.indexOf('%23');
            if (hashIndex !== -1) {
                let newUrl = this.url.href.replace('%23', '#');
                this.url = new URL(newUrl);
            }
        }

        search = {
            get: (p) => this.params.get(p),
            set: (p, q, r = true) => {
                this.params.set(p, q);
                this.url.search = this.params.toString();
                this.updateHistory(r);
                return this.url;
            },
            append: (p, q, r = true) => {
                this.params.append(p, q);
                this.url.search = this.params.toString();
                this.updateHistory(r);
                return this.url;
            },
            delete: (p, q = true) => {
                this.params.delete(p);
                this.url.search = this.params.toString();
                this.updateHistory(q);
                return this.url;
            },
            deleteAll: (e = true) => {
                this.url.search = '';
                this.params = new URLSearchParams();
                this.updateHistory(e);
                return this.url;
            }
        };
    }

    class CacheStorage {
        constructor(a, b = false) { this.name = a, b && caches.delete(a) }
        async add(a, b, c = "application/json") { let d = await caches.open(this.name); await d.put(a, new Response(typeof b == "string" ? b : JSON.stringify(b), { headers: { "Content-Type": c } })) }
        async get(a) { let b = await caches.open(this.name), c = await b.match(a); if (!c) return null; return (c.headers.get("Content-Type") || "").includes("application/json") ? c.json() : c.text() }
        async delete(a = null) { return a ? (await caches.open(this.name)).delete(a) : caches.delete(this.name) }
    }

    class SvgIcon {
        constructor(cacheName = 'ws-assets') {
            this.cacheName = cacheName;
            this.svgNS = "http://www.w3.org/2000/svg";
            this.cache = new MAPX();
        }
        createIcon(name) {
            const i = document.createElement("icon"), s = document.createElementNS(this.svgNS, "svg");
            for (const [n, j] of Object.entries({ id: name, class: "emsvg", viewBox: "0 0 24 24", width: 24, height: 24 }))
                s.setAttribute(n, j);

            i.className = `icon_${name}`;
            i.append(s); i.svg = s;
            return i;
        }
        get(n, c) {
            const v = this.cache.get(n);
            let i = this.createIcon(n);
            v ? (i.svg.outerHTML = v)
                : this.add(n, i, c);
            return i;
        }
        export(name, fallback = null) {
            return this.cache.hasOwnProperty(name) ? this.cache[name] : fallback;
        }

        async fetchIcons(n, q = new URLManager(false)) {
            console.log(n);

            q.setPath("/media/svg/m=v2");
            q.search.deleteAll();
            if ($.irs === 1) {
                await new Promise(r => {
                    const i = setInterval(() => ($.irr) && (clearInterval(i), r()), 200);
                });
                return $.irr;
            }
            $.irs = 1;
            console.log("fetchIcons", n);

            $.iconRequest = await $.apirequest(q.url.href, true).get(res => {
                if (res.status === 200) $.irr = JSON.parse(res.responseText);
            });
            return $.irr;
        }

        async getCachedIcons(i, f = {}, m = []) {
            const n = Array.isArray(i)
                ? i : typeof i === 'string' ? [i]
                    : Object.values(i || {});
            for (const x of n) {
                const d = this.cache.get(x);
                d ? f[x] = d : m.push(x);
            }

            const r = await this.fetchIcons(m);
            for (const [x, g] of Object.entries(r || {})) {
                this.cache.add(x, g);
                f[x] = g;
            }

            return f;
        }
        async storeIcons(v, f) {
            const s = new CacheStorage(this.cacheName);
            for (const [n, g] of Object.entries(v)) {
                await s.add(`/media/svg/${n}.svg`, g, 'image/svg+xml');
                if (f.includes(n)) this.cache.add(n, g);
            }
            return this.cache;
        }
        async initIcons(i, r = false) {
            const n = Array.isArray(i) ? i : typeof i === 'string' ? [i] : Object.values(i || {}), m = [];

            for (const x of n) {
                const c = await caches.open(this.cacheName);
                const t = await c.match(`/media/svg/${x}.svg`);
                t ? this.cache.add(x, await t.text()) : m.push(x);
            }
            if (m.length || r) {
                const f = await this.getCachedIcons(m);
                this.cache = await this.storeIcons(f, n);
            }
            return this.cache;
        }
        async add(n, c, g) {
            let s = S(n) ? 1 : 0, o = n, r = new MAPX();
            if (O(n)) n = Object.entries(n)
            if (s) n = [n];
            if (F(n)) (c = n, n = o = []);
            const v = d => s ? d.get(o) : d;
            if (!F(c)) {
                let oc = c;
                c = h => {
                    let svg = oc.querySelector("svg");
                    if (s && E(oc) && h) svg.outerHTML = h;
                    svg && typeof g === "object" && svg.css(g);
                    return h;
                };
            }
            for (const p of n) {
                let i = this.cache.get(p);
                if (i) r.add(p, i), delete o[p];
            }
            const f = async l => {
                l = l?.get ? l : new MAPX(l);
                let ch = s || o.length === 0;
                for (const [k, v_] of Object.entries(ch ? l : o)) {
                    let i = l.get(ch ? k : v_);
                    if (i) r.add(k, i);
                }
                c(v(r));
            };

            let d = typeof caches !== "undefined"
                ? await this.initIcons(o)
                : await this.getCachedIcons(s ? [o] : o);

            f(d);
        }
        set(e, n, c = false) {
            const i = this.get(n, c);
            c === true && (e.innerHTML = "");
            e.append(i);
            return [i.svg, i];
        }

    }

    function NodeLists(a, b, c) {
        return function (qu) {
            qu.filter = function Filter(a, b) {
                var r = [], g = function (n) {
                    a(n) ? r.push(n) : n;
                };
                try { this.forEach(b => g(b)); }
                catch ($) {
                    for (const n in this) {
                        if (Object.hasOwnProperty.call(this, n)) g(this[n])
                    }
                }
                return exports("nodeLists", r, true)
            }
            qu.for = function For(a, b) {
                try {
                    for (const [i, v] of Object.entries(this))
                        a(v, Number(i), this);

                    // this.forEach((b, c, d) => a(b, c, d)) 
                }
                catch (error) { for (const insex of this) a(exports("bindFunction", insex), this) }
                return this
            }
            qu.combined = function Combined(a, b) {
                const Nodes = Array.from(a);
                const directly = this[Symbol.toStringTag]
                const combined = this instanceof NodeList || this instanceof HTMLCollection
                    ? Array.from(this)
                    : this;

                // Add new new NodeList for this _NodeLists 
                for (const Node of Nodes) {
                    if (combined.indexOf(Node) <= -1) {
                        combined.push(Node)
                    }
                }

                // Add propertys for  combined result
                for (const property in qu) {
                    try { combined.__proto__[property] = qu[property] }
                    catch (error) { }
                }
                return combined
            }
            qu.add = function Import(a, b) {
                // Add propertys for  given by a result
                F(a)
                    ? qu[a.name] = a
                    : qu[a] = b;

                return this
            }
            qu.find = function find(a, r = null) {
                for (const i in this) {
                    const b = this[i];
                    if (a(b)) { r = b; break; }
                }
                return r;
            }
            return a;
        }(a instanceof NodeList || a instanceof HTMLCollection || b == true ? a.__proto__ : {});
    }

    const globals = function (s, c) { return globals.choose(s, c); };
    globals.fn = globals.prototype = {
        length: 0,
        vidya: "0.4.1e",
        constructor: globals
    }

    const icons = new SvgIcon();
    const translate_string = new Objects();
    Array.prototype.push.apply(Y, X);

    const exports = (n, a, b, c, d) => {
        const t = globals[n];
        if (!Object.hasOwn(globals, n)) return null;
        return typeof t === "function" && a !== undefined
            ? t(a, b, c, d) : t;
    };

    const isdefine = function (a, b) {
        return typeof a == "function"
            ? globals[a.name] = a
            : globals[a] = b;
    }

    const addString = function (string) {
        if (B(string)) {
            for (const [code, value] of Object.entries(string)) {
                translate_string.add(code, value)
            }
        }
        return translate_string
    }
    const getString = function (string) {
        return translate_string.find(e => e.toLocaleLowerCase() == string.toLocaleLowerCase()) || string
    }

    isdefine("makeid", makeid)
    isdefine("export", exports);
    isdefine("isdefine", isdefine);
    isdefine("getid", function getNewId() {
        const used = new Set([...document.querySelectorAll('[id]')].map(el => el.id));
        let id;
        do id = makeid(6);
        while (used.has(id));
        return id;
    })
    isdefine("go", function Go(u, o) {
        return o
            ? history.pushState({}, typeof o === "string" ? o : "", u)
            : (t.location.href = u);

    });
    isdefine("nodeLists", function nodeLists(e, a, qus = NodeLists) {
        return qus(e, a);
    });
    isdefine("bindFunction", function bindFunction(a, b, c) {
        if (a == null) return a;
        const e = a, R = e.removeEventListener
            , set = (a, b, c, d) => {
                if (!a || typeof b != "string" || b.length <= 1) return a;
                d = (b === "type" && a instanceof HTMLTextAreaElement)
                typeof c != "undefined" && c != null
                    ? (a.setAttribute(b, c), !d && (a[b] = c))
                    : (a.removeAttribute(b), !d && delete a[b])
                return a;
            }
            , attrs = (a, b, c) => { for (let [d, e] of Object.entries(b)) set(a, d, e, c); return a }
            , classes = (a, b, c, d) => {
                typeof b != "object" && (b = b.split(U[3]));
                return b.filter(x => x && x.trim()).forEach(x => {
                    let y = x.split(U[3]);
                    y.length > 1 ? classes(a, y, c, d) : d ? a.classList.add(x.trim()) : a.classList.remove(x.trim())
                }), a
            }
            , attrClass = (a, b, c, d) => {
                if (E(b)) return a.in(b), a;
                if (b == null) return a;
                let e = typeof b == "object" ? [] : b.split("=");
                return e.length > 1 && (b = e[0], c = e[1]),
                    B(b) ? attrs(a, b, d) :
                        c === undefined && typeof c != "boolean" ? classes(a, b, c, d) :
                            set(a, b, c, d)
            }
            , node = (a, b) => {
                if (typeof b == "string") return document.createTextNode(b);
                return B(b) && b.tagName && (b = $.create(b)), E(b) && (b.p = a), b ?? null
            }
            , insert = (a, b, c) => {
                if (!b) return a;
                if (c === true) a.innerHTML = null;
                try {
                    return N(c) ? (a.insertBefore(node(a, b), a.children[c]), b) :
                        S(b) ? (a.innerHTML = b, b) : (a.append(node(a, b)), b)
                } catch { return a }
            }
            , parent = (a, f, s = a.p) => s ? f(s) === true ? s : parent(s, f) : null
            , dimensions = (a, b) => {
                let d = ["height", "width", "left", "right", "top", "bottom", "x", "y"],
                    e = a.getBoundingClientRect(),
                    f = Object.fromEntries(d.map(x => [x, e[x]]));
                return Object.assign(f, {
                    class: a.classList,
                    corners: {
                        topLeft: { x: e.left, y: e.top }, topRight: { x: e.right, y: e.top },
                        bottomLeft: { x: e.left, y: e.bottom }, bottomRight: { x: e.right, y: e.bottom }
                    },
                    side: { left: e.left, top: e.top, right: innerWidth - e.right, bottom: innerHeight - e.bottom },
                    target: a,
                    centerX: e.left + e.width / 2,
                    centerY: e.top + e.height / 2,
                    set_preant() {
                        let b = a.p.get(); f.set_preant = b;
                        for (let c of d) f["to_" + c] = e[c] - b[c];
                        return f
                    }
                }), b ? b == "inner" ? a.innerHTML : typeof b == "object" ? copy(b, f, {}) : a.getAttribute(b) : f
            }
            , copy = (a, b, c) => { for (let d of a) c[d] = b[d]; return c }
            , toggle = (a, b, c) => {
                c.toToggle = true;
                a && b && S(b) ? c.toggleAttribute(a, b) : c.classList.toggle(a)
            }
            , style = (a, b, c) => {
                let d = getComputedStyle(c), e = x => d[x] == "none" ? null : d[x];
                return F(a) ? a(d) : F(b) ? b(e(a)) : e(a)
            }
            , bind = (a, b) => {
                F(a) && (b = a, a = b.name);
                try { e.__proto__[a] = b; e[a] = b } catch { }
            };

        bind(function setStyle(a, b, c) {
            if (a && typeof a == "object")
                for (let [d, e] of Object.entries(a)) this.setStyle(d, e);
            else this.style.setProperty(a, b, c);
            return this
        });

        bind(function setDomStyle(a, b, c) {
            if (this.classList.length == 1 && ALT.indexOf(this.tagName)) {
                $.domStylelist ??= FlEXMAP();
                if (a && typeof a == "object") $.domStylelist.add(this.className, a);
                else if (S(a) && b) $.domStylelist.get(this.className)[a] = b;
                return this
            }
            return this.setStyle(a, b, c)
        });

        bind("set", function (a, b, c) {

            if (a?.tagName) return e.append(a), e;
            if (typeof a == "object") return attrs(e, a, c);
            let d = a.split("=");
            return d.length > 1 && (a = d[0], b = d[1]),
                b === undefined
                    ? classes(e, a, c)
                    : set(e, a, b, c)
        });

        bind(function add(a, b, c) { return attrClass(this, a, b, true) });
        bind(function removed(a, b) { return attrClass(this, a, b, false) });
        bind(function copy(a) { return e.cloneNode(a) });
        bind("in", function (a, b, c) {
            let d = insert(this, a, b);
            return c === true ? a : d, S(a) ? e : d
        });
        bind(function push(a) { return e.appendChild(a), e });
        bind(function pop() {
            let a = e.children;
            a.length && e.removeChild(a[a.length - 1]);
            return e
        });
        bind(function unshift(a) {
            let b = e.children;
            b.length ? e.insertBefore(a, b[0]) : e.appendChild(a);
            return e
        });
        bind(function shift() {
            let a = e.children;
            a.length && e.removeChild(a[0]);
            return e
        });
        bind(function replaceClass(a, b) {
            b ? e.classList.remove(b.trim()) : e.removeAttribute("class");
            e.classList.add(a.trim());
            return e
        });
        bind(function splice(i, a) {
            let c = e.children;
            a === undefined ? i >= 0 && i < c.length && e.removeChild(c[i]) :
                e.insertBefore(a, c[i] || null);
            return e
        });
        bind(function replace(a) {
            let b = e.parentNode;
            return b && (b.insertBefore(a, e), b.removeChild(e)), a
        });
        bind(function to_toggle(a, b, c = e) {
            typeof c.toToggle == "undefined" && e.event.on(x => toggle(a, b, c));
            return e
        });
        bind(function toggle(a, b, c) {
            c = typeof b == "object" ? b : this;
            a && b & S(b) ? c.toggleAttribute(a, b) : c.classList.toggle(a);
            return this
        });
        bind(function create(a, b, c) { return e.in(exports("create", a, b), c) });
        bind(function cx(a, b, c, d) { return e.in(exports("cx", a, b, c), d) });
        bind(function css(a, b) {
            let c = (a, b) => { N(b) && (b += "px"); try { this.style[a] = b } catch { } };
            return S(a) && S(b) ? c(a, b) : Object.entries(a || {}).forEach(([a, b]) => c(a, b)), this
        });
        bind(function getStyle(a, b) { return style(a, b, e) });
        bind(function isclass(a) { return e.classList.contains(a) });
        bind(function inclass(a, b) {
            let c = e.classList.contains(a);
            return F(b) && c ? b(this) : c, this
        });
        bind(function parentFilter(a, b) { return parent(this, a, b) });
        bind(function find(a) { return exports("bindFunction", e.querySelector(a)) });
        bind(function weres(a, b, c) {
            return exports("weres", a, b, e).filter(x => x.parentFilter(p => p == e))
        });
        bind(function choose(a, b) { return exports("choose", a, b, e) });
        bind(function get(a, b) { return dimensions(this, a, b) });
        bind(function c(a, b, c) { return e.in(exports("c", a, b, c)) });
        bind(function clear() { return e.innerHTML = null, e });
        bind(function addIcon(a, b) {
            let [g, i] = icons.set(e, a, b);
            return e.icon = i, e.svg = g || i, e
        });

        e.get.px = (a, b = 0, d = e.get()) => d[a] + b + "px";
        e.css.add = (a, b) => e.style[a] = b;

        if (X.indexOf(e.tagName.toLowerCase()) <= 0) {
            e.event = function (a, b, c) {
                let l = this._listeners ??= {};
                return (!l[a] || l[a] === b) && (l[a] = b, this.addEventListener(a, b, c)), this
            };
            e.event.add = (a, b) => e.event(a, b);
            e.event.remove = (a, b) => R(a, b);
            e.event.on = a => e.event("click", a);
            e.event.off = a => R("click", a);
            for (let a of Z) e.event[a] = b => (e.event(a, b), e)
        }

        for (let a of ALT) e.create[a] = function (b, c, d) {
            return N(c) && (d = c, c), e.in(exports("create", a, b, c, d), d)
        };

        e.childrens = exports("nodeLists", e.children);
        e.p = exports("bindFunction", e.parentElement);
        return e
    }
    )
    isdefine("timeAchead", function timeAchead(a, b, c = new Date()) {
        c.setTime(c.getTime() + (a * 24 * 60 * 60 * 1000));
        b === true ? c = c.toUTCString() : c;
        return c;
    })
    isdefine("choose", function choose(a, b, c, d) {
        // a => condition
        // b => firstSelector
        // c => secondSelector
        // d => context

        function dc(b, c) {
            return (b.length > 1) && (b = c.choose(b[0])) && (b.get("class") == a)
                ? b
                : null;
        }

        if (F(a)) {
            let array = new Objects(b);
            for (const item of ["is", "get", "add", "export", "remove", "filter"]) {
                a.prototype[item] = array.__proto__[item]
            }

            return new a(b, c);
        }

        S(a) && a.startsWith(specialCharsMap.leftBracket)
            ? b = false
            : null;

        if (!a) { return this; }

        d = d || document;

        let nt = a.split(" "),
            s = "string",
            t = typeof a,
            m = specialCharsMap.period,
            q = t === s ? a.split(specialCharsMap.comma) : a;

        if (nt = dc(nt, this)) {
            return nt;
        }

        const g = function (element, choose) {
            return element.querySelector(choose);
        };

        const h = function (obj, func) {
            for (const key in obj) {
                if (Object.hasOwnProperty.call(obj, key)) {
                    try {
                        obj[key] = exports("bindFunction", obj[key]);
                    } catch (error) { }
                }
            }
            return obj;
        };

        if (typeof b === "boolean") {
            m = b ? specialCharsMap.hash : "";
        } else if (typeof b === s) {
            d = exports("choose", b, c, e);
        } else if (b?.tagName) {
            d = b;
        }
        if (c?.tagName) {
            d = c;
        }


        for (let n = 0; n < q.length; n++) {
            q[n] = F(c)
                ? h(exports("nodeLists", c(d, m + q[n])))
                : exports("bindFunction", g(d, m + q[n]));
        }

        let data = q.length === 1 ? q[0] : q;

        if (F(b) && data.forEach) {
            data.forEach(b);
        }

        return data
    })
    isdefine("weres", function weres(a, b, c) {
        return exports("choose", a, b, function (d, e) {
            return d.querySelectorAll(e)
        }, c)
    })
    isdefine("storage", function storage(a, b, c) {
        if (typeof localStorage == "undefined") return null; let d = localStorage, e = a => FlEXMAP(JSON.parse(d.getItem(a))); class StorageHandler {
            constructor(a, b, c) { this.name = a; this.expiry = I(7200000); for (let k of Object.keys(d)) e(k).get("expiry") < I() && d.removeItem(k); let g = e(a); this.expiry = g?.expiry || this.expiry; N(b) && (this.expiry = b); c === true && this.insert(b) }
            set_expiry(a = 0) { return this.expiry = I(a) }
            insert(a) { return a && d.setItem(this.name, JSON.stringify({ expiry: this.expiry, data: a })) }
            get(a) { let b = e(this.name), c = b?.data || null; return a && c ? FlEXMAP(c) : c }
            remove() { return d.removeItem(this.name), true }
            export(a, b) { let c = this.get(true)?.get(a); return c && b === true ? new Objects(c) : c }
            update(a, b) { let c = this.get(true).add(a, b); return this.insert(c), c }
            delete(a) { let b = this.get(true).remove(a); return this.insert(b), b }
            getAll() { let a = new $(function Storage() { return this }); for (let b = 0; b < d.length; b++) { let c = d.key(b); a.add(c, new Objects(JSON.parse(d.getItem(c)))) } return a }
        } return new StorageHandler(a, b, c)
    })
    isdefine("cookie", function Cookie(a, b, c, d) {
        let j = ".", o = ":", s = "=", O = a => Array.isArray(a) ? a.join(j) : Object.entries(a).map(([a, b]) => Array.isArray(b) ? `${a + o}|${b.join(j)}|` : `${a + o}${b}`).join(oj),
            S = (a, b) => { let c = a.search(oj) >= 0 ? a.split(oj).reduce((a, b) => { let [c, d] = b.split(o); return a[c] = d.startsWith("|") ? d.slice(1, -1).split(j) : isNaN(d) ? d : Number(d), a }, {}) : a.split(j); return b === true ? new Objects(c) : c },
            U = a => !N(a) && Ss(a, [j, oj, o, s]) ? (console.error("Not valid cookie name :", a), true) : null,
            T = (a, b, c, d) => U(c) ? null : (a === true && b.add(c, d), b),
            M = a => Object.keys(a || {}).some(a => isNaN(a)),
            D = a => { let b = a === true ? t.location.hostname.replace(/^www\./, "") : a; return typeof b == "string" ? `; domain=${b}` : "" },
            X = (a, b) => (document.cookie = `${a}= ${D(!b)}; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`, true),
            G = a => { if (a == null) return; let b = {}, c = {}; document.cookie.split(";").forEach(a => { let [d, e] = a.split("="); d = d.replace(/\s+/g, ""); b[d] ? c[d] = e : b[d] = e }); return a === true ? { ...b, duplicate: c } : b[a.replace(/\s+/g, "")] },
            I = (a, b, c, d, e) => { if (!a) return; let f = `${a}${s}${b}${D(c)}`; return U(d) && (f += `; expires=${exports("timeAchead", d || 1)}`), f += `; path=${e || "/"}`, document.cookie = f, f };
        class Coocke {
            constructor(a, b, c, d) { this.name = a; this.type = d || !-1; this.domain = c; this.expires = b }
            insert(a) { let { name: b, domain: c, expires: d, path: e } = this, q = G(true); return q.duplicate?.[b] && X(b, c), this.value = a ?? this.value, I(b, a && typeof a != "string" ? O(this.value) : a, c, d, e) }
            get() { let a = G(this.name); return a && this.type === true ? S(a, true) : a }
            remove() { return document.cookie = this.name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;", this.value = null, true }
            export(a, b) { let c = this.get(true); return c ? this.type === true ? c.export(a) : c : b }
            add(a, b) { let c = this.get(true); return c = M(c) === false && c.search(".") ? Object.values(c) : c, A(c) ? (c.push(a), c = [...new Set(c)]) : c = T(this.type, c, a, b), c == null ? c : (this.insert(c), c) }
            update(a, b) { if (U(a)) return null; let c = this.get(true); return this.type === true && c.add(a, b), this.insert(M(c) === false ? Object.values(c) : c), c }
            delete(a) { let b = this.get(true); return b = M(b) === false ? Object.values(b) : b, A(b) ? b = b.filter(a => a !== b) : this.type === true && (b = M(b) === false ? b.add(a, null) : b.remove(a)), this.insert(b), b }
        }
        return new Coocke(a, b, c, d)
    })
    isdefine("create", function create(a, b, c, d) {
        let ab;
        function sel(a) {
            const b = new globals.choose(function () {
                this.index = -1;
                this.classList = [];
                this.tagName = Y[0];
                return this;
            });
            for (const c of a) {
                const d = ALT.indexOf(c);
                if (d >= 0) b.tagName = c, b.index = d;
                else b.classList.push(c);
            }
            return b;
        }
        function create(a, b, c) {
            const { tagName: d, classList: e, index: f, inner: g, style: h, cssText: i, children: j, icon: k, on: l, ...m } = a, n = exports("bindFunction", document.createElement(d || Y[0]));
            Object.entries(m).forEach(([a, b]) => n.add(a, b));
            n.bindLess = () => Object.entries(E(n.parentElement) ? n.parentElement.get() : {}).forEach(([a, b]) => m[a] === true && n.add(a, b));
            F(l) && n.event.on(l);
            g && n.in(g); Array.isArray(j) && j.forEach(a => n.create(a)); Array.isArray(e) && !e.length && f > 3 && ALT.indexOf(d) <= 0 && e.push(d);
            E(c) && n.in(c); ab ? n.in(b, c) : (f === -1 && n.in(b, c), b && f !== -1 && e.push(b)); n.add(e) && !n.className && (n.className = getNewClassName());
            h && Object.assign(n.style, h); i && (n.style.cssText = i); d === "a" && !n.href && (n.href = "javascript:void(0)"); k && n.addIcon(k);
            return n;
        }

        ALT.indexOf(a) < 0 && S(b) && (ab = true);
        typeof a === "undefined" && (a = Y[0]);

        if (b && ALT.indexOf(a) >= 0 && typeof b === "object" && !b.tagName) {
            b.tagName = a;
            a = b;
            b = undefined;
        }
        else if (S(a)) {
            a = sel(a.split(U[3]));
        }
        a = create(a, b, c);
        try {

            E(b) && b.in(a, c);
            E(c) && c.in(a, d);
            S(c) && a.in(c, d);
            A(c) && c.forEach(e => E(e) && a.in(e))

        } catch (e) { }
        return a;
    })
    isdefine("getKey", function generateKey(a) {
        const uuid = () => ([1e3] + -1e3 + -4e3 + -8e3 + -1e3).replace(/[018]/g, c =>
            (c ^ Math.random() * 16 >> c / 4).toString(16)
        );
        return a === true ? uuid() : Math.random().toString(16).substring(2, a || 10);

    })
    isdefine("onlink", function onlink(a, b, c) {
        b = a.choose(b);
        b = b.get("href");
        t.location = b;
    })
    isdefine("buttonAnimation", function buttonAnimation(a, b) {
        var time, h, i, st, an = exports("buttonAnimation"), p = this.color?.backgroundFocus || "#7e7e7e4d", t = 'array-click', e = an.class || (new function e() {
            this.c = [];
            for (let a = 0; a < 8; a++) {
                this.c.push(exports("makeid", 8))
            }
            this.s = exports("makeid", 16);
            an.class = this;
            return this;
        }
            ())
            , f = function (a, b = exports("create", e.c[3]), bn = "button") {
                h = b.create(e.c[4]).create(e.c[5]);

                let m = b.create('DIS01');
                let c = m.create([e.c[6]]);
                let array = new Objects(a.childNodes)
                for (const [k, v] of array) c.append(v);

                a.add(e.c[2]);
                b.appended = a.appended;
                c.add("IN078");
                a.in(b, true);
                a.loader = function (q) {
                    let ah = m.getStyle("height");
                    let aw = m.getStyle("width");
                    let sp = a.loaderSpiner || m.addIcon("ic_spin");
                    sp.icon.css({ width: ah, height: ah })
                    aw == ah
                        ? sp.icon.css({ position: "absolute" })
                        : sp.icon.css({ marginLeft: 5 });
                    a.loadingAction = q;
                    a.loaderSpiner = sp;
                    sp.icon.css("display", q == true ? "inline-flex" : "none");
                    a.disabled = q === true;
                    return a.loadingAction;
                }
                a.in = function (e, o) {
                    o === true && m.clear();
                    return m.append(e);
                };
                return g(a, h);
            }
            , g = function (a, b) {
                b.css({
                    padding: a.offsetWidth + "px",
                    display: "none"
                });
                a.event.mousedown(e => k(e, a, b))
            }, k = function (a, b, c) {
                let ew = b.get();
                c.css({
                    top: `${a.clientY - ew.y}px`,
                    left: ` ${a.clientX - ew.x}px`,
                    display: "block"
                }),
                    b.add(t, false),
                    time = 0;
                if (i)
                    clearInterval(i);
                i = m(b, c);
            }, m = function (a, b, c) {
                return setInterval(() => {
                    a.add(t, true);
                    if (time > 10)
                        b.style.display = "none",
                            clearInterval(i);
                    time++
                }
                    , 50);
            }, sc = function (a, b) {
                an.body.in(exports("create", "style", e.s, `.${e.c[3]}{flexs: 0;}.${e.c[2]}{position: relative;overflow: hidden;}.${e.c[6]} {member-select: none;z-index: 1;position: relative;}[array-click="false"] .${e.c[5]} {opacity: 1; transform: translate(-50%, -50%) scale(0);transition: 0s;}.${e.c[5]}{background: ${p};opacity: 0; position: absolute; transform: translate(-50%, -50%) scale(1); border-radius: 50%; content: ''; transition: transform 0.5s, opacity 1s, padding 1s;`), 0);
            }, q = function (a, b) {

                p = a || p, st = an.body?.weres("style", false).filter(function (a) {
                    return a.isclass(e.s)
                });
                if (b === !0) {
                    st.forEach(n => n.remove()), sc()
                }
                if (st?.length <= 0) { sc() }
            };

        an.lists = an.lists || [];
        for (const n in a) {
            if (Object.hasOwnProperty.call(a, n) && !an.lists.includes(a[n])) {
                an.lists.push(a[n]);
                try { a[n] = exports("bindFunction", a[n]) }
                catch (error) { }

                an.body = an.body || a[n].parentFilter(function (e) {
                    return e.tagName == "BODY"
                });
                f(a[n]);
            }
        }
        q(b);
        an.cssUpdate = q;
        return an;
    })
    isdefine("event", function event(a, b, c) {
        a = exports("choose", a, c);
        return a !== null ? b(a, globals) : a;
    })
    isdefine("windows", function (target, { container, functions, noremove } = {}, type) {
        const bgClass = type === 2 ? "IN032" : "IN033";

        function md(e, vq) {
            return (e.parentFilter && e.parentFilter(ev => ev == vq) != null) || e == vq
        }
        // Remove previous session
        const old = exports("windowSession");
        if (old) old.remove();

        // Create background
        const bg = exports("create", bgClass);

        const event = ["click", "mousedown", "contextmenu", "touchstart"]
        if (type === true || type === 2) document.body.append(bg);
        else if (E(type)) type.append(bg);
        const session = {
            target,
            container,
            noremove,
            background: bg,

            remove() {
                if (type == true || E(bg)) bg.remove();
                event.forEach(event => t.removeEventListener(event, this.close));
            },

            exit(e) {

                if (!is(e)) {
                    !this.noremove && this.container ? this.container.remove() : null;
                    return session.remove()
                }

                if ((md(e, t) || md(e, container))) {
                    console.log("click session", md(e, a), md(e, container));
                    return;
                }

                if (is(e) && e.clientX == 0) {
                    console.log("is(e) && e.clientX == 0");
                    return;
                }

                if (functions === true && !this.noremove) this.container.remove();
                if (F(functions)) functions();
                return this.remove();

            },

            close: (e) => {
                let item = e?.target;
                if (!container || !container.contains(item))
                    session.exit(item)
            }
        };

        setTimeout(() => {
            event.forEach(event => t.addEventListener(event, session.close));
        }, 100);

        isdefine("windowSession", session);
        return session;
    })
    isdefine("fch", function fch(u, o = {}, cb) {
        let old = "";
        const d = globals, { session: s, extend: e } = isExtend(function request() { });
        e("retryCount", 0); e("isOffline", false);
        if (!d.export("cache")) d.cache = new Objects();
        for (const [k, v] of Object.entries(o || {})) try { e(k, v); } catch { }

        const online = () => true || navigator.onLine,
            rr = () => {
                const base = t.location.origin + "/api/v1/";
                if (!base.startsWith("http")) throw new Error("Base URL must be absolute!");
                return !u.startsWith("http") ? new URL(u, base).href : u.replace(/([^:]\/)\/+/g, "$1");
            },
            rm = () => s.method || "get", rc = () => rm() !== "post" && d.cache.get(rr()),
            rp = (p) => {
                const g = $("IN002") || $.bindFunction(document.body).create("IN001").create("progress").create("IN002");
                if (rp.Ri) clearInterval(rp.Ri);
                g.css({ display: "block", width: p + "%" });
                if (p === 100) rp.Ri = setInterval(() => (g.style.display = "none", clearInterval(rp.Ri)), 1000);
            },
            rh = (e) => {
                const cbk = s.onprogress || s.progress || rp;
                if (e.lengthComputable) cbk(Math.round((e.loaded / e.total) * 100));
            },
            rb = (x, b) => {
                const r = x.json(), { session: ss, extend: ee } = isExtend(b);
                for (const [k, v] of Object.entries(((x) => ({ success: x[0], meta: x[1], data: x[2] }))(r)))
                    ee(k, v);

                proto.call(ss, function parse() { return r; });
                return ss;
            },
            ro = x => {
                let res, cbk = s.callback || s.finish;
                try { res = rb(x, function Response() { }); }
                catch { res = new Objects({ error: "Invalid JSON" }); }
                const bindFlag = res.is("rb"), REST = res.data, err = res.is("error");
                proto.call(x, function getResponseObject() { return res.data; });
                proto.call(x, function getParams(k) {
                    let { session: ss, extend: ee } = isExtend(function Params() { });
                    let R = res.data || {};
                    ee(Object.keys(R || res), R || res);
                    return k ? ss.is(k) : ss;
                });

                proto.call(x, function getArray() { return res.parse(); });
                x.res = res; bindFlag && $.exuter(bindFlag, REST, x);
                x.id = mt();

                if (err) F(s.error) ? s.error(res) : s.reject(res);
                else F(cbk) ? cbk(res) : s.resolve(s.getType ? res : x);
            },
            rx = () => {
                const x = new XMLHttpRequest();
                x.upload.onprogress = rh;
                x.onprogress = rh;
                x.onreadystatechange = function () {
                    const diff = this.responseText.replace(old, "");
                    old = this.responseText;
                    cb && cb(x, diff.trim());
                };
                x.onload = () => x.status === 200 ? (d.cache.add(u, x), ro(x)) : s.reject(x);
                x.json = () => { try { return JSON.parse(x.response); } catch { return x.response; } };
                return x;
            },
            rs = x => { let b = s.body; if (B(b) || A(b)) b = Is(b); rp(0); x.send(b); return x; },
            rsh = x => {
                if (s.headers) Object.entries(s.headers).forEach(([k, v]) => x.setRequestHeader(k, v));
                else if (s.body instanceof FormData) x;
                else if (s.body && typeof s.body === "object") x.setRequestHeader("Content-Type", "application/json"); return rs(x);
            },
            bu = () => { s.head ??= {}; const p = Object.entries(s.head).map(([k, v]) => `${k}=${v}`).join("&"); return p ? rr() + "?" + p : rr(); },
            ri = () => { const x = rx(); x.open(rm(), bu(), true); return rsh(x); },
            ry = () => {
                const t = setInterval(() => {
                    if (online() || s.retryCount > 30) { clearInterval(t); ri(); $.isOffline = false; }
                    else if (!$.isOffline) { d.message({ message: "You're offline", class: "topCenter", time: 6000 }); $.isOffline = true; }
                    s.retryCount++;
                }, 1000);
            };

        return new Promise((res, rej) => {
            const c = rc(); e("resolve", res); e("reject", rej);
            (rm() === "get" && c) ? ro(c) : online() ? ri() : ry();
        });
    });
    isdefine("socket", function SocketRequest(a, b, c) {
        const d = new WebSocket(a.includes("http") ? a : t.location.origin + (b ? "" : "/ws/") + a), e = [];
        const f = a => new TextEncoder().encode(JSON.stringify(a)),
            g = a => JSON.parse(new TextDecoder().decode(a)),
            h = a => { a = JSON.parse(a); return Array.isArray(a) ? a : a && typeof a == "object" ? new $.array(a) : a };

        d.export = (a, b) => {
            const c = a.request_key;
            d.readyState == 1 ? (d[c] = b, d.send(f(a))) : d.readyState == 0 && e.push([a, b]);
        };
        d.onmessage = async a => {
            const b = h(await a.data.text());
            if (b instanceof Object && !Array.isArray(b)) {
                const { request_key: c } = b, d_ = d[c];
                typeof d_ == "function" ? (delete d[c], d_(b)) : d.finish(b);
            } else typeof d.finish == "function" && d.finish(b);
        };

        d.addEventListener("open", () => {
            while (e.length) { const [a, b] = e.shift(); d.export(a, b) }
        });

        return d;
    })
    isdefine("apirequest", function ApiRequest(a, b, c) {
        const d = (a, b) => { const c = Gm(b); for (const [k, v] of Object.entries(a)) c[k] = v; !B(b) && (c.body = b); return c; }, e = (a, b, c) => { const d = $.fch(a, b); return d.then(a => F(c) && c.call(a?.Ro, a)), d; }, { extend: f, session: g } = isExtend(function () {
            this.path = a;
            this.getResponceCount = 0;
            this.hostname = t.location.origin + (b === true ? "" : "/api/v1/");
        });

        f("get_path", function () { return this.path.includes("http") ? this.path : this.hostname + this.path; });
        f("change_path", function (a) { this.path = a; return this; });
        f("get", function (a) { return e(this.get_path(), null, a); });
        f("error", function (a, b) { console.log(a); return this; });
        f("send", function (a, b) { return e(this.get_path(), d(this, a), b); });

        return g;
    }
    )
    isdefine("string", function Strings(a, b, c) {
        c = $.setting();
        $.apirequest(t.location.origin + "/string/" + c.language + a).get(function (e) {
            let r = e.getResponseObject();
            for (const [code, value] of Object.entries(r.lists))
                translate_string.add(code, value);

            F(b) && b(translate_string);
        });
    })
    isdefine("copy", async function copyToClipboard(text, sm = "Copied to clipboard!") {
        if (!navigator.clipboard)
            return "Clipboard API not supported in this browser.";

        try {
            await navigator.clipboard.writeText(text);
            return sm;
        } catch (error) {
            return `Failed to copy: ${error.message}`;
        }
    })
    isdefine("message", function message(a, b) {
        if (a === undefined) return;
        const c = S(a) ? a : a.message || "", d = a.class || "f4nM", e = (N(b) ? b : a.time) || 4000, f = (!N(b) && b) || $.getHtmlBody(), g = this.choose("IN027", f) || f.create("IN027");
        return g.in(this.create(d, c), true), setTimeout(() => g.remove(), e), true
    }
    );
    isdefine("c", function createElement(a, b = "", c, d) {
        b = b.toString();
        function parseTags(htmlStrings, children) {
            if (typeof htmlStrings != "string") {
                return null;
            }
            // Regex to parse tag name, classes, id, attributes, nested elements, repetitions, and inner HTML
            //  ^(\w+): Captures the tag name.
            // (?:\.([\w.-]+))?: Optionally captures classes (dot-separated).
            // (?:#(\w+))?: Optionally captures the ID.
            // (?:\[(.*?)\])?: Optionally captures attributes within [].
            // (?:>([^{}]*))?: Optionally captures nested elements (without {}).
            // (?:\*(\d+))?: Optionally captures repetition count.
            // (?:\{(.*)\})?: Optionally captures inner HTML within {}
            const tagRegex = /^(\w+)(?:\.([\w.-]+))?(?:#(\w+))?(?:\[(.*?)\])?(?:>{(.*?)})?(?:>([^{}]*))?(?:\*(\d+))?(?:\{(.*)\})?$/
            var match = htmlStrings.match(tagRegex);
            if (match == null) {
                const regex = /(\w+)\*(\d+)\.(\w+)>((?:\w+>)?)/;
                match = htmlStrings.match(regex);

                const [, tag, count, className, repit] = match;
                const childrens = parseTags(repit);
                for (const [name, value] of Object.entries(childrens)) {
                    if (value == null) delete childrens[name]
                }

                return Array.from({ length: parseInt(count, 10) }, () => ({ tag, class: className, children: childrens }));
            }

            if (match[6]) {
                children = parseTags(match[6])
            }

            return {
                tagName: match[1] || null,
                classList: match[2] || null,
                id: match[3] || null,
                attributes: match[4] || null,
                children: children || null
            };
        }

        function htmlToArray(structure) {
            var structure_arr = structure.split(/(?<=})|(?={)/).filter(Boolean);
            var structure_arrs = $(function structure() { return this });
            let children = structure_arrs;

            structure_arr.forEach(structure => {
                let inner;
                if (structure.startsWith('{') && structure.endsWith('}')) {
                    inner = structure.slice(1, -1).trim();
                    structure_arr = structure_arr.filter(item => item !== structure);
                    children.inner = inner
                }
                else if (structure.endsWith('>')) {
                    const data = parseTags(structure);
                    for (const [name, value] of Object.entries(data)) {
                        if (value != null && name != "repeatCount") { children[name] = value }
                    }
                    structure_arr = structure_arr.filter(item => item !== structure);
                }
                else {
                    const data = parseTags(structure);
                    for (const [name, value] of Object.entries(data)) {
                        if (value != null && name != "repeatCount") { children[name] = value }
                    }
                    structure_arr = structure_arr.filter(item => item !== structure);
                }

                if (children.tagName && (children.children || children.inner)) {
                    if (children.classList) {
                        children.classList = children.classList.split(".")
                    }

                    if (!children.children?.length) {
                        let datalist = {}
                        children.children = [datalist];
                        children = datalist
                    }
                }
                if (children.attributes) {
                    let attributes = children.attributes.split("|");
                    for (const e of attributes) {
                        let [name, value] = e.split("=");
                        children[name] = value
                    }
                    delete children.attributes;
                }
            });
            return structure_arrs
        }

        console.log(a);

        // return;
        var element = globals.create(htmlToArray(a))
        return element

    })
    isdefine("setting", function setting(a, b, c) {
        const d = { encode: a => btoa(unescape(encodeURIComponent(JSON.stringify(a)))).replace(/=+$/, ""), decode: a => { try { return JSON.parse(decodeURIComponent(escape(atob(a + "=".repeat((4 - a.length % 4) % 4))))) } catch (b) { return null } } };
        class e {
            cookie = $.cookie("_cf_bm", 360, Gd());
            static languageList = ["en", "hi", "sa", "ta", "te"];
            static themeList = ["default", "light", "dark"];
            static DEFAULT_TOKEN = "eyJja2V5IjoiRWpMdzRDTU0wVXpNMkkvLy9NVFkiLCJsYW5nIjowLCJ0aGVtZSI6MH0";
            constructor(a) { this.name = a; this.cookie.get() || this.reset(); this.data = d.decode(this.cookie.get()) || { lang: 0, theme: 0 }; this.config() }
            config(a) { a ? (this.data.lang = e.languageList.indexOf(this.language), this.data.theme = e.themeList.indexOf(this.theme)) : (this.language = e.languageList[this.data.lang] || "en", this.theme = e.themeList[this.data.theme] || "default") }
            get(a, b = null) { return Object.hasOwn(this, a) ? this[a] : a === true ? this.cookie.get() : b }
            update(a, b) { if (!(a in this)) return false; this[a] = b; this.config(true); this.cookie.insert(d.encode(this.data)); return true }
            reset() { return this.cookie.insert(e.DEFAULT_TOKEN), true }
            logout(e) { return $.loader(true) && exports("fch", "logout", { method: "post", body: { session: e, option: !1 }, callback(a) { $.loader(false); a.is("logout") && (t.location.href = location.origin + "?refresh=true") } }) }
        }
        return new e(a || "5DB6lIE")
    }
    )
    isdefine("exuter", function Et(a, b, c) {
        $.scopes ??= SEOPES();

        var [f = null, g = null, p = null] = a || [];
        g = $.scopes.get(g), f = g?.get(f);

        if (typeof f === "function") f.call(this, b, c);
        else if (!$.scopes.includes(p)) {
            $.scopes.push(p);
            script("scopes/" + p, e => $.exuter(a, b, c));
        }

    })
    isdefine("module", function Module(a, b, c) {
        var g;
        $.module.list ??= $(function Module() { return this; })
        var Cb = function (e) {
            console.log("module not load edite function plese");
        }
        var Cr = function (e, f) {
            if (g = $.module.list.get(e)) {
                f(g);
            }
            return g;
        }
        var Ms = function (a) {
            var spt = script(this, a);
            spt.id = btoa(this);
            spt.addEventListener("error", e => Cb);
            return spt;
        }

        if (B(a) && (typeof Cr(b, c) == "function")) {
            return;
        }

        for (const [group, list] of Object.entries(a || {})) {
            if (list.includes(b)) {
                return Ms.call(group, Cr(b, c));
            }
        }

        return Ms.call(a, e => Cr(b.name, b));

    })
    isdefine("define", (a, b) => {
        $.define.list ??= FlEXMAP();

        const fn = typeof a === "function" ? a : b;
        if (!fn) return;

        $.define.list.add(typeof a === "string" ? a : fn.name, fn);
        return fn;
    });
    isdefine("require", function Req(a, b) {
        $.define.list ??= FlEXMAP();

        const fail = e => console.log("require not found:", e)
            , load = (a, b) => {
                const s = script(a, b);
                s.id = btoa(a);
                s.addEventListener("error", fail);
                return s;
            }
            , get = () => {
                if (typeof b !== "function") return null;

                const fn = $.define.list.get(b.name) ||
                    $.define.list.get(a);

                if (!fn) return null;

                b(fn);
                return {};
            }
            , mod = get() || load(a, get);

        set(mod, "css", () => style(a));
        return mod;
    });
    isdefine("extend", function Extend(a, b, c) {
        if (typeof a != "function") {
            return
        }
        a.add = this.add;
        for (const item of this) {
            let bindkey = item[0];
            let bindvalue = item[1];

            if (bindkey && bindvalue) {
                a.add(bindkey, bindvalue)
            }
        }
        return a;
    })
    isdefine("getFunction", function getFunction() {
        return {
            getNewClassName,
            is,
            set,
            mapx,
            SEOPES,
            FlEXMAP,
            proto,
            script,
            ks,
            A,
            N,
            I,
            S,
            E,
            F,
            B,
            Is,
            Gd,
            isExtend,
            urlParts,
            addString,
            getString,
            getNewClassName,
            LIST
        }
    })
    isdefine("getClass", function getClass() {
        return {
            MAPX,
            AUTH_TOKEN,
            URLManager,
            CacheStorage,
            Objects,
        }
    })
    isdefine("req", function Request(e) {
        this.RequestBind = this.RequestBind || new URLState(e);
        return this.RequestBind;
    })
    for (const [name, value] of Object.entries({
        "array": Objects,
        "URLState": URLState,
        "request": URLManager,
        "URLManager": URLManager,
        "cacheStorage": CacheStorage
    })) {
        isdefine(name, value);
    }
    isdefine("isfor", function (a, b) {
        let elementList = $.weres(a);
        F(b)
            ? elementList.for(e => e.event.on(b))
            : null;

        return elementList
    })
    isdefine("bind", function Bind(a, b) {
        let bind = exports(a);
        if (F(bind)) return bind(b);
    })
    isdefine("getHtmlBody", function getHtmlBody(callback) {
        let body = exports("bindFunction")(document.body)
        if (F(callback)) {
            return callback(body)
        }
        return body;
    })
    isdefine("loader", function Loader(a) {
        let opacity = 1;
        function f() {
            opacity -= 0.03;
            loader.style.opacity = opacity;
            opacity > 0 ? requestAnimationFrame(f) : loader.style.display = "none";
        }
        let body = $.getHtmlBody(), loader = $("IN013") || body.create("IN013")
        loader.clear(), loader.create("icon");

        body.style.position = a === true ? "fixed" : "relative";
        a === true ? (loader.style.display = "flex", loader.style.opacity = 1) : f();

        return a;
    })
    isdefine("icons", function Icon() {
        return icons;
    })
    isdefine("DOMContentLoaded", function DOMContentLoaded(a, b, c) {
        $.onReadyCallbacks ??= [];
        !$.onReadyCallbacks.some(item =>
            item.evt === a && item.log === b && item.net === c
        ) && $.onReadyCallbacks.push({ call: a, b, c });

        document.addEventListener('DOMContentLoaded', () => {
            $.onReadyCallbacks.forEach(item =>
                !item.executed && (item.executed = true, item.call($, $.bindFunction(item.b), item.c))
            );
        });

        // document.addEventListener('DOMContentLoaded', e => a($, globals.bindFunction(b), c))
    })
    isdefine("popup", function PopupMessage(t, o) {
        const b = $.getHtmlBody();
        !o && this.windowPopup?.close();
        const r = o
            ? (b.choose(o) || b.create(o).add("IN031"))
            : b.create("IN031"),
            p = r.create("IN034"),
            h = p.create.header("DIS01");

        p.header = h.create("hrg");
        p.hrg = h.create("hrg");
        p.closeButton = p.hrg.create.button(null).addIcon("ic_close").event.on(e => p.close(e));

        p.close = () => r.remove();
        p.width = () => p.css({ width: "100%" })
        p.absolute = () => h.css({ position: "absolute", width: "100%" })

        if (t) {
            p.t = p.header.create.h2(null, t);
            h.css({ padding: "2px 8px", borderBottom: "1px solid" });
        }

        return o ? p : (this.windowPopup = p);
    })
    isdefine("sde", function setDefaultElement(a) {
        $.sdeList ??= mapx();
        if ($.sdeList.has(a)) return $.sdeList.get(a);
        const b = $.getHtmlBody().create.span();
        $.sdeList.add(a, b);
        return b;
    });
    isdefine("tooltip", function ToolTip(a, g) {
        const tai = $.tai ??= {}, t = window;
        const radii = { '1_1': '0 10px 10px 10px', '1_0': '10px 10px 10px 0', '0_1': '10px 0 10px 10px', '0_0': '10px 10px 0 10px' };

        const sp = (e, c) => {
            const rect = e.target.getBoundingClientRect(), x = e.clientX, y = rect.bottom;
            const isL = x < t.innerWidth / 2, isT = y < t.innerHeight / 2;
            const w = (c[0] || c).offsetWidth || 0;
            c.css({
                left: isL ? x : x - w,
                top: isT ? y : 'auto',
                bottom: isT ? 'auto' : t.innerHeight - rect.top,
                borderRadius: radii[`${+isL}_${+isT}`],
                maxWidth: Math.min(t.innerWidth / 2 | 0, 500)
            });
        }

        const b = ($.choose("tcont") || $.getHtmlBody().create("tcont"));
        const c = $.create("tooltip-container"), d = c.create("tooltip-body");

        if (!a.get("id")) a.set("id", $.getid());
        const r = tai[a.id] ??= c;

        c.close = () => (r.remove(), F(r.bind) && r.bind());
        c.executed = m => d.append(m);

        let h;
        a.event.mouseenter(e => {
            clearTimeout(h);
            h = setTimeout(() => {
                if (!b.contains(r)) {
                    b.clear().append(r);
                    sp(e, r);
                }
            }, 1000);
        });

        a.event.mouseleave(() => clearTimeout(h));

        $.event.mousemove ??= [];
        const talltiph = () => {
            if (!r.contains($.cursorElement) && !a.contains($.cursorElement)) {
                $.event.mousemove = $.event.mousemove.filter(f => f !== talltiph);
                r.close();
            }
        };
        $.event.mousemove.push(talltiph);

        return c;
    })

    isdefine("tooltip_menu", function ToolTip(a, t, cb) {
        if (a.showContent)
            return;

        const tooltip = exports("tooltip", a, t, cb)
            , d = tooltip.create("tooltip-body")
            , mc = d.create("menu-container");

        tooltip.executed = ex => ex.forEach((m, n) => {
            let o = $.create.span("nOvE7 width", m.name);
            if (m.icon) {
                const p = $.create("nOvE6");
                p.append($.create.span().addIcon(m.icon), o);
                o = p;
            }
            const q = mc.create.button(null, o);
            m.active && q.add("active");
            if (typeof m.event == "function")
                q.event.on(r => (m.event.call(q, r, tooltip.close), tooltip.close(), typeof cb == "function" && cb()));
            if (n < ex.length - 1) d.create("border");
            if (n < ex.length - 1) console.log("boder");

        })
        return tooltip
    })
    isdefine("menuexitue", function MenuExItue(a) {
        const b = $.sde("mcont"); b.clear();
        const c = b.create("menu-container")
            , d = c.create("IN060 IN028")
            , e = f => f.preventDefault()
            , g = f => f.stopPropagation()
            , h = f => {
                const u = ["ArrowUp", "PageUp"], v = ["ArrowDown", "PageDown"], k = ["Home", "End", " "].concat(u, v), H = d.children[0].height;
                if (!k.includes(f.key)) return;
                f.preventDefault();
                if (u.includes(f.key)) d.scrollBy({ top: -H, behavior: "smooth" });
                else if (v.includes(f.key)) d.scrollBy({ top: H, behavior: "smooth" });
                else if (f.key === "Home") d.scrollTo({ top: 0, behavior: "smooth" });
                else if (f.key === "End") d.scrollTo({ top: d.scrollHeight, behavior: "smooth" });
            };

        const i = () => ["wheel", "touchmove"].forEach(f => t.addEventListener(f, e, { passive: false })),
            j = () => ["wheel", "touchmove"].forEach(f => t.removeEventListener(f, e));

        t.addEventListener("keydown", h, { passive: false });
        const k = () => t.removeEventListener("keydown", h);

        c.close = () => { j(); k(); c.remove(); c.active = false; F(c.bind) && c.bind(); };
        c.executed = (l, v) => {
            i();
            ["wheel", "touchmove", "keydown"].forEach(f => d.addEventListener(f, g, { passive: false }));
            l.forEach((m, n) => {
                let o = $.create.span("nOvE7 width", m.name);
                if (m.icon) { const p = $.create("nOvE6"); p.append($.create.span().addIcon(m.icon), o); o = p; }
                const q = d.create.button(null, o);
                m.active && q.add("active");
                if (F(m.event)) q.event.on(r => m.event.call(q, r, c.close, v) && c.close());
                if (F(m.hover)) q.event.mouseover(r => m.hover.call(q, r, c.close));
                if (m.event === false) q.event.on(c.close);
                if (n < l.length - 1) d.create("border");
            });

            const { clientX: r, clientY: s } = a,
                j = r < t.innerWidth / 2,
                u = s < t.innerHeight / 2;

            c.css({ left: j ? r : r - c.offsetWidth, top: u ? s : "auto", bottom: u ? "auto" : t.innerHeight - s });
            c.css({ borderRadius: j ? (u ? "0 10px 10px 10" : "10px 10px 10px 0") : (u ? "10px 0 10px 10" : "10px 10px 0 10") });
            c.active = true;
        };

        $.windows(null, { container: c, functions: c.close }, null);
        return c;
    });
    isdefine("alert", function Alerts(a, b, c) {
        let d = $.popup()
            , e = d.create("IN035")
            , f = d.create("IN036");
        d.header.p.remove();
        d.container = e;
        e.create.h2("ctitle", a || "Confirm");
        e.create.p("confirm-message", b);
        f.create.button("save", "OK").event.on(() => { F(c) && c(), d.close() });
        return d
    })
    isdefine("confirm", function Confirm(a, b) {
        let c = $.popup(null, "IN03G");
        c.clear();
        let d = c.create("IN035"), e = c.create("IN036");
        c.header.p.remove();
        d.create.h2("ctitle", a.h || "Confirm");
        d.create.p("confirm-message", a.t);
        e.create.button("cancle", a.c || "Cancle").event.on(() => c.close());
        a.b && e.create.button("save", a.b).event.on(function () { return F(b) && this.loader(true) && b(c.close) && c.close() });
        return { p: c, c: d }
    })

    isdefine("session", function Session() {
        return this(function Session() {
            return this
        });
    })
    isdefine("domStyle", function domStyle(name, value) {
        $.domStylelist ??= FlEXMAP();
        let cls = getNewClassName.call($.domStylelist, name)
        if (S(name) && B(value)) {
            $.domStylelist.add(name, value)
        }
        else if (B(name) && E(name)) {
            console.log("edit index domStyle");

            return cls;
        }
        else if (B(name)) {
            $.domStylelist.add(cls, name)
            return cls;
        }
        else {
            return cls;
        }
    })
    isdefine("cx", function createReElement(a, b, c) {
        let g = $.domStyle(a, b);
        return $.create(g, c);
    })
    isdefine("isMobile", function isMobile(a, b, c) {
        return $("mobile") ? true : false;
    })
    isdefine("conversations", function Conversations(a, b) {
        let c = globals.choose(function Conversations() { this.element = globals.choose(a); this.conversationsName = b; this.chenge = function () { } });

        async function d(a) {
            let e = "", f = $.create("IN079 boc");
            function g(a, b = "data:") {
                if (a.startsWith(b) && (a = a.replace(b, ""))) {
                    let c = new $.array(JSON.parse(a)); e += c.is("parts");
                    f.innerHTML = markdownToHtml(e); f.scrollTop = f.scrollHeight
                }
            }

            $.fch("/api/v1/conversations", a, function (a, b) {
                let d = globals.choose(function Event() { return this }), e = Object.getPrototypeOf(a);
                for (let c in e) d.add(c, a[c]);
                d.responseType = a.responseType; d.withCredentials = a.withCredentials;
                d.response = b; d.responseText = b;
                let h = b.split("\n\n");
                h.length && c.element.ok !== true && (c.element.in(f, 0), c.element.ok = true);
                c.abort = a.abort; h.forEach(e => g(e)); c.chenge(d)
            })
        }
        return c.add("connect", a => d({ method: "POST", body: a, type: json })), c
    })
    isdefine("loadjs", function LoadJsData(a, b) {
        this.require ??= {};
        let c = a => Array.isArray(a) ? Object.fromEntries(a.map(a => [a.split("-").map(a => a[0].toUpperCase() + a.slice(1)).join(""), a])) : null,
            d = a => Array.isArray(a) ? Object.fromEntries(a) : a,
            [e, f, g, h] = Array.isArray(a?.require) ? a.require : [], [i, j] = Array.isArray(h) ? h : [];
        return f = d(f), g = c(g), e ? (this.require[e] = { string: f, _c: g, id: i, session: j }, this.require[e]) : null
    });
    for (const tag of ALT) globals.create[tag] = function create(a, b, c) {
        return this(tag, a, b, c)
    }
    "function" == typeof define && define.amd && define("globals", [], function () { return globals });
    if (typeof n === "undefined") {
        t.$ = globals; t.globals = globals; t.isdefine = isdefine;
    }

    $.DOMContentLoaded(function () {
        const x = (b = globals.weres) => b("button").combined(b("button", false)),
            b = (c = globals.weres) => { c("[data-sjs]", false).for(e => globals.loadjs(JSON.parse(e.textContent))); let d = Object.entries($.domStylelist || {}).map(([a, b]) => { let c = document.createElement("div"); return Object.assign(c.style, b || {}), $(a) && c.style.cssText ? `.${a} { ${c.style.cssText} }` : null }).filter(Boolean).join("\n"); $.styleContainer ??= $.bindFunction(document.head).create("style"), $.styleContainer.setAttribute("rel", "stylesheet"), $.styleContainer.textContent != d && ($.styleContainer.textContent = d) };
        Array.prototype.getbase = function () { return globals.require.find(a => a[0] == "base") };
        let c = new MutationObserver(a => { b(), globals.buttonAnimation(x()); for (let b of a) for (let a of b.addedNodes) { try { F(a.bindLess) && a.bindLess() } catch (b) { } F(a.appended) && (a.appended(a), a.appended = undefined) } });
        b(), globals.buttonAnimation(x()), c.observe(document.body, { childList: true, subtree: true });
        document.addEventListener("mousemove", function (a) { $.cursorElement = document.elementFromPoint(a.clientX, a.clientY); if (Array.isArray($.event.mousemove)) for (let b of $.event.mousemove) b.call(this, a) })
    });
    return globals
});