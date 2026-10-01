
$(function Setting(r) {
    var s = this, R = {}, l = $.module.list, { FlEXMAP, addString, getString, I, S, A, N, I, E, F, B } = $.getFunction();
    const setting = $.setting();
    var getpathname = function () {
        let arr = r.pathname.split("/");
        let meta = arr.filter(Boolean);

        return {
            resource: meta[0] || null,
            entity: meta[1] || null,
            detail: meta[2] || null
        };
    }
    var sa = function () {
        let bind = R[this];

        if (F(bind)) {
            settitle(this);
            return bind.call(this, r);
        }

        return s.error(this);
    }
    var api_route = function (a, b) {
        R[a] = b;
        return R;
    }

    const ElementHendler = new $(function ElementHendler() {
        var window = this;
        this.container = $("IN091");

        this.b_container_list = function (params, condition) {
            if (condition) {
                window.container.clear()
            }

            return window.container.create("b_container_list")
                .create("box-container")
                .add(params)
        }
        this.container_loged = function (params, condition) {
            if (!condition) {
                condition = $;
            }
            condition = condition.create("container_loged").add(params);
            return {
                "main": condition.create("main_container"),
                "aside": condition.create("aside_container"),
            }
        }

        return this;
    });

    var icons, $icons = $.icons();

    var boxs = function (a) {
        let b = $.create("b_container_list");
        let c = b.create("box-container");

        E(a) && a.in(b);
        return [b, c];
    }
    var icon = function (a, b, c) {
        let uri = null;
        const tag = c ? (uri = c, "a") : "icon";
        const el = (a || $).create(tag);
        el.add("icon");
        el.in(icons[b]);
        if (uri) el.href = uri;
        return el;
    };
    var tolbar = function (a, b) {
        let t = N(b.title) ? s.getTitle(b.title) : b.title;
        a = (a || query).create("padding-ten-twenty space-between width");
        let c = a.create("DIS01")
        c.in(icon(null, b.icon))
        c.create("s-tital", t);

        a.in(icon(null, b.iconCode || 5009, b.uri).add("button"));
        return a;
    };
    var colloun = function (a, b, c) {
        a = a || query;
        a = a.create("colloun")
        b = a.create("s-tital", b)
        c = a.create("sm-tital", c)
        return [a, b, c];
    }
    var input_update = function (a, b, c) {
        a = a || $;
        a = a.create("padding-ten-twenty space-between width");
        a = a.create("input-box DIS01");
        let q
            , cr = $.create
            , ee = "edit_enable"
            , d = a.create.label("label", b.title)
            , ib = a.create("inputs")
            , e = ib.create.span("input-name")
            , f = ib.create.a("action")
            , i = cr.input("input")
            , t = cr.textarea("textarea")
            , r = cr.span("error")
            , show_value = function () {
                ib.clear();
                e.in(b.value, !0)
                f.in("edit", !0);
                ib.in(e);
                ib.in(f);
                ib.removed(ee);
                return ib;
            }
            , edit_value = function () {
                let h = e.get();
                q = typ_long(h);
                ib.clear();
                q.name = b.name.toLocaleLowerCase();
                q.value = b.value;
                f.in("Save", !0);
                ib.in(q);
                ib.in(f);
                ib.add(ee);
                r.remove();
                return ib;
            }
            , typ_long = function (q) {
                return (q.height > 40 || b.long) ? t : i
            }
            , utc_data = function (query) {
                b.value = query;
                return show_value();
            }
            , update_db = function (query) {
                let { name, value } = query;
                value != b.value ? update_user_data(name, value, function (data) {
                    let er = data.export("error");
                    let na = data.export("name");
                    r.in(er, !0);
                    !er && na
                        ? utc_data(na)
                        : ib.in(r);
                }) : show_value();
            };

        f.href = "javascript:void(0)"
        f.event.on(function () {
            !ib.isclass(ee)
                ? edit_value()
                : update_db(q);
        });
        show_value();
        return [a, b, c];
    }
    var switch_button = function (a, b, c) {
        var o = a.option || []
            , v = a.values || []
            , co = $.create("padding-twenty switch_button width")
            , ti = function (p, q, r) {
                return p != null
                    ? co.create("s-tital", p)
                    : p;
            }
            , ts = function (p, q, r) {
                let id = $.makeid(7);
                q.in(o[r]);
                is(p, ch, r)
                p.id = id;
                q.add("for", id);
            }
            , is = function (p, q, r) {
                p.type = ty;
                p.name = n;
                p.value = v[r] || r;
                if (a.checked == r) {
                    p.add("checked=true")
                }
                p.event.on(e => q(p, v[r] || r, r));
            }
            , ch = function (p, q, r) {
                return co?.change(new (function Change(a, b, c) {
                    this.element = a;
                    this.value = b;
                    this.index = c;
                    return this;
                })(p, q, r));
            }
            , t = ti(a.title || null)
            , n = a.name || "switch"
            , cl = a.class || "IN089"
            , ty = "radio";

        c = co.create("width IN090");
        for (let nx = 0; nx < o.length; nx++) {
            let co = c.create("IN089");
            ts(co.create.input(ty), co.create.label("label"), nx);
        }
        return co;
    }
    var settitle = function (title) {

        function decodeTitle(title) {
            const lastSegment = title.split("/").pop();
            return lastSegment
                .split("-")
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ");
        }

        function setDocumentTitle(t) {
            document.title = "Setting" + (t ? " • " + t : "");
        }

        let [a, bxcon] = boxs(true),
            menu = bxcon.create("left-session", 0),
            ienu = menu.create("menu-session", 0),
            titleEl = menu.create.h1("title", 1),
            save = $.create("save-button button hidden", "Update");

        bxcon.in(save);
        bxcon.add("title-container padding-ten-twenty");

        title = decodeTitle(title);
        titleEl.in(title);
        setDocumentTitle(title);
        s.each.IN091.clear();
        s.each.IN091.in(a, true);

        s.isMobile(function (width) {
            if (!width) return;
            var arr = r.pathname.split("/").filter(item => item.trim() !== '');
            var back = function () {
                if (arr.length > 2) {
                    let aarr = arr.slice(0, -1);
                    return r.path("/" + aarr.join('/'))
                }
            }
            let aside = $("aside"), tq = {
                trget: arr.length > 2,
                event: document.referrer ? r.back : back
            };
            aside.add("side-navigation");
            bxcon.add("side-IN039");
            bxcon.create.div("title", "Setting");

            aside.layout_function ||= e => s.NavigationLayoyt(aside);
            let btn = ienu.create({ tagName: "button", class: "button" }, 0);

            tq.trget
                ? (btn.in(icon(null, 5003)), ev = tq.event)
                : (btn.in(icon(null, 5002)), ev = aside.layout_function);
            btn.event.on(ev);
        });
    };
    var session_user_checks = function (a, b) {
        if (!b?.name) {
            a.requreprofiles("profiles")
            return true;
        }
    }
    var uploadImage = function (profile_image, b) {
        $.require("widgets/image_upload", function ImageUpload(imageUpload) {
            var uploder = new imageUpload({
                aspectRatio: 1,
                responsive: true,
                reqSize: 1024 * 2000,
                title: "Select Profile Pictures",
                header: {
                    location: "profile_image"
                },
                finish: function (e) {
                    let images = e.is("url");
                    if (e.is("uploaded") == true && images) {
                        profile_image && profile_image.add("src", images);
                        uploder.close_container()
                    }
                }
            });

            // var windows = $.windows(null, {
            //     container: uploder.container,
            //     functions: uploder.close_container
            // }, true);

        }).css();
    }

    s.load_image = function () {
        let profile_image = this.p.choose("img") || s.each.get("member_atr");
        uploadImage(profile_image, this)
    }

    api_route("/profiles", function () {

        let aa, ab, ac, ad, grt = function (member) {
            if (session_user_checks(s, member)) {
                return null;
            }

            [a, aa] = boxs(s.each.IN091);
            aa.create.hr("IN005");
            tolbar(aa, {
                icon: 5004,
                iconCode: 5008,
                title: getString("Edit Account"),
                uri: "/settings/profiles/edit"
            });

            aa = aa.create("padding-twenty width DIS01", false, 0);
            img = aa.create("member-image")
            ac = img.create.img("img");
            ac.add("src=" + member.img);
            ac.add("alt=User Image");

            ad = img.create.span("change");
            // ad.add("src=/static/icon/member-icon-change.png");
            ad.add("alt=Change Image");
            ad.addIcon("ice_refresh");
            ad.event.on(s.load_image);

            info = aa.create("member-info");
            info.create("name", member.name);
            info.create("email", member.email);

            ab = aa.create.button("button logout", "Logout");
            ab.event.on(e => setting.checks());

            [, aa] = boxs(s.each.IN091);
            tolbar(aa, {
                icon: 5005,
                iconCode: 5008,
                title: getString("Change Password"),
                uri: "profiles/change-password"
            });
            aa.create.hr("IN005");

            tolbar(aa, {
                icon: 5005,
                iconCode: 5008,
                title: getString("Verify Password"),
                uri: "profiles/password-verify"
            });
            aa.create.hr("IN005");

            tolbar(aa, {
                icon: 5006,
                title: getString("Sync")
            });
            aa.create.hr("IN005");


            [, aa] = boxs(s.each.IN091);
            tolbar(aa, {
                icon: 5005,
                iconCode: 5008,
                title: getString("Are you Teacher"),
                uri: "/ut/accounts/teacher/verify-indentity"
            });

            s.window(true);
            $.loader(false);
        }

        !s.member
            ? s.importUser(grt)
            : grt(s.member);
        return true;

    });
    api_route("/profiles/edit", function () {
        var grt = function () {
            $.require("widgets/edit_profiles", function EditProfiles(editProfiles) {
                let query = editProfiles(s);
                $.changeimage = function (a) {
                    console.log("Change Image");
                }
            })
        }

        !s.member
            ? s.importUser(grt)
            : grt();
        return true
    });
    api_route("/profiles/password-verify", function (a, session, c) {

        function Form(module) {
            let settings = s;
            let form = module(settings.each.IN091);

            form.input({
                title: "Password",
                type: "password",
                name: "password",
                spellcheck: "true",
                placeholder: "Enter Password",
                description: "By using this method you can check the password of the login account. This method is used so that you can remember your password before logging out."
            });

            form.change = function (event, action) {
                var submitValue = action.getValue();
                var submitButton = action.getSubmitButton();
                var checkValue = function (a, b) {
                    return is(a) && is(b)
                        ? a.trim() == b.trim()
                        : false;
                }
            }

            form.finish = function (query) {
                $.loader(false);
                if (message = $.is("message")) {
                    $.alert(message);
                    form.resetCaptcha();
                }
                s.window();
            }
            form.error = function (query) {
                $.loader(false);
                if (message = $.is("message")) {
                    $.alert(message);
                    return form.resetCaptcha();
                }
                let errors = $.export("error");
                errors.for(function (item) {
                    if (item[0] == "captcha_virification_error") {
                        $.alert(item[1]);
                        form.resetCaptcha();
                    }
                })
            }

            form.addCaptcha();
            form.submitButton("Verify");
            form.setRequestRoot("profile/password_verify");


            let bodx = form.getForm();
            bodx.create.input({
                disabled: "disabled",
                type: "text",
                name: "email",
                value: s.member.email
            }).css({ display: "none" });

            $.loader(false);
        }

        let grt = function () {
            $.require("widgets/forms", Form).css();
        }
        !s.member
            ? s.importUser(grt)
            : grt();

        return true

    })
    api_route("/profiles/change-password", function (a, session, c) {

        function Form(module) {
            let settings = s;
            let form = module(settings.each.IN091);

            form.input({
                title: "Old Password",
                type: "password",
                name: "password",
                spellcheck: "true",
                placeholder: "Enter Old Password",
                description: "Enter the current password associated with your account to verify your identity."
            });

            form.input({
                title: "New Password",
                type: "password",
                name: "new_password",
                spellcheck: "true",
                placeholder: "Enter New Password",
                description: "Create a new password for your account. Ensure it meets the required security guidelines."
            });

            form.input({
                title: "Confirm Password",
                type: "password",
                name: "confirm_password",
                spellcheck: "true",
                placeholder: "Re-enter New Password",
                description: "Re-enter the new password to confirm it matches and avoid mistakes."
            });


            form.change = function (event, action) {
                var submitValue = action.getValue();
                var submitButton = action.getSubmitButton();
                var checkValue = function (a, b) {
                    return is(a) && is(b)
                        ? a.trim() == b.trim()
                        : false;
                }
            }

            form.finish = function (query) {
                $.loader(false);
                if (message = $.is("message")) {
                    $.alert(message);
                    form.resetCaptcha();
                }
                s.window();
            }
            form.error = function (query) {
                $.loader(false);
                if (message = $.is("message")) {
                    $.alert(message);
                    return form.resetCaptcha();
                }
                let errors = $.export("error");
                errors.for(function (item) {
                    if (item[0] == "captcha_virification_error") {
                        $.alert(item[1]);
                        form.resetCaptcha();
                    }
                })
            }

            form.addCaptcha();
            form.submitButton("Verify");
            form.setRequestRoot("profile/change_password");

            let bodx = form.getForm();
            bodx.create.input({
                disabled: "disabled",
                type: "text",
                name: "email",
                value: s.member.email
            }).css({ display: "none" });
            $.loader(false)
        }

        let grt = function () {
            $.require("widgets/forms", Form).css();
        }
        !s.member
            ? s.importUser(grt)
            : grt();
        return true

    })
    api_route("/appearance", function () {
        [a, b] = boxs(s.each.IN091);
        c = b.create("padding-ten-twenty space-between width");
        colloun(c, "Overall Appearance", "Applies to new tabs, pages, dialogs, and other menus.");
        icon(c, 5008);

        let values = ["default", "dark", "light"];
        let option = ["System default", "Dark", "Light"];


        m = switch_button({
            title: "Theme",
            name: "baseThemeOptions",
            class: "theme-option",
            option: option,
            values: values,
            checked: values.indexOf(setting.theme)
        });
        b.in(m);
        m.change = function (a) {
            var head = $.bindFunction(document.head);
            var body = $.bindFunction(document.body);

            setting.update("theme", a.value);
            body.add("theme", a.value);

        }
        $.loader(false);
        return true;
    });
    api_route("/languages", function (a, b, c) {
        var languages_list = [
            { name: "English (US)", code: "en" },
            { name: "Hindi", code: "hi" },
            { name: "Sanskrit", code: "sa" },
            { name: "Tamil", code: "ta" },
            { name: "Telugu", code: "te" }
        ];
        [a, b] = boxs(s.each.IN091);
        c = b.create("padding-ten-twenty space-between width")
        colloun(c, "{{function.utc('Languages')}}", "{{function.utc('Applies to new tabs, pages, dialogues and other menus')}}");
        icon(c, 5008);

        let values = [];
        let option = [];
        for (const index of languages_list) {
            values.push(index.code);
            option.push(index.name);
        }

        m = switch_button({
            name: "baseLanguagesOptions",
            class: "languages-option",
            option: option,
            values: values,
            checked: values.indexOf(setting.language)
        });
        b.in(m);
        m.change = function (a) {
            setting.update("language", a.value);
        }
        $.loader(false);
        return true;
    });
    api_route("/reset-settings", function () {
        [a, b] = boxs(s.each.IN091);
        c = b.create("padding-ten-twenty space-between width");
        var [c,] = colloun(c, "Overall Setting", "Restore default values across all customizable settings");
        c.p.create.button("reset", "Reset All").event.on(function () {
            console.log(setting);

            setting.resate(), r.reload()
        })
        $.loader(false);
        return true;
    });

    s.each ??= new $(function Each() {
        return function eachElement(e) {
            if (E(e)) {
                let n = e.id || e.className;
                this.each.add(n, e);
            }
            return this
        }
    });

    s.add("elementHendler", new function $ElementHendler(element, callback) {
        var elementHendler = ElementHendler;
        var isHendler = elementHendler.export(element)
        isHendler
            ? isHendler(element, callback)
            : null;
        return elementHendler
    })

    s.add(function error(e) {
        if (e.length == 0) {
            r.path(r.pathname + "/profiles");
            return true;
        }

        s.each.IN091.clear()
        let a = s.each.IN091.create("rE002");
        a.create.h1("hedline", "404")
        a.create.h2("sub-hedline", "Oops! Something bad happened!")
        a.create.span("desc", "We apologize for any inconvenience, but an unexpected error occurred while you were browsing our site.")
        $.loader(false)
        return true;
    });

    var buttons = $.weres("a", false)
    s.add(function window(a) {
        var j = "jsname";
        buttons.combined($.weres("a", false)).filter(insex => !insex.get(j) && (0 <= insex.href.search("settings"))).for(function (insex) {
            let uri = new URL(insex.href);
            insex.href = uri;
            insex.add(j, false)
            insex.event.on(function (event) {
                event.preventDefault();
                r.path(insex.pathname);
                return false;
            })
        });
        buttons = buttons.filter(item => item.get(j));
        buttons.filter(button => button.isclass("menu-list")).for(function (button) {
            let a = "active", uri = button.pathname.substring(1);
            r.u.pathname.indexOf(uri) != 1 ? button.removed(a) : button.add(a);
        });

        if (a === true) {
            return;
        }
        let p = r.pathname.slice(9);
        let n = sa.call(p);
    })

    s.add(function isMobile(a, b) {
        let mobile = $("mobile");
        return mobile?.nodeName == "BODY"
            ? F(a) ? a(true, mobile) : true : null;
    })
    s.add("NavigationLayoyt", function $NavigationLayoyt(aside, callback) {
        let a = aside.get(), b = this.each.IN091, c = { functions: aside.layout_function };
        a.left == 0
            ? aside.css({ left: "-280px" })
            : (aside.css({ left: 0 }), $.windows(null, c, b));
    })
    s.add(function importUser(a, b) {
        $.loader(true)
        let api = $.apirequest("profile/query");
        console.log(api);
        api.finish = function (query) {

            s.member = new $.array(query.is("auth_session") || {})
            if (F(a)) { return a(s.member) }
            $.loader(false)
        }
        api.error = function (query) {
            $.loader(false)
        }
        api.send();
    })
    s.add(function requreprofiles(element) {
        let container = s.elementHendler.b_container_list("padding-ten-twenty width", false)
        container = s.elementHendler.container_loged(null, container)
        let b_tween = container.main.create("b_tween");
        b_tween.create("title", "You must be loogged in to access this page");
        b_tween.create.p("desc", "The following benefits ofter logging int this Website");
        let ul = b_tween.create("ul", "f4n50");
        let list = [
            "65% of the advertisement will now be visible.",
            "You will get to reading 70% premium articles every day",
            "You will get premission to comment.",
            "Try once",
        ]

        for (const item of list) {
            ul.create({ tagName: "li", inner: item })
        }
        let button_group = b_tween.create("button_group");
        button_group.create({
            tagName: "a",
            class: "button",
            href: "/ut/accounts/login",
            inner: "Login"
        })
        $.loader(false)
    })
    s.isHendler = function (list) {
        icons = list;
        r.onChange(e => s.window()), s.window();
    }

    // Not change for this line
    s.each($("IN091 "));
    $icons.add({
        5002: "ic_menu",
        5003: "ice_arrow_left",
        5004: "ic_user",
        5005: "user_message",
        5006: "ic_key",
        5007: "ic_refresh",
        5008: "open_link",
        5009: "ice_chevron_right",
        5010: "ic_upload",
    }, s.isHendler);

    $.string('/setting', function (e) {
        console.log("string update", e);
    })

}, $.req(e => false));
