
$.define(function navigation(a, NAVIGATION = $(function Navigation() { return this })) {
    const $icons = $.icons();
    const { F } = $.getFunction();
    const extend = function (name, opretar) {
        if (F(name)) {
            opretar = name;
            name = name.name;
        }
        return NAVIGATION.add(name, opretar)
    };
    extend(function drawerLayout(cb) {
        $icons.add([
            "home", "ic_menu", "ic_trending", "ic_shopping", "ic_result", "ic_course",
            "ic_like", "ib_inbox", "chat", "ic_setting", "ic_help", "ib_evaluation", "ib_bulb",
            "ib_elearning", "ib_syllabus", "ib_question", "ib_trending", "ib_shopping",
            "ib_analysis", "ic_courses_think", "ic_mcq", "ic_close", "ic_logo",
            "ic_logo", "ic_voice", "ic_download", "books"
        ], function (i) {
            const d = $.create("IN061")
                , l = d.create("IN039 DIS01")
                    .create.span("button icon IN040", i[1])
                    .p.create("IN041")
                    .create("logo")
                    .addIcon("logo_main")

                , m = d.create("IN060").create("IN063 menu-home")
                , f = d.create("IN062").create("IN063 menu-home");

            for (const x of [
                { href: "/", title: "{{function.utc('Home')}}", icon: "home" },
                { href: "/books", title: "{{function.utc('Books')}}", icon: "books" },
                { href: "/courses", title: "{{function.utc('Courses')}}", icon: "ic_course" },
                { href: "/trending", title: "{{function.utc('Trending')}}", icon: "ic_trending" },
                { href: "/shopping", title: "{{function.utc('Shopping')}}", icon: "ic_shopping" },
                { href: "/exam/result", title: "{{function.utc('Check Result')}}", icon: "ic_result" },
                { href: "/liked-questions", title: "{{function.utc('Liked Questions')}}", icon: "ic_like" },
                { href: "/practice", title: "{{function.utc('MCQ Questions')}}", icon: "ic_mcq" },
                { href: "/download/app", title: "{{function.utc('Download App')}}", icon: "ic_download" }
            ]) {
                const a = m.create({
                    tagName: "a",
                    class: "IN064",
                    href: x.href,
                    title: x.title
                });
                a.create.span("IN065")
                    .addIcon(x.icon)
                    .p.create.span("IN040-title", x.title);

                location.href == a.href ? a.add("active") : null;
            }

            for (const x of [
                { href: "/settings/profiles", title: "{{function.utc('Settings')}}", icon: "ic_setting" },
                { href: "/help", title: "{{function.utc('Help')}}", icon: "ic_help" }
            ]) {
                f.create({
                    tagName: "a",
                    class: "IN064",
                    href: x.href,
                    title: x.title
                })
                    .create.span("IN065")
                    .addIcon(x.icon)
                    .p.create.span("IN040-title", x.title);
            }

            document.body.append(d);
            cb(d);
        });
    }
    );
    extend(function subMenu(cb) {
        const m = {
            ib_evaluation: "Exam/{{function.utc('Exam')}}",
            ib_bulb: "Practice/{{function.utc('MCQ')}}",
            ib_elearning: "Courses/{{function.utc('Courses')}}",
            ib_syllabus: "Syllabus/{{function.utc('Syllabus')}}",
            ib_question: "Questions/{{function.utc('Questions')}}",
            ib_trending: "Topic/{{function.utc('Topic')}}",
            ib_shopping: "Shopping/{{function.utc('Shopping')}}",
            ib_analysis: "Trending/{{function.utc('Trending')}}",
            ib_inbox: "Inbox/{{function.utc('Inbox')}}"
        }
            , c = $.create("IN076")
            , b = c.create.div().create("IN0104 IN075");

        for (const [k, v] of Object.entries(m)) {
            const [u, t] = v.split("/");
            b.create({
                tagName: "a",
                href: "/" + u.toLowerCase(),
                class: "list button",
                title: t
            })
                .create("IN091")
                .create.span("IN065")
                .addIcon(k)
                .p.create.span("IN040-title", t);
        }

        document.body.append(c);
        cb(c);
    })
    return NAVIGATION;
})