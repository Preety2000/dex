$.define("components/search-filter", $(function SearchFilter(a) {
    this.add(function filter(a, b = [], g = ["Filter", "Apply Filter"]) {
        (a || $).create.button(null, g[0]).event.on(() => $.require("widgets/forms", fn => {
            const cs = "DIS01"
                , w = $.popup(g[0])
                , fm = fn(w)
                , r = $.req();
            const p = fm.getContainer().create.div().setDomStyle({
                gap: "16px",
                margin: "6px",
                display: "grid",
                marginBottom: "16px",
                gridTemplateColumns: "repeat(auto-fit,minmax(270px,1fr))"
            });
            for (const [i, v] of b) {
                let value = r.get(v.name);
                if (i == "input")
                    p.append(fm.input({
                        ...v,
                        value
                    }).css({
                        marginLeft: 16
                    }).p.replaceClass(cs).p);
                else if (i == "select")
                    fm.select({
                        ...v,
                        checked: value
                    });
                else if (i == "checkbox")
                    fm.checkbox({
                        ...v,
                        checked: value ? value.split("|") : []
                    })
            }
            w.hrg.in(fm.submitButton(g[1]), 0);
            w.css({ width: "100%" })
            fm.submit = e => {
                for (let [k, v] of Object.entries(e))
                    Array.isArray(v) && (v = v.join("|")),
                        v ? r.u.searchParams.set(k, v) : r.u.searchParams.delete(k);
                r.navigate(r.u.href);
                w.close()
            }
                ;
            fm.container.css({
                padding: 20,
                minWidth: 380,
                maxHeight: 400,
                overflowY: "scroll"
            });
            for (const i of p.weres("F0019"))
                i.css({
                    margin: 0
                });
        }
        ).css())
    })
    this.add(function gsSearch(r) {
        const b = $.create("T003"), g = (i, fm, v) => {
            const bt = $.choose("T004") || b.create.span("button T004").addIcon("ice_close-x").event.on(e => (r.delete("gs", e.gs), i.value = null, bt.remove()))
            v ? fm.container.in(bt) : bt.remove()
        };
        $.require("widgets/forms", e => {
            const fm = e(b), i = fm.getContainer().create.input({ name: "gs", value: r.get("gs"), placeholder: "Global Search: Use Search Terms Like tram with Multiple key=value Filters" });
            fm.submitButton(null).addIcon("ice_search");
            fm.submit = e => e.gs && r.set("gs", e.gs)
            if (r.get("gs")) g(i, fm, true);
            i.event.input(e => g(i, fm, e.target.value));
        })
        return b;
    })
    return this;
}))