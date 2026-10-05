
/**
 * @file worker.js
 * @desc Auto-scaling & core worker modules logic.
 * @copyright (c) 2026 Your Name / Company. All rights reserved.
 */

$.define("worker", function Worker() {
    "use strict";
    const S = $.setting(), { F } = $.getFunction(), m = $.module.list ??= $(function Worker() { return this; });
    m.add(function navigation(op, cb) {
        $.require("sess/navigation", function navigation(nav) {
            nav = nav(); op = nav.export(op);
            F(op) && op(cb);
            return cb !== true && op ? op : nav;
        });
    });

    m.add(function importData(p, q, cb) {
        $.callback ??= r => cb(r);
        $.fch(p, q);
        return this;
    });

    m.add(function likes() {
        let d = this.get("aria-label"), lc = this.choose("like-count"), l = +lc.get("inner");
        let opt = () => this.isclass(d) ? "like" : "removelike";
        let up = () => {
            opt() == "like" ? (this.removed(d), l++) : (this.add(d), l--);
            lc.in(String(l), true);
        };
        let err = a => {
            up();
            let p = $.popup(), box = p.create("IN092");
            p.closeButton.remove(); box.addIcon("help"); box.create.h2("IN093", "Sorry!"); box.create.p("alert-massags", a.details || "Internal Server Error");
            let IN094 = box.create("IN094")
            for (const [n, f] of Object.entries({ Login: () => (p.close(), $("login").click()), Cancel: () => (p.close(), this.loader(false)) }))
                IN094.create.button("button", n).event.on(f);
        };

        up();
        let o = opt(), v = new FormData(), ars = $.apirequest("feedback");
        ars.progress = () => this.loader(true);
        ars.finish = a => {
            console.log(a);

            this.loader(false);
            a.export(o) && (up(), $.message("Like is not update :("));
        };
        ars.error = a => a.meta.error && err(a.meta.error);

        v.append("log_", $.makeid(57));
        v.append("opg_", $.makeid(o == "like" ? 20 : 25));
        ars.send(v);
    });

    m.add(function subMenu() {
        m.navigation("subMenu", c => {
            c.css({ right: this.get().side.right - 50 });
            $.windows(null, { container: c, functions: () => c.remove() }, false);
        });
    });

    m.add(function accountWindow() {
        const b = this;
        b.loader(true);
        $.require("sess/account", function Account(acc) {
            b.loader(false);
            let ev = $(function Event() { return this; });
            let c = $.create("account fixed");
            let close = () => c.remove();
            c.append(acc(ev));

            ev.add("close", close);
            ev.add("logout", (a, b) => {
                let n = e => (close(), S.logout(e));
                +b <= 1 ? n("th") : $.menuexitue(a).executed([
                    { icon: 'ice_logout', name: 'This device only', event: () => n(false) },
                    { icon: 'ice_logout', name: 'All other devices', event: () => n(true) }
                ]);
            });

            document.body.append(c);
            c.css({ right: b.get().side.right - 6 });
            $.windows(null, { container: c, functions: close }, false);
        });
    });

    return m;
});


// $.define(function Worker(modules) {

//     module.add(function likes(callback) {

//         var details = this.get("aria-label");
//         var like_count = this.choose("like-count");
//         var like = Number(like_count.get("inner"));

//         var get_option = (a, b) => {
//             return this.isclass(details)
//                 ? "like"
//                 : "removelike";
//         }
//         var update_button = (a, b) => {
//             get_option() == "like"
//                 ? (this.removed(details), like++)
//                 : (this.add(details), like--);
//             like_count.in(String(like), true);
//         }
//         var login_error = (a, b) => {
//             update_button()
//             let popup = $.popup();
//             let IN092 = popup.create("IN092");
//             popup.closeButton.remove();
//             IN092.addIcon("help");
//             IN092.create.h2("IN093", "Sorry!")
//             IN092.create.p("alert-massags", a.is("message") || "Internal Server Error")
//             let button = IN092.create("IN094");
//             button.create.button("button", "Login").event.on(function () { popup.close(), $("login").click() });
//             button.create.button("button", "Cancel").event.on(e => { popup.close(), this.loader(false) });
//         }

//         update_button();

//         var value = new FormData();
//         var option = get_option();

//         let ars = $.apirequest("feedback");
//         ars.progress = (a, b) => this.loader(true);
//         ars.finish = (a, b) => {
//             this.loader(false)
//             if (a.export(option)) {
//                 update_button();
//                 $.message("Like is not update :(");
//             }
//         };
//         ars.error = (a, b) => {
//             return a.is("error_code") == "Xe022524"
//                 ? login_error(a) : null;
//         };

//         value.append("log_", $.makeid(57))
//         value.append("opg_", $.makeid(option == "like" ? 20 : 25))
//         ars.send(value);
//     });

// });



// function card(a) {
//     const p = $.popup("Logout");
//     const c = p.create.div("thecontainer")
//     const b = p.create.div("DIS01 buttondf")

//     p.add("logout-pop")

//     for (const n of a) {

//         const [login_time, logout_time, active, divice, brouser, divice_tipe] = n

//         console.log(login_time, logout_time, active, divice, brouser, divice_tipe);

//         const a = c.create("DIS01 boc");
//         const i = a.create("card-icon");
//         const m = a.create("card-info");

//         i.addIcon("ib_shopping")

//         m.create.h3("dateda-name", `${divice} • ${brouser}`)
//         const g = m.create("dateda-name")


//         const l = g.create.div()
//         l.create.span(null, "Login time :")
//         l.create.span(null, String(login_time))

//         g.create.div(null, "Aive")
//     }
//     b.create.button(null, "Logout All Divice")
//     b.create.button(null, "Logout This Divice")

// }

// card([
//     ["25/52/2025", "", "active", "Windows", "Opera", "0010"],
//     ["25/52/2025", "", "active", "Windows", "Opera", "0010"]
// ])


































function markdownToHtml(text) {
    // Convert headings
    text = text.replace("<p></p>", '');
    text = text.replace(/##### (.+)/g, '<h5>$1</h5>');
    text = text.replace(/#### (.+)/g, '<h4>$1</h4>');
    text = text.replace(/### (.+)/g, '<h3>$1</h3>');
    text = text.replace(/## (.+)/g, '<h2>$1</h2>');

    // Convert bold text
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a rel="noopener" target="_new" href="$2">$1</a>');

    // Convert code blocks
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Convert lists
    text = text.replace(/- (.+)/g, '<ul><li>$1</li></ul>');

    // Convert paragraphs and ensure proper spacing
    text = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');

    // Wrap in paragraphs
    text = '<p>' + text.replace(/<\/ul>\s*<ul>/g, '</p><p>').replace(/<\/p>\s*<p>/g, '</p><p>') + '</p>';

    return text;
}

function typeText(element, text, speed = 50) {
    let index = 0;
    innerHTML = "";

    function type() {
        if (index < text.length) {
            innerHTML += text[index];
            index++;
            element.innerHTML = innerHTML
            setTimeout(type, speed);

        }
    }

    type();
}