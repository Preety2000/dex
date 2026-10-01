$.define(function Setting(a, SETTING = $(function Setting() { return this })) {
    const $icons = $.icons();
    const { F, is,A, E } = $.getFunction();
    const extend = function (name, opretar) {
        if (F(name)) {
            opretar = name;
            name = name.name;
        }
        return SETTING.add(name.toLocaleLowerCase(), opretar)
    }
    const exports = function (name) {
        let bind = SETTING.export(name);
        if (SETTING.isArray(name) && bind) {
            return bind
        }
        return SETTING.isArray(name)
    }

    extend(function Element(name) {
        if (E(this)) {
            !isArray(SETTING.$LinkList)
                ? SETTING.$LinkList = []
                : SETTING.$LinkList.push(this);
        }
    })
    const vs = !0
        , get_location = function (pathname, request = new $.request()) {
            let location;
            request.opreter = false;
            request.setPath(pathname);
            request.functions = function () {
                return this
            };
            location = request.href;
            return {
                location, onchange: function () {
                    request.opreter = true;
                    request.updateHistory();
                }
            }
        }

    extend(function $Menu(list, callback) {
        const container= $.create("b_menu_list")
            , $bc = container.create("IN077 IN0104")
            , $1 = function (e, i, v) {
                return $2($bc.create({
                    href: e,
                    title: v,
                    tagName: "a",
                    class: "button menu-list",
                }), i, v)
            }
            , $2 = function (e, i, v) {
                e.addIcon(i);
                e.create.span("menu-name", v);
                return e;
            };

        callback($1);
        for (const [key, value] of Object.entries(list)) {
            let { location, onchange } = get_location("settings/" + key);
            let element = $1(location, key, value);
            element.event.on(function (e) {
                e.preventDefault();
                return onchange();
            })

        }
        return container;
    });

    extend(function getFunction() {
        return {
            5001: function (document = $, callback, element) {
                element = document.create("b_menu_list");
                element = element.create("box-container");
                callback(element);
                return element;
            },
            5002: function (document = $, callback, element) {
                element = document.create("padding-ten-twenty space-between width");
                callback(element);
                return element;
            },

        }
    })

    extend(function $Profiles(list, callback) {
        var b_container_list = exports("getfunction")(true);
        console.log(b_container_list);

        const container= $.create("b_menu_list");
    });

    $.module("widgets/profile", function Profile(Profile) {
        
        $("IN091").append(Profile({
            a: function () {
                console.log("ok");

            }
        }))

    })
    return SETTING;
})