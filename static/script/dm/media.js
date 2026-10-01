var uploader = $.choose("uploader");
var preview = $.choose("preview", true);
var upload_button = $.choose("upload-btn", true);
// upload_button.addEventListener('click', uploadImages);
document.getElementById('insert-url-btn').addEventListener('click', insertFromUrl);
document.querySelectorAll('.menu-btn').forEach(btn => btn.addEventListener('click', filterMediaLibrary));





const createFileCard = (a, b, c) => {
    const d = $.create("file-card")
        , k = d.create("cards")
        , e = k.create("file-preview")
        , f = (a.thumbnail || a.src) && e.create({
            tagName: "img",
            src: a.thumbnail || a.src,
            alt: a.name || "",
            width: a.width || 100,
            height: a.height || 100
        }) || e.addIcon(a.icon);

    f.dataset.type = a.type;

    const g = k.create("file-info");
    const h = g.create("file-details");

    h.create("file-name").in(a.name || "Untitled");

    const i = a.name
        ? a.name.split(".").pop().toUpperCase()
        : "FILE";

    h.create("file-meta").in(`${i} • ${a.size || ""}`);
    d.ac = d.create("action-btn")
        .create.button("file-action", b)

    return [d, k];
}

const image_sowing_container = function (a, i, e) {
    const [card, k] = createFileCard(a, i, e);
    k.event.dblclick(function () {
        if (!card.get("root"))
            return;

        console.log("ok");
    })
    k.event.on(() => {
        if (!card.get("root"))
            return;

        card.toggle("select");
        const a = () => right_header_session.choose("action-button")
            || right_header_session.create.button("action-button", "Action", 0);

        card.p.children.filter(e => e.isclass("select")).length
            ? a() : a().remove();
    })

    return card
}

// File size format
function formatFileSize(size) {
    if (size < 1024) {
        return size + ' B';
    }

    if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB';
    }

    if (size < 1024 * 1024 * 1024) {
        return (size / (1024 * 1024)).toFixed(2) + ' MB';
    }

    return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

// File type ke according icon
function getFileIcon(file) {
    const ext = file.name.split('.').pop().toLowerCase();

    if (file.type.startsWith('image/')) return 'ib_image';
    if (file.type.startsWith('video/')) return 'ib_video';
    if (file.type.startsWith('audio/')) return 'ib_audio';

    if (ext === 'pdf') return 'ib_pdf';
    if (/^(doc|docx)$/.test(ext)) return 'ib_doc';
    if (/^(xls|xlsx|csv)$/.test(ext)) return 'ib_excel';
    if (/^(ppt|pptx)$/.test(ext)) return 'ib_ppt';
    if (/^(zip|rar|7z|tar|gz)$/.test(ext)) return 'ib_zip';
    if (/^(txt|log|md)$/.test(ext)) return 'ib_text';
    if (/^(js|ts|jsx|tsx|html|css|php|py|java|json)$/.test(ext)) return 'ib_code';

    return 'ib_null';
}

function uploadImages() {
    const files = document.getElementById('file-upload').files;
    const formData = new FormData();

    for (const file of files) {
        formData.append('files', file);
    }

    fetch('/api/v1/media/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert('Files uploaded successfully.');
                loadMediaLibrary(request);
            }
        })
        .catch(error => console.error('Error:', error));
}

function insertFromUrl() {
    const url = document.getElementById('image-url').value;
    if (url) {
        const library = document.getElementById('library-content');
        const div = document.createElement('div');
        div.className = 'library-item';
        const img = document.createElement('img');
        img.src = url;
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '&times;';
        deleteBtn.onclick = () => div.remove();
        div.appendChild(img);
        div.appendChild(deleteBtn);
        library.appendChild(div);
        document.getElementById('image-url').value = '';
    } else {
        alert('Please enter a valid URL.');
    }
}

function filterMediaLibrary(event) {
    const type = event.target.dataset.type;
    const items = document.querySelectorAll('.library-item img');

    items.forEach(item => {
        const itemType = item.dataset.type;
        if (type === 'all' || itemType === type) {
            item.parentElement.style.display = 'block';
        } else {
            item.parentElement.style.display = 'none';
        }
    });
}

