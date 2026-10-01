(!function (query) {
    const { AUTH_TOKEN } = $.getClass();
    const { is, N, E, A, B, F, isExtend, getNewClassName } = $.getFunction();
    const { session, extend, bind } = isExtend(function Admin() {
        return this;
    })

    const ks = (e = $.cookie("_ad_eSt", 360, 1), s = (d) => e.insert(AUTH_TOKEN.encode(d)), r = v => v(AUTH_TOKEN.decode(e.get()) || {})) => ({
        set: (i, v) => r(d => (d[i] = v, s(d))),
        res: i => r(d => i && (delete d[i], s(d)) || e.remove()),
        get: i => r(d => i ? Object.prototype.hasOwnProperty.call(d, i) ? d[i] : null : d)
    });

    extend(function Acrtion(condition) {
        // Checke condition true / false
        if (!condition) {
            return;
        }
        // Extend Function 
        return this.export(condition)(this)
    })

    extend(function Container(container) {
        container.container = container.popup_window.create("container");
        return container
    })

    extend(function icon(iconname) {
        return $.c("i.fa-regular").add(iconname);
    })


    const body = $.bindFunction(document.body);
    const head = $.bindFunction(document.head);
    const was = $(function Was() { return this });


    $.event("tablenav", function () {
        $.module("dm/tablenav", function tableNav(modules) {
            modules($, extendss, $(function Module() {
                return this
            }))
        })
    })


    const _andow = ks()
    var theme = "theme";
    $.event("theme-button", ev => ev.event.on(function () {
        _andow.get(theme) == "light" && this.checked
            ? _andow.set(theme, "dark")
            : _andow.set(theme, "light");
        body.add(theme, _andow.get(theme))
    }))

    // Navigation Function 
    const main = $("main");
    const navigation = $("navigation", true);
    $("menu-button").event.on(() => {
        Number(_andow.get("collapsed"))
            ? (_andow.set("collapsed", 0), body.removed("collapsed_nav"))
            : (_andow.set("collapsed", 1), body.add("collapsed_nav"));
    })

    var title_show = function (a) {
        if (!body.inclass("collapsed_nav")) { return $.create("title-show") }
        var titleshow = navigation.choose("title-show") || navigation.create("title-show")
        if (a == true) { titleshow.remove() }
        return titleshow;
    }

    var URLState = new $.URLState()
    var menu_button = navigation.weres("list").filter(function (e) { return e.parentFilter(function (e) { return e.isclass("main-manu") }) });
    var activeQuery = function (element, option) {
        if (option && element.p.childrens.for(menu => menu.removed("active")));
        return (element.href && (0 <= location.href.search(element.href)))
            ? element.add("active")
            : element.removed("active");
    }


    menu_button.for(function (element, index) {
        activeQuery(element)

        var get_top_position = function (a) {
            a = a || 0;
            return element.get().top - 36 + a + "px"
        }

        element.event.mouseenter(function (e) {
            $.event("collapsed_nav", function () {
                var titleshow = title_show()
                titleshow.in(element.innerText)
                titleshow.css({ top: get_top_position() })
                main.add("blur_e")
            })
        })
        element.event.mouseleave(function (e) {
            title_show(true), main.removed("blur_e")
        })
        element.event.on(e => {
            e.preventDefault(); element.href && URLState.navigate(element.href);
            element.p.choose("indector")?.css({ top: get_top_position(-6) });
            activeQuery(element, true); URLState.reload(); return !1
        })

    })


    // Content Function 
    $.event("cb-select-all", function (choose) {
        var cb_select = $.weres("cb-select");
        var action_selector = $.choose("bulk-action-choose-top", true)
        console.log(action_selector);


        var edit = function (items) {
            if (items.length <= 0) {
                return;
            }
            var container_close = function (p, q = $("IN033") || $.create()) { p.remove(), q.click() }
            var container = body.choose("fixed-container") || body.create("fixed-container");
            var form = container.create("form", "add-quiz");
            var title = form.create("F0006").create("hndle", "Add Json Data")
            var IN0100 = title.p.create("handle-actions").event.on(e => container_close(container));
            spinner = title.create("span", "spinner");

            var uri_option = form.create("F0035");
            uri_option.create("switch-label", items.length + " Question are ")
            var input_query = {};
            input_$.tagName = "input"
            input_$.id = "question_status_option"
            input_$.class = "question_status_option"
            input_$.type = "checkbox"
            input_$.name = "question_status"
            input_$.checked = true

            uri_option = uri_option.create("F0036")
            var question_status_option = uri_option.create(input_query);
            question_status_option.p.create("label",).add("for", input_$.id)


            var category_container = form.create("category-container", $.choose("categorydiv", true).innerHTML);
            form.create("submit", "Update All Questions").add("button").event.on(function () {

                var category = form.weres("category-input");
                var categorys_value = [];
                var data = [];
                category.for(function (category) {
                    if (category.checked) { categorys_value.push(category.value) }
                })

                // Create a new FormData object
                var formData = new FormData();

                spinner.css({ visibility: "visible" })
                items.for(function (element) {
                    element.terms = categorys_value,
                        element.status = question_status_option.checked ? "Publish" : "Draft",
                        data.push(element);

                })
                formData.append("json_data", JSON.stringify(data));

                // Create a new XMLHttpRequest object
                var xhr = new XMLHttpRequest();

                // Configure the request
                xhr.open('POST', "/admin/update?path=quiz&item=query")

                // Set the onload function
                xhr.onload = function () {
                    // Request was successful
                    if (xhr.status >= 200 && xhr.status < 400) {
                        // Handle the response here
                        data = JSON.parse(xhr.response);
                        if (data[0].error.length <= 0) {

                            window.location.reload()
                        }
                    } else {
                        // Request failed
                        console.error('Request failed with status:', xhr.status);
                    }
                    // IN0100.click()
                };

                // Set the onerror function
                xhr.onerror = function () {
                    // Request failed
                    console.error('Request failed');
                };

                // Send the request with the FormData object
                xhr.send(formData);
                console.log(formData);
            })
            $.windows(form, o => container_close(container), true)
        }

        choose.event.on(function () {
            cb_select.for(option => option.checked = choose.checked);
            action_selector.value = -1;
        });

        cb_select.for(e => e.event.on(o => action_selector.value = -1))
        action_selector?.event.change(function () {
            let cb_data = [];
            cb_select.for(function (items) {
                if (items.checked) {
                    let data = {};
                    data.id = items.p.choose("quick-edites").id;
                    data.question = items.p.p.choose("query-title").innerText;
                    cb_data.push(data);
                }
            })
            switch (this.value) {
                case 'edit':
                    edit(cb_data);
                    break;
                case 'trash':
                    trash(cb_data);
                    break;
                default:
                    console.log('No action selected or invalid action');
            }
        })
    }, true)


    var slugInput, jshendler;
    if ((slugInput = $('[name="slug"]')) && (jshendler = $.makeid(20))) {
        let e, h = function (c) {
            return slugInput.add("jscode", c);
        }, g = function (z) {
            let code = slugInput.value ? 1 : 0;
            h(code);
            return ["Add slug", "Translate"][code];
        }, j = g(), b = slugInput.add("jshendler", jshendler).p.create({
            tagName: "a",
            id: jshendler,
            class: "translate",
            jsname: "AC0TT",
            href: "javascript:void(0)",
            title: j,
            inner: j
        }, null);
        slugInput.event.input(e => {
            let j = g();
            b.in(j, true);
            b.add("title", j);
        })
    }

    var imageInput, jshendler;
    if ((imageInput = $('[name="image_src"]')) && (jshendler = $.makeid(20))) {
        let button = imageInput.add("jshendler", jshendler).p.choose("p", false)
            .create.span("media-button")
            .create.a("insert-media add_media");

        button.add("data-editor", "content");
        button.add("type", "button");
        button.add("jsname", "addMedia");

        // button.create.span("media-buttons-icon");
        button.create.span("media-buttons-title", "Add Media");
        button.event.on(e => $.require("widgets/media", f => {
            const data = new f({
                c: $("main-body"),
                name: "indian-economay",
                location: "category",
                cb: function (e) {
                    console.log(e, this);
                }


            })
            console.log(data);


        }).css());
        button.click()
    }
}($ || window.$))