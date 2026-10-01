// © 2025 Your MyApplication. All rights reserved.
// This script is licensed under the MIT License.
$(function onlineTestSeries(_, a, b, c, d, e, f, g, h, i, j, k, l, S, T, U, R) {
    "use strict";

    const { AUTH_TOKEN } = $.getClass()
        , { FlEXMAP, F, B } = $.getFunction()
        , RV = { REQUEST_VIEW: 0, JOIND_VIEW: 1 }
        , RCB = { REQUEST_VIEW: 1, REQUEST_POPUP_VIEW: 2 }
        , r = $.req()
        , ES = FlEXMAP({
            eventLogger: true,
            students: {},
            STUDENT_JOINED_EXAM: [],
            STUDENT_COMPLETED_EXAM: [],
        })
        , _exmeg = $.cookie("_exmeg", 0, true)
        , listen = (a, cb) => ES.add(a, cb)
        , binding = (a, b, c, d, e) => {
            const f = ES.get(a);
            return typeof f === "function" && f(b, c, d, e)
        }
        , rsc = (p, v) => {
            v && v.loader(false);
            $.weres(`[id$="${AUTH_TOKEN.encode([p.request_id, RV.REQUEST_VIEW], true)}"]`).forEach(e => {
                let i = +e.get("callback_id"), c = ES.get(i);
                if (typeof c == "function") {

                    if (i == RCB.REQUEST_VIEW) return e.remove(), c();
                    if (p.update_code == 1 && i == RCB.REQUEST_POPUP_VIEW) return c(1), e.remove();
                }
                if (i == RCB.REQUEST_VIEW || p.update_code == 1) e.remove();
                if (p.update_code == 2 && v) e.add("disabled"), v.in("Delete", true);
            });
        }
        , gs = (a, b, c, d) => {
            var url = new URL(window.location.href), params = new URLSearchParams(url.search);
            return params.get(a) || b;
        }
        , tm = function (a, b, c) {
            var form = this
                , t = form.input({
                    type: 'hidden',
                    name: c,
                    value: a
                })
                , g = $.create.span(null)
                , h = g.create.span(null, b).css({ marginRight: 5 })
                , f = function () {
                    return form.timePiker(null, (e, b) => {
                        t.value = e.getTime();
                        form.getForm()?.change(e, form);
                        h.in(b, true);
                        return true;
                    }, t.value)
                };
            g.create.a(null, a ? 'Change' : 'Set').event.on(f).set('href', null);
            return g;
        }
        , ks = (e = $.cookie("_cf_eSt", 360, 1), s = (d) => e.insert(AUTH_TOKEN.encode(d)), r = v => v(AUTH_TOKEN.decode(e.get()) || {})) => ({
            set: (i, v) => r(d => (d[i] = v, s(d))),
            res: i => r(d => i && (delete d[i], s(d)) || e.remove()),
            get: i => r(d => i ? Object.prototype.hasOwnProperty.call(d, i) ? d[i] : null : d)
        })
        , df = (a, b, c) => (r.e = false, a(), r.e = true, typeof b == "function" && b(c))
        , sd = (a, b, c) => df(() => (r.delete(a), r.navigate(r.u.href)), b, c)
        , ef = (a, b, c) => df(() => r.navigate(a), b, c)
        , gq = function () {
            const b = $.create("T003");
            $.require("widgets/forms", e => {
                let fm = e(b);
                fm.getContainer().create.input({ name: "gs", value: r.get("gs"), placeholder: "Global Search: Use Search Terms Like tram with Multiple key=value Filters" });
                fm.submitButton(null).addIcon("ice_search");
                fm.submit = e => e.gs && r.set("gs", e.gs)
            })
            return b;
        }
        , dc = a => $.confirm({
            h: "Delete Confirmation",
            t: "Do you really want to delete this item? Once deleted, it cannot be restored.",
            c: "Cancel",
            b: "Delete"
        }, a)
        , getLinkWimdow = (r) => {
            const p = $.popup('Share'), g = p.create("IN0104"), s = { margin: '22px 40px', display: 'flex', justifyContent: 'center' };
            g.css(s)
            for (const n of [
                { t: "WhatsApp", i: "circle_whatsapp", l: `https://wa.me/?text=${encodeURIComponent(r)}` },
                { t: "Facebook", i: "circle_facebook", l: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(r)}` },
                { t: "Email", i: "circle_email", l: `mailto:?subject=Exam&body=${encodeURIComponent(r)}` },
                { t: "Pinterest", i: "circle_pinterest", l: `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(r)}` },
                { t: "Twitter", i: "circle_twitter", l: `https://twitter.com/intent/tweet?url=${encodeURIComponent(r)}` }
            ]) {
                let a = g.create.a({ class: 'F0047', href: n.l, target: "_blank" });
                a.addIcon(n.i);
                a.create.span(null, n.t);

            }
            const b = p.create("box");
            b.css({ overflow: 'hidden', ...s });
            b.create.input({ value: r, disabled: true, name: 'exam_link' }).css({ fontSize: 'medium' });
            b.create.button(null, "Copy").css({ margin: 3 }).event.on(e => $.copy(r, 'Copy Successful').then(e => $.message(e)))
        };


    const useServerConnectionData = ks();
    const EventHub = (function (event) {
        const EventHub = {};

        event.export = (id) => {
            EventHub[id] ??= [];
            return EventHub[id];
        };
        event.import = (id, value) => {
            let d = event.export(id);
            return d.push(value);
        };
        event.call = (id, fn) => {
            for (const item of event.export(id)) {
                fn(item);
            }
        }
        return event;
    }($(function EventHub() { })));

    const req = (d, cb = () => { }, f) => {
        const k = JSON.stringify(d)
            , p = ES.pending ??= {}
            , c = ES.requestCatch ??= {}
            , api = ES.reqApi ??= $.apirequest("auth/t");

        if (!d && r.pathname == "/exam/r/setting" && c[r.pathname]) {
            var re = c[r.pathname];
            (ES.get(re.__ac) || cb)(re, null);
            return null;
        }
        if (d !== null && p[k])
            return api;

        p[k] = true;

        if (location.href === location.origin + "/exam") {
            ES.get(100)();
            $.loader(false);
            return api;
        }

        if (!f && handleAction() && api.calls > 0)
            return api;

        api.progress = () => { };
        api.send(d, (res, body) => {
            api.calls++;
            delete p[k];

            const re = res.getParams();
            c[r.pathname] = re;
            ES.justResponce = re;
            if (re.message)
                $.message(re.message);

            if (re.jump)
                (r.navigate(re.jump), $.loader(true));

            (ES.get(re.__ac) || cb)(re, body);
            $.loader(false);
        });

        return api;
    };
    const sendReq = (d, cb, s) => $(function () {

        if (!s)
            return req(d, cb);

        d.request_key = $.getKey(true);
        this.request = doSession();

        console.warn("sending", d);
        return this.request.export(d, e => {
            console.warn("response", e, d.request_key);
            cb.call(this, e);
        });
    });
    const editSetting = function (key, callBack) {
        const form = ES.form()
            , dialog = form.opp(true)
            , setting = getString()[key];
        dialog.pop.absolute();
        form.radio({ ...setting, checked: this[key] });

        typeof callBack == "function" && dialog.submit.event.on(function (e) {
            callBack.call(this, e, form)
        })
        return dialog
    };
    const getString = (q) => {
        const query = {
            req_appr_mode: {
                "class": "join-request-action",
                "type": "button",
                "required": true,
                "title": "Join Request Handling",
                "desc": "Choose how incoming student join requests should be handled.",
                "name": "req_appr_mode",
                "value": [
                    {
                        "title": "Auto Accept Requests",
                        "desc": "All eligible student join requests will be approved automatically without requiring your review.",
                        "value": "auto_accept"
                    },
                    {
                        "title": "Auto Reject Requests",
                        "desc": "All incoming join requests will be declined automatically, preventing students from joining the class.",
                        "value": "auto_reject"
                    },
                    {
                        "title": "Manual Approval",
                        "desc": "Review each join request individually and decide whether to accept or reject it.",
                        "value": "manual"
                    }
                ]
            },
            open_request: {
                "class": "join-request-expiry",
                "type": "button",
                "required": true,
                "title": "Join Request Availability",
                "desc": "Choose when students can send join requests to your class.",
                "name": "open_request",
                "value": [
                    {
                        "title": "Only When You're Active",
                        "desc": "Students can send join requests only while you are online or actively managing the class.",
                        "value": "active_only"
                    },
                    {
                        "title": "Available for 24 Hours",
                        "desc": "Students can send join requests for up to 24 hours after you share the invite.",
                        "value": "24_hours"
                    },
                    {
                        "title": "Available Until You Disable It",
                        "desc": "Students can send join requests at any time until you manually turn off joining.",
                        "value": "lifetime"
                    }
                ]
            },
            join_mode: {
                "class": "join-settings",
                "type": "button",
                "required": true,
                "title": "Join Request Settings",
                "desc": "Control how students can join your class. You can limit access to listed students, allow requests, or open it to everyone.",
                "name": "join_mode",
                "value": [
                    {
                        title: "Direct Access (Listed Students)",
                        desc: "Only students pre-added to your class roster can join directly without requiring approval.",
                        value: "directAccess"
                    },
                    {
                        title: "Approval Required (Listed Students)",
                        desc: "Only students in your roster may request access. Each request must be reviewed and approved by you.",
                        value: "approvalRequired"
                    },
                    {
                        title: "Open Access Requests",
                        desc: "All students can submit join requests. You retain full control to review and approve each request.",
                        value: "openAccessRequests"
                    }

                ]
            },
            result_visibility: {
                "class": "result-visibility",
                "type": "button",
                "required": true,
                "title": "Test Result Visibility",
                "desc": "Choose how the test results will be published.",
                "name": "result_visibility",
                "value": [
                    {
                        "title": "Auto Publish",
                        "value": "auto_publish"
                    },
                    {
                        "title": "Manual Publish",
                        "value": "manual_publish"
                    }
                ]
            },
            exam_category: {
                "class": "class",
                "required": true,
                "title": "Select Student Class",
                "desc": "Choose the class this exam is intended for. You may also select 'Any' to allow all students to participate.",
                "name": "exam_category",
            }
        }
        return q ? query[q] : query;
    }
    const getWin = (ttl, cls, bind) => {
        ES.handelAct = true;
        const pop = $.popup();
        const clsFn = pop.close;
        const con = pop.create(cls || "container");
        const ti = pop.header.create.h2(null, ttl);
        pop.header.p.css({ borderBottom: '1px solid' })
        ti.setDomStyle({ padding: '2px 57px 2px 16px' });

        pop.close = () => {
            if (typeof bind == "function") bind();
            else r.back();
            clsFn();
            ES.handelAct = false;
            pop.close = e => true
        };
        ES.pop = pop;
        return [pop, con, ti];
    };
    const createCard = (element, exam_category) => {
        let card = element.create("T002");
        exam_category && card.add(exam_category);
        return card.create("session");
    }
    const createWithPosition = (content, dataId) => {
        const id = "oKHntm";
        const el = $(id, true) || $.cx({ display: "block", width: "100%" });

        el.add("id", id);
        el.clear();
        if (content) el.append(content);
        if (dataId) el.set("data-id", dataId);

        return el;
    };
    function createHeader(title, countValue) {
        const selfHeader = this.create('T037');
        selfHeader.create('T040', $.create.span(null, title));
        const headerGrup = selfHeader.create('DIS01');

        const count = typeof countValue !== 'undefined'
            ? headerGrup.create.span(null, String(countValue))
            : null;

        const updateCount = count ? (n) => {
            count.innerText = n;
        } : () => { };

        return {
            count,
            updateCount,
            selfHeader,
            add(bind, title) {
                const link = headerGrup.create.span('link', title || 'Add');
                link.event.on(bind);
                link.css({ marginLeft: 5 });
                return link;
            },
            addMenuButton(data) {
                return headerGrup.create
                    .button(null)
                    .addIcon("ic_description")
                    .event.on(e => {
                        return $.menuexitue(e).executed(data);
                    })
                    .css({ marginLeft: 5 });
            }
        };
    }
    const createSectionGroup = (cfg, c) => {
        const body = c.create('T035')
            , header = createHeader.call(body, cfg.title, cfg.count)
            , container = body.create('T036')
            , bind = (callback) => Object.values(cfg.list).forEach(item => callback(item, container));
        return { body, bind, container, ...header };
    };
    const addRequestTocontainer = function ([id, [s, total_request, total_exam_joins, t, is_joined, is_re_requested]], { table, callBack, actionCallBack, buttons }) {
        const [n, r] = ES.students[id] || [];
        const request = { id, n, r, t, s }
        const group = $.create("DIS01");
        const lists = table.addRow({ a: group, ...request });
        const delet = function () {
            lists.add("disabled");
            EventHub.call(request.id, e => e.nodeName == "DIV" && e.remove());
            return this.in("Delete", true)
        };

        lists.id = AUTH_TOKEN.encode([request.id, RV.REQUEST_VIEW]);
        lists.add("callback_id", RCB.REQUEST_POPUP_VIEW)

        for (const label of buttons || ["Accept", "Reject"]) {
            const btn = group.create.button("btn", label).add("title", label);
            typeof actionCallBack == "function" && btn.event.on(function (e) {
                actionCallBack.call(this, e, request)
            });
            request.s === 1 && label == "Reject" && delet.call(btn);
        }

        EventHub.import(request.id, lists);
        typeof callBack == "function" && callBack(lists, request)

    };
    const createRequestList = (t, s, l, id, r, m, bts) => {
        let w, c, h, d, load = 1;

        const tb = createJsonTable({
            header: { r: "", n: "", t: "", a: "" },
            body: [],
            loader: 4
        }).css({ minWidth: 700 });
        const sort = (k, v) => {
            useServerConnectionData.set(k, v);
            while (l.length) l.pop().remove();
            req();
        };
        const req = (n = 5) => sendReq({ reqRoute: r, payload: [l.length, n], useFilter: true }, res);
        const res = ({ record, students, srs_tr }) => {
            Object.assign(ES.students, students);
            ES.StuReqSes[s] = srs_tr;

            record.forEach(d =>
                addRequestTocontainer(d, {
                    table: tb,
                    buttons: bts,
                    callBack: (a, b) => {
                        l.push(a);
                        id = b.id;
                    },
                    actionCallBack: function (e, a) {
                        const k = this.innerText.toLowerCase();
                        this.loader(true) && sendReq([[300, [203, [k, [a.id, a.r], []]]]], x => rsc(x, this));
                    }
                })
            );

            load = 1;
            if (!w) {
                [w, c, h] = getWin(t, "pop-containerT019", e => e), d = [{
                    icon: "ice_sort", name: "Sort by",
                    hover(e, b) {
                        let x = $.tooltip_menu(this, e.target, b);
                        if (!x?.executed) return;
                        x.executed(Object.entries({ date_asc: "Oldest First", date_desc: "Newest First", name_asc: "Student Name (A–Z)", name_desc: "Student Name (Z–A)", roll_no_asc: "Roll No (Ascending)", roll_no_desc: "Roll No (Descending)" }).map(([i, n]) => ({  name: n, active: useServerConnectionData.get("reqOrder") == i, event: () => sort("reqOrder", i) })));
                    }
                }];
                c.in(tb);
                w.hrg.unshift($.create.button("menu").addIcon("ic_description").event.on(e =>
                    $.menuexitue(e).executed(typeof m == "function" ? m(d) : d)
                ));

                c.event.scroll(e => {
                    let x = e.target;
                    if (x.scrollTop + x.clientHeight + 40 >= x.scrollHeight && load && ES.StuReqSes[s] > l.length) {
                        load = 0;
                        req(1);
                    }
                });
            }


            if (srs_tr > l.length && c.scrollHeight < c.get().height)
                req();
        };
        return [req, sort];
    };
    const requestListView = (e) => {
        ES.StuReqSes ??= FlEXMAP();
        ES.StuReqSes.sendReqList = [];
        ES.StuReqSes.sendReqLastId = null;

        const m = e => { sort("reqView", e); return true };
        const h = e => useServerConnectionData.get("reqView") == e;
        const [req, sort] = createRequestList(
            "Student Requests",
            "sendReqAllListCount",
            ES.StuReqSes.sendReqList,
            ES.StuReqSes.sendReqLastId,
            "studentReqs",
            e => {
                const g = $.create('DIS04', 'Live Update');
                useServerConnectionData.get("liveUpd") && g.addIcon('ice_done-v');
                return [
                    { icon: 'ice_3users', name: 'Show All Requests', active: h("all"), event: e => m("all") },
                    { icon: 'ice_user-close', name: 'Show Rejected Requests', active: h("rejected"), event: e => m("rejected") },
                    { icon: 'ice_live', name: g, event: e => { useServerConnectionData.set("liveUpd", !useServerConnectionData.get("liveUpd")); return true } }, ...e
                ]
            }
        )

        return req();
    }
    const viewBlockStudent = (e) => {
        ES.StuReqSes ??= FlEXMAP();
        ES.StuReqSes.blockReqList = [];
        ES.StuReqSes.blockReqLastId = null;

        const [req, sort] = createRequestList(
            "Blocked Student",
            "blockReqListCount",
            ES.StuReqSes.blockReqList,
            ES.StuReqSes.blockReqLastId,
            "stuReqsBlk",
            null,
            ["UnBlock", "Delete"]
        )

        return req()
    }
    const viewRemoveStudent = (e) => {
        ES.StuReqSes ??= FlEXMAP();
        ES.StuReqSes.removeReqList = [];
        ES.StuReqSes.removeReqLastId = null;

        const [req, sort] = createRequestList(
            "Removed Student",
            "removeReqListCount",
            ES.StuReqSes.removeReqList,
            ES.StuReqSes.removeReqLastId,
            "stuReqsRemv",
            null,
            ["Add", "Delete"]
        )

        return req()
    }
    const addRequestStudentsInExam = (d, ls) => {
        const { ec, std, ch } = d || {}, [pop, con] = getWin('Add Student', 'T042', e => true), c = pop.close
            , btn = (txt, fn, data) => {
                const b = con.create.button(null, txt);
                b.event.on(() => fn(b, data));
                b.setDomStyle({ float: 'right', margin: '32px 0' });
            }
            , requr = (r, act, g = null) => [[300, [203, [act, [g, r], ls]]]]
            , lc = (r, f) => (f = ES.get(150), typeof f === "function" && f(r.data))
            , ig = (f, r, b) => {
                let c = f.getContainer(), bt = f.submitButton("Save"), w = window.innerWidth - 200;
                w > 700 && pop.css({ width: w > 1200 ? 980 : w });
                c.append(b); b.append(bt); con.css({ padding: 10 });
                f.checkbox({
                    class: "category", type: "button", required: true, checked: ch,
                    title: "Select Eligible Exams",
                    desc: "Choose all exams for which the student is eligible or intends to appear. Matching exam results can be used to determine direct admission eligibility.",
                    name: "category", value: ec, css: { maxHeight: 200, "grid-template-columns": "repeat(auto-fit, minmax(320px, 1fr))" }
                });
                f.submit = e => e.category.length <= 0
                    ? $.message("Please select at least one eligible exam to continue.")
                    : bt.loader(true) && req([[300, [203, [525, [e.category, r.rollno], ls]]]], e => (e.status === true && (lc(e), location.reload(), $.message(e.message)), pop.close()))

            }
            , cn = r => {
                const { img, name, reg_no, rollno } = r, b = $.create('T043'), l = b.create('image'), i = b.create('info');
                l.create({ tagName: 'img', src: img, title: "User Pic" });
                for (const [t, v, h] of [['Name', name, "h3"], ['Reg. No.', reg_no], ['Roll. No.', String(rollno)]])
                    i.create({ tagName: h || 'div', class: 'T040', inner: t }).create.span('T041', v);

                con.in(b, true);
                return b
            }
            , ld = (r, b) => loadForm(es => (b = cn(r), e = es(con), ig(e, r, b)))
            , search = () => {
                con.clear();
                const input = con.create.label(null, 'Enter Roll Number').create.input({ type: 'text', name: 'rollno' })
                    , gn = (r) => (Array.isArray(ec)
                        ? ld(r)
                        : (cn(r), btn('Add', rq, () => requr(r.rollno, 'addStudent', r.user_id))))

                    , rq = (b, payload) =>
                        !input.value && $.message("Please enter your Roll Number")
                        || b.loader(true) && req(payload(), (r, fn) => {
                            b.loader(false);
                            r.__ac && (fn = ES.get(r.__ac[0])) && fn(r.__ac[1]);
                            r.message ? (con.in($.create(r.errorKey || 'isinfo', r.message), true), btn('Again Search', search)) : gn(r);
                        }, true);

                btn('Search', rq, () => requr(input.value, 'qStudent'));
            };
        pop.close = e => sd("add", c, e);
        typeof std == "object" && std?.name ? ld(std) : search();
        return pop;
    };
    const examListSession = (a, b, c, d) => {
        ES.exViewRes = a;
        Object.assign(ES.students, ES.exViewRes.students)
        ES.STUDENT_JOINED_EXAM.push(...ES.exViewRes.STUDENT_JOINED_EXAM);
        ES.STUDENT_COMPLETED_EXAM.push(...ES.exViewRes.STUDENT_COMPLETED_EXAM);

        const liveAmimation = () => {
            const c = (e, r) => e?.animate(
                [{ r: 0, opacity: 1 }, { r, opacity: 0, offset: .4 }, { r, opacity: 0 }],
                { duration: 3e3, iterations: 1, easing: "linear", fill: "forwards" }
            );

            if (R === undefined) {
                R = true; c($("l1"), 50);
                setTimeout(() => c($("l2"), 40), 280);
                setTimeout(() => R = undefined, 2000);
            }
        }
        const examSetting = (e, fom) => {
            const changeExamStartTime = () => fom().timePiker(null, (e, b, c) => {
                c.loader(true) && sendReq([[302, [5608, [null, { start_timestamp: Number(e) }]]]], res => {
                    ES.exViewRes.start_timestamp = Number(e);
                    EventHub.call('EST', e => e.in(b));
                    if (res.update === true) c.close();
                })
            }, ES.exViewRes.start_timestamp);
            $.menuexitue(e).executed([
                { icon: 'ice_time', name: 'Change Exam Start Time', event: e => changeExamStartTime(e) },
                { icon: 'ice_2users', name: 'Change Request Mode', event: e => ES.setRsyt("join_mode") },
                { icon: 'ice_live', name: 'Change Request Availability', event: e => ES.setRsyt("open_request") },
            ])
        }
        const examLiveSession = (r) => {
            const c = $.domStyle({ marginBottom: 6, gap: 5, display: "flex" });
            r.create.h3(c, "Live Updade");
            r.css({ margin: "10px 20px" });

            const studentRequestSend = r.create.div(c, "Student Requests").create.strong(null, String(ES.exViewRes.STUDENT_REQUEST_SEND_COUNT));
            const studentInStudent = r.create.div(c, "Students In Exam").create.strong(null, String(ES.exViewRes.STUDENT_JOINED_EXAM_COUNT));
            const studentsCompliteExam = r.create.div(c, "Students Complite Exam").create.strong(null, String(ES.exViewRes.STUDENT_COMPLETED_EXAM_COUNT));

            if (ES.exViewRes.isPublish === true || ES.exViewRes.start_timestamp == null)
                return;

            r.create.span("corm").addIcon("an_live");
            doSession().finish = function (q) {
                const [c, e] = q;
                const set = (el, ui, v) => {
                    el.innerText = v;
                    ui.updateCount(v);
                };

                liveAmimation();

                if (c !== 5060 || !e || typeof e !== "object" || Array.isArray(e))
                    return console.log("Event=>", e, q);

                e.students && Object.assign(ES.students, e.students);
                e.STUDENT_REQUEST_SEND_COUNT != null && set(studentRequestSend, ES.sr, e.STUDENT_REQUEST_SEND_COUNT);
                e.STUDENT_JOINED_EXAM_COUNT != null && set(studentInStudent, ES.si, e.STUDENT_JOINED_EXAM_COUNT);
                e.STUDENT_COMPLETED_EXAM_COUNT != null && set(studentsCompliteExam, ES.st, e.STUDENT_COMPLETED_EXAM_COUNT);


                for (const r of e.STUDENT_JOINED_EXAM || e.STUDENT_LEFT_EXAM || []) {
                    const i = ES.STUDENT_JOINED_EXAM.findIndex(v => v[0] === r[0]);
                    i > -1
                        ? ES.STUDENT_JOINED_EXAM[i] = r
                        : ES.STUDENT_JOINED_EXAM.push(r);

                    ES.students[r[0]] && ES.addStudentsInExam(r[0]);
                }

                for (const r of e.STUDENT_COMPLETED_EXAM || []) {
                    ES.STUDENT_COMPLETED_EXAM.push(r);
                    ES.students[r[0]] && ES.addComoletedList(r[0])

                }
                // for (const r of e.STUDENT_REQUEST_SEND || []) {
                //     ES.students[id] && ES.addRequestList(id)
                // }

                e.STUDENT_REQUEST_SEND?.forEach(([id]) =>
                    ES.students[id] && ES.addRequestList(id)
                );
            }
        }
        const showWimdow = (r) => {
            const p = $.popup('Exam Code'), g = p.create("IN0104");
            g.css({ margin: 40, display: 'flex', justifyContent: 'center' })
            for (const i of String(ES.exViewRes.code)) {
                g.create("mlfznw").setDomStyle({ fontSize: "200%", border: '1px solid var(--border)', margin: '5px', fontFamily: 'monospace' })
                    .create.span('wChqif', i).setDomStyle({ margin: '5px', overflow: 'hidden', display: 'table' });
            }
        }
        const examHeaderSession = (r, f) => {
            const h = r.create("header DIS00"),
                i = createCard(h, "T015"),
                l = createCard(h, "T017"),
                c = i.create;

            c.h2("exam-name", ES.exViewRes.exam_name);
            EventHub.import("JRM", c("T016", ES.exViewRes.joinModeTitle));

            const b = c("IN0104 DIS01").create;
            b.button(null, "Get Exam Code").event.on(showWimdow);
            b.button(null, "Get Exam Link").event.on(e => getLinkWimdow(`${location.origin}/exam?join=${ES.exViewRes.code}`));
            c.button("corm")
                .event.on(e => examSetting(e, f))
                .addIcon("ic_setting");

            return examLiveSession(l);
        };
        const examSubjectSession = (r, fom) => {

            const detailsTable = createJsonTable({
                header: { aa: "", bb: "", cc: "", dd: "" },
                body: [
                    { aa: "Exam Code", bb: ES.exViewRes.code, cc: "Total Questions", dd: ES.exViewRes.totalQuestion },
                    { aa: "Exam End Time", bb: formatTimestamp(ES.exViewRes.endTime), cc: "Total Time (Minutes)", dd: ES.exViewRes.totalTime },
                    { aa: "Exam Start Time", bb: ['EST', formatTimestamp(ES.exViewRes.start_timestamp)], cc: "Total Marks", dd: ES.exViewRes.totalMarks },
                    { aa: "Exam Creation Time", bb: formatTimestamp(ES.exViewRes.timestamp), cc: "Notification", dd: (ES.exViewRes.notification ? "On" : "OF") },
                    { aa: "Join Request Mode", bb: ['JRM', ES.exViewRes.joinModeTitle], cc: "Result Visibility", dd: getString().result_visibility.value.find(e => e.value == ES.exViewRes.result_visibility)?.title },
                    { aa: "Change Request Availability", bb: ['JRM', ES.exViewRes.openRequestTitle], cc: "Exam Category", dd: ES.exViewRes.exam_category },
                ]
            });

            const details = r.create("T018");
            const paperTable = createJsonTable({
                header: {
                    paper: "Paper",
                    sub: "Subject",
                    cat: "Topic / Category",
                    noq: "Quantity",
                    dur: "Test Duration",
                    mpq: "Marks / Question",
                    negr: "Negative Marking",
                }, body: []
            });
            details.create.h2(null, "Some Details").p.in(detailsTable)
            details.create.h2(null, "Paper Details").p.in(paperTable);

            Object.entries(ES.exViewRes.details).forEach(([key, [noq, sub, cat, dur, mpq, negr]]) =>
                paperTable.addRow({ paper: key.replace("pe", "Paper "), sub, cat, noq, dur: `${dur} Minutes`, mpq, negr })
            );
        };
        const createGrid = (r, fom) => {
            const warp = r.create.div()
                .create.h2(null, "Student Details")
                .p.create("grid")
                .css({ gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))" });

            const makeList = (container, rollNo, name, img, extra) => {
                container.children.for(e => e.get("auth-token") == AUTH_TOKEN.encode(rollNo, true) && e.remove())
                // if (container.children.length > 5) container.pop();

                const list = createTableRowList.call(container, rollNo, name, img);
                if (extra) list.addRow(extra);
                return list;
            };

            const btn = (label, handler) => $.create.span("button", label).event.on(handler).add("title", label);
            ES.addStudentsInExam = (id) => {
                if (!ES.students[id]) {
                    return
                }
                const [name, rollNo, img] = ES.students[id];
                const [, [
                    joinedStatus, totalRequest, totalExamJoins,
                    requestTimestamps, isJoined, isReRequested
                ]] = ES.STUDENT_JOINED_EXAM.find(([e]) => e == id);

                console.warn([
                    joinedStatus, totalRequest, totalExamJoins,
                    requestTimestamps, isJoined, isReRequested
                ], name, id);

                const btng = $.create("DIS01");
                const list = makeList(ES.si.container, rollNo, name, img, btng);
                btng.create.span(null).add("title", "Student Status").addIcon("ice_live");
                btng.create.span("button", "Action").event.on(function (e) {
                    const event = function (e, close) {
                        this.loader(true) && sendReq([[300, [203, [this.innerText.toLocaleLowerCase(), [id, rollNo], []]]]], res => {
                            if (res.request_id == id && [3, 4, 5].includes(res.update_code)) {
                                list.remove();
                                close()
                            }
                        })
                    }
                    $.menuexitue(e).executed([
                        { icon: 'ic_delete_profile', name: 'Block', event },
                        { icon: 'ic_delete_profile', name: 'Delete', event },
                        { icon: 'ic_remove_profile', name: 'Remove', event }
                    ])
                })

                list.css({ position: "relative" })
                list.add("aria-status", AUTH_TOKEN.encode([50, joinedStatus], true))

                ES.WzULDBd ??= (function (document) {
                    return document.create.style("WzULDBd", `
                    [aria-status=${AUTH_TOKEN.encode([50, 3], true)}] svg{fill:#0f0}
                    [aria-status=${AUTH_TOKEN.encode([50, 4], true)}] svg{fill:#f00}
                    `);
                }($.getHtmlBody()))

                // for (const i of ES.sr.container .childrens)
                //         i.get("auth-token") == AUTH_TOKEN.encode(rollNo, true) && i.remove();
            };

            ES.addRequestList = (id, cb) => {
                if (!ES.students[id]) {
                    return
                }
                const [name, rollNo, img] = ES.students[id];

                const card = $.create("DIS01");
                const list = makeList(ES.sr.container, rollNo, name, img, card);

                list.add("callback_id", RCB.REQUEST_VIEW);
                list.id = AUTH_TOKEN.encode([id, RV.REQUEST_VIEW]);

                ["Accept", "Reject"].forEach(e => card.create.span('button', e).event.on(function () {
                    return this.loader(true) && sendReq([[300, [203, [e.toLowerCase(), [id, rollNo], []]]]], r => rsc(r, this))
                }));
            };
            ES.addComoletedList = (id, cb) => {
                for (const i of ES.st.container.children)
                    i.remove()

                for (const [id, , n] of [...ES.STUDENT_COMPLETED_EXAM].sort((a, b) => a[2] - b[2])) {
                    if (!ES.students[id]) {
                        return
                    }
                    const [name, rollNo, img] = ES.students[id];
                    const card = $.create("DIS01");
                    makeList(ES.st.container, rollNo, name, img, card);
                    for (const i of ES.si.container.childrens)
                        i.get("auth-token") == AUTH_TOKEN.encode(rollNo, true) && i.remove();
                    card.create.span('button', "Check Result").event.on(function () {
                        return window.open(
                            `/qs/${AUTH_TOKEN.encode(["result", id, rollNo, getRequestSearch("id")], true)}`,
                            "_blank",
                            "width=1080,height=680,left=200,top=10"
                        )
                    })
                }
                console.log("addComoletedList", ES.st.container.children);
            };

            const section = (title, count, list) => createSectionGroup({ title, count, list }, warp);

            ES.exViewRes.STUDENT_REQUEST_SEND.reverse();
            ES.si = section('Total Students In Exam', ES.exViewRes.STUDENT_JOINED_EXAM_COUNT, ES.exViewRes.STUDENT_JOINED_EXAM);
            // ES.re = section('STUDENT_REMOVED_FROM_EXAM', ES.exViewRes.STUDENT_REMOVED_FROM_EXAM?.length, ES.exViewRes.STUDENT_REMOVED_FROM_EXAM);
            ES.sr = section('Student Requests', ES.exViewRes.STUDENT_REQUEST_SEND_COUNT, ES.exViewRes.STUDENT_REQUEST_SEND);
            ES.st = section('Student Completed Exam', ES.exViewRes.STUDENT_COMPLETED_EXAM_COUNT, ES.exViewRes.STUDENT_COMPLETED_EXAM);


            ES.si.addMenuButton([
                { icon: 'ic_add_profile', name: 'Add Student', event: e => addRequestStudentsInExam(null, ES.exViewRes.code) },
                { icon: 'ic_list', name: 'View Block Student', event: viewBlockStudent },
                { icon: 'ic_list', name: 'View Remove Student', event: viewRemoveStudent },
            ]);

            const event = (e, close) => {
                let el = e.target;
                while (!el.loader) el = el.parentElement;

                el.loader(true) && sendReq({ reqRoute: "reqApprAct", payload: el.innerText }, pms => {
                    el.loader(false);
                    for (const item of pms.results || [])
                        rsc(item);
                    typeof close == "function" && close();
                }, true)
                return false
            }
            ES.sr.addMenuButton([
                { icon: 'ic_list', name: 'View All', event: requestListView },
                { icon: 'ic_add_profile', name: 'Accept All', event },
                { icon: 'ic_remove_profile', name: 'Reject All', event },
                { icon: 'ic_delete_profile', name: 'Delete All', event },
                { icon: 'ice_gear-settings', name: 'Setting', event: e => ES.setRsyt("req_appr_mode") }
            ]);

            ES.si.bind(([id]) => ES.addStudentsInExam(id));
            ES.sr.bind(([id]) => ES.addRequestList(id));

            ES.st.bind(([id], container) => ES.addComoletedList(id))
            // ES.st.bind(([id, , allmarks], container) => {
            //     if (ES.exViewRes.students[id] === undefined) return;
            //     const [name, rollNo, img] = ES.exViewRes.students[id];
            //     makeList(container, rollNo, name, img, $.create.span(null, String(allmarks)));
            // });
        };
        const contante = (form) => {
            const d = createWithPosition(null, 'eEimYe'); b.in(d);
            for (const bind of [examHeaderSession, createGrid, examSubjectSession]) {
                bind(d, form)
            }
            ES.t.remove()
        }
        return loadForm(contante)
    }

    // Apply a function to a bind if it exists
    function applyBind(key, callback) {
        $.loader(true);
        return sendReq(null, function (e) {
            e.jump && location.reload();
        })
    }
    // Add numbers or concatenate strings
    function sum(...args) {
        if (args.every(arg => typeof arg === 'number')) {
            return args.reduce((acc, num) => acc + num, 0);
        } else if (args.every(arg => typeof arg === 'string')) {
            return args.join('');
        }
    }
    // Load form module with a callback
    function loadForm(callback, context) {
        if (!$.loader(true)) return;
        $.require("widgets/forms", function (form, n) {
            ES.form ??= form;
            callback.call(context, form, n);
            $.loader(false);
        }).css();
    }
    // Initialize the containerfor the MCQ interface
    function initializeContainer(widgetClass, option) {
        const containerId = "T001";
        const container = $(containerId);

        ES.homeIndex ??= container.choose("index", true);
        !option && container.clear();
        container.removed("class");
        container.add([containerId, widgetClass]);

        return container;
    }
    // Bind input events for form logic
    function bindInputEvents(form, input) {
        if (input.get("name") === "Nq") {
            input.event.on(() => { for (const i of form.getInputs()) i.name == "category" && updateCheckedStatus(i, form) });
        }
    }
    // Update checkbox state based on form input
    function updateCheckedStatus(item, form) {
        const disabled =
            Number(form.getValue("Nq")) >
            Number(item.get("lco"));

        item.disabled = disabled;
        item.checked && (item.checked = !disabled);
    }
    // Filter form items by subject
    function filterBySubject(event, form) {
        const selected = event.target.value;

        for (const i of form.getInputs()) {
            if (i.name == "category") {
                const inputSubject = i.get("subject");
                const shouldShow = selected === "All Subject"
                    || selected === inputSubject
                    || inputSubject === "Any";

                i.disabled = true;
                i.p.css("display", shouldShow ? "flex" : "none");

                updateCheckedStatus(i, form);
            }
        }
    }
    // Sends the request and handles progress/finish
    function handleSubmitRequest(form, values) {
        return sendReq(values, function (query) {
            let id = $.jump;
            return id
                ? (form.close())
                : null;
        });
    }
    // Handles form validation and submission
    function onSubmitForm(form) {
        var values = form.getValue();
        if (values.category && values.Nq) {
            return handleSubmitRequest(form, values);
        }
    }
    // Creates left/right containers for form layout
    function buildFormLayout(container, form, callback) {
        if (callback !== true) {
            container.clear()
        }
        return form(container, function (body, form) {
            let container = body.create("T028");
            let left = container.create("left");
            let right = container.create("right");

            form.add("alc", function alc() {
                return form.setcontainer(left);
            });
            form.add("arc", function arc() {
                return form.setcontainer(right);
            });

            form.alc();
            if (typeof callback == "function") {
                callback(form)
            }
        })
    }
    // Builds header and starts layout + configuration
    function initializeFormUI(form) {
        var con = initializeContainer();
        con.create.h2("IN014", "Select Your Test Preferences").setDomStyle({
            textAlign: 'center',
            padding: '8px',
        })
        var container = con.create("T029");
        return buildFormLayout(container, form, function (form) {
            // form.close = popupWindow.close;
            // form.errorcontainer= popupWindow.close;
            // ES.close = popupWindow.close;
        });
    }
    // Adds fields like subject, timing, and category
    function configureFormFields(form, callback) {
        var ncat = ["20", "25", "40", "50", "60", "70", "75", "80", "90", "100"];

        // Create multiple input fields using an array of options
        form.select({ title: "Select Subject", name: "subject", value: ES.subjects, checked: ES.subjects[0], addCustonValue: true, change: e => filterBySubject(e, form) })
        form.radio({ type: "button", required: true, title: "Select set as per number of Questions", name: "Nq", value: ncat })
        form.radio({ type: "button", required: true, title: "Select Test Duration", name: "timing", value: ncat })


        form.arc();
        if ($('mobile') == null) {
            form.container.add('border-left');
        }
        form.radio({
            type: "button", required: true, title: "Select Topic", name: "category", value: ES.category.map(item => item.entry), bind: function (a, value) {
                ES.category.find(item => item.entry == value);
                a.add("lco", ES.category.find(item => item.entry == value).count)
                a.add("subject", ES.category.find(item => item.entry == value).subject)
            }
        })
        if (typeof callback == "function") {
            return callback(form)
        }

        return form;
    }
    function createNavigation(q, t) {
        var n = (q || $).create("T032"),
            c = (q || $).create("IN097"),
            g = n.create("IN0104");

        c.h = c.create('header');

        t instanceof Element
            ? (c.h.append(t), c.t = t)
            : (c.t = c.h.create.h2(null, t));

        for (const i of [
            { icon: 'ic_dashboard', href: "/exam/r/dashboard", inner: "Dashboard" },
            { icon: 'ic_list', href: "/exam/r/index", inner: "Test Lists" },
            { icon: 'ice_3users', href: "/exam/r/student", inner: "Student" },
            { icon: 'ic_setting', href: "/exam/r/setting", inner: "Setting" },
        ]) {
            let a = g.create({ tagName: 'a', href: i.href, class: "list", jsname: false }),
                b = $.create('T033', i.inner);

            a.append($.create('button').addIcon(i.icon), b);
        }

        c.t.css({ padding: '0 5px' });
        c.h.css({ display: 'flex', justifyContent: 'space-between', marginBottom: 14 })
        ES.h = c.h;
        ES.t = c.t;
        return [c, n];
    }
    function Paginator(a, c, d) {
        let i = "paginator"
            , e = $(i, true) || $.create(i)
            , t = function (a) {
                let b = $.req(e => false)
                typeof c == "undefined"
                    && (b.e = true)
                    && b.navigate(this.href);

                typeof c == "function"
                    && this.loader(true)
                    && c.call(this, a)
                    && this.loader(false);
            }
            , n = new $.URLState(false);
        e.clear();
        for (const i of a) {
            let f = $.create.a("button");
            e.set(f);
            f.in(String(i.name));
            f.add(i.clas);
            f.event.on(e => (e.preventDefault(), t.call(f, e)));
            n.e = false;
            n.set("page", i.page);
            f.href = n.u.href;
        }
        e.add("id", i);
        d && $.require("components/search-filter", s => s.filter.call(this, e, d));
        return e;
    }
    function createJsonTable({ header: h, body: b = [], callBack: cb, title: t, loader: l = 0, mx, css }) {
        const c = $.create.div();
        const m = $.isMobile();
        const f = Object.keys(h).flatMap(k => k.split("&"));

        c.listIndex = 1;
        if (t) c.create("header").create.h2(null, t);

        const p = m
            ? c.create("DIS03").css({ gap: 16 })
            : ((
                x = c.create("table").css({ width: "100%", borderCollapse: "collapse" })
                , r = x.create("thead").create("tr")) => Object.values(h).forEach(v => v && (r.create("th").textContent = v))
                || x.create("tbody"))();

        const v = (r, k, i) => {
            const d = r.create(m ? "T011" : "td");
            if (m) d.css({ gap: 5 });

            let x = cb?.call(d, k, i[k] ?? "", i) ?? i[k] ?? "";

            if (m && typeof x !== "object")
                d.in($.create.strong("name", h[k])).css({ width: 100 });

            if (x instanceof HTMLElement) return d.in(x);

            const w = $.create.div("width");

            if (k === "no" && !x) {
                x = c.listIndex++;
            } else if (k === "action") {
                w.create.button(null, x);
            } else if (k === "img" || k === "image") {
                const z = w.create({ tagName: "img" });

                if (typeof x === "string") z.src = x;
                else if (x && typeof x === "object") {
                    const { width, height, ...a } = x;
                    w.css({ width, height });
                    Object.entries(a).forEach(([k, v]) => z.set(k, v));
                }
            } else {
                if (Array.isArray(x)) {
                    EventHub.import(x[0], w);
                    x = x[1];
                }
                w.in(typeof x === "number" ? String(x) : x);
            }

            d.in(w);
        };

        c.addRow = i => {
            const r = $.create(m ? "T002" : "tr");

            if (m) r.css({ padding: 16 });
            if (i.id) r.add("id", i.id);

            if (i.option) {
                const o = i.option;
                i.option = $.create.div("T012 link").event.on(e => {
                    const d = $.menuexitue(e);
                    d.executed(typeof mx === "function" ? mx(o, i) : o, { v: i, e: r });
                }).addIcon("ic_list");
            }

            f.forEach(k => v(r, k, i));

            if (i.isActive) r.add("isActive");
            if (i.active && css) r.css(css);

            p.in(r, p.childrens.length - l);
            return r;
        };

        for (let i = 0; i < l; i++)
            c.addRow(Object.fromEntries(f.map(k => [k, $.create("loader")])));

        b.forEach(c.addRow);
        return c;
    }

    function formatTimestamp(t) {
        if (!t) {
            return "No"
        }
        const d = new Date(t),
            M = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            h = d.getHours(),
            m = h % 12 || 12,
            a = h >= 12 ? "PM" : "AM";
        return `${d.getDate().toString().padStart(2, '0')} ${M[d.getMonth()]} ${d.getFullYear()} at ${m}:${d.getMinutes().toString().padStart(2, '0')} ${a}`;
    }
    function getRequestSearch(a, b, c) {
        return r.get(a, b, c)
    }
    function gp() {
        return getRequestSearch("page") || 1
    }
    function activateWebSocket(url) {

        // Reuse existing socket
        if (ES.ws?.readyState < WebSocket.CLOSING && ES.ws.url?.includes(url))
            return ES.ws;

        // Close existing socket if CONNECTING or OPEN
        if (ES.ws && ES.ws.readyState < WebSocket.CLOSING) {
            ES.ws.close();
        }

        console.log("Activating WebSocket...", url);

        const socket = $.socket(url);
        const originalExport = socket.export;
        ES.ws = socket;

        socket.finish = async (data = {}) => {
            const actions = data.__ac || {};
            console.warn("WS message:", data);

            for (const [id, val] of Object.entries(actions)) {
                const fn = ES.get(+id);
                if (typeof fn === "function") fn(val);
            }

            if (typeof data.is === "function" && data.is("session") === "close") {
                socket.close();
            }
        };

        socket.export = (a, b, c) => {
            if (a && typeof a === "object" && ES.ExamSessionKey) {
                a.key = ES.ExamSessionKey;
            }
            return originalExport(a, b, c);
        };

        // Events
        socket.onclose = (e) => {
            console.log("WebSocket closed");
        };

        socket.onerror = (e) => {
            console.error("WebSocket error:", e);
        };

        socket.callBack = (e) => {
            socket?.close()
        };

        socket.startUrl = r.href
        r.onChange(e => !e.href.includes(socket.startUrl) && socket.callBack(socket, e))
        return socket;
    }
    function doJoine(connect_key, b, c) {
        if (!connect_key) {
            console.error("Invalid exam ID provided.");
            return {};
        }
        const key = $.getKey();
        const id = $.getKey(true);

        _exmeg.insert([key, id, connect_key].join("-"));

        return activateWebSocket("exam/connect/q=" + key);
    }
    function doSession(a, b, c) {
        return activateWebSocket("exam/sn/t=" + getRequestSearch('id'))
    }
    function getHexKey(id, connect_key, session_key) {
        session_key = session_key || $.getKey();

        _exmeg.insert([session_key, id, connect_key].join("-"));
        ES.ExamSessionKey = session_key;

        return connect_key;
    }
    function doExame(session_key) {
        const keys = getHexKey(getRequestSearch("hx"), $.getKey(), session_key)
        return activateWebSocket("exam/do/q=" + keys)
    }
    function eventLogger(callBack, hendler, exquiter) {
        ES.eventLogger = false;
        callBack(hendler, exquiter);
        ES.eventLogger = true;
    }

    function createTableRowList(rollNo, name, src) {

        const list = $.create("DIS04");
        const row = list.create("_row DIS00");
        const img = $.create.img({
            src,
            width: 40,
            height: 40
        })

        list.add('auth-token', AUTH_TOKEN.encode(rollNo, true));
        row.create.span('ml-5 BOX30', img);

        img.event.mouseover(function (event) {
            $.tooltip(this, null).executed(
                $.create.span(null).css({
                    display: "block",
                    width: 100,
                    height: 120,
                    backgroundImage: `url(${img.src})`,
                    backgroundSize: "cover",
                    backgroundPosition: "center"
                })
            )
        })

        row.create.span('ml-5', String(rollNo));
        row.create.span('ml-5', String(name));

        list.addRow = function (value) {
            return this.create('_row', value);
        };
        this.unshift(list);
        return list;
    }
    function getCountdown(start) {
        const diff = Math.floor((new Date(start) - new Date()) / 1000);
        if (diff < 0) return;
        const h = String(Math.floor((diff / 3600) % 24)).padStart(2, '0');
        const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
        const s = String(diff % 60).padStart(2, '0');
        return `${h} hours : ${m} minutes : ${s} seconds`;

    }

    r.homepage = function () {
        return r.navigate("/exam");
    }

    var handleAction = function () {

        if (ES.handelAct == true) {
            return true
        }

        var q, woen = getRequestSearch('woen');
        console.error("handleAction", ES.handelAct, q, woen);

        if (q = Number(getRequestSearch('q'))) {
            ES.handelAct = true;
        }
        return null

    }


    listen(RCB.REQUEST_VIEW, function () {
        return sendReq(
            { reqRoute: "studentReqs", payload: [0, 4] },
            e => {
                // ES.students ??= {};
                e.students && Object.assign(ES.students, e.students);
                e.record.reverse()
                for (const [id,] of e.record) ES.addRequestList(id)
            },
            true
        );

    })
    listen("setRsyt", function (a, b, c, d) {
        const dialog = editSetting.call(ES.exViewRes, a, (e, form) => {
            const value = form.getValue();
            dialog.submit.loader(true) && sendReq([[302, [5608, [null, value]]]], res => {

                ES.exViewRes[a] = value[a];
                var setting = getString()[a]

                EventHub.call("JRM", e =>
                    e.in(setting.value.find(v => v.value === value[a]).title)
                );

                res.update && dialog.pop.close();
            });
        });
        return true;
    })


    // This Function Is Home Page
    listen(100, function (a, b, c, d, e) {
        "use strict";

        a = initializeContainer(null, true);
        if (a.innerText != ES.homeIndex.innerText) {
            a.in(ES.homeIndex, true)
        }
    });
    listen(101, function (a, b, c, d, e) {
        "use strict";
        ES.category = a.category;
        ES.subjects = a.subjects;
        var storageInstance = $.storage(getRequestSearch("hx")), dataStore = {};
        if (storageInstance.get() != null) {
            for (const key of ["id", "title", "subject", "category", "timing", "expiry", "timeup"]) {
                dataStore[key] = storageInstance.export(key);
            }
        }

        return loadForm(function (m, n) {
            var form = initializeFormUI(m);
            form.container.add("berTr")

            form = configureFormFields(form);
            for (const input of form.getInputs()) {
                bindInputEvents(form, input);
            }
            form.submitButton("Start Test").css({ float: "right", margin: '16px' });
            form.submit = e => onSubmitForm(form);
            form.errorcontainer = form.container;
            return true;
        })

    });
    listen(102, function (a, b, c, d, e) {
        "use strict";
        let pop = $.popup(), clo = pop.close, cs = { padding: "0 16px" };
        pop.css({ maxwidth: 480, padding: 10 })
        pop.header.create.h2(null, a.title)
        pop.header.p.css({ marginBottom: 20 });
        pop.close = e => (clo(), r.path("exam"));
        for (const content of a.content) {
            B(content) ? pop.create(content).css(cs)
                : pop.create.p(null, content).css(cs);
        }
    });
    listen(103, function (a, b, c, d, e) {
        "use strict";
        let T001 = initializeContainer('container');
        let [con, n] = createNavigation(T001);
        con.t.in("Error 404");
        con.create.h2(null, "Oops! Something bad happened!")
        con.create.p(null, "We apologize for any inconvenience, but an unexpected error occurred while you were browsing our site.")
    });
    listen(104, function (a, b, c, d, e) {
        "use strict";

        const head = $.create("DIS01");
        const T001 = initializeContainer('T034');
        let [con, n] = createNavigation(T001, head);

        head.create.h2(null, "Students").css({ marginRight: 16 });
        head.create.button(null, "Add a New Student").event.on(e => ef(r.u.pathname + `?add=student`, e => addRequestStudentsInExam({ ec: a.exam_category, std: null }, 112)))
        getRequestSearch('add') == "student" && addRequestStudentsInExam({ ec: a.exam_category, std: null }, 112);


        $.require("components/search-filter", f => con.h.in(f.gsSearch(r), 1));
        con.h.create.div(null, Paginator(a.pagination || [], undefined, [
            ["input", { title: "Roll No", name: "rollno", placeholder: "Enter Roll No." }],
            ["checkbox", {
                name: "cls",
                grid: 270,
                title: "With In Class Name",
                value: a.exam_category
            }]

        ]))

        const css = { background: "#ff000030" }
        const header = {
            "sno": "No",
            "name": "Student Name",
            "rollno": "Roll No.",
            "attempt": "Attempt Exam",
            "inclass": "In Class",
            "timestamp": "Adding Time",
            "option": "Action"
        };
        const su = (r, v, e) => {
            v.status = r.link_status;
            e.css({ background: "none" });
            v.status == 2 && e.css(css)
        }
        const option = [
            { icon: 'ice_edit', name: 'Edite Class', event: (e, c, { v }) => (addRequestStudentsInExam({ ec: a.exam_category, std: v, ch: v.exam_category }, 113), c()) },
            { icon: 'ice_circle-block', name: 'UnBlock', event: (i, c, { e, v }) => req([[300, [203, [525, [null, v.rollno], 115]]]], r => su(r, v, e)) },
            { icon: 'ice_circle-block', name: 'Block', event: (i, c, { e, v }) => req([[300, [203, [525, [null, v.rollno], 114]]]], r => su(r, v, e)) },
            { icon: 'ice_trash-delete', name: 'Delete', event: (i, c, { e, v }) => req([[300, [203, [525, [null, v.rollno], 116]]]], r => r.status === true && e.remove()) }
        ]
        const tableElement = createJsonTable({
            css, header, body: [], callBack: (a, e, v) =>
                a == "inclass" && v.exam_category.join(", ").toLocaleUpperCase()
                || a == "timestamp" && formatTimestamp(e)
                || e,
            mx: (e, v) => (e = [...e], e.splice(v.status, 1), e)
        });
        ES.add(150, function (e) {
            e["option"] = option;
            tableElement.addRow(e)
        })
        for (const item of a.list) {
            item["option"] = option;
            item["active"] = item.status == 2;
            tableElement.addRow(item)
        }
        con.in(tableElement)
    });
    listen(105, function (a, b, c, d) {
        let T001 = initializeContainer('T034');
        let [con, n] = createNavigation(T001);
        con.t.in("Dashboard");
        con.h.create.a({
            class: "button",
            jsname: false,
            inner: "Create a New Exame",
            href: "/exam/r/create",
        })


        con = con.create("flexs")

        // Create summary cards
        const grid = con.create("grid stats");
        const stats = [
            { label: "Total Exam", value: a.totalExamCount },
            { label: "Results Published", value: a.totalResultsPublished },
            { label: "Student Requests", value: a.studentRequests },
            { label: "Students Joined", value: a.studentsJoined },
            { label: "Exam with Results", value: a.totalTestResultsPublished }
        ];

        stats.forEach(stat => {
            const card = grid.create("div", "card");
            card.innerHTML = `<h2>${stat.label}</h2><div class="value">${stat.value}</div>`;
        });

        const header3 = {
            "image": "Image",
            "studentName&userName": "Name",
            "score": "Score",
            "rank": "Rank",
        };
        const tableElement3 = createJsonTable({
            title: "Top Teachers",
            header: header3,
            body: a.dataRankList,
        });

        const header2 = {
            "studentName": "Name",
            "testsJoined": "Exam Joined"
        };
        const tableElement2 = createJsonTable({
            title: 'Top Student Test Participation',
            header: header2,
            body: a.topStudentTestParticipation,
        });
        // con.append(tableElement2)


        const header = {
            "testCode": "Code",
            "exam_name": "Name",
            "testOpeningTime": "Opening Time",
            "studentsJoined": "Students Joined",
            "timing": "Timing"
        };
        const tableElement = createJsonTable({
            title: 'Recent Exam List',
            header,
            body: a.recentExam,
        });
        con.append(tableElement);
    })
    listen(106, function (a, b, c, d, e) {
        "use strict";
        return loadForm(function (m, n) {
            let [con, nv] = createNavigation(initializeContainer('_setting'));
            con.t.in("Setting");

            let form = m(con);
            form.radio(a.requestMode);
            form.radio(a.result_visibility);
            form.checkbox(a.class);

            form.change(function (e) {
                con.action ??= con.h.create
                    .button("save", "Save")
                    .event.on(function () {
                        this.loader(true);
                        let value = form.getChangeValue();
                        sendReq(value, (re) => {
                            this.loader(false);
                        })
                    });
            })

        })
    })
    listen(107, function (a, b, c, d, e) {
        "use strict";
        $.loader(true);
        return doExame(a.session_key)
    })
    listen(199, function (a, b, c, d, e) {
        "use strict";
        function bR(b, s, n = '/') {
            let r = [b], g = i => { for (const k in i) for (const x of i[k]) r.push(sum(b, n, k, n, x)) };
            return (s.forEach(i => typeof i === 'string' ? r.push(sum(b, n, i)) : g(i)), r);
        }
        a = bR('/exam', ['create', { r: ['list', 'create', 'student', 'dashboard', 'setting'] }]);
        b = sum(a.indexOf(r.pathname), 100);

        if (F(ES.closeAction)) {
            ES.closeAction();
            ES.closeAction = null;
        }
        console.error("main function");


        return applyBind.call(ES, b, function (bind) {
            if (ES.eventLogger === true) {
                bind = bind.call(null, r.u.pathname);
            }
            handleAction()
            return bind;
        });
    });
    listen(405, function (a, b, c, d) {
        let container = initializeContainer('container');
        let [con, n] = createNavigation(container);
        const nav = con.h.create("DIS01 T050");
        con.css({ maxWidth: 1200 })

        const m = (e, f) => {
            let i = r.get("id")
                , qc = new URL(e.href).searchParams.get("qc")
                , q = r.get("qc") || i && "behaviors"
                , b = qc == q
                , d = a[q || "behaviors"] || {}
                , t = d.title || "Some important Setting"

            !i && !q && r.navigate(e.href);
            i && e.remove(), e.event.on(() => r.navigate(e.href));

            return e.add("active", b)
                && b
                && typeof f === "function"
                && (loadForm((fo, n) => {
                    let fm = fo(con);
                    d.desc && fm.desc(d.desc);
                    return f.call(fo, fm, d, e, n);
                }), con.t.in(t));
        }

        if (a.account) {
            const ac = (forms, data) => {
                forms.container = forms.container.create("account-s").css({ margin: 6 });
                forms.input({
                    title: "Profile Photo",
                    desc: "Upload a clear photo of the teacher. This image will be displayed on the teacher's profile, certificates, and reports.",
                    type: "img",
                    name: "img",
                    key: data.key,
                    width: 140,
                    height: 160,
                    reqSize: 1024 * 1000,
                    value: data.img,
                    default_img: data.img,
                    // required: true
                });

                forms.input({
                    title: "Display Name",
                    desc: "Enter the teacher's full name exactly as it should appear on profiles, certificates, reports, and other official documents.",
                    name: "name",
                    value: data.name,
                    required: true
                });

                forms.textarea({
                    title: "Biography",
                    desc: "Provide a brief introduction highlighting the teacher's qualifications, teaching experience, areas of expertise, and professional background.",
                    name: "biography",
                    value: data.biography,
                    required: true
                });

                forms.input({
                    title: "Signature",
                    desc: "Upload a clear image of the teacher's signature. It may be used on certificates, report cards, and other official documents.",
                    type: "img",
                    name: "signature",
                    default_img: data.signature || "/media/icon/signature.jpg",
                    height: 80,
                    width: 240,
                    reqSize: 1024 * 50,
                    key: data.key,
                    value: data.signature,
                    required: true
                });

                forms.submitButton(data.signature ? "Update" : "Save")
                forms.submit = function (i) {
                    this.loader && this.loader(true);
                    sendReq(i, e => this.loader(false))
                }
            }
            const be = (forms, data) => {
                var bind;
                for (const item of data.data) {
                    if ((bind = forms[item.listType]) && F(bind)) {
                        if (item.listType == "checkbox") {
                            item.value = {
                                css: {
                                    // display: "grid",
                                    gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))'
                                }, ...item.value
                            }
                        }
                        item.listType && bind(item.value);
                    }
                    else {
                        var e = item.value;
                        var g = tm.call(forms, e.start_timestamp, e.startTimeFormat, "start_timestamp");
                        var st = forms.container.create("start-time").css({ marginLeft: 16, paddingBottom: 25 })


                        st.create('T040 F0019', $.create.h3(null, 'Test start time')).create.span('T041', g);
                        st.create.p('F0020', "Set the exact date and time when the test will begin. Users can start the test only after this time");

                        var h = tm.call(forms, e.publish_timestamp, e.publishTimeFormat, "publish_timestamp");
                        // var h = tm.call(forms, e.publish_timestamp, e.publishTimeFormat, "publish_timestamp");
                        var ge = $.create("IN0104");
                        var pco = forms.container.create("publish-time").css({ marginLeft: 16, paddingBottom: 25 });

                        console.log(e.publish_timestamp, e.publishTimeFormat, h);

                        ge.create('T040 F0019', $.create.h3(null, 'Result Publish Time')).create.span('T041', h);
                        ge.create.p('F0020', "Set the exact date and time when your result will be published and visible to member. Once this time is reached, the result will automatically become available to everyone");
                        var mj = function () {
                            let value = forms.getValue();
                            value.result_visibility == "auto_publish"
                                ? pco.in(ge, true)
                                : ge.remove();
                        }
                        forms.change(mj), mj();
                    }
                }
                forms.submit = function (e) {
                    if (e.exam_category.length < 5) {
                        $.message("Please Select 5 Competitive Exam Class")
                        return true
                    }
                    return sendReq({ ...e, dataType: "settionQuery" }, function (e) {
                        console.log(e);
                    })
                }
                forms.change(function (e) {
                    con.action ??= nav.create
                        .a("button", "Save", 0)
                        .event.on(function () {
                            this.loader(true);
                            let value = forms.getChangeValue();
                            sendReq(value, (re) => {
                                this.loader(false);
                            })
                        }).add("active", true);
                })
                !a.use_action && forms.submitButton("Save and Continue");
            }

            for (const k of [{ t: "Account", e: ac }, { t: "Behaviors", e: be }])
                m(nav.create.a({ inner: k.t, class: "button", jsname: false, href: "/exam/r/setting?qc=" + k.t.toLocaleLowerCase() }), k.e)
        }

        for (const content of a.content || []) {
            B(content)
                ? con.create({ class: 'ml-5', ...content })
                : con.create.p('ml-5', content);
        }
    })
    listen(110, function (a, b, c, d) {
        return loadForm(fn => {
            const { pop, form, submit } = fn(true, 'Next');
            pop.width();
            pop.absolute();
            submit.apply();

            pop.closeButton.event.on(r.back)
            ES.closeAction = pop.close;
            form.radio({
                css: { gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', maxHeight: 264 },
                "required": true,
                "title": "📚 Select / Enter Exam Name",
                "name": "slexam",
                "value": a.result
            })
            var input = form.input({ name: "exam_name", required: true });
            input.css({ margin: "0 12px", fontSize: 'large' });
            form.requiredmessage = "Fill the Exam Name"
            form.container.create("DIS01").append(input, submit);
            submit.css({ float: "right", margin: 12 })
            form.change(function (e) {
                if ("exam_name" != this.name)
                    input.value = this.title;

            })
            form.submit = function (value) {
                for (const [i, v] of Object.entries({ id: navigation.currentEntry.id, t: Date.now(), tn: btoa(value.exam_name) })) {
                    r.e = false;
                    r.set(i, v);
                }
                ES.closeAction();
                ES.closeAction = null;
                r.e = true;
                r.change();
                console.log(r);

            }
            form.getForm().setDomStyle({ padding: "10px", });
        })
    })
    listen(111, function (a, b, c, d) {
        var cg = $.cx({ display: "block", width: "100%" })
        var inc = function () {
            let T001 = initializeContainer('T034');
            let [con, n] = createNavigation(T001);
            con.append(cg);
            return cg;
        }

        ES.category = a.category;
        ES.subjects = a.subjects;
        loadForm(form => {
            var defaultValue = {
                "negative_marking": "None",
                "category": "All Topic"
            }

            form = form(cg, function (body, form) {
                let title = body.create.h3("exam_name", "Exam Name : ")
                let container = body.create("select_container");
                let formSession = container.create("DIS03");

                title.create.span(null, a.exam_name);
                form.add("sessionStart", function sessionStart(query = {}) {
                    formSession.clear();
                    form.setcontainer(formSession);
                    // let bind = function (a, value) {
                    //     ES.category.find(item => item.entry == value);
                    //     a.add("lco", ES.category.find(item => item.entry == value).count)
                    //     a.add("subject", ES.category.find(item => item.entry == value).subject)
                    // }
                    for (const name in form.STPSDD) {
                        if (!Object.hasOwn(form.STPSDD, name)) continue;
                        const value = form.STPSDD[name];
                        const title = "Select " + form.STPTHD[name];
                        const checked = query[name];
                        form.select({
                            title, name, value, checked, addCustomValue: true,
                            change: (e, form) => form.changeAction(name, form)
                        });
                    }
                });
                form.add("selfBodyContainer", function selfLeftContainer() {
                    return form.setcontainer(container);
                });
                const header = {
                    "no": "No",
                    "subject": "Subject",
                    "num_questions": "Question Quantity",
                    "duration": "Test Duration (minutes)",
                    "marks_per_question": "Marks for Each Question",
                    "negative_marking": "Negative Marking",
                    "category": "Topic / Category"
                };
                var ncat = ["10", "20", "25", "40", "50", "60", "70", "75", "80", "90", "100"];

                form.add("STPSDD", {
                    num_questions: ncat,
                    subject: e => ES.subjects,
                    category: e => ES.category.map(item => item.entry[1]),
                    duration: ncat,
                    marks_per_question: ["1", "2", "3", "4", "5"],
                    negative_marking: ["None", "1:1", "2:1", "3:1", "4:1", "5:1"],
                });
                const tableElement = createJsonTable({
                    header,
                    body: []
                });
                body.append(tableElement);
                tableElement.css("min-height", "200px");
                form.add("STPTHD", header);
                form.add("STPATV", function STPATV(item, callBack) {
                    return tableElement.addRow(item, callBack);
                });

                form.add("changeAction", function changeAction(item) {
                    var value = form.getValue(), qu = parseInt(value.num_questions);

                    if (item == "num_questions") {
                        sendReq({ inte: [qu, null] }, function (e) {
                            ES.subjects = e.category;
                            if (F(form.valueUpdateCallback.subject)) {
                                form.valueUpdateCallback.subject(e.category)
                            }
                        })
                    }

                    if (item == "subject") {
                        if (!qu) return $.confirm({
                            h: "Oops!",
                            t: "Please Select Question Quantity",
                            c: "OK"
                        });
                        sendReq({ inte: [qu, value.subject] }, function (e) {
                            ES.category = e.category;
                            if (F(form.valueUpdateCallback.category)) {
                                form.valueUpdateCallback.category(e.category)
                            }
                        })
                    }
                });


            });

            form.sessionStart(defaultValue);
            form.selfBodyContainer();
            form.button({ title: "Add Exam Preferences" }, function (e) {
                const missing = Object.entries(e)
                    .filter(([_, val]) => !val?.trim())
                    .map(([key]) => form.STPTHD[key]);
                if (missing.length) return $.confirm({
                    h: "Oops!",
                    t: `Please fill in the following fields:\n${missing.join(", ")}`,
                    c: "OK"
                });

                // e["no"] = form.selectedExamPreferences.length
                for (const item of form.selectedExamPreferences) {
                    if (item.subject === e.subject && (item.category === e.category || e.category === "All Topic")) {
                        return $.confirm({
                            h: "Oops!",
                            t: "Duplicate entry detected",
                            c: "OK"
                        });
                    }
                }
                form.addExamPreferences(e)
                form.STPATV(e);
                form.sessionStart(defaultValue);
            }).css({ margin: "15px 0 5px 6px" });

            const foco = cg.create("T046");
            const T045 = foco.create("T045 DIS01");
            const value = {
                "totle_question": "Total Question",
                "total_number": "Total Number",
                "total_duration": "Total Duration (minutes)",
                "passing_number": "Passing Number",
            }
            for (const i in value) {
                if (!Object.hasOwn(value, i)) continue;
                const gruup = T045.create("T047 DIS01");
                gruup.create("ti", value[i]);
                value[i] = gruup.create("count", "0");
            }

            form.add("selectedExamPreferences", []);
            form.add("addExamPreferences", function addExamPreferences(item) {
                form.selectedExamPreferences.push(item);
                let total_duration = 0,
                    totle_question = 0,
                    total_number = 0;
                for (const i of form.selectedExamPreferences) {
                    let questions = parseInt(i.num_questions);
                    let mpq = parseInt(i.marks_per_question)
                    let marks = questions * mpq;
                    total_duration += parseInt(i.duration);
                    totle_question += questions;
                    total_number += marks;
                }

                value["passing_number"].in(String(33), true)
                value["total_duration"].in(String(total_duration), true)
                value["totle_question"].in(String(totle_question), true)
                value["total_number"].in(String(total_number), true)
            });

            foco.create.button(null, "Save and Select Question").event.on(function () {
                const examPreferences = form.selectedExamPreferences.map(Object.values);
                sendReq({ examPreferences }, function (e) {
                    if (getRequestSearch("entry") == null && e.entry) {
                        r.set("entry", e.entry)
                    }
                })
            })

            for (const input of form.getInputs()) {
                bindInputEvents(form, input);
            }
            ;
            let g = inc();
            form.getForm().add("T029");
            g.create.h2('IN014', 0).in("Select Test Preferences").setDomStyle({
                textAlign: 'center',
                padding: '8px',
            })
            return true
        })
    })
    listen(112, function (a, b, c, d) {
        var p, q;
        const f = a.is("error");
        if (f && $.message(f, 4000))
            return r.homepage(this);

        var cg = $.cx({ display: "block", width: "100%" })
        var inc = function () {
            let T001 = initializeContainer('T034');
            let [con, n] = createNavigation(T001);
            con.append(cg);
            return cg;
        }

        inc();
        const item = a;
        ES.dtr ??= FlEXMAP();
        ES.dtr.add(gp(), item);

        loadForm(form => {
            cg.clear();
            var m = "quit";
            var [Nq, subject, cog] = item.oictionary;
            var c = $.cx({ display: "flex" })
            var t = $.cx({ "margin-left": "10px" })
            var j = $.cx({ display: "block", width: "100%" })
            var g = $.cx({ display: "flex", "justify-content": "flex-start", "margin-bottom": "10px" })
            var o = $.cx({ display: "block", margin: "5px 0 10px 10px" })
            var b = $.cx({ display: "flex", gap: "10px", "align-items": "center" })
            var y = $.cx({ display: "flex", gap: "5px", "font-size": "18px" })

            var C1 = $.domStyle();
            var C2 = $.domStyle();
            var C3 = $.domStyle();
            var C4 = $.domStyle({ position: "relative", color: "var(--success-text)" });
            var Fc = buildFormLayout(cg, form);

            var mg = cg.create("T049", null, 0)
            var mn = mg.create("DIS01")
            mn.create.span().addIcon("ice_folder-open")
            mn.create.span(null, subject)
            mn.create.span().addIcon("ice_chevron_right")

            var fos = form($.create.div())
            fos.select({ name: "cg", container: mn, value: [[cog, "default"], ...item.co_list], checked: r.get("Cg") || cog })
            fos.change(e => { r.o = false; r.set("Cg", e.target.value); r.o = true; r.set("page", 1); });

            var co, on = function () {
                let a = ES.slt.length;
                let b = +Nq;
                (a < b)
                    ? $.message(`Only ${a} out of ${b} questions have been selected. Please complete the selection.`)
                    : (ES.slt.forEach((item, i) => { item.sno = i + 1 }), r.delete("page"), sendReq({
                        questions: ES.slt,
                        question_submit: true,
                        oictionary: item.oictionary
                    }, e => {
                        var params = e;
                        S.remove();
                        params.url && r.navigate(params.url);
                    }))
            }, re = function () {
                for (const i of d || []) {
                    let a = ES.slt.length;
                    let b = +Nq;
                    if (a < b && i.checked == false) i.click()


                }
            }, un = function () {
                for (const i of d || []) {
                    i.checked && i.click();
                }
                ES.slt = [];
                ES.sessionStorage[item.active] = ES.slt;
                S.insert(ES.sessionStorage);
                co();
            }

            var s = function () {
                let id = "udAXgc", a = $(id, true) || $.cx({ display: "flex", alignItems: "center" });
                a.clear(), a.add("id", id);

                var sc = function (t, i) {
                    let b = a.cx({ display: "flex", marginRight: "10px", borderRight: "2px solid var(--border)", paddingRight: "10px", height: "fit-content", alignItems: "center" });
                    let n = b.cx({}, null, `${t} `)
                    let d = b.cx({ fontWeight: 600, marginLeft: "5px" });
                    if (typeof i == "function") {
                        let f = b.create("info");
                        f.addIcon("ib_bulb");
                        i.call(f.css({ position: "relative", marginLeft: 5 }), f.event);
                    }
                    return function (a, b) {
                        return d.in(`${a}/${b}`)
                    };
                }

                let contc = 0;
                for (const [, b] of item.paper_list) {
                    if (b === true) contc++;
                }
                let d = sc("Paper of :", function (event) {
                    event.mouseover(function () {
                        var element = $.create("ol");
                        for (const [, b, c] of item.paper_list) {
                            let f = element.create.li("flexCeh");
                            f.css("line-height", "1.6");
                            f.create.span(null, c);
                        }
                        return $.tooltip(this, null).executed(
                            element.css("margin", "8px 16px 6px 0")
                        );
                    })
                });

                d(item.paper_list.length, contc);

                let b = sc("Question of :");
                co = e => b(Nq, ES.slt.length);
                co();

                let c = a.cx({ display: "flex", alignItems: "center" });
                c.create.button("button", "Select All").css({ margin: "5px", padding: "3px 12px" }).event.on(re);
                c.create.button("button", "Deselect All").css({ margin: "5px", padding: "3px 12px" }).event.on(un);
                c.create.button("button", "Submit").css({ margin: "5px", padding: "3px 12px" }).event.on(on);


                return a;
            }

            let cb = function (a) {
                let v = Number(a);
                return this.find(item => item.id === v)
            }
            var N = function (a, b, c = 0) {
                let m = a => `${(a + c).toString().padStart(2, '0')}.`;
                let e = $.create.span(C3, m(a));
                e.add("eid", "count");
                e.updateCount = function (a) {
                    return this.in(m(a), true)
                };
                return b ? m(a) : e;
            }
            g.append(c, t);
            j.append(g);

            j.st = function (i) {
                o.clear();
                c.add(y.className);
                c.in(N(i.sno, true))
                t.in($.create.span(C3, i.title), true);
                t.create({
                    tagName: "a",
                    inner: "𝖎",
                    title: "Report",
                    role: "button",
                    jsname: "report",
                    target: "_blank",
                    class: "EXAME_COUNT01 button",
                    href: `/report/${btoa(i.id)}/generate?href=${r.href}`
                })

                for (const [count, value] of Object.entries(i.options)) {
                    b.clear();
                    b.create.span(C1, `(${count})`);
                    b.create.span(C2, value);
                    i.correct_answer == value
                        ? (b.add(C4), b.create.span(C4)
                            // .addIcon("ic_check")
                        )
                        : b.removed(C4);
                    o.append(b.copy(true));
                    t.append(o)
                }
            }
            S = $.storage(gs("entry"));
            ES.slt = S.get() || []
            ES.sessionStorage = S.get() || {}
            ES.slt = ES.sessionStorage[item.active] || []
            Fc.arc();


            Fc.change(e => {
                const t = e.target,
                    v = +t.value,
                    n = t.checked,
                    o = +Nq,
                    h = cb.call(ES.slt, v),
                    g = cb.call(ES.dtr.get(gp()).lists, v),
                    p = ES.slt.length;
                if (n && !h) {
                    delete g.category;
                    delete g.subject;
                    delete g.status;
                    if (p < o) ES.slt.push(g);
                    else {
                        t.checked = false;
                        return $.confirm({ t: "You have reached the maximum number of selected questions. You cannot add more.", c: "Ok" });
                    }
                } else if (!n && h) {
                    ES.slt = ES.slt.filter(i => i.id !== v);
                }

                co();

                ES.sessionStorage[item.active] = ES.slt
                S.insert(ES.sessionStorage);
            });

            let d = Fc.checkbox({
                name: m,
                value: item.lists,
                label: false,
                callBack: (e, v) => {
                    j.st(e);
                    v.add($.domStyle({ display: "flex", "align-items": "flex-start", "margin-bottom": "16px" }));
                    v.p.css({ display: "grid", "max-height": "fit-content", "grid-template-columns": "repeat(auto-fit, minmax(320px, 1fr))" });
                    return { value: e.id, title: j.copy(true), }
                }
            });
            // ES.t.in('Select Question')

            for (const e of d || []) {
                e.add($.domStyle({ width: "18px", height: "18px", flex: "none" }));
                for (const i of ES.slt) { i.id === +e.value && (e.checked = true) }
            }

            let p = Paginator(item.paginators);

            Fc.getForm().cx({ display: "flex", justifyContent: "space-evenly" }).append(p);

            // ES.h.append(s());
            mg.append(s())
        })

    })
    listen(113, function (a, b, c, d) {


        let hedlet = $.create("DIS01");
        let T001 = initializeContainer('T034');
        let [con,] = createNavigation(T001, hedlet);

        hedlet.create.h2(null, "Exam List").css({ marginRight: 16 })
        hedlet.create.a({ href: "/exam/r/create", inner: "Create a New", class: "button" });

        T001 = con
        ES.$list ??= FlEXMAP();
        let Ma = function (a, b) {
            let id = "oKHntm", d = $(id, true) || $.cx({ display: "block", width: "100%" });
            d.add("id", id); d.clear(); a && d.append(a);
            d.set('data-id', b || null);
            return d;
        }
        var ls = function (e, f, g) {
            $.require("components/search-filter", f => T001.h.in(f.gsSearch(r), 1));
            T001.h.append(Paginator(e.paginators || [], undefined, [
                ["input", { title: "Exam Name", name: "name", placeholder: "Enter Exam Name" }],
                ["input", { title: "Exam id", name: "exam_id", placeholder: "Enter Exam Id" }],

            ]))

            const header = {
                "exam_name": "Exam Name",
                "subject": "Subject",
                "totalTime": "Timing",
                "joinModeTitle": "Join Mode",
                "openRequestTitle": "Request Availability",
                "startTimeFormat": "Start Time",
                "timestampFormat": "Create Time"
            };

            const tableElement = createJsonTable({
                header,
                body: e.list,
                callBack: function (e, v, l) {
                    if ("exam_name" == e) {
                        const container = $.create.div()
                        container.cx({}, null, v);
                        let b = container.cx({ display: "flex", alignItems: "center", gap: "2px", fontSize: "80%", padding: "5px 1px" });
                        let g = r.u.pathname + `?id=${l.id}`;
                        let n = { tagName: "a", inner: "more", href: "", jsname: false }

                        b.add("action-ls");
                        for (const i of [{ inner: "View", href: "" }, { inner: "Setting", href: "&_request_type=c7b4e436-ab36-4a93-834-565159552bdc" },]) {
                            let href = g + i.href;
                            let edit = b.create({ ...n, ...i, href });
                            edit.event.on(e => r.navigate(edit.href));
                            b.create("boader", "|");
                        }

                        b.create(n).event.on(function (e) {
                            d = $.menuexitue(e);
                            d.executed([
                                { icon: 'ice_share', name: 'Share', event: () => (getLinkWimdow(`${location.origin}/exam?join=${l.code}`), true) },
                                { icon: 'ic_copy', name: 'Copy Id', event: () => ($.copy(l.code, `${l.code} : Copy Successful`).then(e => $.message(e)), true) },
                                { icon: 'ic_add_profile', name: 'Add Student', event: () => (addRequestStudentsInExam(null, l.code), true) },
                                { icon: 'ic_delete', name: 'Delete', event: () => dc(c => req([[300, [203, ["dExam", [l.timestamp, l.isPublish], l.code]]]], e => (e.status === true && container.closest(`#${l.id}`)?.remove(), c())) && false) }
                            ])
                        });
                        return container
                    }
                    if ("subject" == e) {
                        const c = $.create("width");
                        for (const i of Array.from(new Set(Object.values(l.details || {}).map(([, i]) => i)))) {
                            c.children.length >= 1 && c.create.span(null, ", ");
                            c.create.span(null, i);
                        }
                        return c
                    }
                    if ("totalTime" == e) return $.create("width", `${v} Min`);
                }
            });
            T001.append(Ma(tableElement));
        }

        let f = a.is("error"), route = a.is("route");
        if (f && $.message(f, 4000)) return r.homepage(this);
        if (route == "list") {
            let d = {
                list: a.is("list"),
                results: a.is("results"),
                paginators: a.is("paginators")
            }
            ES.$list.add(gp(), d);
            ls(d);
        }
        if (route == "examListSession") {
            examListSession(a.is("query"), con);
        }
    })
    listen(114, function (a, b, c, d) {
        if (a.submitExame == true) {
            const [pop, container, ti] = getWin(a.title, 'IN035 ', e => true);
            ti.css({ padding: "10px 14px 0" });
            for (const item of a.desc) {
                container.create.p(null, item)
            }
        }
        if (a.message) {
            binding(200, a.title, a.message, () => r.deleteAll())
        }

        if (a.status == "open") {
            var ws, [pop, container] = getWin(null, 'T042', e => {
                r.delete("join");
                ws?.close && ws?.close();
            });
            const Nt = function (e, ws) {
                if ([2, 3, 4].includes(e.statusCode) && e.joinLink) {
                    $.message(e.infoMessage);
                    ws?.close && ws?.close();
                    r.navigate(e.joinLink);
                    pop.close();
                    return true
                }
            }
            ES.pop = pop;
            pop.header.p.set('style', null)
            container.create.div(null).addIcon('loader_2')
            container.create.strong("teacherName", `Instructor : ${a.teacherName}`)
            container.create.h2('titles', `Exam Name : ${a.exam_name}`);
            container.create('mass', a.message);
            if (!Nt(a)) {
                ws = doJoine(a.connect_key);
                let wsf = ws.finish;
                ws.finish = function (e) {
                    wsf(e); Nt(e, ws);
                }
            }
        }
        if (a.status == "close" && a.content) {
            let bind = ES.get(116);
            typeof bind == "function" && (bind(a), r.deleteAll());

        }
    })
    listen(115, function (a, b, c, d) {
        function MCQ(callback) {
            let container = initializeContainer('F0046');
            callback(container, a, ES);
        }

        if (a.requestTimeout === true) {
            ES.ws.close();
            $.message("Request Time Out, Please Try Agen")
        }
        if (a.code) {
            $.loader(true);
            $.require("widgets/exams", MCQ).css();
        };
    })
    listen(122, function (a, b, c, d) {

        function MCQ(callback) {
            let container = initializeContainer('F0046');
            callback(container, a, ES);
        }

        $.loader(true);

        // Populate member session info
        ES.pop && ES.pop.close();
        $.require("widgets/exams", MCQ).css();

    })
    listen(116, function (a, b, c, d) {
        a.session == "close" && ES.ws?.close();
        return a.content && binding(200, a.content.title, a.content.desc, () => {
            a.index
                ? r.navigate('/exam')
                : r.deleteAll()

            // a.content.action == "fe40dt" && r.deleteAll()
        })
    })
    listen(117, function (a, b, c, d) {
        if (a.id) {
            console.warn("Connecting to exam with ID:", a, ES.ws);
            return activateWebSocket("exam/attach/q=" + getHexKey(a.id, a.connect_key, a.session_key))
        }
    })
    listen(118, function (a, b, c, d) {
        let count = 0;
        function updateCountdown() {
            const formatted = getCountdown(a.start)
            const bind = ES.get(116);
            if (typeof bind === "function" && !U) {

                U = bind({ content: a.content })
            };

            if (!U.formatted) U.formatted = (U.container || U).create.p(null, formatted);
            U.formatted.in(formatted, null);

            if (++count > 10 && ES.ws?.export) {
                ES.ws.export({ check: true });
                count = 0;
            }
        }

        updateCountdown();
        if (T) clearInterval(T);
        T = setInterval(updateCountdown, 1000);
    })
    listen(119, function (a, b, c, d) {
        if (a.endTime && ES.storage)
            ES.storage.update("expiry", a.endTime)
    })
    listen(121, function (a, b, c, d) {
        let con = initializeContainer('T034 T005');
        const openWindow = function (a) {
            window.open(
                a,
                "_blank",
                "noopener,noreferrer"
            );
            return true;
        };

        const m = con.create("T006"),
            p = m.create("card"),
            h = p.create("cheader"),
            i = h.create("image"),
            g = h.create("IN0104 info");

        const x = m.create("card");
        const y = m.create("card");
        const z = (n, i) => {
            let j = n.create("T008");
            j.create.strong("center", String(i.a));
            j.create.span("center", i.b);
        }
        const f = (p, d) => {
            var o = p.create("T007");
            for (const i of d)
                z(o, i);
        }


        i.create.img({ src: a.student.img, height: 100, width: 100 })
        g.create.h4(null, a.student.name), g.create.span(null, a.student.username), p.create("bio", a.student.biography)

        f(p, [
            { a: a.all_time, b: "Attempts" },
            { a: a.join, b: "Join" },
            { a: a.self, b: "Self" },
        ])

        var t = p.create.span(null);
        t.create.strong(null, "Account Type : "),
            t.create.span(null, a.account_type),
            t.create.span(null, " | "),
            t.create.a({ inner: "Upgrade", href: null })


        x.create.h3(null, "Exam Attempt Statistics");
        x.create.span(null, "Track exam attempts over different time periods.");

        f(x, [
            { b: "Today", a: a.today },
            { b: "This Month", a: a.this_month },
            { b: "This Year", a: a.this_year },
            { b: "All Time", a: a.all_time },
        ])

        x.create.div(null).create.span(null, "Track exam attempts over different time periods.")
            .create.a(null, "Create New").event.on(e => openWindow("/exam/create"));

        con = con.create("T009 card")
        const header = {
            "sno": "No.",
            exam_name: "Exame Name",
            subject: "Subject",
            category: "Category",
            timing: "Timing",
            timestamp: "Timestamp",
            option: " "
        };
        const ch = con.create.header(null);
        const bg = ch.create("T010");


        const ac = (n) => {
            const te = createJsonTable({
                header, callBack: function (e, i, v) {
                    if (e == "exam_name" && v.examinant) {
                        const co = $.create("width");
                        co.create.h3(null, i), co.create.span(null, $.create.strong(null, "Examinant -")).css({ fontSize: "small" }).create.span(null, v.examinant)
                        return co
                    }
                }
            });
            con.append(te);
            for (const item of a[n] || []) {
                const { exam_name, subject, category, examinant, timing, rus_link } = item;
                if (!exam_name)
                    continue;

                const option = item.is_submitted == false
                    ? [{ icon: 'ic_link', name: 'Continue', event: e => openWindow(`/exam?hx=${item.key}`) }]
                    : [{ icon: 'ic_result', name: 'Get Result', event: e => openWindow(`/exam/result/${rus_link}`) }, { icon: 'ic_list', name: 'Get Ans Seet', event: e => openWindow(`/exam/answer_sheet/${rus_link}`) }]

                !examinant && option.push({
                    icon: 'ice_trash-delete', name: 'Delete', event: function (e, v) {
                        return this.loader(true) && dc((c) => sendReq({ reqRoute: "practiceDelete", payload: [item.key, a.student.roll_no] }, e => e.status === true && (te.choose(item.rus_no, true)?.remove(), v(), c())) && !c)
                    }
                })
                te.addRow({ ...item, exam_name, timing, subject: subject.join(",<br>"), category: category.join(",<br>"), timestamp: formatTimestamp(item.timestamp), option }).add("submitted", item.is_submitted).add("id", item.rus_no);
            }
        }


        a.pagination?.length != 1 && ch.create.div(null, Paginator(a.pagination || []));
        for (const i of ["Practice", "Examiner Conducted"]) {
            let b = bg.create.button(null, i)
                , u = i.toLocaleLowerCase().replaceAll(" ", "_");

            if (!r.get("ls"))
                r.set("ls", u, false);

            r.get("ls") == u &&
                (b.add("active", true), ac(u))
            b.event.on(() => (r.set("page", 1, false), r.set("ls", u)));
        }
        // bg.create.span(null, "|")
        // bg.create.button(null, "Create New")
    })

    listen(200, function (a, b, c, d) {
        let h = b;
        if (Array.isArray(b)) {
            h = $.create();
            for (const i of b || [])
                typeof i === "string"
                    ? h.create.p(null, i)
                    : h.create(i);
        }

        return $.alert(a, h, c);
    })



    r.onChange(e => applyBind.call(ES, 800, null))
    applyBind.call(ES, 800, null);
    console.log(r);


    const module = $.module.list ??= FlEXMAP();
    module.add("createTest", function createObject(a) {
        const getActionMethod = (string) => this.get(string) == "True";

        // This function builds and displays the popup UI
        function showPopup(strings) {

            if (!getActionMethod("data-controller")) {
                r.path(strings.hrefPracticeTest);
                return true;
            }

            const popup = $.popup("Create Examination Environment");
            const container = popup.create("T030");

            const options = [
                { title: strings.buttonCreateRoom, desc: strings.descCreateRoom, href: strings.hrefCreateRoom },
                { title: strings.buttonPracticeTest, desc: strings.descPracticeTest, href: strings.hrefPracticeTest }
            ];

            for (const opt of options) {
                const button = container.create.a("T031");
                const content = button.create("inten");

                button.href = opt.href;
                button.add("jsname", false);
                content.create.h2("box-title", opt.title);
                content.create.p("box-sedc", opt.desc);

                button
                    .add("button")
                    .event.on(e => popup.close());
            }
        }

        return loadForm(function (m, n) {
            return showPopup.call(m, $.require.usepass.string)
        })
    });

    module.add("testList", function testList($) {

        var container = $("T001");
        container.clear();
        var header = container.create("header");
        header.create.h2("session-title", "Test List");
        header.create({
            tagName: "a",
            href: "/exam/r/create",
            class: "button",
            jsname: "false",
            inner: "Create new test r"
        });
    })

    $.event('joincode', function (code) {
        let join = $('join'), ac = function () {
            let codes = code.value.replace(/\s/g, "");
            codes.length !== 9 || !Number(codes)
                ? $.message('Plese vilad code')
                : eventLogger(e => r.set('join', codes));
        };
        join.event.on(ac), code.event.keyup(e => {
            code.value ? join.add('active') : join.removed('active');
            e.keyCode == 13 && ac.call(code, e);
        })

    }, true)

})

