// $.define("MCQ", function MCQ(container, opretar, ES) {
$.define(function MCQ(container, opretar, ES) {
    "use strict";

    const { I } = $.getFunction();
    const hx = () => new $.request().get("hx")
        , st_code = hx()
        , storage = $.storage(st_code)
        , cookie = $.cookie("B6rZtuBb", 360, true);

    cookie.get()
        ? cookie.add(st_code)
        : cookie.insert([st_code]);

    if (!questions) {
        storage.remove();
    }

    storage.insert({
        id: I(),
        details: opretar.details,
        pe_point: opretar.pe_point,
        question: opretar.questions,
        expiry: opretar.endTime,
        timing: opretar.timing,
        subject: opretar.subject,
        category: opretar.category,
        submit: opretar.submit,
        position: opretar.position,
    });


    ES.storage = storage;
    ES.selfExam = Array.isArray(opretar.questions);
    const MCQ = new $(function MCQ() {
        this.submitValue = new $.array(storage.export("submit", true));
        return this
    });

    const mcqe = new $(function Element() {
        return this
    });

    const extend = function (name, opretar) {
        if (typeof name == "function") {
            opretar = name;
            name = name.name;
        }
        return MCQ.add(name, opretar)
    };
    const geeter = function (opretar) {
        return MCQ.is(opretar)
    };
    const bind = function (opretar, opacity) {
        opretar = geeter(opretar);
        return typeof opretar == "function"
            ? opretar(opacity)
            : null;
    };
    var questions = storage.export("question");
    const details = storage.export("details")
    const keys = Object.keys(details || {})


    var pe_point = storage.export("pe_point");
    pe_point = pe_point || keys[0]

    extend("SESSION", function Session() {
        let session = this.export("session")
        return session;
    })

    extend(function startCountdown(a, b, c) {
        let d = 0, e = a(), f = setInterval(() => {
            ES.ws?.readyState > WebSocket.CLOSING && (!$("IN031") && hx() && $.confirm({
                h: "Connection Blocked",
                t: "The server connection was blocked by your browser or network settings. Check your internet connection, disable VPN/proxy if needed, and ensure cookies are enabled.",
                c: "Exit", b: "Retry"
            }, () => location.reload()), clearInterval(f));

            d++ > 5 && (d = 0, e = a());

            b.innerHTML = [
                Math.floor(e / 3600),
                Math.floor(e / 60) % 60,
                e % 60
            ].map(x => String(x).padStart(2, "0")).join(":");

            MCQ.SESSION.active && storage.update("timeup", --e);
            e < 0 && (clearInterval(f), c(), b.innerHTML = "Time's up!");
        }, 1000);
    })

    extend(function submitValueGet(a) {
        const b = storage.export("submit", true)?.[pe_point];
        if (b) for (const c in b) if (Array.isArray(b[c]) && b[c][0] === a) return b[c];
        return null;
    })

    extend(function submitValueAdd(value) {
        var iex = Number(ES.loadedQuestion.sno) - 1;

        for (const sub in MCQ.submitValue) {
            MCQ.submitValue[sub] = MCQ.submitValue[sub].map(item =>
                item[0] === value[0] ? value : item
            );
        }
        ES.ws.export({ iex: [pe_point, iex, value] })
        storage.update("submit", MCQ.submitValue);
    })
    extend(function getElement(element) {
        return mcqe.is(element)
    })
    extend(function saveQuery() {
        MCQ.submitValueAdd(MCQ.getValue())
        const total = questions[pe_point].length;
        if (++MCQ.SESSION.index >= total) MCQ.SESSION.index = 0;
        if (MCQ.SESSION.index === total - 1) {
            console.log(pe_point);
        };
        bind("loadQuestion", questions)
    })
    extend(function saveEvent() {
        $.loader(true)
        mcqe.submitbutton.disabled = true;
        ES.ws.export({ submit: true });
        location.reload();
    })
    extend(function submit(target) {
        return target
            ? $.confirm({
                t: "If you save it once, you will not get the option to change it again. After this, you will see the result in some time.",
                b: "Save"
            }, this.saveEvent) : this.saveEvent();
    })
    extend(function getValue() {
        let o = [], i = null, s = false;
        const inputs = mcqe.T052.weres("input", false);
        inputs.forEach(input => {
            const count = input.get("count");
            if (input.type === "radio") {
                o[count] = input.value;
                if (input.checked) s = Number(count);
            } else { i = Number(input.value); }
        });

        return [i, o, s];
    })
    extend(function loadQuestion(questions) {
        const question = questions[pe_point][MCQ.SESSION.index];
        MCQ.SESSION.active = true;
        ES.loadedQuestion = question;
        storage.update("position", MCQ.SESSION.index)

        ES.ws.export({ position: MCQ.SESSION.index, pe_point: pe_point })
        mcqe.T052.clear();
        mcqe.T052.create({
            tagName: "input",
            class: "hidden",
            name: "question",
            value: question.id
        })
        var T053 = mcqe.T052.create.h2("T053 flexStart")
        var options = mcqe.T052.create("options")
        T053.create("sno", String(question.sno))
        T053.create("question", question.title)
        var count = 0;

        var [id, option, exits] = MCQ.submitValueGet(question.id, []);
        for (const value of option) {
            const id = $.getid()
            const F0009 = options.create("label", "F0009 DIS00");
            const input = F0009.create({
                id,
                value,
                count,
                name: "option",
                type: "radio",
                tagName: "input",
                class: "F0023"
            });
            F0009.set("id", id);
            F0009.create.span("CONAME", `(${opretar.option_name[count]})`);
            F0009.create.span("checkbox-title", value);

            exits !== null && exits !== false && count === Number(exits) && input.add("checked", "checked");
            input.event.change(e => F0009.closest(".options").children.for(e => e.set("data-select", e == F0009)))
            count++
        }
        const buttons = mcqe.noqu.weres("button", false);
        for (const [, data] of MCQ.submitValue) {
            for (const [a, , c] of data || []) {
                const button = buttons.find(e => e.questionId === Number(a));
                if (button && c === false) button.add("arira", "deactive");
                else if (button && c != null) button.add("arira", "active");
            }
        }

        for (const button of buttons) {
            button.add("active", button.id == String(MCQ.SESSION.index) ? true : false);

            if (button.id == String(MCQ.SESSION.index)) {
                console.log(button, button.p);

                button.scrollIntoView({
                    block: "nearest",
                    behavior: "smooth",
                });
            }

        }


        let backButton = mcqe.T055.choose("back");
        MCQ.SESSION.index <= 0 ? backButton.add("hidden") : backButton.removed("hidden");

        try { MathJax.typeset() }
        catch (error) { }
    })
    extend(function RUN() {
        window.onkeydown = function (e) {
            e.keyCode == 8 && 0 < MCQ.SESSION.index
                ? mcqe.backbutton.click()
                : e.keyCode == 13
                    ? MCQ.saveQuery(e)
                    : mcqe.T052.weres("input", false).for(input => String(e.key - 1) == input.get("count") ? input.click() : null)
            return false;
        }

        const importElement = function (element, operator) {
            if (typeof operator == "string") {
                operator = mcqe.export(operator.trim());
            }

            if (!operator || typeof operator.create !== "function") {
                throw new TypeError(
                    `Invalid operator for "${element}": ${operator}`
                );
            }

            return mcqe.add(element, operator.create(element));
        };

        container.clear();

        const bindings = {
            header: container,
            container: container,
            main: "container",
            amsads: "main",
            aside: "container",
            T052: "main",
            footer: "main",
            left_footer: "footer",
            T055: "footer",
            T051: "header",
            right_header: "header",
            aside_c: "aside",
            T056: "aside_c",
            T054: "aside_c",
            noqu: "aside_c"
        };

        for (const [name, operator] of Object.entries(bindings)) {
            importElement(name, operator);
        }


        MCQ.SESSION.index = storage.export("position") || 0;

        var time = mcqe.right_header.create("T058", "Time Left : ").create.span("time", "00:00:00");

        MCQ.startCountdown(e => Math.floor(((storage.export("expiry") || 0) - I()) / 1000), time, function (e) {
            MCQ.SESSION.active = false;
            storage.remove();
            MCQ.submit(e);
        })

        mcqe.amsads.create("adscontainer").create({
            tagName: "ins",
            class: "adsbywseditor",
            cssText: "display:inline-block;max-width: 728px;max-height:90px;"
        });
        $.bind("Ads");
        mcqe.backbutton = mcqe.T055.create.button("back", "Back").event.on(function () {
            MCQ.SESSION.index--
            bind("loadQuestion", questions)
        });

        mcqe.savebutton = mcqe.T055.create.button("save", "Save").event.on(e => MCQ.saveQuery(e))
        mcqe.submitbutton = mcqe.left_footer.create.button("submit", "Save & Submit").event.on(e => MCQ.submit(e))

        function loadDomeQuestionNumber() {
            mcqe.noqu.clear()
            mcqe.noqu.create.h2("title", "Questions")
            var group = mcqe.noqu.create("IN0104");
            for (const [i, item] of Object.entries(questions[pe_point])) {
                const button = group.create.button({
                    class: "opt",
                    xt: item.id,
                    id: i,
                    inner: String(item.sno),
                });
                button.questionId = item.id;
                button.event.on(function () {
                    MCQ.SESSION.index = Number(this.id);
                    bind("loadQuestion", questions)
                })
            }
        }
        loadDomeQuestionNumber()

        // mcqe.T054
        if (ES.selfExam !== true) {
            mcqe.T054.create.h2("title", "Paper")
            var group = mcqe.T054.create("IN0104");
            for (const [key, item] of Object.entries(details)) {
                const [qn, sub, cog] = item;
                const a = "active", btn = group.create.button(null, sub).event.on(function () {
                    this.p.children.for(e => {
                        if (e.isclass(a)) e.selectIndex = MCQ.SESSION.index;
                        e.removed(a)
                    });
                    this.add(a);
                    pe_point = key;
                    MCQ.SESSION.index = this.selectIndex || 0;

                    loadDomeQuestionNumber();
                    bind("loadQuestion", questions);

                });
                btn.create.span(null, " ~ ")
                btn.create.span(null, cog)
                if (pe_point == key) {
                    btn.add("active")
                }
            }
        }

        // User Modal 
        mcqe.T056.create({ tagName: "img", class: "T057", src: opretar.stu_img })
        var table = mcqe.T056.create.div().css({ width: '-webkit-fill-available' });
        function sm(a, b) {
            let tr = table.create('T040');
            tr.create.span('msq1', a);
            tr.create.span('T041 msq2', b);
            return tr;
        }
        sm("Name", opretar.stu_name)
        sm("Roll No", String(opretar.roll_no))

        if ($.getHtmlBody(e => e.isclass("mobile"))) {
            mcqe.T051.create.button("menu").event.on(function () {
                mcqe.aside.css({ "height": mcqe.aside.getStyle("height") === "0px" ? mcqe.aside_c.get().height + 30 : "0px" })
            }).addIcon("menu_nine");
        }


        var subcode = mcqe.T051.create("subcode");
        var mubcode = subcode.create("mubcode");

        mubcode.create("tilce", `Exam Name : ${opretar.exam_name}`)
        // mubcode.create("subce", `( ${opretar.subject || "Any"} ~ ${opretar.category} )`)

        MCQ.SESSION.active = true;
        bind("loadQuestion", questions);
        console.error("ok");

        var x = setInterval(() => {
            ES.ws ? ES.ws.export({ log_check: true }) : clearInterval(x)
        }, 2000);
        $.loader(false);


        // Check if the member is really leaving
        window.addEventListener('beforeunload', function (event) {
            if (st_code != storage.name) {
                MCQ.SESSION.active = false;
                storage.remove();
                const confirmMessage = 'Are you sure you want to leave?';
                if (confirm(confirmMessage)) { }
                else { event.preventDefault() }
            }
        });
    })
    MCQ.RUN()

    return this
})