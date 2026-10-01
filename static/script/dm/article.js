(!function (query, sub) {
    const body = $.bindFunction(document.body), main_body = $.choose("main-body")
    const request = $.apirequest("/api/admin/insert", true);
    const { E, F, FlEXMAP } = $.getFunction();
    const cr = (a, b, c, d) => (a || $).create(b, c, d)
    const sp = (a, b, c, d) => (a || $).create.span(b, c, d)
    const rm = (a, b, c, d) => (a || $.create.span(null)).remove()
    const If = (a) => a.innerHTML = "";

    var ve = '[{"title":"स्वतंत्रता प्राप्ति के समय महात्मा गांधी थे।","correct_answer":"कांग्रेस के सदस्य नहीं थे","incorrect_answer":["कांग्रेस कार्यसमिति के सदस्य","कांग्रेस के महासचिव","कांग्रे्रेस के अध्यक्ष"],"subject":"History","category":["इस्लामिक समाज","भारत छोड़ो आन्दोलन"]},{"title":"स्वतंत्रता प्राप्ति के समय महात्मा गांधी थे।","correct_answer":"कांग्रेस के सदस्य नहीं थे","incorrect_answer":["कांग्रेस कार्यसमिति के सदस्य","कांग्रेस के महासचिव","कांग्रे्रेस के अध्यक्ष"],"subject":"History","category":["इस्लामिक समाज","भारत छोड़ो आन्दोलन"]}]'


    var d, script_data = {};
    for (const e of $.weres("script", false)) {
        e.get("data-content-len")
            ? (d = JSON.parse(e.textContent), script_data[d.id] = d)
            : null;
    }

    const rcs = {
        float: 'right',
        marginRight: 14,
        marginBottom: 14,
        position: 'relative'
    }

    const zp = e => e.in(`${e.replace(/\b\w/g, x => x.toUpperCase())} is required *`, true)

    const actionMap = FlEXMAP({ eventLogger: true });

    function getx(data, callBack) {
        let rq = $.apirequest("/api/admin/auth/t", true);
        callBack ??= function () { }
        rq.progress = function (count) {
        }
        rq.send(data, function (a, b) {
            let params = a.getParams();
            let bind = actionMap.get(params.__ac)
            F(bind) && bind(params, b);
            callBack.call(this, params, b)
        });
        return rq;
    }


    const zg = (a, b, c) => {
        const { t, ...d } = b;
        return a.input({
            title: t, placeholder: t, required: true, F0012: true, ...d
        }, c)
    }
        , xs = (a, b) => a.select({
            name: "subject",
            type: true,
            checked: b,
            value: Object.fromEntries(
                (Geolobal || []).map(({ name: a }) => [a, a])
            )
        })
        , xo = (a, b) => a.switchHolder({
            title: "Save Options",
            name: "datatype",
            desc: "Choose whether to save the current item or save all items.",
            switchValue: ["Next", "All Save"],
            value: b
        })
        , xm = (a, b, c) => a.switchHolder({
            title: "Questions are ", name: c || "status",
            value: b,
            switchValue: ["Publish", "Draft"]
        })
        , xv = (a, b) => {
            const c = a || $.create.span("F0035");
            b && c.in(b instanceof HTMLElement ? b : $.create.span(null,
                `Save Questions (${b.dcount - b.jsonData.length}/${b.dcount})`
            ), !(b instanceof HTMLElement));
            return c;
        }
        , zn = a => String(a ?? "").toLowerCase().replace(/\s+/g, "").trim()

        , zb = (a, b, c, d, e, f, g) => {
            const n = e => typeof g?.loader == "function" && g?.loader(e)
            for (const x of Object.values(b))
                if (Array.isArray(x) ? !x.length : typeof x == "string" && !zn(x))
                    return a.submitError();

            c.addIcon("ic_loader");

            request.error = q => {
                c.choose("icon", false)?.remove();
                a.submitError(q.error), n(false);

                if (b.datatype) {
                    const x = g.p.choose("sskip") || g.p.create("sskip DIS01");
                    x.in($.create.button(null, "Skip").event.on((e) => {
                        e.preventDefault();
                        f();
                    }), true);
                    x.in($.create.button(null, "Replace").event.on((e) => {
                        e.preventDefault()
                        a.input({ name: "replace", value: "replace", class: "hidden" });
                        g.click();
                    }));
                }
            };

            n(true);
            request.send({ ...b, root: e }, q => {
                c.choose("icon", false)?.remove();
                d.push(q.res);
                f(q.res), n(false);
            });
        }
        , zc = (a, b, c) => {
            if (a.status && a.jsonValue) {
                try {
                    b.status = a.status;
                    b.jsonData = JSON.parse(a.jsonValue || "[]");
                    b.dcount = b.jsonData.length;
                }
                catch {
                    c.submitError("Invalid JSON");
                    // return true;
                }
            }
        }
        , zd = (a, b) => $.require("widgets/forms", (f, m = $.popup(a)) => b(f, m));

    const window_event = (t, b) => zd(t, (f, m) => typeof b === "function" && b(f(m), m))
    const gm = (t, b, i, c) => {
        const gh = (f, e, a, w, s, g, t) => {
            const h = "hidden", v = () => f.getValue("tag") || [], r = () => { t.reStore(); s.in(b, null); g.add(h) };
            for (const i of a) if (!v().includes(i)) {
                const c = cr(g, "tag-list-container"), b = f.input({ class: h, type: "checkbox", name: "tag", value: i, title: i, checked: true }, c);
                sp(c, null).event.on(() => (rm(b), rm(c), !v().length && r())).addIcon("ic_close");
                g.removed(h)
            }
            a.length && (rm(t), s.in("Insuet Json", null));
            if (e.tag) { const a = e.tag.filter(x => x !== null).join(","); $("tax-input-post_tag", true).in(a); w.close() }
        }
        return window_event(t, (f, w) => {
            const g = cr(f.getContainer(), "hidden", 0)
                , t = i(f)
                , s = f.submitButton(b);
            g.css({ maxWidth: 700, minHeight: 180, display: "flex", DIS03: "wrap", alignContent: "flex-start" });
            f.submit = e => c(e, a => gh(f, e, a, w, s, g, t), s)
        })
    }


    var category;
    const ga = (sv) => {
        if (!category || !category.length <= 0) {
            category = $.weres("category")
        }
        for (const i of category || [])
            i.get("sub-id") == sv || sv == 0 ? i.removed("hidden") : i.add("hidden")
    }


    actionMap.add(1001, function (a, b) {
        var list, button = $.weres("[jsname]").find(e => e.get("jsname") == a.jsname && e.get("data-content-len") == a.id);
        if (button && (list = button.parentFilter(e => e.nodeName == "TR"))) {
            list.set("class", null);
            button.in(a.inner, true);
            a.cls && list.add(a.cls)
            console.log(a, button, list);
        }
    })


    function teacherRejectIdentity(f, p, a, d) {
        const s = (t, n, x) => f.switchHolder({
            title: t, name: n, desc: x, switchValue: ["No", "Yes"]
        });

        p.t?.in("Educator Reject Verification", true);
        f.clear();

        const t = f.textarea({
            title: "Enter Message",
            name: "rejection_message",
            placeholder: "Enter rejection reason"
        });

        f.arc();
        f.tableList({ value: { Name: d.name, Email: d.email } });

        [["uid", d.uid], ["id", d.id], ["email", d.email]].forEach(([n, v]) =>
            f.input({ type: "hidden", name: n, value: v })
        );

        const r = Object.entries(reasons || {});
        const m = r.map(([key, v]) => [v.title, key]);
        f.select({ name: "reasons", type: true, value: m });
        f.change(e => {
            if (e.target.name === "reasons") {
                const d = r.find(([key]) => key === e.target.value);
                if (d) t.value = d[1].description;
            }
        });

        s("Block Teacher", "block_teacher", "Block this teacher account after rejecting verification.");
        s("Block Private Account", "block_private", "Also block the linked private account.");

        f.button(
            { title: "Save", container: f.container.create("button-container") },
            e => getx(
                { ...e, id: d.id, verify: false, email: d.email },
                r => {
                    if (r.message) $.message(r.message);
                    if (r.status) p.close();
                }
            )
        );
    }



    for (const button of $.weres("a", false).filter(function (a) { return a.get("href") == "javascript:void(0)" })) {

        button.inclass("edit", e => e.event.on(function (e) {
            const span = this.choose("span"), option = this.p.choose(this.get("aria-label"), true)
            span.in(option.isclass("hidden") ? "Ok" : "Edit")
            option.toggle("hidden")
            console.log(span, option.isclass("hidden"));
        }))
        button.inclass("select-parameter", e => e.event.on(function () {
            console.log(this);
        }));
        button.inclass("add-parameter", e => e.event.on(function (e) {
            console.log(this);
        }));

    }





    $.require("dm/action", e => {
        for (const i of $.weres("[jsname]") || []) {
            const b = e.export(i.get("jsname"));
            i.event.on(() => typeof b == "function" && b(i, i.get("data-content-len") || 0));
        }
    })

}($ || window.$));


(function (form, request = $.apirequest("/api/v1/content/update", true)) {
    request.progress = function (e) {
        console.log("progress=>", e);
    }
    request.finish = function (e) {
        console.log("finish=>", e);
    }
    return form ? form.event.change(e => request.send(new FormData(form))) : null
})($("as-action-form"));



