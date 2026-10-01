class Element {
    constructor() {
        this.hooks = FlEXMAP();
        this.classNameContainer = FlEXMAP();
        this.styleContainer = document.createElement("style");
        this.styleContainer.setAttribute("rel", "stylesheet");
        document.head.append(this.styleContainer);
    }
    create(name, value = {}) {
        let session = this;
        let set_style = this.exquitStyle
        let XCS = typeof name == "object" ? name : value;
        let XCN = typeof name == "string" ? name : this.getNewClassName();
        let element = document.createElement(this.tagName || "div");
        let match = Object.values(this.hooks).find(e => {
            if (e.constructor !== ElementBind) {
                return
            }
            (e.element.isConnected || $(e.XCN)) && (e.isConnected = true);
            return Object.keys(e.XCS).length !== 0 && Xj(e.XCS, XCS)
        });

        match && (XCN = match.element.classList[0]);
        element.classList.add(XCN);
        let elem = element;

        set(elem, "XCS", XCS);
        set(elem, "XCN", XCN);

        set(elem, "setStyle", function setStyle(name, value, important) {
            if (typeof name === "object" && name !== null) {
                for (const [key, val] of Object.entries(name))
                    this.setStyle(key, val);
            }
            else { this.style.setProperty(name, value, important); }
            return this;
        })
        set(elem, "scs", function setStyle(name, value, important) {
            if (typeof name === "object" && name !== null) {
                for (const [key, val] of Object.entries(name))
                    this.scs(key, val);
            }
            else { this.CCS ??= {}; this.CCS[name] = value; }
            set_style.call(session);
            return this;
        })

        set(elem, "set", function toggleAttr(attrOrCls, value, shouldSet) {

            // Function to handle attribute setting and removal
            const setOrRemoveAttribute = function (attributeName, value, shouldSet) {
                if (attributeName.length <= 1 || typeof element === "undefined") {
                    return element;
                }
                shouldSet === !0 && S(attributeName) && value !== null
                    ? element.setAttribute(attributeName, value)
                    : element.removeAttribute(attributeName, value);
                return element;
            };

            // Function to handle attribute setting
            const setAttribute = function (attributes, shouldSet) {
                for (const [attributeName, value] of Object.entries(attributes)) {
                    element = setOrRemoveAttribute(element, attributeName, value, shouldSet)
                }
                return element
            };

            // Function to handle class addition and removal
            const addOrRemoveClass = function (classNames, shouldAdd) {

                if (typeof classNames !== "object") {
                    classNames = classNames.split(" ");
                }
                classNames = classNames.filter(name => name && name.trim() !== '');
                for (const className of classNames)
                    shouldAdd === !0
                        ? element.classList.add(className.trim())
                        : element.classList.remove(className.trim());

                return element;
            };

            if (typeof attrOrCls === "undefined" || attrOrCls == null) {
                return element;
            }

            if (attrOrCls?.tagName) {
                element.append(attrOrCls)
                return element;
            }

            if (typeof attrOrCls === "object" && !attrOrCls?.tagName) {
                return setAttribute(attrOrCls, shouldSet)
            }

            let parts = attrOrCls.split("=");
            parts.length > 1 && (attrOrCls = parts[0], value = parts[1]);

            return typeof value === "undefined" && typeof value !== "boolean"
                ? addOrRemoveClass(attrOrCls, shouldSet)
                : setOrRemoveAttribute(attrOrCls, value, shouldSet);
        })
        set(elem, "build", function createElement(name, value, index) {
            let element = session.create(name, value);
            this.element.append(element.element);
            return element
        })
        set(elem, "event", function addEventListener(eventType, handler) {
            element.addEventListener(eventType, handler);
            return element;
        })
        set(elem, "getStyle", function getStyle() {
            const getStyleProxy = function (source, callback) {
                const ComputedStyle = window.getComputedStyle(element);
                const getVelue = function name(source) {
                    return ComputedStyle[source] == "none" ? null : ComputedStyle[source]
                }
                return F(source)
                    ? source(ComputedStyle)
                    : F(callback)
                        ? callback(getVelue(source))
                        : getVelue(source)
            }
            return getStyleProxy(content, callback)
        })
        set(elem, "replace", function replaceElement(replace_element) {
            var parent = element.parentNode;
            parent.insertBefore(replace_element, element);
            return replace_element;
        })
        set(elem, "isclass", function checkClass(className) {
            return element.classList.contains(className);
        })

        if (MURCHED.indexOf(elem.tagName.toLocaleLowerCase()) <= 0) {
            elem.event.add = function (eventType, handler) {
                elem.event(eventType, handler);
                return a;
            };
            elem.event.remove = function (eventType, handler) {
                removeEventListenerBackup(eventType, handler);
                return a;
            };
            elem.event.on = function (handler) {
                meta.event("click", handler);
                return a;
            };
            elem.event.off = function (handler) {
                removeEventListenerBackup("click", handler);
                return a;
            };
            for (let i = 0; i < EVENT.length; i++) {
                elem.event[EVENT[i]] = function eventHandler(handler) {
                    elem.event(EVENT[i], handler);
                    return a;
                };
            }
        }

        this.hooks.add(XCN, elem);
        set_style.call(this);
        return elem;
    }
    add(name, value) {
        let gt = (a, b) => {
            F(a) ? this[a.name] = a : this[a] = b;
            return this;
        }
        let gf = (a, b) => {
            for (const i of a) this[i] = b[i];
            return this;
        }
        let gk = a => {
            for (const [k, v] of Object.entries(a)) gt(k, v);
            return this;
        }

        return B(name)
            ? gk(name)
            : A(name) && typeof value == "object"
                ? gf(name, value)
                : gt(name, value);
    }
    get(name, value = null) {
        return this.hasOwnProperty(name) ? this[name] : value;
    }
    remove(key) {
        if (this.hasOwnProperty(key)) {
            delete this[key];
        }
        return this;
    }
    exquitStyle() {
        const cssRules = Object.entries(this.hooks).map(([className, elem]) => {
            const tempDiv = document.createElement("div");
            Object.assign(tempDiv.style, elem.XCS, elem.CCS || {});
            return tempDiv.style.cssText ? `.${className} { ${tempDiv.style.cssText} }` : null;
        }).filter(Boolean).join("\n");

        this.styleContainer.textContent = cssRules;
        return this;
    }
    getNewClassName() {
        let e = Xi();
        let g = $.makeid(6);
        while (e.indexOf(g) > -1) {
            g = $.makeid(6);
        }
        this.lastClassName = g;
        return g;
    }
}


