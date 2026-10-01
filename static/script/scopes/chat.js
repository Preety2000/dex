// © 2025 Your MyApplication. All rights reserved.
// This script is licensed under the MIT License.


// Do not remove this notice.
$(function $Chat(r, a, b, c, d, e, f, g, h, i, j) {
    const { AUTH_TOKEN } = $.getClass();
    const chat = this, E = fn => this.add(fn), { SEOPES, F, S, N, B, A, mapx } = $.getFunction(), { MAPX } = $.getClass();

    const ks = (e = $.cookie("_cf_iNd", 360, 1), s = (d) => e.insert(AUTH_TOKEN.encode(d)), r = v => v(AUTH_TOKEN.decode(e.get()) || {})) => ({
        set: (i, v) => r(d => (d[i] = v, s(d))),
        res: i => r(d => i && (delete d[i], s(d)) || e.remove()),
        get: i => r(d => i ? Object.prototype.hasOwnProperty.call(d, i) ? d[i] : null : d)
    });
    const uscd = ks();

    // Extend the MessageList class
    class MAPXS extends MAPX {
        constructor() {
            super();
        }
        has(key) {
            return Object.prototype.hasOwnProperty.call(this, key);
        }
        changeKey(a, b) {
            if (a in this) {
                this[b] = this[a];
                delete this[a];
            }
        }
    }


    function timeAgo(ms) {
        if (!ms) return ms;
        const d = new Date(ms), now = new Date();
        const df = Math.floor((new Date(now.getFullYear(), now.getMonth(), now.getDate()) - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 86400000);

        const time = () => {
            let h = d.getHours(), m = d.getMinutes(), a = h >= 12 ? 'PM' : 'AM';
            h = h % 12 || 12;
            return `${h}:${m.toString().padStart(2, '0')} ${a}`;
        };

        if (df === 0) return time();
        if (df === 1) return `Yesterday ${time()}`;
        if (df < 7) return d.toLocaleDateString(undefined, { weekday: 'long' });
        if (df < 30) return `${Math.floor(df / 7)} week${df < 14 ? '' : 's'} ago`;
        if (df < 365) return `${Math.floor(df / 30)} month${df < 60 ? '' : 's'} ago`;
        return `${Math.floor(df / 365)} year${df < 730 ? '' : 's'} ago`;
    }

    chat.chatBoxList ??= new MAPXS();
    chat.messageList ??= new MAPXS();
    chat.messageStatusList ??= new MAPXS();



    E(function updateTestForms(action) {
        console.log(action);
    });

    const rs = $.apirequest("chat/query")
    r = $.socket("chat?t=" + Date.now())
    const mx = new MAPXS();
    const st = new MAPXS();
    var userConversionsLists = new MAPXS();

    var chat_view = $("chat-view");
    var conv_list = $("conv-list");
    var chat_window = $("window");

    const fs = function (b, c) {
        b.scrollTop = c && c.choose('message--send') ?
            c.scrollHeight :
            b.scrollHeight;
    }
    const ft = function (a, b, c, d) {
        b = $.create("status" + (S(b) ? " " + b : ""));
        b.create("figure __avatar").create({
            tagName: "img",
            src: a.img
        })
        c = b.create.div("meta-see");
        b.add(a.__m)
        d = c.create("meta-see-head DIS00")
        d.create("meta__name", a.name);
        nu.call(d, a);
        return [b, c];
    }
    const gt = function (a, b, c, d, e) {
        [b, c] = ft(a, "cursor");
        d = c.create("meta__sub--dark");
        if (e = a.last_message) {
            d.create("sub--dark", e.__ms)
        }
        else { d.create("sub--dark", a.userName) }

        d.create("sub-status");
        return b;
    }
    const ht = function (a, b, c, d) {
        [b, c] = ft(a);
        d = c.create("__group");
        for (const i of ["Confirm", "Remove"]) {
            let g = i.toLocaleLowerCase().replaceAll(' ', '-'), h = d.create.button(g, i);
            h.event.on(e => it.call(h, g, a.id, d));
        }
        return b;
    }
    const it = function (a, b, c, d) {
        c.clear();
        ga(null, { a, b, action: "relationships" });
        // ga({ a, b, action: "relationships" });
        if (a == 'message') {
            console.log(a);
        }
        c.create("__sub", { confirm: "You are now friends", remove: "Request remove", request: "Your request send" }[a]);
    }
    const jt = function (a, b, c, d) {
        [b, c] = ft(a, "cursor");
        d = c.create("__group");
        d.create("__bio", a.userName)
        return b;
    }
    const ga = function (a, b, c, d) {
        // d = {
        //     ids: [, chat.aid],
        //     chatBox: chat.aci, ...a
        // }
        // console.log(chat.aci, [a, b]);


        d = [a, [chat.aci, chat.aid], b, c]
        console.error('Send message query', d);
        return r.export(d);
    }

    const gs = function (a, b, c, d, e) {
        if (b = $.weres('[data-timestamp]').find(e => e.get("data-timestamp") == a.timestamp)) {
            c = b.create("dartr DIS00");
            e = c.create('message-time', timeAgo(Number(a.timestamp)));
            d = c.create("wamere");
            chat.messageStatusList.add(a.massid, d)
            ad(a);
        };
    }
    const ac = function (a, b, c, d, e) {
        c = a.create("acbulo");
        c.create('button').addIcon('errow_down');
        c.event.on(function (e) {
            d = $.menuexitue(e)
            d.executed(b)
        })
        a.event.mouseenter(function () {
            c.style.opacity = 1
        })
        a.event.mouseleave(function () {
            e = a => c.style.opacity = 0;
            d?.active !== true && e()
            d && (d.bind = e);
        })
    }
    const sendbox = function (e, i, f, g, h) {
        let cf = $.create("cf send");
        cf.hold(function () {
            $.message("hold 2")

        })
        let d = cf.create("message--send");
        const { __ms, timestamp, massid } = i;



        var DIS02, elm = f === true ? e.firstElementChild : e.lastElementChild;
        if (elm && elm.isclass('send') && (DIS02 = elm.choose('DIS02'))) { }
        else {
            DIS02 = d.create("DIS02");
            if (f === true) { e.in(cf, 0); }
            else { e.in(cf) }
        }

        let m = $.create("message__bubble--send");
        if (f === true) { DIS02.in(m, 0); }
        else { DIS02.in(m) }


        i.massid ??= $.getid();
        chat.messageList.add(i.massid, d);
        d.add('id', i.massid)

        m.create.span('display-message', __ms)
        m.add("data-timestamp", timestamp)
        gs(i)
        d.create("message__avatar").create({ tagName: "img", src: "{{auth_session.img or 'icon/member.png'}}?size=50x50" })

        fs(e, cf);
        ac(m, [
            { name: 'Delete for averyone', event: e => { ga("remove", [2, __ms, timestamp]); return true } },
            { name: 'Delete foe me', event: e => { ga("remove", [1, __ms, timestamp]); return true } },
            // { name: 'Delete for averyone', event: e => { ga({ __ms, timestamp, YatraLine: 'remove', act: 2 }); return true } },
            // { name: 'Delete foe me', event: e => { ga({ __ms, timestamp, YatraLine: 'remove', act: 1 }); return true } },
            { name: 'Edite', event: function () { console.log(i.__ms); } },
            { name: 'Cancel', event: false },
        ])
    }
    const mt = function (i) {
        let a, b, c, d, e, f, g, h, [n, item] = userConversionsLists.get(i.__m) || [];
        item ||= i;

        if (chat.aci == item.chatBox) {
            return;
        }


        a = $.create('status')
        b = a.create('figure __avatar')
        c = a.create('middel width')
        d = a.create('right')
        e = c.create("meta-see")
        f = d.create("button")
        chat_view.header = a;
        e.create("meta__name", item.name)
        b.create({ tagName: "img", title: "avatar", src: item.img })
        nu.call(e, item);

        a.__m = item.__m;
        chat.activeChatBox = a;
        f.addIcon("logo_main")
        f.event.on(function (e, d) {
            d = $.menuexitue(e)
            d.executed([
                { name: 'Search', event: false },
                { name: 'Mute notifactions', event: false },
                { name: 'Report', event: false },
                { name: 'Block', event: false },
                {
                    name: 'Clear chat', event: e => {
                        ga('clear', [1, item.chatBox]);
                        return true
                    }
                },
                { name: 'Export chat', event: false },
                { name: 'Cancel', event: false }
            ])
        })
        chat_view.clear()
        chat_view.create.header("chat-view__header", a);
        var session = chat_view.create("session message-view");
        session.session = true;
        chat.chatBoxList.add(item.chatBox, session)
        chat.aci = item.chatBox, session.add("id", chat.aci);

        if (item.acountType == 2) {
            console.log(item.acountType, session);

            let info = session.create("chat-info");
            info.create("logo").addIcon("ic_private")
            info.create.h2("hedline", 'This account is private!')
            info.create("desc", "Hi there! I came across your profile and found it really interesting. I’d love to connect and follow your content. If you're okay with it, please accept my request. Looking forward to seeing more from you. Thanks and have a great day!")
            info.create.button("button", "Send Request")
            return false
        }
        chat.aui = item.img;
        chat.aid = item.id;


        var footer = chat_view.create.footer("message-footer DIS01")
        var inpuC = footer.create("width relative")
        var input = inpuC.create({
            tagName: "input",
            name: "message",
            placeholder: "Type message..."
        });
        let sb = inpuC.create("send-message").create.button("button");
        var ht = function (input) {
            let message = { __ms: input.value, timestamp: Date.now() }
            sendbox(session, message);
            ga("sendmessage", message);
            ast(1);
            input.value = "";
            fs(session);
            return true;
        }
        let sto, ast = function (cst) {
            sto = undefined;
            ga("ons", 2);
        };
        sb.addIcon("ic_send");
        sb.event.on(() => ht(input));
        sb.set('disabled', true);
        input.event.keyup(function (e) {
            let t = Date.now(), up = function () {
                if (Math.abs(t - item.__t) >= 5000) {
                    item.__t = t;
                    return true;
                }
            };

            this.value.trim()
                ? sb.removeAttribute('disabled')
                : sb.set('disabled', true)
            if (e.keyCode === 13 && this.value.trim()) ht(input) && sb.set('disabled', true);

            clearTimeout(sto);
            if (up() || typeof sto === "undefined" && e.keyCode !== 13) ast(2);
            sto = setTimeout(() => ast(1), 2000);
        });

        session.event.scroll(function (e) {
            if (session.scrollTop == 0 && session.lasstMassage) {
                if (!chat.massageLoder) {
                    chat.massageLoder = $.create('cf');
                    chat.massageLoder.addIcon('ic_loader');
                }
                session.in(chat.massageLoder, 0);
                ga("get", [session.lasstMassage.massid, session.lasstMassage.timestamp, 10])
            }
        });

        console.log(chat.get(item.chatBox));


        if ((g = chat.get(item.chatBox)) && (j = mx.get(5004))) {
            let [a, b, c] = g || []
            j(a, b, c);
        }
        else {
            ga("get")
        }

    }
    const nu = function (a, b) {
        const f = 'meta_last_time'
            , t = function (a) {
                const g = ['online', 'typing...'][a._s - 1];
                return g ? $.create('online', g) : timeAgo(+a.__t)
            }
            , g = function (a) {
                const el = this.choose(f);
                if (el) el.in(t(a), true);
            };

        b === true ? g.call(this, a) : this.create(f, t(a));
        return g;
    };
    const mu = function (a, b, c, d) {
        c = chat.activeChatBox;
        g = nu.call(this, a, true);
        if (c && c.__m == a.__m) {
            g.call(c, a)
        }
    }
    const ab = function (a, b, c, d) {
        c = 0, userConversionsLists = new MAPXS();
        conv_list.clear();
        for (const i of a) {
            const f = b(i), g = conv_list.create("cp224", f);
            userConversionsLists.add(i.__m, [g, i]), g.css({ transform: `translateY(${c}px)` }), g.add('jsname', 'MlHeYt')
            f.event.on(e => mt(i)), mu.call(g, i);
            c = c + 64;
        }
        return userConversionsLists;
    }
    const ad = function (a, b, c, d) {
        b = chat.messageStatusList.get(a.massid), c = 'ic_msg_dblcheck';
        b?.clear()
        if (a.status === 2 && b) { b.addIcon(c), b.add("reads"); }
        else if (a.status === 1 && b) { b.addIcon(c); }
        else if (b) { b.addIcon("ic_msg_check"); }
    }
    mx.add(5001, function (e, f, g, h) {
        g = ab(e, gt);
    })
    mx.add(5002, function (e, f, g, h) {
        g = ab(e, ht);
    })
    mx.add(5003, function (e, f, g, h) {
        g = ab(e, jt);
        console.log('5003', g);
    })
    var resavemessageInsurt = function (a, b, c, d) {
        let { __ms, timestamp, massid } = b;
        let cf = $.create("cf resave");
        d = cf.create("message");
        cf.hold(function () {
            $.message("hold 1")
        })
        d.create("message__avatar").create({
            tagName: "img",
            src: chat.aui
        })

        var DIS02, elm = c === true ? a.firstElementChild : a.lastElementChild;
        if (elm && elm.isclass('resave') && (DIS02 = elm.choose('DIS02'))) {
            console.log(elm, DIS02);
        }
        else {
            DIS02 = d.create("DIS02");
            if (c === true) { a.in(cf, 0); }
            else { a.in(cf) }
        }

        let m = $.create("message__bubble")
        if (c === true) { DIS02.in(m, 0); }
        else { DIS02.in(m) }


        m.create.span('display-message', __ms), m.create('message-time', timeAgo(Number(timestamp)))
        chat.messageList.add(massid, d);
        d.add("id", massid);

        fs(a, cf);
        ac(m, [
            { name: 'Delete', event: e => { ga("remove", [__ms, timestamp]); return true } },
            { name: 'Cancel', event: false }
        ])

        if (b.status != 2) {
            ga("messageUpdated", massid);
        }
    }
    mx.add(5004, function (e, f, g, h) {
        if (!f) return;
        g = f.is('chatBox');

        console.log(g);


        chat.massageLoder?.remove()
        if (g && (g = $(g, true))) {
            for (const item of e || []) {
                if (item.__d == "send") sendbox(g, item, true);
                if (item.__d == "resave") resavemessageInsurt(g, item, true);
                g.lasstMassage = item;
            }
        }
        if (!chat.get(chat.aci))
            chat.add(chat.aci, [e, f]);
    })
    mx.add(5005, function (a, b, c, d) {
        if (a.chatBox && (b = chat.chatBoxList.get(a.chatBox))) {
            b.clear();
        }
    })
    mx.add(400, function (a, b, c, d) {
        for (const i of a) {
            const b = userConversionsLists.get(i.__m);
            if (b) mu.call(b[0], b[1] = { ...b[1], ...i });
        }
    })
    mx.add(401, function (a, b, c, d) {
        const [e, i] = userConversionsLists.get(a.__n) || [];
        if (chat.messageList.get(a.omassid)) {
            chat.messageList.changeKey(a.omassid, a.massid)
            chat.messageStatusList.changeKey(a.omassid, a.massid)
        }
        chat.massageLoder?.remove()
        if (b = chat.chatBoxList.get(a.chatBox)) {
            if (a.__d == 'resave' && b.session === true) {
                resavemessageInsurt(b, a);
            }
            if (a.omassid && a.__d == 'send') {
                ad(a)
            }
            b.lasstMassage = a;
        }


        if (d = e?.choose('sub--dark')) {
            d.in(a.__ms, true);
        }
    })
    mx.add(402, function (a, b, c, d) {
        b = chat.messageList.get(a.massid);
        if (b) {
            b.remove();
        }

    })
    mx.add(404, function (a, b, c, d) {
        ad(a);
    })
    mx.add(405, function (a, b, c, d) {
        const [e, i] = userConversionsLists.get(a.__n) || [];
        if (d = e?.choose('sub--dark')) {
            d.in(i.userName, true);
        }

        if (a.chatBox && (b = chat.chatBoxList.get(a.chatBox))) {
            b.clear();
            if (chat.get(a.chatBox)) {
                chat.add(a.chatBox, [])
            }
        }
    })
    mx.add(406, function (a, b, c, d) {
        chat.massageLoder?.remove();
        if (b = chat.chatBoxList.get(a.chatBox)) {
            b.lasstMassage = null;
        }
    })
    r.finish = async function (data) {
        console.log(data);
        let __ac = data.is("__ac");

        for (var [bimd, vall] of Object.entries(__ac || {})) {
            if ((bimd = mx.get(Number(bimd))) && F(bimd)) {
                bimd(vall, data)
            }
        }
        console.warn("Message from server realtime:", JSON.stringify(data));
    }


    const bg = $("IN094"),
        wt = a => rs.send([[400, [a, [$.getKey(203), 203], null]]], e => {
            g = e.getResponseObject();

            for (let [k, v] of Object.entries(g.is("__ac") || {}))
                (k = mx.get(+k)) && F(k) && k(v);

            $.loader(false);
        }),
        cln = (a, b) => {
            const e = b ? uscd.res("cln", a) : uscd.get("cln");
            return e == null || b ? !!uscd.set("cln", a) : e == a;
        },
        df = (a, b, c = "active") => {
            for (const e of bg.childrens || [])
                e[e.id == a ? "add" : "removed"](c),
                    e.id == a && !b && cln(a, true);

            wt.call(bg, a);
        };

    for (const i of ["Chats", "Request", "Search"]) {
        const a = i.toLocaleLowerCase()
            , b = bg.create.button(null, i);

        b.id = a, b.event.on(() => df(a)), cln(a) === true && df(a, true);
    }

    $.loader(true);
    $.DOMContentLoaded(function () {
        ;
    })

    $.scopes ??= SEOPES();
    $.scopes.add("Chat", this);
    if ($('mobile')) {
        $.module.list ??= FlEXMAP();
        var listBox = $('conv-list-view');
        $.module.list.add(function MlHeYt() {
            if ($('mobile')) {
                listBox.add('hidden');
                chat_view.add('chatactive');
                if (!chat_view.header.choose('back-button')) {
                    let back_button = $.create.button('back-button');
                    chat_view.header.in(back_button, 0);
                    back_button.addIcon('ice_arrow_left');
                    back_button.event.on(e => {
                        for (const [k, v] of Object.entries(chat.chatBoxList)) {
                            if (chat_view.choose(v.id, true)) {
                                v.session = false;
                            }
                        }
                        chat_view.removed('chatactive');
                        listBox.removed('hidden');
                    })
                }
            }
        })
    }
});

var x = setInterval(() => {
    $.socket("chats")
}, 1000);

clearInterval(x)






