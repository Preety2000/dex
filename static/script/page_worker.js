
$.define(function Worker(modules) {
    "use strict";
    const setting = $.setting();
    const { F, urlParts, FlEXMAP } = $.getFunction();
    $.module.list ??= FlEXMAP();
    const module = modules || $.module.list
    module.add(function navigation(opreter, callback) {
        $.require("widgets/navigation", function navigation(navigation) {
            navigation = navigation();
            opreter = navigation.export(opreter);
            if (F(opreter)) {
                opreter(callback)
            }
            return callback != true && opreter ? opreter : navigation;
        })
    });
    module.add(function importData(params, query, callback) {
        let reseve = function (response) {
            return callback(response)
        }
        if (!F($.callback)) {
            $.callback = reseve;
        }
        $.fch(params, query);
        return this
    });
    module.add(function likes(callback) {

        var details = this.get("aria-label");
        var like_count = this.choose("like-count");
        var like = Number(like_count.get("inner"));

        var get_option = (a, b) => {
            return this.isclass(details)
                ? "like"
                : "removelike";
        }
        var update_button = (a, b) => {
            get_option() == "like"
                ? (this.removed(details), like++)
                : (this.add(details), like--);
            like_count.in(String(like), true);
        }
        var login_error = (a, b) => {
            update_button()
            let popup = $.popup();
            let IN092 = popup.create("IN092");
            popup.closeButton.remove();
            IN092.addIcon("help");
            IN092.create.h2("IN093", "Sorry!")
            IN092.create.p("alert-massags", a.is("message") || "Internal Server Error")
            let button = IN092.create("IN094");
            button.create.button("button", "Login").event.on(function () { popup.close(), $("login").click() });
            button.create.button("button", "Cancel").event.on(e => { popup.close(), this.loader(false) });
        }

        update_button();

        var value = new FormData();
        var option = get_option();

        let ars = $.apirequest("feedback");
        ars.progress = (a, b) => this.loader(true);
        ars.finish = (a, b) => {
            this.loader(false)
            if (a.export(option)) {
                update_button();
                $.message("Like is not update :(");
            }
        };
        ars.error = (a, b) => {
            return a.is("error_code") == "Xe022524"
                ? login_error(a) : null;
        };

        value.append("log_", $.makeid(57))
        value.append("opg_", $.makeid(option == "like" ? 20 : 25))
        ars.send(value);
    });
    module.add(function subMenu(callback) {
        // Assume this code is inside a method or a function where `this` is defined
        const button = this;

        module.navigation("subMenu", function (container) {
            // Function to close and remove the menu
            const closeMenu = () => container.remove();

            // Position the containerbased on the button's position
            container.css({ right: button.get().side.right - 50 });

            // Set up an event listener to close the menu when a click outside occurs
            var win = $.windows(null, {
                container: container,
                functions: e => closeMenu()
            }, false);
        });

    });
    module.add(function accountWindow(callBack) {
        const button = this;
        button.loader(true);
        $.require("widgets/account", function Account(account) {
            button.loader(false);
            var event = $(function Event() {
                return this
            })
            var query = account(event)

            // Create the containerelement with specific CSS classes
            const container = $.create("account fixed");

            // Append the children of the parsed document's body to the container
            container.append(query)

            // Define a function to remove the container
            const closeMenu = () => container.remove();

            // Set up event listeners
            event.add("close", closeMenu);


            event.add("logout", (a, b) => {
                const n = e => (closeMenu(), setting.logout(e)); +b <= 1 ? n("th") : $.menuexitue(a).executed([
                    { icon: 'ice_logout', name: 'This device only', event: () => n(false) },
                    { icon: 'ice_logout', name: 'All other devices', event: () => n(true) },
                ]);
            }
            )
            // event.add("logout", () => setting.logout())

            // Append the containerto the document body
            document.body.append(container);

            // Set CSS styles for positioning
            container.css({ right: button.get().side.right - 6 });

            // Set up an event listener to close the menu when clicking outside
            var win = $.windows(null, {
                container: container,
                functions: e => closeMenu()
            }, false);


        });
    });


    console.log("okkkkk");

    return module
});



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