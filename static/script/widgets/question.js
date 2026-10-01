$.define(function Questions(a, b) {
    "use strict";
    const ws = !0
        , breadcrumb = function (e = $, g) {
            let breadcrumb = e.create({ tagName: "nav", class: "breadcrumb" }), delimiter = function () {
                breadcrumb.create({
                    tagName: "em",
                    inner: "&gt;",
                    class: "delimiter",
                })
            };
            breadcrumb.create({
                tagName: "a",
                href: "/",
                title: "Home",
                inner: "Home",
                "array-menu": "true"
            });
            delimiter();
            if (g.label) {
                breadcrumb.create({
                    tagName: "a",
                    href: g.label.href,
                    title: g.label.name,
                    inner: g.label.name,
                })
                delimiter();
            }
            breadcrumb.create({
                tagName: "span",
                inner: g.question,
                class: "current",
            });
            return breadcrumb;
        }
        , meta = function (e = $, g) {
            e.create.span("rank", g.rank);
            e.create.span("article-view", `<strong class="view">${g.like}</strong> times,`);
            e.create.span("article-date", g.datetime).add("datetime", g.datetime);
            e.create({
                tagName: "a",
                class: "button article-like feedback",
                inner: `<span class="like-count">${g.like}</span> Like`,
                "jsname": "likes",
                "aria-label": "feedback"
            });
        }
        , info = function (e = $, g) {
            let info = e.create("article-info");
            meta(info.create.span("left-side DIS01"), g);
            info.create.span("writer DIS01").addIcon("writer");
            info.create.span("article-IN069 ");
            return info;
        }




    console.log(breadcrumb(
        $, {
        label: {
            name: "jharkhand",
            href: "/",
        },
        question: "झारखंड में 1857 का विद्रोह।"
    }
    ));

    return breadcrumb
}())