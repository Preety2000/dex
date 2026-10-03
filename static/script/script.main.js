
$.DOMContentLoaded(query => $.require("worker", function (module) {
    const worker = module();

    console.log("Worker module loaded successfully:", worker);

    // Navigation Menu 
    worker.navigation("drawerLayout", function (drawer_layout) {
        var a, c
            , d = function () { c === true ? e() : f() }
            , e = function () { c = false, drawer_layout.removeAttribute("style"), a.close() }
            , f = function () { c = true, drawer_layout.style.left = 0, a = $.windows(null, { container: drawer_layout, functions: e, noremove: true }, true) };
        $.weres("IN040").for(e => e.event.on(d));
    })

    $.event("IN056", function (scrolltopButton) {
        let scrolling = function () {
            document.body.classList.toggle('scroll', window.scrollY > 20);
            scrolltopButton.classList.toggle('active', window.scrollY > 380);
            scrolltopButton.event.on(function () { window.scrollTo({ top: 0, behavior: 'smooth' }) });
        };
        scrolling();
        window.onscroll = scrolling;
    })

    $.weres("tallbar").for(e => e.event.on(function (button) {
        button = this.p.choose("options");
        if (this.p.get("aria-expanded") == "true") {
            height = 0;
            marginTop = 0;
            opacity = 0;
            this.p.add("aria-expanded", false)
        }
        else {
            height = "max-content";
            marginTop = "10px";
            opacity = "inherit";
            this.p.add("aria-expanded", true)
        }
        button.style.height = height
        button.style.marginTop = marginTop
        button.style.opacity = opacity

    }))


    $.weres("label-link").for(a => a.event.mouseover(function () {
        const g = a.p.choose("tag-info");
        g && $.tooltip(this, null).executed(
            $.create("tag-tooltip", a.p.choose("tag-info").innerHTML)
        );
    }))


    $.getHtmlBody(function (htmlBody) {
        htmlBody.isclass("mobile") && $.require("mobile", (bind) => bind(htmlBody));
    });

    // Remove old  Session
    let storage = $.storage();
    for (const [name, value] of Object.entries(storage.getAll() || {})) {
        let expiry = value.export("expiry");
        if (expiry && (Math.floor((expiry - Date.now()) / 1000) <= 0)) {
            try { $.storage(name).remove() }
            catch (error) { }
        }
    }

    // Voice Search 
    (function (spr, search) {
        spr && search ? function (rec, str, forms = search.parentFilter(e => e.localName == 'form'), voice = forms.create("IN048")) {
            voice.addIcon("ic_voice");
            rec.lang = "hi-IN";
            rec.interimResults = false;
            rec.maxAlternatives = 1;
            voice.event.on(e => str(rec, forms))
        }(new spr(), function (rec, forms, win = $.popup()) {
            win.add("IN050")
                , win.create("IN051").addIcon("anm_voice")
                , win.create("see-text", "Listening...")
                , rec.start()
                , rec.onresult = function (event) {
                    search.value = event.results[0][0].transcript.toLocaleLowerCase()
                        , (forms.choose("IN058") || forms.choose("IN049")).click()
                        , win.close();
                }
                , rec.onerror = (e) => {
                    if (e.error === "not-allowed") {
                        $.message("Microphone access denied. Please allow mic permissions in your browser settings.");
                    } else if (e.error === "network") {
                        $.message("You're offline. Please check your internet connection.");
                    } else {
                        $.message("Speech recognition error: " + e.error);
                    }
                    console.error("SpeechRecognition error:", e.error);
                    win?.close();
                }

        }) : null
    }(window.SpeechRecognition || window.webkitSpeechRecognition, $('[type="search"]')));


    $(function $ActionButton() {
        const m = this, r = $.req(), x = f => m.add(f);

        x(function linkAction(a) {
            let b = a.get?.("href") || a.href, c = b && new URL(b, location.href);
            return !c || (c.href !== r.href && a.get?.("action") !== "false" && r.navigate(c.href)), true;
        });

        x(function clickAction(a) {
            if (a.get?.("target")) return;
            try { new URL(a.href).href === r.href && a.get?.("jsname") && m.inhance(a); } catch { }
            return a.addEventListener("click", b => (b.preventDefault(), m.inhance(a)));
        });

        x((name, cb) => $.module({
            worker: ["subMenu", "accountWindow", "likes", "navigation"],
            worker: ["createTest", "createObject", "testDashbord", "testList"],
            quits: ["functionQuedt", "LogMetel", "SourceBuffer"]
        }, name, cb));

        x(function inhance(a) {
            let b = a.get?.("jsname"), c = a.loader || (() => { }), d = $.module.list.get(b);
            return typeof d == "function" ? d.call(a) : (!m.linkAction(a) || a.loadingAction || b == "false") ? void 0 : c(true) && m.lM(b, k => (c(false), typeof k == "function" ? k.call(a, query) : $.message("Your request could not be processed. Please reload this page.")));
        });

        x(function exquiter(e) {
            $.weres("IN028").for(a => {
                if (a.scrollHeight <= a.clientHeight || a.p.querySelector('.IN029')) return;
                const b = a.p.create('IN029'), c = b.create('IN030');
                a.style.position = 'relative'; a.add('scro');
                const s = () => [b.clientHeight - c.clientHeight, a.scrollHeight - a.clientHeight],
                    u = () => {
                        if (c.isclass("active")) return;
                        c.css({ height: Math.max(a.clientHeight * (a.clientHeight / a.scrollHeight), 20) });
                    };
                a.sv ??= d => {
                    const [m, n] = s();
                    a.scrollCount = Math.max(0, Math.min(d, m));
                    a.scrollTop = m ? (a.scrollCount / m) * n : 0;
                };
                a.event.mouseover(u);
                c.event.mousedown(() => (c.add("active"), document.body.classList.add('IN006')));
                document.addEventListener("mouseup", () => (c.removed("active"), document.body.classList.remove('IN006')));
                a.event.scroll(() => {
                    const [m, n] = s(), t = n ? Math.round((a.scrollTop / n) * m) : 0;
                    c.css({ top: t }); a.scrollCount = t;
                });
                document.addEventListener("mousemove", g => c.classList.contains("active") && a.sv((a.scrollCount ?? 0) + g.movementY));
                u();
            });

            $.weres("[jsname]", false).for(b => b.module || (m.clickAction(b), b.module = true));
        });

        new MutationObserver(e => m.exquiter(e)).observe(document.body, { childList: true, subtree: true });
        m.exquiter(null);
    });

}));