$.require("widgets/forms", (f, m = $.popup("Add New Category")) => {
    f = f(m, (b, f) => {
        let a = b.create("new-category"),
            c = a.create("left"),
            d = a.create("right");

        f.add("alc", () => f.setcontainer(c));
        f.add("arc", () => f.setcontainer(d));
        f.alc();
    });

    const d = { jsonData: [] },
        sd = [],
        lo = xv(),
        r = (e, v) => e.datatype
            ? d.jsonData?.length
                ? l(d.jsonData.shift(), true, e.datatype)
                : (sd.forEach(u), m.close())
            : (u(v), m.close()),

        u = e => {
            console.log(e);
            let a = e.is("data");
            if (!a?.id) return;

            let b = sdd.parentFilter(e => e.isclass("inside"))
                .choose("categorychecklist", true)
                .create.li("category")
                .add("id", "category" + a.id)
                .add("sub-id", a.subject_id),
                c = b.create.label("F0009");

            c.create({
                tagName: "input",
                value: a.id,
                type: "checkbox",
                checked: true,
                class: "category-input category-" + a.id,
                "aria-label": "category-" + a.id,
                name: "category[]"
            });

            c.create({
                tagName: "input",
                id: "post-type",
                value: a.id,
                type: "radio",
                name: "type",
                class: "category-input category-" + a.id,
                "aria-label": "category-" + a.id
            });

            c.create.span("span", a.name);
        },

        s = e => {
            const cb = sub?.loader;

            for (const [k, x] of Object.entries(e))
                if (Array.isArray(x) ? !x.length : typeof x == "string" && !zn(x))
                    return f.submitError();

            lo.addIcon("ic_loader");
            typeof cb == "function" && cb(true);

            request.error = q => {
                lo.choose("icon", false)?.remove();
                f.submitError(q.error);
                typeof cb == "function" && cb(false);

                e.datatype && (sub.p.choose("sskip") || sub.p.create("sskip"))
                    .in(
                        $.create.button(null, "Skip")
                            .event.on(() => r(e)),
                        true
                    );
            };

            request.send({ ...e, root: "cot" }, q => {
                lo.choose("icon", false)?.remove();
                sd.push(q.res);
                r(e, q.res);
                typeof cb == "function" && cb(false);
            });
        },

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

            xs(
                f,
                Geolobal.find(a => zn(a.name) == zn(e.subject))?.name
            );

            f.radio({
                name: "topic",
                value: [
                    { title: "Disable", value: 0 },
                    { title: "Enable", value: 1 }
                ],
                desc: "Use this Category in URL parameters?",
                checked: 0,
                type: "button"
            });

            f.radio({
                name: "resource",
                value: [
                    { title: "Disable", value: 0 },
                    { title: "Enable", value: 1 }
                ],
                desc: "Use this Category in search category?",
                checked: 1,
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

            if (v.status && v.jsonValue) {
                d.status = v.status;
                d.jsonData = JSON.parse(v.jsonValue || "[]");
                d.dcount = d.jsonData.length;
            }

            if (d.jsonData?.length) return l(d.jsonData.shift(), true);

            f.clear();
            f.textarea({
                name: "jsonValue",
                placeholder: "Fill Json Query",
                value: ve
            });

            xm(f)

            f.nextButton(g);
        };

    l({});
    m.css({ minWidth: 1080, maxHeight: 700 });
});

$.require("widgets/forms", (f, m = $.popup("Add Questions")) => {
    f = f(m, (x, y) => {
        const c = x.create("json-practice-container"), a = c.create("left").css({ width: "100%" }), b = c.create("right");
        y.add("alc", () => y.setcontainer(a)), y.add("arc", () => y.setcontainer(b));
        y.add("clr", () => { for (const i of y.getInputs() || []) rm(i); If(a), If(b), y.alc() });
        y.alc()
    });

    f.textarea({ name: "jsonValue", placeholder: "Fill Json Query", value: ve }), xm(f);

    const d = { jsonData: [] }, l = xv(), s = [], o = () => {
        f.clr(); let g = f.container.create("sfully").create;
        g.strong(null, "Successfull");
        g.p(null, `Successfully inserted ${s.length} question${s.length != 1 ? "s" : ""}.`);
        g.button(null, "Close").event.on(() => m.close());


    }, n = () => d.jsonData?.length ? r() : o(), q = v => {
        const c = nx?.loader;
        typeof c == "function" && c(1);
        request.error = e => {
            l.choose("icon", 0)?.remove(), f.submitError(e.error),
                typeof c == "function" && c(0),
                e.datatype && (nx.p.choose("sskip") || nx.p.create("sskip")).in(
                    $.create.button(null, "Skip").event.on(() => n(e)), 1
                )
        };
        return request.send({ ...v, root: "practice" }, e => {
            l.choose("icon", 0)?.remove(), s.push(e.res), n(v, e.res),
                typeof c == "function" && c(0)
        })
    }, r = () => {
        if (!d.jsonData.length) return;
        f.clr();
        const a = d.jsonData.shift();
        zg(f, { name: "title", t: "Title", value: a.title });

        const o = f.container.create("F0011"), t = o.create.div(), z = o.create("list-input");
        t.create.strong(null, "Answer Options");
        t.create.p("F0020", "Enter the correct answer and up to three incorrect answers.");

        zg(f, { name: "correct_answer", t: "Correct Answer", value: a.correct_answer }, z);
        a.incorrect_answer.forEach((x, i) => zg(f, { name: "incorrect_answer[]", t: `Incorrect Answer ${i + 1}`, value: x }, z));
        f.textarea({
            name: "excerpt",
            desc: "Add any additional details or context to help understand the question",
            value: a.excerpt
        }).css({ minHeight: 200 });

        f.arc(), f.append(xv(l, d)), xm(f, d.status, "s-status");

        const c = f.container.create("boderx"), e = p => {
            const d = p.terms.filter(x => x.name && x.slug), x = d.map(x => [x.slug, x.name]),
                y = d.filter(x => a.category.includes(x.name)).map(x => x.slug);
            If(c), f.checkbox({ title: "Categories", name: "category", value: x, checked: y, container: c })
        };

        if (a.subject) {
            const x = Geolobal.find(x => zn(x.name) == zn(a.subject));
            x && (xs(f, x.name), e(x))
        }

        f.append(c), xo(f);

        f.change(x => {
            if (x.target.name != "subject") return;
            for (const i of f.getInputs()) i.name == "category" && i.remove();
            e(Geolobal.find(y => y.id == +x.target.value))
        });

        nx.in("Submit Question", true), f.append(nx.p)
    }, x = () => {
        const v = f.getValue();
        if (v.status && v.jsonValue)
            d.status = v.status, d.jsonData = JSON.parse(v.jsonValue || "[]"), d.dcount = d.jsonData.length;

        if (v.title) {
            if (!Object.keys(v).includes("category")) return f.submitError();
            for (const [k, x] of Object.entries(v))
                if (Array.isArray(x) ? !x.length : typeof x == "string" && !zn(x)) return f.submitError();
            l.addIcon("ic_loader");
            return q(v)
        }
        r()
    }, nx = f.nextButton(x);

    m.css({ minWidth: 1080, maxHeight: 700 })
})



    , oa = function (a) {
        let c = "T001", t = $(c);
        th.homeIndex ??= t.choose("index", true);
        t.clear();
        t.removed("class");
        t.add([c, a]);
        return t;
    }
    , Ea = function (a, s) {
        if (typeof a != "string") {
            s = a;
            a = _.dom.getIndex();
        }
        let c = $.create
            , e = Eb.call(_, c)
            , r = Eg(a, { e, s, c: e.className })
            , t = function (a, b) {
                let e = a?.e || a;
                return e?.tagName
                    ? this.in(e, b)
                    : null;
            };

        r.e.session = a;
        s.__proto__.add = function (a, b) {
            this[a] = b;
            return this;
        }
        r.Ex = function (a, b) {
            return a.call(this, this.e, b)
        }
        r.bind = function (a, b) {
            let g = Ea(a, b);
            this.e.append(g.e);
            g.preant = this.e;
            return g;
        }
        r.append = function (a, b) {
            return !a.length
                ? t.call(this.e, a, b)
                : a.for(n => t.call(this.e, n, b));
        }
        r.get = function () {
            return this.e.cloneNode(true)
        }
        return Ef(a, s), r;
    }
    , Eb = function (a) {
        let n = Ec()
            , c = this.create || a
            , e = c(n);
        _.element = e;
        return e;
    }
    , Ec = function (a) {
        let e = Ei();
        let g = $.makeid(6);
        while (e.indexOf(g) > -1) {
            g = $.makeid(6);
        }
        $.lastClassName = g;
        return g;
    }
    , Ed = function (a) {
        return Math.floor(Date.now() / 1000);
    }
    , Ef = function (s) {
        var g, n, id, st, k = false, tagName = "style";
        if (typeof this == "object" && this?.nodeName) {
            return Ef.call(this.className, s)
        }
        if (typeof this == "object" && this?.s) {
            for (const [n, v] of Object.entries(s)) {
                this.s.add(n, v);
            }
        }
        if (typeof this == "string") {
            for (const { e, s } of Object.values(Eg())) {
                if (e?.isclass(this)) {
                    k = true; break;
                }
            }
            if (k == false) {
                let e = $(this) || $.create(this);
                Eg(_.dom.getIndex(), { e, s, c: e.className })
            }
        }

        g = Eg();
        n = Ej();

        id = g.id;
        st = $.weres(tagName, false).find(e => e.id === id) || $.bindFunction(document.head).create({ id, tagName, rel: "stylesheet" });
        st.textContent = Object.entries(n).map(([c, s]) => `.${c}{${s}}`).join('\n');

        if (typeof this == "string") {
            return this;
        }
    }
    , Ez = function () {
        b["t"] = Ed();
        _.dom[a] = b;
        return b;
    }
    , Eg = function (a, b) {
        _.dom ??= {};
        if (typeof b == "object") {
            _.$e ??= [];

            b["t"] = Ed();
            typeof a !== "number" && (_.dom[a] = b.e);

            _.$e.push(b);

            return b;
        }
        _.dom.id = "EyUky";
        _.dom.add = function (i, v) {
            if (!this[i] && v?.e)
                this[i] = v;

            return this[i]
        }
        _.dom.getIndex = function () {
            for (let i = 0; ; i++) {
                if (!this[i]) return i;
            }
        }
        return _.dom
    }
    , Eh = function (a) {
        return Object.entries(a)
            .filter(([k, v]) => Object.prototype.hasOwnProperty.call(a, k) && typeof v !== "function")
            .map(([k, v]) => `${k}:${v};`)
            .join('');
    }
    , Ei = function (a) {
        a = Array.from(document.querySelectorAll('*')).map(el => Array.from(el.classList)).flat();
        return [...new Set(a)];
    }
    , Ej = function () {
        _.$tm = {};
        let s = _.$e;


        for (const item of s) {
            item.e.isConnected && (item.execute = true);
        }

        for (const item of [...s]) {
            if (item.e && item.s) {
                let g = s.filter(o => JSON.stringify(o.s) == JSON.stringify(item.s));
                if (g.length > 1 && !item.e.isConnected && s.find(o => o == item)?.execute) {
                    _.$e = s.filter(o => o.c !== item.c);

                }
                _.$tm[item.c] = Eh(item.s)
            };
        }

        return _.$tm;
    }
    , Ek = function (a, b, c) { }
    , El = function (a, b, c) { }
    , Em = function (a, b, c) { }
    , En = function (a, b, c) { }
    , Eo = function (a, b, c) { }
    , Ep = function (a) {
        var form = th.logick(_.dom.container.e, a.export("form"));
        th.formEster(form)
        return form;
    }
    , Eq = function (a, b, c) {


        var m = Ea("container", { display: "block", width: "100%", height: window.innerHeight })
        m.append(Ea({ display: "block", font: Eo(12) }).Ex(function (e) {
            return this;
        }))


    };