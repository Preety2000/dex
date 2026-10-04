$.define("dm/action", function Action(ED) {
    var category = $.weres("category");
    const { N, E, A, B, F } = $.getFunction();
    var ve = '[{"title":"स्वतंत्रता प्राप्ति के समय महात्मा गांधी थे।","correct_answer":"कांग्रेस के सदस्य नहीं थे","incorrect_answer":["कांग्रेस कार्यसमिति के सदस्य","कांग्रेस के महासचिव","कांग्रे्रेस के अध्यक्ष"],"subject":"History","category":["इस्लामिक समाज","भारत छोड़ो आन्दोलन"]},{"title":"स्वतंत्रता प्राप्ति के समय महात्मा गांधी थे।","correct_answer":"कांग्रेस के सदस्य नहीं थे","incorrect_answer":["कांग्रेस कार्यसमिति के सदस्य","कांग्रेस के महासचिव","कांग्रे्रेस के अध्यक्ष"],"subject":"History","category":["इस्लामिक समाज","भारत छोड़ो आन्दोलन"]}]'
    const request = $.apirequest("/api/admin/insert", true);
    const cr = (a, b, c, d) => (a || $).create(b, c, d)
    const sp = (a, b, c, d) => (a || $).create.span(b, c, d)
    const rm = (a, b, c, d) => (a || $.create.span(null)).remove()
    const If = (a) => a.innerHTML = "";
    const rcs = {
        float: 'right',
        marginRight: 14,
        marginBottom: 14,
        position: 'relative'
    }

    const zp = e => e.in(`${e.replace(/\b\w/g, x => x.toUpperCase())} is required *`, true)
        , zd = (a, b) => $.require("widgets/forms", (f, m = $.popup(a)) => b(f, m))
        , zg = (a, b, c) => {
            const { t, ...d } = b;
            return a.input({ title: t, placeholder: t, required: true, F0012: true, ...d }, c)
        }
        , xs = (a, b) => a.select({
            name: "subject", type: true, checked: b,
            value: Object.fromEntries((Geolobal || []).map(({ name: a }) => [a, a]))
        })
        , xo = (a, b) => a.switchHolder({
            title: "Save Options", name: "datatype",
            desc: "Choose whether to save the current item or save all items.",
            switchValue: ["Next", "All Save"], value: b
        })
        , xm = (a, b, c) => a.switchHolder({
            title: "Questions are ", name: c || "status", value: b,
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
                c.choose("icon", false)?.remove(); a.submitError(q.error), n(false);
                if (b.datatype) {
                    const x = g.p.choose("sskip") || g.p.create("sskip DIS01");
                    x.in($.create.button(null, "Skip").event.on((e) => { e.preventDefault(); f(); }), true);
                    x.in($.create.button(null, "Replace").event.on((e) => {
                        e.preventDefault(), a.input({ name: "replace", value: "replace", class: "hidden" }); g.click();
                    }));
                }
            };

            n(true); request.send({ ...b, root: e }, q => { c.choose("icon", false)?.remove(); d.push(q.res); f(q.res), n(false); });
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
        , za = (t, b) => zd(t, (f, m) => typeof b === "function" && b(f(m), m))
        , gm = (t, b, i, c) => {
            const gh = (f, e, a, w, s, g, t) => {
                const h = "hidden", v = () => f.getValue("tag") || [], r = () => { t.reStore(); s.in(b, null); g.add(h) };
                for (const i of a) if (!v().includes(i)) {
                    const c = cr(g, "tag-list-container"), b = f.input({ class: h, type: "checkbox", name: "tag", value: i, title: i, checked: true }, c);
                    sp(c, null).event.on(() => (rm(b), rm(c), !v().length && r())).addIcon("ic_close"); g.removed(h)
                }
                a.length && (rm(t), s.in("Insuet Json", null));
                if (e.tag) { const a = e.tag.filter(x => x !== null).join(","); $("tax-input-post_tag", true).in(a); w.close() }
            }
            return za(t, (f, w) => {
                const g = cr(f.getContainer(), "hidden", 0), t = i(f), s = f.submitButton(b);
                g.css({ maxWidth: 700, minHeight: 180, display: "flex", flexWrap: "wrap", alignContent: "flex-start" });
                f.submit = e => c(e, a => gh(f, e, a, w, s, g, t), s)
            })
        }
        , ga = (sv) => {
            if (!sv) return;
            const a = $("categorychecklist", true);
            if (!category || category.length < 0) {
                category = $.weres("category")
            }
            for (const i of category || []) {
                i.remove();
                (i.get("sub-id") == sv
                    || sv == 0
                    || i.isclass("_checkbox")
                    || i.isclass("_radio")) && a.append(i)
            }
        }
        , getx = (data, callBack) => {
            let rq = $.apirequest("/api/admin/auth/t", true);
            callBack ??= function () { }
            rq.progress = function (count) {
            }
            rq.send(data, function (a, b) {
                let params = a.getParams();
                params.__ac == 1001 && gl(params, b);
                callBack.call(this, params, b)
            });
            return rq;
        }
        , gl = (a, b) => {
            var list, button = $.weres("[jsname]").find(e => e.get("jsname") == a.jsname && e.get("data-content-len") == a.id);
            if (button && (list = button.parentFilter(e => e.nodeName == "TR"))) {
                list.set("class", null);
                button.in(a.inner, true);
                a.cls && list.add(a.cls)
                console.log(a, button, list);
            }
        }

    $.DOMContentLoaded(() => {
        const s = $('[jsname="ACSTC"]')
            , h = $('[jsname="ACSSC"]')
            , t = (i, o) => i.checked
                ? o.add("_" + i.type)
                : o.removed("_" + i.type);

        if (!s || !h) return;
        h.value = s.value; ga(h.value);
        for (const i of category || []) {
            for (const j of i.querySelectorAll("input"))
                j.onclick = () => t(j, i), t(j, i);
        }
    });

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

    var d, script_data = {};
    for (const e of $.weres("script", false)) {
        e.get("data-content-len")
            ? (d = JSON.parse(e.textContent), script_data[d.id] = d)
            : null;
    }


    $.event("insert-media-button", e => e.event.on(function () {
        console.log(this);

        zd("Media", (f, m) => {
            var iframe = m.create({
                tagName: "iframe",
                class: "myFrame add-media",
                src: "/container/media",
                height: true,
            });
            iframe.css({
                minHeight: 500,
                minWidth: 840,
            });

            var uplode = iframe.create.a("option-button", "Uplode")
            var select = iframe.create.a("option-button", "Select")

            console.log(iframe, uplode);

        });
    }), true)

    return $(function Action() {
        var a;
        const _ = this, ep = (a, b) => this.add(a, b);
        ep(function ACANC(a, b) {
            return zd("Add New Category", (f, m) => {
                f = f.buildFormLayout(m, true);
                const d = { jsonData: [] },
                    sd = [],
                    lo = xv(),
                    r = (e, v) => e.datatype ? d.jsonData?.length
                        ? l(d.jsonData.shift(), true, e.datatype)
                        : (sd.forEach(u), m.close()) : (u(v), m.close()),

                    u = e => {
                        let d = e.is("data");
                        if (!d?.id) return;

                        let m = a.parentFilter(e => e.isclass("inside"));
                        if (!m) { return; }

                        let b = m.choose("categorychecklist", true)
                            .create.li("category")
                            .add("id", "category" + d.id)
                            .add("sub-id", d.subject_id),
                            c = b.create.label("F0009");

                        c.create({
                            tagName: "input",
                            value: d.id,
                            type: "checkbox",
                            checked: true,
                            class: "category-input category-" + d.id,
                            "aria-label": "category-" + d.id,
                            name: "category[]"
                        });

                        c.create({
                            tagName: "input",
                            id: "post-type",
                            value: d.id,
                            type: "radio",
                            name: "type",
                            class: "category-input category-" + d.id,
                            "aria-label": "category-" + d.id
                        });

                        c.create.span("span", d.name);
                    },
                    s = e => zb(f, e, lo, sd, "cot", (rs) => r(e, rs), sub),
                    l = (e, m, t) => {
                        f.clear();
                        f.alc();

                        zg(f, { name: "name", value: e.name, t: "Name" });
                        zg(f, { name: "slug", value: e.slug, t: "Slug" });

                        f.textarea({
                            name: "description",
                            value: e.description,
                            placeholder: "Abouts",
                            required: true
                        });

                        f.arc();
                        m && f.append(xv(lo, d));

                        xs(f, Geolobal.find(a => zn(a.name) == zn(e.subject))?.name);

                        f.radio({
                            name: "resource",
                            value: [
                                { title: "Disable", value: 0 },
                                { title: "Enable", value: 1 }
                            ],
                            desc: "Use this Category in URL parameters?",
                            checked: e.resource || 0,
                            type: "button"
                        });

                        f.radio({
                            name: "topic",
                            value: [
                                { title: "Disable", value: 0 },
                                { title: "Enable", value: 1 }
                            ],
                            desc: "Use this Category in search category?",
                            checked: e.topic || 1,
                            type: "button"
                        });

                        m && xo(f, t);

                        sub = f.submitButton("Submit");
                        !m && sub.p.in(
                            $.create.button(null, "Use Json Data Insurt")
                                .event.on(g),
                            0
                        );

                        f.submit = s;
                        f.alc();
                        f.error = e => f.container.create.p("F0017", e.error);

                        t == "All Save" && sub.click();
                    },

                    g = () => {
                        const v = f.getValue();

                        if (zc(v, d, f)) return;
                        if (d.jsonData?.length) return l(d.jsonData.shift(), true);

                        f.clear();
                        f.textarea({
                            name: "jsonValue",
                            placeholder: 'Fill Json Query like: {"name": "","slug": "","subject": "","description": ""}'
                        });

                        xm(f)

                        f.nextButton(g);
                    };

                l({ resource: true });
                m.css({ minWidth: 1080, maxHeight: 700 });
            })
        })
        ep(function ACANS(a, b) {
            zd("Add New Subject", (form, popupWindow) => {
                form = form(popupWindow);
                form.switchHolder({
                    title: "Multiple Categories",
                    name: "onof",
                    switchValue: ["on", "of"],
                    desc: "Enable this option to assign multiple category to a subject."
                });

                form.input([
                    { name: "name", value: "", placeholder: "Name" },
                    { name: "slug", value: "", placeholder: "Slug" }
                ]);

                form.textarea({
                    name: "content", value: "", placeholder: "content"
                });
                form.submitButton("Add Subject");
                form.setRequestRoot("/api/admin/subject/insert", true)

                form.error = r => $.confirm({ t: r.data.error, c: "Ok" })

                form.finish = r => {
                    if (!r.success)
                        return

                    let s = $("[name='subject_id']", false);
                    s && s.create.option({
                        "sub-id": r.data.data.id,
                        value: r.data.data.id,
                        inner: r.data.data.name
                    });
                    popupWindow.close();
                }

            })
        })
        ep(function AC0ST(a, b) {
            return gm("Search Tag for DataBace", "Search", e => e.input({ name: "q", value: "", placeholder: "Tag Keywords" }), (e, b, bt) => $.apirequest("/api/admin/tags/search", true).send(e, r => b([...r.res.is("query")].map(e => e.name))));
        })
        ep(function ACAGT(a, b) {
            return gm(a.innerText, "Apply", e => e.textarea({ class: "description", name: "description", placeholder: "Enter json $." }), (e, b) => { const f = s => s.replace(/<\/?b>/g, ""); b([...new Set((JSON.parse(e.description?.slice(6) || "[]")?.[0] || []).map(x => f(x[0])))]) });
        })
        ep(function ACAJQ(a, b) {
            return zd("Add Questions", (f, m) => {
                f = f.buildFormLayout(m, true
                    // , "json-practice-container"
                )
                f.textarea({ value: ve, name: "jsonValue", placeholder: "Fill Json Query" }), xm(f);

                const d = { jsonData: [] }, l = xv(), s = [], o = () => {
                    f.clear(); let g = f.container.create("sfully").create;
                    g.strong(null, "Successfull");
                    g.p(null, `Successfully inserted ${s.length} question${s.length != 1 ? "s" : ""}.`);
                    g.button(null, "Close").event.on(() => m.close());
                }, n = (v) => d.jsonData?.length ? r(v) : o()
                    , r = (v) => {
                        try {
                            f.clear();
                            const a = d.jsonData.shift();
                            zg(f, { name: "title", t: "Title", value: a.title });

                            const o = f.container.create("F0011"), t = o.create.div(), z = o.create("list-input");
                            t.create.strong(null, "Answer Options");
                            t.create.p("F0020", "Enter the correct answer and up to three incorrect answers.");

                            zg(f, { name: "correct_answer", t: "Correct Answer", value: a.correct_answer }, z);
                            (a.incorrect_answer || []).forEach((x, i) => zg(f, { name: "incorrect_answer[]", t: `Incorrect Answer ${i + 1}`, value: x }, z));
                            f.textarea({
                                name: "excerpt",
                                desc: "Add any additional details or context to help understand the question",
                                value: a.excerpt
                            }).css({ minHeight: 200 });

                            f.arc(), f.append(xv(l, d)), xm(f, d.status, "s-status");



                            const c = f.container.create("boderx"), e = p => {
                                const d = (p || []).filter(x => x.name && x.id), x = d.map(x => [x.id, x.name]),
                                    y = d.filter(x => (a.category || []).includes(x.name)).map(x => x.id);
                                If(c), f.checkbox({ title: "Categories", name: "category", value: x, checked: y, container: c })
                            };

                            if (a.subject) {
                                const x = Geolobal.find(x => zn(x.name) == zn(a.subject)) || {};
                                xs(f, x.name), e(x.terms)

                            } else { e() }
                            f.append(c), xo(f, v.datatype);
                            f.change(x => {
                                if (x.target.name != "subject") return;
                                for (const i of f.getInputs()) i.name == "category" && i.remove();
                                e((Geolobal.find(y => zn(y.name) == zn(x.target.value)) || {}).terms)
                            });

                            nx.in("Submit Question", true), f.append(nx.p);
                            setTimeout(() => v.datatype == "All Save" && nx.click(), 50);
                        } catch (e) {
                            f.clear();
                            f.submitError(e);
                        }

                    }, x = () => {
                        const v = f.getValue();
                        zc(v, d, f)

                        if (Object.keys(v).includes("title") > 0) {
                            if (!Object.keys(v).includes("category")) return f.submitError();
                            return zb(f, v, l, s, "practice", (rs) => n(v, rs), nx)
                        }
                        r(v)
                    }, nx = f.nextButton(x);

                m.css({ minWidth: 1080, maxHeight: 700 })
            })
        })
        ep(function ACSSC(a, b) {
            if (_.subject_id == a.value) return;
            _.subject_id = a.value; ga(_.subject_id);

        })
        ep(function ACSTC(a, b) {
            const s = $('[jsname="ACSSC"]');
            s.value = a.value || 0;
            _.ACSSC(s);
        })
        ep(function AC0TT(a, b) {
            let r, i = $(`[jshendler="${a.id}"]`), title = $('[name="title"]') || $('[name="name"]');

            if (i.jscode == 0) {
                i.value = title.value;
                i.dispatchEvent(new Event('input'));
                return
            }
            let ar = $.apirequest("/translate");
            ar.finish = function (e) {
                if (r = e.is("data")) i.value = r;
            }
            ar.send({ q: i.value });
        })
        ep(function ACTVU(a, b) {
            zd(null, (m, p) => {
                const d = script_data[a.get("data-content-len")];
                p = $.popup("Educator Identity Verification", "verification");

                const g = p.create("top-group");
                const f = m.buildFormLayout(g);

                if (d.status === 1)
                    return teacherRejectIdentity(f, p, a, d);

                console.log(d);

                const o = () => window.open(
                    d.document_url,
                    "documentWindow",
                    "width=600,height=800,resizable=yes,scrollbars=yes"
                )


                f.tableList({
                    value: {
                        Name: d.name,
                        Phone: d.phone,
                        Email: d.email,
                        Subject: d.subject,
                        Experience: d.experience,
                        Biography: d.biography,
                        Rejects: String(d.rejects.length),
                        "Request Time": f.formatZenoTime(d.request_timestamp, "F"),
                        Document: {
                            tagName: "a",
                            href: d.document_url,
                            class: "DIS00",
                            inner: d.document_name,
                            target: "_blank",
                            icon: "ic_link",
                            onclick: e => (e.preventDefault(), o())
                        }
                    }
                });

                f.arc();
                f.container.css({ width: 150, flex: "none" });
                f.container.create("img-container").create({
                    tagName: "img",
                    src: d.img
                });

                const b = f.container.create("button-container");

                const x = (title, verify) => f.button(
                    { title, container: b },
                    () => getx(
                        { id: d.id, verify, email: d.email },
                        r => {
                            if (r.message) $.message(r.message);
                            if (r.status) p.close();
                        }
                    )
                );

                x("Verify", true);
                f.button(
                    { title: "Reject", container: b },
                    () => teacherRejectIdentity(f, p, a, d)
                );

                b.css(rcs);
            });
        })
        ep(function setting(a, b) {
            zd("Setting", (form, popupWindow) => {
                var database = popupWindow.create("database");
                $.require("dm/setting", function (adminSetting) {
                    adminSetting($, database)
                })
            })
        })

        console.log(this);

        return this
    })
}())












$.define("actionForm", function actionForm(was, extend, modules) {
    "use strict";
    const { E, F, FlEXMAP } = $.getFunction();
    // function dtg(form, id, array, groli, popup) {
    //     let forse = form.getFormSession();
    //     let submit = forse.choose("submit");
    //     var group = forse.choose(id, true) || forse.create("IN0104");
    //     var bind = function () {
    //         array.forEach(function (insex, index) {
    //             if (!groli[insex]) {
    //                 groli[insex] = group.create("tag-list-container");
    //                 var tag_title = groli[insex].create.span("tag-title", insex)
    //                 groli[insex].create.span("close-button").event.on(function () {
    //                     tag_title.remove();
    //                     groli[insex].add("hidden");
    //                     delete array[index];
    //                     delete groli[insex];
    //                 }).addIcon("ic_close")
    //             }
    //         });
    //     }

    //     group.add("id", id);
    //     bind();

    //     E(submit)
    //         ? submit.remove()
    //         : null;

    //     forse.create("combine", "Combine").add("button").event.on(function () {
    //         let box = $("tax-input-post_tag", true);
    //         let oldtags = box.value.split(",");

    //         array = [...new Set([...array, ...oldtags])]
    //         array = array.filter(item => item !== null && item !== "" && item !== undefined);
    //         bind();
    //         this.remove();

    //         submit = forse.create("submit", "Insuet");
    //         submit.add("button").event.on(function () {
    //             array = array.filter(e => e !== null);
    //             box.in(array.join(","));
    //             popup.close();
    //         })
    //     });
    //     return submit;
    // }

    // Create the central action map
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







    modules = modules || $.module.list;

    modules.add("addNewUniversity", function addNewUniversity() {
        // Import the form module and PopupWindow from previously defined modules
        var form = was.export("form");
        var PopupWindow = was.export("PopupWindow");

        // Create a new popup window with the title "Add a new subject"
        var popupWindow = PopupWindow("Add a new University");

        // Initialize the form inside the popup window container
        form = form(popupWindow.container);

        // Create a switch input holder inside the form for toggling subject options
        form.switchHolder({
            title: "Subject Option on off",  // Title of the switch
            name: "onof",                    // Name attribute for the switch input
            switchValue: ["on", "of"]        // Values for the switch (on/off)
        });

        // Create multiple input fields using an array of options
        form.input({ name: "slug", value: "", placeholder: "Uri" });

        // Create a textarea input for additional details (name field)
        form.textarea({ name: "name", value: "", placeholder: "University Name" });

        // Create a submit button with the label "Add Subject"
        form.submitButton("Add University");

        // Override the form's submit method to handle form submission
        form.submit = function () {
            var values = form.getValue()
            var formData = new FormData();
            var dataSubmit = was.export("dataSubmit");

            for (const [name, value] of Object.entries(values)) {
                formData.append(name, value);
            }

            dataSubmit({
                progress: popupWindow.onprogress,
                callBack: function (e) {
                    console.log(e);
                },
                formData: formData,
                request: "/admin/insert/university"
            })
        };

    })


    modules.add("filter", function Filter() {
        console.log("Filter");


    })



    modules.add(function userBlockUnblock(a) {
        console.log(this);
    });

    // function errorHandler(error) {
    //     alert("Error getting location: " + error.message);
    // }
    // navigator.geolocation.getCurrentPosition(e => console.log(e), errorHandler, {
    //     enableHighAccuracy: true,
    //     timeout: 10000,
    //     maximumAge: 0
    // });

    const rcs = {
        float: 'right',
        marginRight: 14,
        marginBottom: 14,
        position: 'relative'
    }

    modules.add(function teacherVerifyTndentityView(a) {
        console.log(this);
    });
    modules.add(function addMedia(a) {

        var mediaUplode = function (button) {
            console.log(button, this);

        }
        var mediaSelect = function (button) {
            console.log(button, this);

        }
        // Import the form module and PopupWindow from previously defined modules
        var form = was.export("form");
        var PopupWindow = was.export("PopupWindow");

        // Create a new popup window with the title "Add a new subject"
        var popupWindow = PopupWindow("Add Media", "verification");
        // var navigation = popupWindow.container .create("DIS00 navigation");
        var navigation = popupWindow.container.create({
            tagName: "iframe",
            class: "myFrame add-media",
            src: "/container/media",
            height: true
        });
        console.log(popupWindow.container.get("height"));

        return
        var uplode = navigation.create.a("option-button", "Uplode")
        var select = navigation.create.a("option-button", "Select")
        var contentContainer = popupWindow.container.create("content-container");
        uplode.event.on(mediaUplode), select.event.on(mediaSelect);
        mediaUplode()
        console.log(popupWindow.container);
    });

    $.event("as-action-form", function () {
        $.fch("/api/admin/category?lgx=id/name", {
            callback: function (category) {
                console.log(category.is("category"));
                modules.add("category", category.is("category"));
            }
        });
    })


    return modules;
})