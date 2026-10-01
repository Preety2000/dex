


// Import the formWindow module and define the logic inside the function.
(!function (Ed) {
    const { FlEXMAP, getString, F, S, N, B, A, E, getNewClassName } = Ed.getFunction();
    function formatZenoTime(ts, type) {
        // Convert timestamp to milliseconds and create a Date object]
        const d = new Date(ts * 1000);
        const day = String(d.getUTCDate()).padStart(2, '0');
        const month = d.getUTCMonth();
        const year = d.getUTCFullYear();
        let hr = d.getUTCHours(), min = String(d.getUTCMinutes()).padStart(2, '0');
        const ampm = hr >= 12 ? 'PM' : 'AM';
        hr = hr % 12 || 12;
        const hour = String(hr).padStart(2, '0');

        // Month names for formats
        const monthMap = {
            JAN: 'January', FEB: 'February', MAR: 'March', APR: 'April',
            MAY: 'May', JUN: 'June', JUL: 'July', AUG: 'August',
            SEP: 'September', OCT: 'October', NOV: 'November', DEC: 'December'
        };
        const monthsFull = Object.values(monthMap);
        const monthsShort = Object.keys(monthMap);

        if (type === "F") return `${day} ${monthsFull[month]}, ${year} at ${hour}:${min} ${ampm}`;
        if (type === "H") return `${day} ${monthsShort[month]}, ${year} at ${hour}:${min} ${ampm}`;
        if (type === "N") return `${day}/${String(month + 1).padStart(2, '0')}/${year} ${hour}:${min} ${ampm}`;
        return ts;
    }
    function Clock(o) {
        o = o || {};
        o.color ??= "#222";
        var c = o.canvas instanceof HTMLCanvasElement ? o.canvas : (function () {
            var el = o.el;
            if (typeof el == "string") el = document.querySelector(el);
            el = el || document.body;
            var x = document.createElement("canvas");
            x.width = o.width || 180; x.height = o.height || 180;
            el.appendChild(x); return x;
        })();

        var ctx = c.getContext("2d"), r = c.height / 2;
        ctx.translate(r, r);

        var h = 0, m = 0, s = 0, drag = 0, hand = null, ev = {};

        function on(t, f) { (ev[t] = ev[t] || []).push(f); }
        function emit(t, d) { if (ev[t]) for (var i = 0; i < ev[t].length; i++) ev[t][i](d); }

        function drawHand(a, l, w, col) {
            ctx.beginPath(); ctx.linewidth = w; ctx.lineCap = "round";
            ctx.strokeStyle = col;
            ctx.rotate(a); ctx.moveTo(0, 0); ctx.lineTo(0, -l); ctx.stroke();
            ctx.rotate(-a);
        }

        function draw() {
            ctx.clearRect(-r, -r, c.width, c.height);
            ctx.beginPath();
            ctx.arc(0, 0, r * 0.95, 0, 7);
            ctx.strokeStyle = o.color;
            ctx.stroke();

            for (var i = 0; i < 60; i++) {
                var a = i * Math.PI / 30 - Math.PI / 2;
                ctx.beginPath();
                ctx.fillStyle = o.color;
                ctx.arc(Math.cos(a) * r * .88, Math.sin(a) * r * .88, i % 5 ? 2 : 4, 0, 7);
                ctx.fill();
            }

            ctx.font = (r * .15) + "px Arial";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillStyle = o.color;
            for (i = 1; i <= 12; i++) {
                var ang = i * Math.PI / 6;
                ctx.rotate(ang); ctx.translate(0, -r * .75); ctx.rotate(-ang);
                ctx.fillText(i, 0, 0);
                ctx.rotate(ang); ctx.translate(0, r * .75); ctx.rotate(-ang);
            }

            drawHand(((h % 12) + m / 60) * Math.PI / 6, r * .4, 7, o.color);
            drawHand(m * Math.PI / 30, r * .55, 5, "blue");
            drawHand(s * Math.PI / 30, r * .80, 2, "red");

            ctx.beginPath();
            ctx.fillStyle = "red";
            ctx.arc(0, 0, 5, 0, 7);
            ctx.fill();
        }

        function pos(e) {
            var b = c.getBoundingClientRect();
            return { x: e.clientX - b.left - r, y: e.clientY - b.top - r };
        }
        function ang(x, y) {
            var a = Math.atan2(y, x) + Math.PI / 2;
            return a < 0 ? a + 2 * Math.PI : a;
        }
        function diff(a, b) {
            var d = Math.abs(a - b);
            return d < Math.PI ? d : 2 * Math.PI - d;
        }
        function pick(x, y) {
            var a = ang(x, y), d = Math.sqrt(x * x + y * y) / r;
            var Ah = ((h % 12) + m / 60) * Math.PI / 6, Am = m * Math.PI / 30, As = s * Math.PI / 30;

            if (d > .4 && d < .7 && diff(a, Am) < .25) return "m";
            if (d > .2 && d < .45 && diff(a, Ah) < .25) return "h";
            if (d > .7 && d < .95 && diff(a, As) < .25) return "s";
            return null;
        }

        c.onmousedown = function (e) {
            var p = pos(e);
            hand = pick(p.x, p.y);
            drag = hand ? 1 : 0;
        };
        c.onmousemove = function (e) {
            if (!drag) return;
            var a = ang.apply(null, Object.values ? Object.values(pos(e)) : (function (P) { return [P.x, P.y]; })(pos(e)));
            if (hand == "m") m = Math.round(a / (2 * Math.PI) * 60) % 60;
            else if (hand == "h") {
                var x = a / (2 * Math.PI) * 12;
                h = Math.floor(x) % 12;
                m = Math.round((x - h) * 60);
            } else if (hand == "s") s = Math.round(a / (2 * Math.PI) * 60) % 60;

            draw();
            emit("change", api.getValue());
        };
        c.onmouseup = function () { drag = 0; };
        draw();
        var x, api = {
            on: on,
            rasete: draw,
            setColor: function (e) { o.color = e; draw(); },
            getValue: function () { return { hour: h, minute: m, second: s }; },
            setValue: function (v, o) {
                if (v.hour != null) h = v.hour % 12;
                if (v.minute != null) m = v.minute % 60;
                if (v.second != null) s = v.second % 60;
                draw();
                if (o !== false) {
                    emit("change", api.getValue());
                }
            },
            start: function () { if (x) return; x = setInterval(function () { if (!drag) { s = (s + 1) % 60; draw(); emit("change", api.getValue()); } }, 1000); },
            close: function () { clearInterval(x); x = null; }
        };
        return api;
    }
    function Form(a, callBack, input_error = "IN0102") {
        var aa, ab, ac, ad, ae, af, ag, ah;
        const oldValue = {}
            , ai = new Set();

        const body = (a instanceof Element ? a : $).create("form");

        const fi = (w, d, a) => {
            const {
                default_img: src,
                key: k,
                name: n,
                type: t,
                height: h,
                width: wd,
                value: v,
                reqSize: rs,
                ...attrs
            } = d;

            let input, ratio;
            const btn = ["Select Image", "Change Image"];

            if (t == "img") {
                w.add("F0014").removed("block").css({ marginTop: 16 });

                $.require("widgets/image_upload", function ImageUpload(IU) {
                    if (wd && h) ratio = wd / h;

                    const prev = w.create("F0015");
                    const img = prev.create.img({ src: src || "/media/icon/empty_img.png" }).css({
                        width: wd,
                        height: h
                    });
                    const upload = prev.create.span(null, btn[v ? 1 : 0]);
                    upload.event.on(() => {
                        const o = {
                            title: btn[0],
                            reqSize: rs,
                            aspectRatio: ratio,
                            responsive: true,
                            header: {
                                key: k,
                                name: n,
                                location: "examiner"
                            }
                        };

                        const update = (src, val = src) => {
                            img.add("src", src);
                            input.add("value", val);
                            upload.in(btn[1]);
                            up.close_container()
                        };

                        if (k) {
                            o.finish = e => {
                                const url = e.is("url");
                                const path = e.is("path");

                                if (e.is("uploaded") && url)
                                    update(url, path);
                            };
                        } else {
                            o.submit = (_, img) => update(img);
                        }

                        const up = new IU(o);
                    });
                }).css();

                input = w.create({
                    accept: "image/*",
                    name: n,
                    value: v,
                    class: "hidden",
                    ...attrs
                });

            } else {
                input = w.create({
                    accept: a,
                    name: n,
                    value: v,
                    type: t,
                    ...attrs
                });
            }

            return input;
        }
        const cif = (a, b = $, c) => {
            const {
                F0012: f,
                name: n,
                title: t,
                description: d,
                desc: x,
                type: y = "text",
                tagName: g = "input",
                ...attrs
            } = a;

            const id = $.getid()
            const w = t ? b.create("block") : b;
            const l = w.create({ tagName: "label", for: id });
            const ti = t && l.create("F0019", getString(t));

            x && l.create.p("F0020", getString(x));
            attrs.required && ti?.create.span(null, "*");

            const cfg = {
                id,
                tagName: g,
                name: n,
                type: y,
                ...attrs
            };

            const i = ["img", "file"].includes(y)
                ? fi(w, cfg)
                : w.create(cfg);

            f && (w.add("F0012"), w.append(l));

            i.event.input(e => body.change(e, form));
            d && w.create.p("description", getString(d));
            i.showError = e => {
                const x = w.choose(input_error) || $.create.p(input_error);
                x.in(e);
                w.add("IN0101");
                w.insertBefore(x, i);
            };

            i.l = l;
            i.wrapper = i.header = w;
            ai.add(i);
            const r = i.remove;
            i.remove = function (q, s) {
                const m = c || b,
                    { p, childrens: ch } = m,
                    pos = [...p.children].indexOf(m);

                r.call(this, q, s);
                ai.delete(i);
                m.remove();
                i.reStore = () => {
                    p.in(m, pos);
                    ch.forEach(x => m.append(x));
                    m.append(i);
                    ai.add(i);
                };
            };

            return i;
        }

        function getContainer(form) {
            if (!form.container) {
                form.container = body.create("F0021")
            }
            return form.container;
        }

        const form = $(function Form() {
            this.clear = function () {
                ai.clear();
                this.valueUpdateCallback = {};
                body.clear();
                this.container = body.create("F0021");
                callBack(this.container, this);
            };

            this.formatZenoTime = formatZenoTime;
            this.getBackButton = function () { };
            this.getNextButton = function () { };
            this.append = function (a) {
                getContainer(this).append(a)
            };
            this.valueUpdateCallback = {};

            // Return the form object
            return this;
        })
            , fc = e => getContainer(form).create(e);

        body.add('method', 'post');
        body.setDomStyle({ position: 'relative', display: 'block' })
        if (F(callBack)) {
            form.add("setcontainer", function (container) {
                form.container = container;
            });
            callBack(body, form);
        }



        let sub = function (e, submit = true) {
            e.preventDefault();
            let values = form.getValue();
            let bind = form.submit || function () { }
            let required = body.weres("input", false).filter(ev => ev.required);

            body.weres("F0024").for(ev => ev.removed("F0024"));
            required.forEach((input, index) => required.findIndex(i => i.name === input.name) === index ? function (input) {
                if (!values[input.name]) {
                    submit = false;
                    input.header.add("F0024");
                }
            }(input) : null);

            if (submit === false) form.submitError();

            all_error_item = body.weres(input_error);
            all_error_item.for(item => (item.remove(), item.p.removed("IN0101")));



            if (submit === true && bind.call(this, values)) {
                $("IN033")?.click();
                body.parentFilter(e => e.isclass("fixed-container"))?.remove();
            }
            if (submit === true && form.apirequest) {
                $.loader(true);
                form.apirequest.send(values);
            }
        }



        body.change = function (element, action) {
            let hooks = form.Forms$Hooks || []
            body.weres("F0017").for(ev => ev.remove());
            for (const cb of hooks)
                cb.call(element.target, element, action);
        }

        form.add("submitError", function (e) {
            const m = (form.errorContainer || getContainer(form))
            return (m.choose("F0017") || m.create.p("F0017", 0)).in(e || form.requiredmessage || "Please select a value that meets the requirements. *")
        })


        // Function to create a date and time inside the form
        form.add("timePiker", function (a, b, t, e) {
            const { pop, submit } = form.opp();
            const mths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
            const c = getComputedStyle(pop), s = { h: 12, u: 0, s: 0, d: 1, m: 0, y: 2025, ampm: "AM" }, pad = n => String(n).padStart(2, '0');
            const g = pop.create('DIS00'), cal = g.create('calendar'), time = g.create('times');
            const clk = Clock({ color: c.color, canvas: time.create({ tagName: "canvas", width: 180, height: 180 }) });
            const he = {}, keys = ['day', 'month', 'year', 'at', 'times']; keys.forEach(k => he[k] = pop.header.create(getNewClassName()));
            submit.event.on(e => pop.submit.call(e)); pop.add("system"); submit.close = pop.close; pop.header.add("F0026"); he.at.in("at"); he.day.setDomStyle({ margin: '5px' });

            window.clk = clk
            console.log(c.color);

            console.log(clk);


            const st = () => { const h = s.h + (s.ampm === "PM" && s.h < 12 ? 12 : 0); return new Date(s.y, s.m, s.d, h, s.u, s.s) };
            const gTime = n => { const h24 = n.getHours(); return { y: n.getFullYear(), m: n.getMonth(), d: n.getDate(), u: n.getMinutes(), s: n.getSeconds(), h: h24, ampm: h24 >= 12 ? "PM" : "AM" } };

            const preventPast = () => {
                if (e === true) return e;
                const sel = st(), now = new Date();
                if (sel < now) { Object.assign(s, gTime(now)); updDate(); clk.setValue({ hour: s.h, minute: s.u, second: s.s }, false); timeUp(s.h, s.u, s.s); return false; }
                return true;
            }
            const amp = ["AM", "PM"];
            const updTs = t => { let n = t === true ? st() : new Date(Number(t) || Date.now()); Object.assign(s, gTime(n), { now: n, timestamp: n.getTime() }); g.add("ampm", n.getHours() >= 6 && n.getHours() < 18); return n; }
            updTs(t ? Number(t) : Date.now());

            const updDate = () => {
                updTs(true);
                const hh = s.h % 12 || 12;
                he.day.in(pad(s.d), true); he.month.in(mths[s.m], true); he.year.in(String(s.y), true); he.times.in(`${pad(hh)}:${pad(s.u)}:${pad(s.s)} ${s.ampm}`, true);
                amp.forEach(a => a.innerText == s.ampm ? a.add("active") : a.removed("active"));
            }
            pop.session = s;
            pop.submit = () => {
                const d = new Date(s.y, s.m, s.d, s.h, s.u, s.s), hh = s.h % 12 || 12;
                a = a || {}; a.timestamp = d.getTime(); a.value = `${s.y}-${pad(s.m + 1)}-${pad(s.d)}T${pad(s.h)}:${pad(s.u)}:${pad(s.s)}`;
                const pretty = `${pad(s.d)} ${mths[s.m]}, ${s.y} at ${pad(hh)}:${pad(s.u)}:${pad(s.s)} ${s.ampm}`;
                b(d, pretty, submit) && pop.close();;
            }

            const monthCh = e => $.menuexitue(e).executed(mths.map((n, i) => ({ name: n, event: () => { s.m = i; updDate(); renderCal(); return true; } })));
            const yearCh = e => { const ys = Array.from({ length: 50 }, (_, i) => 2000 + i); $.menuexitue(e).executed(ys.map(y => ({ name: String(y), active: y === s.y, event: () => { s.y = y; updDate(); renderCal(); return true; } }))); }
            he.month.event.on(monthCh); he.year.event.on(yearCh);

            clk.setValue({ hour: s.h, minute: s.u, second: s.s });
            const tg = time.create('F0030');

            ["ic_minus", "ic_plus"].forEach(ic => tg.create.button(null).event.on(() => {
                if (ic === "ic_plus") { s.u = (s.u + 1) % 60; if (s.u === 0) s.h = (s.h + 1) % 24; } else { s.u = (s.u + 59) % 60; if (s.u === 59) s.h = (s.h + 23) % 24; }
                preventPast(); updDate(); clk.setValue({ hour: s.h, minute: s.u, second: s.s });
            }).addIcon(ic));
            const kk = tg.create('DIS01', null, 1), hD = kk.create('F0031', pad(s.h % 12 || 12)), mD = kk.create('F0031', pad(s.u));
            amp.forEach((p, i) => {
                amp[i] = kk.create('ampm', p).event.on(() => {
                    s.ampm = p; s.h = p === "PM" ? (s.h % 12) + 12 : s.h % 12; preventPast(); updDate();
                });
            });

            const timeUp = (h, m, s) => { hD.in(pad(h % 12 || 12)); mD.in(pad(m)); mD.in(pad(s)); }
            clk.on("change", ({ hour, minute, second }) => { s.h = hour; s.u = minute; s.s = second || 0; preventPast(); updDate(); timeUp(hour, minute, second); })

            const ott = cal.create('F0027 DIS01'), dg = cal.create('F0029');
            ["ice_arrow_left", "ice_arrow_right"].forEach(ic => ott.create.button(null).event.on(() => {
                if (ic === "ice_arrow_left") { s.m = (s.m + 11) % 12; if (s.m === 11) s.y--; } else { s.m = (s.m + 1) % 12; if (s.m === 0) s.y++; }
                preventPast(); updDate(); renderCal();
            }).addIcon(ic));
            const ottSh = ott.create("F0028", "", 1), gt = [monthCh, yearCh], gp = q => {
                for (let i in gt) {
                    gt[i] instanceof Function && (gt[i] = ottSh.create('cursor').event.on(gt[i]));
                    typeof q[i] == 'string' && gt[i].in(q[i], true);
                }
            };

            function renderCal() {
                updDate(); preventPast(); dg.clear();
                const fd = new Date(s.y, s.m, 1).getDay(), days = new Date(s.y, s.m + 1, 0).getDate();
                ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].forEach(d => dg.create('F0032 F0033', d));
                for (let i = 0; i < fd; i++)dg.appendChild(document.createElement('div'));
                for (let d = 1; d <= days; d++) {
                    const c = dg.create('F0032', String(d)); if (s.d === d) c.add('active');
                    c.event.on(() => { s.d = d; if (!preventPast()) return; updDate(); dg.childrens.for(x => x.removed("active")); c.add("active"); });
                }
                gp([mths[s.m], String(s.y)]);
            }
            renderCal();
            return pop;
        });
        form.add("opp", function Window(cb, t = "Submit") {
            const pop = $.popup(), submit = $.create.button(null, t);
            pop.hrg.in(submit, 0);
            cb === true ? pop.append(body) : typeof cb == "function" && submit.event.on(cb);
            submit.id = "F0013";
            submit.apply = e => submit.event.on(sub)
            return { pop, submit };
        });
        form.add("change", function Change(callback) {
            if (!form.Forms$Hooks) {
                form.Forms$Hooks = [];
            }
            if (typeof callback === 'function') {
                form.Forms$Hooks.push(callback);
            }
        })

        form.add("desc", function addText(t) {
            const c = 'F0005', fc = getContainer(form), f = e => B(e)
                ? fc.create({ class: c, ...e })
                : fc.create.p(c, e);

            if (Array.isArray(t)) {
                for (const i of t) {
                    f(i)
                }
            }
            else (f(t))

            return fc;
        })

        form.add("accordion", function (option) {
            var { title, description, name, value, switchValue } = option;
            const holder = fc("accordion-tab");
            id = "toggle_" + (A(name) ? name.map(item => item.name).join("_") : name);
            holder.create({ "id": id, "name": id, "type": "checkbox", "tagName": "input", "class": "checkbox hidden" })
            holder.create.label("accordion-name", title).add("for", id);
            function processItem(item, name) {
                let id = (name + (A(item) ? item.join("_") : item)).replaceAll(" ", "_").toLowerCase();
                let title = A(item) ? item[0] + " " + item[1] : item;
                let value = A(item) ? item[1] : item;
                return { id, title, value };
            }

            var switchs = holder.create("accordion-content");
            var tabswitchs = switchs.create("accordion-switch-content");
            switchs.create("center", "like")
            var tabcontent = switchs.create("accordion-tab-content");

            function deactive(element) {
                element.p.childrens.for(e => e.removed("active"))
            }

            if (A(name)) {
                name.for(item => tabswitchs.create.a("button", item.value).add("name", item.name).event.on(function () {
                    tabcontent.childrens.filter(e => e.type == "radio").for(input => { deactive(this), input.name = this.name, this.add("active") })
                }).add(name[0] == item ? "active" : null))
                name = name[0].name;

            }

            switchValue.for(function (item) {
                item = processItem(item, name);

                var input = cif({
                    "id": item.id,
                    "name": name,
                    "type": "radio",
                    "value": item.value,
                    "tagName": "input",
                    "class": "input-toggle hidden",
                }, tabcontent)
                input.add(value == item.value ? "checked=true" : null)

                tabcontent.create.label("button", item.title).add("for", item.id);
                input.event.on(e => body.change(e, form));
            })
        });

        form.add("switchHolder", function switchHolder({ title: t, desc: d, name: n, value: v, switchValue: s = ["ON", "OFF"] }) {
            var m; const h = fc("F0035")
                , l = h.create("switch-label");
            l.create.h3("F0019", t);
            d && l.create("F0020", d);
            const x = h.create("F0036")
                , c = cif({ name: n, type: "checkbox", class: "F0037", F0012: true }, x, h)
                , o = c.l.create.span("option"), w = c.l.create.span("sWitCh"),
                u = () => {
                    const a = o.childrens[0].get()
                        , b = o.childrens[1].get()
                        , z = c.checked;

                    o.add("sift", z, a);
                    w.css({
                        left: z ? 4 + a.width : 4,
                        height: (z ? b : a).height,
                        width: (z ? b : a).width,
                    });
                };

            s.indexOf(v) >= 0 && (c.checked = s.indexOf(v)); c.switchValue = s; s.forEach(a => o.create.span(null, a)); c.event.on(u);
            u()
            // new MutationObserver(() => !m && document.contains(w) && (m = true, setTimeout(u, 100))).observe(document.body, { childList: true, subtree: true });
            return c;
        });

        // Importing input functionality into the form
        form.add("image", function (option, tig = []) {

            var { info, ...option } = option;
            var { type, x } = info;

            // Create a containerfor the input element
            const container = fc("F0011");
            option.type == "hidden" && container.css({ display: 'none' })


            // Check if the 'option' is an object (single input case)
            if (B(option)) {
                // Create a single input element using cif function
                tig = cif(option, container);
            } else {
                // If 'option' is an array, create multiple input elements
                for (const item of option) {
                    tig.push(cif(item, container));
                }
            }
            return tig;
        });
        form.add("input", function (atter, container, tig = []) {
            const containers = container || fc("F0011");
            atter.type == "hidden" && containers.css({ display: 'none' })

            if (B(atter)) { tig = cif(atter, containers); }
            else {
                for (const item of atter)
                    tig.push(cif(item, containers));

                containers.add("list-input")
            }

            return tig;
        });
        // Importing datetime functionality into the form
        form.add("datetime", function (option) {
            // Create a containerfor the input element
            var { title, name, value, container, required, edit, timestamp } = option;
            container = (container || getContainer(form)).create("F0011");
            container.create("F0006").create("F0019", title);

            function d(e) {
                if (!e) return e;
                const d = new Date(e);
                const pad = n => String(n).padStart(2, '0');
                return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
            }

            value = d(value);

            var label = container.create.label().add('for', 'dbinput')
            var input = cif({
                tagName: 'input',
                name,
                value,
                required,
                id: 'dbinput',
                placeholder: "Select date & time",
                type: 'datetime-local'
            }, label)


            input.event.on(e => (form.timePiker.call(e, input, n => body.change.call(input, e, form))));
            return input;
        });
        // Importing close functionality into the form
        form.add("close", function closeForm() {
            callBack && F(callBack.close)
                ? callBack.close()
                : body.remove();
        })
        // Importing checkbox functionality into the form
        form.add("checkbox", function createCheckbox(option, tig = []) {
            var { grid, change, title, name, value, nontype, container, checked, edit, callBack: cb, css, desc } = option;
            container = (container || getContainer(form)).create.div("F0004");
            var header = container.create("F0006");
            title && header.create("F0019", title);
            desc && header.create("F0020", desc);
            container.add("co-" + name);

            const createCheckboxElement = (name, values) => {
                const F0009 = container.create("F0009");
                let hndle = A(values) ? values[1] : values;
                let value = A(values) ? values[0] : values;

                if (!value) return;
                if (typeof cb == "function") {
                    let callback = cb(value, F0009);
                    value = callback.value;
                    hndle = callback.title;
                }

                const input = cif({
                    name,
                    value,
                    nontype,
                    type: "checkbox",
                    tagName: "input",
                    class: "F0023"
                }, F0009)

                oldValue[name] = checked;

                F0009.append(input.l);
                if ((A(checked) && 0 <= checked.indexOf(value)) || value == checked) {
                    input.checked = true;
                }
                if (edit == true) { input.l.create.input("checkbox-title").add("value", hndle).event.input(value => input.value = value) }
                else input.l.add("checkbox-title").in(hndle)

                input.event.on(e => (body.change(e, form), (F(change) && change(e, form))));
                return input;
            };

            if (A(value)) {
                container = container.create("F0008");
                css && container.css(css);
                grid && container.css({ "grid-template-columns": `repeat(auto-fit, minmax(${270}px, 1fr))` })
                value.forEach(item => tig.push(createCheckboxElement(name, item)));
            }
            else { tig = createCheckboxElement(name, value); }

            return tig;
        });
        // Importing radio functionality into the form
        form.add("radio", function createCheckbox(option, tig = []) {
            var { bind, type, required, title, desc, name, value, container, nontype, checked, edit, titleChange, css } = option;
            container = (container || getContainer(form)).create("F0001");
            titleChange = titleChange || function () { }
            container.add(option.class);
            container.add("co-" + name);
            var header = container.create("F0006");


            if (edit == true) {
                header.create.input("F0019")
                    .add("value", title).event
                    .input(e => titleChange(e));
            }
            else {
                header.create.h3("F0019", title);
                desc && header.create('F0020', desc)
            }

            const createCheckboxElement = (name, values) => {
                const F0009 = container.create("label", "F0009");
                let r = function (q) {
                    if (B(q)) {
                        let a = $.create('reader-meta'), { title: t, desc: d, value: v } = q;
                        a.create.strong('F0025', t);
                        d && a.create.p('reader-meta-desc', d);
                        return [a, String(v)];
                    }
                    if (Array.isArray(q)) return [q[1], q[0]];
                    return [q, q];
                }

                let [hndle, value] = r(values);

                if (!value) return;
                const input = cif({
                    name,
                    value,
                    nontype,
                    required,
                    type: "radio",
                    tagName: "input",
                    class: "F0023",
                }, F0009);

                input.title = hndle instanceof HTMLElement
                    ? hndle.innerText
                    : String(hndle ?? "");



                if (F(bind)) {
                    bind(input, values)
                }

                oldValue[name] = checked;
                F0009.append(input.l);

                if (value == checked) input.add("checked", "checked");
                if (edit == true) input.l.create.input("checkbox-title").add("value", hndle).event.input(value => input.value = value)
                else input.l.add("button").add("roll", type || "checkbox").in(hndle);


                input.header = header;
                input.event.on(e => body.change(e, form));
                return input;
            };

            if (A(value)) {
                container = container.create("F0007");
                css && container.css(css)
                container.add("type", type || "checkbox")
                value.forEach(item => tig.push(createCheckboxElement(name, item)));
            }
            else { tig = createCheckboxElement(name, value); }
            return tig;
        });
        // Importing select functionality into the form
        form.add("select", function createSelect(option, tig = []) {
            var { change, bind, type, required, title, name, value, container, nontype, checked, edit, titleChange, description } = option;
            container = (container || getContainer(form)).create("F0002");
            titleChange = titleChange || function () { }
            container.add("co-" + name);
            container.add(option.class);
            var block = container.create("block");
            var lable = block.create("lables");
            title && lable.create("F0019", getString(title));

            var buttn = lable.create.button("button");
            var F0018 = buttn.create("F0018");
            var hndle = block.create("reader-value");
            var vaddt = hndle.create("vaddt");
            var popst = block.create("pop-select");
            const valueVe = q => {
                q = typeof q === "function" ? q() : q;
                return Array.isArray(q) ? Object.fromEntries(q.map(i => Array.isArray(i) && i.length == 2 ? i : [i, i])) : q;
            };
            var radio = function (name, values, clss) {
                let scroll = $.create("scroll-ys"), group = scroll.create("F0007");
                scroll.textBigLanght = 0;

                for (const [title, value] of Object.entries(values)) {
                    let selet = group.create("label");
                    selet.add("button");
                    selet.create.span("titld", getString(title));
                    selet.create({ name, value, type: "radio", tagName: "input", class: clss || "F0023" }).event.on(function (e) {
                        typeof scroll.change == "function"
                            ? function (q) {
                                typeof q == "undefined" || q === true
                                    ? scroll.remove()
                                    : this;
                            }(scroll.change(e))
                            : null;
                    })
                    if (scroll.textBigLanght < value.length) {
                        scroll.textBigLanght = value.length;
                    }
                }
                return scroll;
            }
            const getChecked = (o, v) => Object.keys(o).find(k => String(o[k]) === String(v));
            var addon = function (value) {
                let input = $.create({
                    name,
                    value,
                    required,
                    type: "text",
                    tagName: "input",
                    class: "hidden"
                })
                input.css({ display: "none" });
                vaddt.in(input, !0);
                return input;
            }


            const getGroup = function () {
                let v = valueVe(value);
                let group = radio(name, v);
                if (checked)
                    checked = getChecked(v, checked);


                optin.in(getString(checked || "Select"), !0);
                addon(checked)
                group.change = function (e) {
                    checked = getChecked(v, e.target.value)
                    addon(e.target.value);
                    optin.in(getString(checked), !0);
                    body.change(e, form);
                    F(change) && change(e, form)
                }
                return group;
            }
            const a = e => {
                let b = e.parentElement;
                while (b) {
                    if (getComputedStyle(b).contain === 'layout') break;
                    b = b.parentElement
                } return b || document.body
            }
            const nr = (g, a) => {
                const s = buttn.get()
                    , t = Math.abs(s.top - a.top)
                    , b = Math.abs(a.bottom - s.bottom)
                    , l = i => i.get().width;

                let max = l(buttn);
                for (const i of g.weres("button")) {
                    max = Math.max(max, l(i));
                }

                g.add("style", `width:${max}px`);
                g.css(t < b ? { maxHeight: (b - 20) } : { bottom: (a.height - t), maxHeight: t });
                g.firstChild.get().height > g.get().height && g.css("overflow-y", "scroll")
            }

            const optin = F0018.create.span("ti", getString("Select"));
            var group = getGroup();


            F0018.addIcon("ice_chevron_down");
            buttn.event.on(function (ev) {
                ev.preventDefault(); popst.in(group, !0); nr(group, a(popst).get());
                $.windows(buttn, { container: group, functions: true });
            });

            if (description) { block.create.p("description", getString(description)) }
            buttn.appended = function () {
                let g = window.getComputedStyle(buttn);
                let a = optin.get().width / optin.innerText.length;
                return buttn.css({ "min-width": (Math.floor(group.textBigLanght * a) + (parseInt(g.paddingLeft) + parseInt(g.paddingRight)) + 34) });
            }

            F(value) && (form.valueUpdateCallback[name] = function () {

                group = getGroup();
            })

            return tig;
        });
        // Importing textarea functionality into the form
        form.add("textarea", function (option, c) {
            const { value, ...atter } = option;
            const container = c || fc("F0011");
            const textarea = cif({ tagName: "textarea", ...atter }, container);
            textarea.in(option.value);

            return textarea;
        });
        // Importing submit button functionality into the form
        form.add("button", function Button(option, cb) {
            var button = (option.container || getContainer(form)).create.button("button", option.title);

            button.event.on(function (e, submit = true) {
                // Prevent the default form submission behavior
                e.preventDefault();
                let values = form.getValue();
                F(cb) && cb.call(button, values, form)
            })
            return button
        })
        form.add("submitButton", function (option, container) {
            // Create a submit button with the specified options
            var submit = (container || getContainer(form)).create("button-container").create.button("submit", option);

            // Add an event listener to handle the submit button click event
            submit.event.on(sub);

            form.add("getSubmitButton", function getSubmitButton() {
                return submit
            })

            // Return the submit button element
            return submit;
        });
        form.add("nextButton", function (cb, container) {
            var next = (container || getContainer(form)).create("button-container").create.button("next", "Next");

            next.event.on(function (e) {
                e.preventDefault();
                cb(this);
            });

            form.add("getNextButton", function getNextButton() {
                return next
            })

            return next;
        });
        form.add("backButton", function (option, container) {
            // Create a submit button with the specified options
            var back = (container || getContainer(form)).create("button-container").create.button("back", "Back");

            // Add an event listener to handle the submit button click event
            back.event.on(function (e) {
                // Prevent the default form submission behavior
                e.preventDefault();
                option(this);
            });

            form.add("getBackButton", function getBackButton() {
                return back
            })

            // Return the submit button element
            return back;
        });
        // Importing input functionality into the form
        form.add("message", function message(option) {
            // Create a containerfor the element
            const container = body.create("form-message-container");
            return this.add("messageContainer", F(option) ? option(container) : container);
        });
        form.add("getHeader", function getHeader() {
            const f = "DIS01"
                , u = $.create(f)
                , h = $.create.header("F0010", 0);

            h.l = h.create(f); h.r = h.create(f); body.in(h, 0);
            h.loader = e => e === false
                ? u.remove()
                : (!h.contains(u) && h.r.in(u, 0), h.lg
                    ? h.lg.in(e, null)
                    : (u.addIcon("ic_loader"), h.lg = u.create.span(null, e)));
            return h;
        })
        form.add("getValue", function getValue(option) {
            const vl = {};
            for (const i of form.getInputs() || []) {
                const n = i.name.replace("[]", "")
                    , v = i.value
                    , t = i.type;

                if (i.name.includes("[]"))
                    (vl[n] ??= []), t == "checkbox"
                        ? i.checked && vl[n].push(v)
                        : vl[n].push(v);

                else if (t == "radio") {
                    const x = i.get("nontype");
                    i.checked
                        ? vl[n] = v
                        : x && (vl[x] ??= [], vl[x].push(v))
                }
                else if (t == "checkbox") i.switchValue
                    ? vl[n] = i.switchValue[+i.checked]
                    : v && ((vl[n] ??= []), i.checked && vl[n].push(v));
                else vl[n] = v;
            }
            for (const n in vl) Array.isArray(vl[n]) && (vl[n] = [...new Set(vl[n])]);
            return typeof option == "string" ? vl[option] : vl;
        });
        form.add("getChangeValue", function getChangeValue(option) {
            let value = form.getValue();
            let inputs = form.getInputs();

            return value


        });
        form.add("getForm", function getForm(container) {
            if (E(container)) {
                container.append(body)
            }
            return body;
        });
        form.add("getFormSession", function getFormSession() {
            return body.choose("F0021");
        });
        form.add("getFormId", function getFormId(idsession) {
            return $.makeid(idsession || 8);
        });
        form.add("getElement", function getElement(a, b, c) {
            return body.choose(a, b, c);
        });
        form.add("getInputs", function getInputs() {
            const inputList = body.weres("input", false) || [];
            ai.forEach(input => {
                if (!inputList.includes(input)) {
                    inputList.push(input);
                }
            });

            return [...new Set(inputList)];
        });
        form.add("setRequestRoot", function setRequestRoot(root, b) {
            let fcn = F;
            let ars = $.apirequest(root, b);
            this.apirequest = ars;
            ars.progress = (a, b) => {
                fcn(this.progress)
                    ? this.progress(a, b)
                    : null;
            };
            ars.finish = (a, b) => {
                $.loader(false);
                fcn(this.finish)
                    ? this.finish(a, b)
                    : null;
            };
            ars.error = (a, b) => {
                $.loader(false);
                fcn(this.error)
                    ? this.error(a, b)
                    : null;
            };
            return ars;
        })
        form.add("resetCaptcha", function resetCaptcha() {
            return null;
        })
        form.add("addCaptcha", function addCaptcha() {
            let af = 1;
            ag = fc("captcha-container");
            ah = function (a) { a.src = "/img/captcha?go=?" + (new Date().getTime()) };
            aa = ag.create("footer");
            ab = aa.create("F0019");
            ac = aa.create("captcha-box");
            ad = form.input({
                type: "text",
                name: "captcha",
                spellcheck: "true",
                placeholder: getString("Enter Captcha"),
            });

            ab.in(getString("Type the word above"));
            ac.append(ad);
            ac.create("refresh").event.on(function () {
                this.css({ transform: "rotate(" + af * 90 + "deg)" });
                ah(ae);
                af++;
            }).addIcon("ic_refresh");

            ae = ac.create({
                class: "F0022",
                tagName: "img",
                height: 40,
                weight: 160
            });

            form.add("resetCaptcha", function resetCaptcha() {
                return ah(ae)
            })
            ah(ae);
            return ae;
        })
        form.add("getContainer", function getFormContainer() {
            return getContainer(form);
        })

        // Html Content 
        form.add("tableList", function (option) {
            const { container, value, title, desc, callBack: cb } = option;
            const ag = (container || getContainer(form)).create("F0042");
            title && ag.create('F0019', getString(title));
            desc && ag.create.p("description", getString(desc));
            for (const [name, vall] of Object.entries(value)) {
                const con = ag.create("F0044");
                const left = con.create("F0043", name);
                const right = con.create("F0045");
                typeof vall == "object"
                    ? right.create(vall)
                    : right.in(String(vall))
                F(cb) && cb.call(con, left, right)
            }
        })

        if (a === true && typeof callBack != "function") {
            return { form, ...form.opp(true, callBack) }
        }

        // Return the form object for further use or modification
        return form;
    }
    // Creates left/right containers for form layout
    Form.buildFormLayout = function buildFormLayout(c, cb, cls) {
        if (cb !== true) c.clear();
        return Form(c, (b, f) => {
            let x = b.create(cls || "F0041")
                , l = x.create("F0039")
                , r = x.create("F0038");
            f.add("alc", () => f.setcontainer(l));
            f.add("arc", () => f.setcontainer(r));
            f.alc();
            typeof cb == "function" && cb(f)
        })
    }

    Ed.define("widgets/forms", Form);
}($))