function deleteImage(id, element, filetype) {
    fetch(`/delete/${filetype}/${id}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                element.remove();
            } else {
                alert('Failed to delete image.');
            }
        })
        .catch(error => console.error('Error:', error));
}



$.request = class QueryRequest {
    constructor(functions) {
        this.functions = functions || function () { };
        this.url = new URL(window.location.href);
        this.params = new URLSearchParams(this.url.search);
    }

    updateHistory() {
        window.history.pushState(null, null, this.url.toString());
        // window.location =  this.url.toString();

        this.functions($)
    }

    search = {
        get: (p) => this.params.get(p),
        set: (p, q) => {
            this.params.set(p, q);
            this.url.search = this.params.toString();
            this.updateHistory();
            return this.url;
        },
        append: (p, q) => {
            this.params.append(p, q);
            this.url.search = this.params.toString();
            this.updateHistory();
            return this.url;
        },
        delete: (p) => {
            this.params.delete(p);
            this.url.search = this.params.toString();
            this.updateHistory();
            return this.url;
        }
    }
}

const request = new $.request();
const right_header_session = $.choose("right-IN038")



let currentPage = 1, b = 0, c, itemsPerPage = 8;
const d = $.choose("data-container", true);
function loadMediaLibrary(r, f = 1) {
    if (b) return; b = 1;
    const g = a => {
        let b = a.create("load-more-button").create("button");
        b.in("Load More"); a.add("data-type", r.search.get("path"));
        b.event.on(() => b.loader(1) && loadMediaLibrary(r, currentPage));
        return b;
    };
    r.search.set("limit", itemsPerPage);
    $.fch("/api/v1/media" + r.url.search + "&page=" + f).then(a => a.json()).then(e => {
        let f = d.choose("library-content");
        c?.remove();
        if (d.get("data-type") != r.search.get("path")) {
            d.clear(); f = d.create("library-content");
        }
        d.removed("hidden");
        e.files.forEach(a => {
            let e = image_sowing_container(a, $.create.span().addIcon("ic_dotsmv"));
            e.add("root", a.src); f.in(e);

            e.ac.event.on((e) => {
                console.log("menu call");
                $.menuexitue(e).executed([
                    { icon: 'ic_delete_profile', name: 'Block', },
                    { icon: 'ic_delete_profile', name: 'Delete', },
                    { icon: 'ic_remove_profile', name: 'Remove', }
                ])

            })
        });
        e.total > e.end && (c = g(d));
        b = 0; currentPage++;
    }).catch(e => (console.error(e), b = 0));
}



$.event("media-group", function (e) {
    const request = new $.request();
    const title = $.choose("title");
    const media_group = e.weres("list");
    const indector = e.p.choose("indector");
    const data_container = $.choose("session-container");

    function appendFileIcon(fileData, file, cb) {
        const formData = new FormData();
        const card = image_sowing_container(fileData, $.create.div().addIcon("ic_close"), () => {
            typeof cb == "function" && cb();
            console.log("button click");
        });

        preview.appendChild(card);
        formData.append('files', file);


        const startTime = Date.now();
        const getProgressData = e => {
            let a = e.loaded
                , b = e.total
                , c = (Date.now() - startTime) / 1e3, d = a / c
                , f = n => {
                    let u = ["B", "KB", "MB", "GB"]
                        , i = 0;
                    while (n >= 1024 && i < 3) n /= 1024, i++; return n.toFixed(2) + " " + u[i]
                }
                , g = n => {
                    n |= 0; let h = n / 3600 | 0, m = n % 3600 / 60 | 0, s = n % 60;
                    return h ? `${h}h ${m}m ${s}s` : m ? `${m}m ${s}s` : s + "s"
                };
            return {
                progress: (a / b * 100).toFixed(1),
                speed: f(d),
                elapsed: g(c),
                remaining: g(d ? (b - a) / d : 0),
                uploaded: f(a)
            }


        }

        $.fch("/api/v1/media/upload", { method: "POST", body: formData }, function (r) {
            const u = card.create("upload-process"),
                s = card.choose("file-meta").create.span();

            r.upload.onprogress = e => {
                if (!e.lengthComputable) return;
                const p = getProgressData(e);
                p.progress >= 100 ? (s.remove(), u.remove())
                    : s.in(p.uploaded, true), u.css({ width: p.progress + "%" });
            };

            r.onload = () => console.log("onload");
            r.onerror = e => console.log("onerror", e);
            card.ac.event.on(() => {
                r.abort();
                console.log("Abourt");
            });
        });

        console.log(card);
    }

    function prosses(files) {
        request.search.set("path", "upload");
        right_header_session.clear(), preview.clear();

        for (const file of files) {
            const fileData = {
                src: null,
                id: file.name,
                name: file.name,
                type: file.type || 'application/octet-stream',
                icon: getFileIcon(file),
                size: formatFileSize(file.size),
            };

            if (!file.type.startsWith('image/')) {
                appendFileIcon(fileData, file);
                continue;
            }

            const reader = new FileReader();
            reader.onload = e => {
                const img = new Image();
                img.onload = () => appendFileIcon({
                    ...fileData,
                    src: e.target.result,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                }, file);
                img.onerror = () => appendFileIcon(fileData, file);
                img.src = e.target.result;
            };

            reader.onerror = () => appendFileIcon(fileData, file);
            reader.readAsDataURL(file);
        }
    }

    $.event("[aria-label=upload]", u => (u.event.on(() => {
        const popup = $.popup("Upload"), input = uploader.find("input");
        input.event.change(() => (input.files && prosses(input.files), popup.close()))
        popup.append(uploader);
    }), uploader.remove()))


    media_group.for(e => e.event.on(function () {
        currentPage = 1;
        request.search.set("path", e.get("aria-label"))
    }))


    request.functions = function () {
        var button_position, path = this.search.get("path");
        if (!path) { request.search.set("path", "all_media") }

        $.weres("a", false).filter(e => e.get("aria-label") == path).for(e => button_position = e.get())
        title.in(button_position.target.innerHTML)
        button_position.target.p.append(indector)
        button_position.set_preant()
        indector.style.top = button_position.to_top + "px"

        if (path != "upload")
            loadMediaLibrary(request, currentPage);


        data_container.children.for(function (item) {
            item.get("data-type") == path
                ? item.removed("hidden")
                : item.add("hidden")
        })
    }

    request.functions()


}, true)
