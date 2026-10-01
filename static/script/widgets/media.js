(!function (ed) {
    const { B, E, ks } = ed.getFunction()
        , sd = ks(ed.cookie("_md_trg", 1, 1))
        , rq = new ed.URLState(!1, "https://myapplication .com")
        , ru = e => (rq.e = false, e(rq), rq.e = true)
        , cn = e => {
            const n = "header", l = "hrg"
                , p = e || ed.popup("Media Files")
                , h = p.find(n) || p.create(n)
                , g = h.find("." + l) || h.create(l)
                , f = g.create.form("M007")
                , id = ed.getid()
                , i = f.create.input({
                    id,
                    name: "gf",
                    placeholder: "Search..."
                });

            p.add("MEDIA"); h.add("IN038");
            f.create.label({
                class: "icon",
                for: id
            }).addIcon("ic_search");

            f.event.submit(async function (e) {
                e.preventDefault();
                i.value && rq.search.set("gf", i.value);
                console.log(rq);
            })
            return { p, h, g }
        }
        , sc = (a, b, c) => {
            const d = a.choose(b), r = d || a.create(b);
            return (!d && typeof c == "function" && c(r)) || r;
        }
        , cm = e => {
            const f = e.create("M006")
            return {
                l: f.create("left"),
                r: f.create("right")
            }
        }

    function Media(m, cb) {

        const te = a => { throw new Error(a) };

        const RootId = {};
        const er = [
            [!new.target, "Media must be called with new"],
            [!B(m), "Invalid object provided"]
        ]
        const sl = e => e.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
        const M = ed(function M() {

            this.Ev = () => {

                console.log(p.g.find("h2")
                    || p.g.create("h2", null, 0), M.rT);

                (p.g.find("h2")
                    || p.g.create("h2", null, 0)
                ).in(M.rT, true);

            }
            this.Tc = (a, b) => {
                let m = 0, t = 0, j = this, c = "Js";
                j.InR.p.childrens.for((i, n) => (
                    i.set(c, b == i || a == i.innerText ? 1 : 0),
                    +i.get(c) == 1 && (t = (n - 1), m = 1)
                ));
                j.InR.css({ top: (t * j.InR.get().height) });
                for (const i of [j.Ul, j.InR])
                    i.set("aria-view", m === 0)

                M.rT = a;
                j.Ev();

                ru(e => e.delete("gf"))
                rq.path(sl(a));
            }
            this.gC = a => {
                const b = this.Cn.choose(a) || this.Cn.create(a);
                this.Cn.children.for(e => e != b && e.remove())
                return b
            }
            return this;
        })
        const getRootNewId = (id) => {
            const used = new Set(Object.keys(RootId));
            do id = ed.makeid(6);
            while (used.has(id));
            return id;
        }
        const g = a => {
            const n = p.p.create("M001")
                , b = n.create("M002")
                , f = n.create("M003")
                , g = (c, i, t) => c = c.create.button(null, ed.create("flexCenter")
                    .addIcon(i)
                    .create.span(null, t).p)
                    .event.on(() => M.Tc.call(M, t, c));

            M.InR = b.create.span("M024");
            for (const [i, t] of Object.entries({
                ice_root: "Media Files",
                ice_picture: "Images",
                ice_video: "Video",
                ice_audio: "Adios",
                ice_pdf: "PDF",
                ice_svg: "SVG"
            })) g(b, i, t); a.location && g(b, "ice_folder-open", "Root File");
            M.Ul = g(f, "ic_upload", "Upload");
            M.Cn = p.p.create("M004");
            return n
        }
        const getFileIcon = a => {
            const ext = a.name.split('.').pop().toLowerCase();

            if (a.type.startsWith('image/')) return 'ib_image';
            if (a.type.startsWith('video/')) return 'ib_video';
            if (a.type.startsWith('audio/')) return 'ib_audio';

            if (ext === 'pdf') return 'ib_pdf';
            if (/^(doc|docx)$/.test(ext)) return 'ib_doc';
            if (/^(xls|xlsx|csv)$/.test(ext)) return 'ib_excel';
            if (/^(ppt|pptx)$/.test(ext)) return 'ib_ppt';
            if (/^(zip|rar|7z|tar|gz)$/.test(ext)) return 'ib_zip';
            if (/^(txt|log|md)$/.test(ext)) return 'ib_text';
            if (/^(js|ts|jsx|tsx|html|css|php|py|java|json)$/.test(ext)) return 'ib_code';

            return 'ib_null';
        }
        const formatFileSize = a => a < 1024 ? a + " B" : a < 1048576 ? (a / 1024).toFixed(2) + " KB" : a < 1073741824 ? (a / 1048576).toFixed(2) + " MB" : (a / 1073741824).toFixed(2) + " GB";
        const createFileCard = (a, b, c) => {
            const d = $.create("M009")
                , k = d.create("M010")
                , e = k.create("M011")
                , f = (a.thumbnail || a.src) && e.create({
                    tagName: "img",
                    src: a.thumbnail || a.src,
                    alt: a.name || "",
                    width: a.width || 100,
                    height: a.height || 100
                }) || e.addIcon(a.icon);

            f.dataset.type = a.type;

            const g = k.create("M012");
            const h = g.create("M013");
            h.create("M014").in(a.name || "Untitled");

            const i = a.name
                ? a.name.split(".").pop().toUpperCase()
                : "FILE";

            console.log(a);


            h.create("M015").in(`${i} • ${formatFileSize(a.size_bytes) || ""}`);
            d.ac = d.create("M016")
                .create.button("M017", b)

            return [d, k];
        }
        const image_sowing_container = (a, b, c) => {
            const [d, e] = createFileCard(a, b, c);
            e.event.dblclick(() => { let a = d.get("id"); if (!a) return; console.log("dblclick") });
            e.event.on(() => {
                if (!d.get("id")) return;
                const a = () => sc(f.r, "M018", e => e.create.button(null, "Action"));
                d.toggle("select");
                d.p.children.for(e => {
                    let s = e.isclass("select"), i = RootId[e.id], a = M.sf ??= [], g = i && a.some(x => x.src === i.src);
                    s && i ? !g && a.push(i) : g && (a = a.filter(x => x.src !== i.src));
                    M.sf = a;
                });
                M.Tif = sc(f.l, "M019");
                M.Tif.clear();
                M.Tif.create.span(null, "Selected file");
                M.Tif.create.span(null, String(M.sf.length));
                M.sf.length ? a() : (a().remove(), M.Tif.remove());
            });
            return d;
        };
        const appendFileIcon = (a, b, c, j) => {
            const d = new FormData, e = image_sowing_container(a, $.create.div().addIcon("ic_close"), () => typeof c == "function" && c())
                , q = ["location", "name"].filter(i => this[i]).map(i => `${i}=${encodeURIComponent(this[i])}`).join("&")
                , k = () => sc(M.Cn, "M022");

            M.abortFiles ??= {};
            !M.Cn.choose("M009") && M.Cn.clear();

            for (const [i, v] of Object.entries(M.abortFiles)) {
                if (v.name == b.name) {
                    j = k().choose(i, !0);
                    break;
                }
            }

            E(j) ? j.replace(e) : k().appendChild(e);
            addfileButton();

            d.append("files", b);
            const f = Date.now(), g = n => { let a = ["B", "KB", "MB", "GB"], b = 0; for (; n >= 1024 && b < 3; b++)n /= 1024; return n.toFixed(2) + " " + a[b] },
                h = n => { n |= 0; let a = n / 3600 | 0, b = n % 3600 / 60 | 0, c = n % 60; return a ? `${a}h ${b}m ${c}s` : b ? `${b}m ${c}s` : c + "s" },
                i = e => { let a = e.loaded, b = e.total, c = (Date.now() - f) / 1e3, d = a / c; return { progress: (a / b * 100).toFixed(1), speed: g(d), elapsed: h(c), remaining: h(d ? (b - a) / d : 0), uploaded: g(a) } };
            $.fch("/api/v1/media/upload?" + q, { method: "POST", body: d }, a => {
                const q = e.create("M020")
                    , c = e.choose("M015").create.span()
                    , f = r => {
                        e.set("wrong", true), e.choose("M013")
                            .create.p("error-file-message")
                            .addIcon("ice_alert").create.span(null, r);
                    }
                    , g = r => {
                        const id = getRootNewId(), q = ed.create.button("M017");
                        e.ac.replace(q); q.addIcon("ic_dotsmv")
                        at(q); e.set("id", id); RootId[id] = r;
                    };

                a.upload.onprogress = e => {
                    if (!e.lengthComputable) return;
                    const a = i(e);
                    a.progress >= 100 ? (c.remove(), q.remove()) : (c.in(a.uploaded, true), q.css({ width: a.progress + "%" }));
                };
                a.onload = e => {
                    const [, m, d] = e.target.json();
                    !d ? f(m.error.message) : g(d);
                };
                a.onerror = e => console.log("onerror", e);
                e.ac.event.on(() => {
                    const id = ed.getid(); a.readyState == 1
                        ? ed.confirm({
                            h: "Action Cancelled",
                            t: "The ongoing operation has been stopped.",
                            b: "Ok"
                        }, () => (a.abort(), M.lf = M.lf.filter(i => i !== b.name), M.abortFiles[id] = b, e.set("id", id), f("Cancelled"), !0))
                        : (delete M.abortFiles[e.get("id")], e.remove());
                });
            });

        };
        const tt = e => {
            const c = sc(p.p, "alert-container", e => (e.css({ display: "block" }), e.clear())), d = c.create("_alert");
            d.addIcon("ice_alert"); d.create.span("infor", e).set("title", e); d.create("alert-close").event.on(() => d.remove()).addIcon("ice_close");
            return !0;
        }

        const prosses = a => {
            M.lf ??= [];
            for (const b of a) {
                console.log(b);

                const c = { src: null, id: b.name, name: b.name, type: b.type || "application/octet-stream", icon: getFileIcon(b), size_bytes: b.size };
                if (M.lf.includes(b.name) && tt(`A file named "${b.name}" already exists.`))
                    continue;

                M.lf.push(b.name);
                if (!b.type.startsWith("image/")) { appendFileIcon(c, b); continue }
                const d = new FileReader;
                d.onload = e => {
                    const a = new Image;
                    a.onload = () => appendFileIcon({ ...c, src: e.target.result, width: a.naturalWidth, height: a.naturalHeight }, b);
                    a.onerror = () => appendFileIcon(c, b);
                    a.src = e.target.result;
                };
                d.onerror = () => appendFileIcon(c, b);
                d.readAsDataURL(b);
            }
        };
        const addfileButton = () => {
            const d = ed.getid();
            return sc(f.r, "media-select-button", e => (
                e.create.input({ type: "file", id: d, multiple: true }).event.change((i) => (
                    i.target.files && prosses(i.target.files)
                )),
                e.create.label({ class: "button", for: d, inner: "Select file+" })
            ));
        }
        const upf = () => {
            const n = M.gC("M008")
            const i = n.create.input({
                type: "file",
                id: "file-upload",
                multiple: true
            });
            const l = n.create.label({ for: "file-upload" });

            l.create("M021").addIcon("ic_upload")
            l.create.div(null, "Select a file or drag here")
            l.create.span("btn button", "Select a file")
            i.event.change(() => (i.files && prosses(i.files)))

            return n
        }

        const at = e => e.event.on(e => $.menuexitue(e).executed([{ icon: "ic_delete_profile", name: "Block" }, { icon: "ic_delete_profile", name: "Delete" }, { icon: "ic_remove_profile", name: "Remove" }]))

        let b = 0;
        const lmf = () => {
            if (b) return; b = 1;
            const d = M.gC("M0medi22"), g = a => {
                a.clear();
                let b = a.create("button");
                b.in("Load More"); d.set("data-type", rq.pathname);
                b.event.on(() => b.loader(1) && lmf());
                return b;
            };

            console.log();


            M.ip ??= 10; M.cp ??= 1;
            d.get("data-type") != rq.pathname && (d.clear(), M.cp = 1); d.removed("hidden");
            ru(e => (e.set("page", M.cp), e.set("limit", M.ip)));

            const k = sc(d, "M022"), t = sc(d, "Loderimg", e => (e.add("M022"), Array.from({ length: M.ip }, () => {
                let c = "loder-element", b = e.create("M010");
                b.create("M011").create(c);
                b.create("M012").create(c).p.create(c);

            }), e)), m = sc(d, "M023");

            t.removed("hidden"); ed.fch("/api/v1/media" + rq.pathname + rq.search).then(a => a.json()).then(e => {
                t.add("hidden")
                e.files.forEach(a => {
                    let id = getRootNewId(), e = image_sowing_container(a, $.create.span().addIcon("ic_dotsmv"));
                    e.set("id", id); k.in(e); M.sf ??= []; RootId[id] = a; M.sf.some(x => x.src === a.src) && e.add("select");
                    at(e.ac);
                });
                e.total > e.end ? (c = g(m)) : m.remove();
                b = 0; M.cp++;
            }).catch(e => (console.error(e), b = 0));
        }

        rq.onChange(u => {
            console.log(M.sf);

            sd.set("l", this.location || null);
            u.pathname.length < 2 && rq.path("media-files");
            u.pathname != "/upload" ? lmf() : upf();
        })

        for (const [i, n] of er)
            if (i) return te(n);
        Object.assign(this, m);


        this.c.clear()
        const p = cn();
        const f = cm(p.p);
        // const p = cn(this.c.create("med"));

        p.p.append(g(this));
        M.Tc.call(M, "Media Files");
        // M.Tc.call(M, "Upload");

        return this;
    }
    // return ed.define("widgets/media", Media);
}($))
