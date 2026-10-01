
console.log("//////////////plese check");





const dataContainer = new $(function dataContainer(e) {
    const mimeTypes = {
        image: [
            "image/jpeg",        // JPEG image
            "image/png",         // PNG image
            "image/gif",         // GIF image
            "image/bmp",         // BMP image
            "image/tiff",        // TIFF image
            "image/svg+xml",     // SVG image
            "image/webp",        // WebP image
            "image/ico",         // ICO image
            "image/heif",        // HEIF image
            "image/heic"         // HEIC image
        ],
        video: [
            "video/mp4",           // MPEG-4 Video
            "video/webm",          // WebM Video
            "video/ogg",           // Ogg Video
            "video/avi",           // Audio Video Interleave
            "video/mpeg",          // MPEG Video
            "video/quicktime",     // QuickTime Video
            "video/x-msvideo",     // Microsoft Video
            "video/x-ms-wmv",      // Windows Media Video
            "video/x-flv",         // Flash Video
            "video/3gpp",          // 3GPP Video
            "video/3gpp2",         // 3GPP2 Video
            "video/x-matroska",    // Matroska Video
            "video/x-m4v"          // M4V Video
        ],
        audio: [
            "audio/mpeg",        // MP3 audio
            "audio/wav",         // WAV audio
            "audio/ogg",         // Ogg Vorbis audio
            "audio/aac",         // AAC audio
            "audio/flac",        // FLAC audio
            "audio/midi",        // MIDI audio
            "audio/x-m4a",       // M4A audio
            "audio/webm",        // WebM audio
            "audio/opus",        // Opus audio
            "audio/3gpp",        // 3GPP audio
            "audio/3gpp2",       // 3GPP2 audio
            "audio/pcm",         // PCM audio
            "audio/x-ms-wma",    // Windows Media Audio
            "audio/ts"           // MPEG-TS audio
        ],
        pdf: [
            "application/pdf",  // Standard PDF format
            "application/x-pdf",// Alternative name for PDF
            "application/acrobat", // Old MIME type for PDF
            "application/vnd.pdf" // Vendor-specific type, rarely used
        ]
    };
    this.isfiles = function (a) {
        for (const [type, types] of Object.entries(mimeTypes)) {
            if (types.includes(a)) {
                return type;
            }
        }
        return null; // Return null if the MIME type is not found
    };

    const itemsPerPage = 12;
    let isLoading = false;
    let insert = function (list, cls) {
        return list.push(cls)
    }
    let lopAppend = function (fun, arr, callback) {
        for (const keys of arr) callback(fun, keys)
    }
    this.currentPage = 1;
    this.element = this.element || new $.array();
    this.nodes = this.nodes || new $.array();
    this.request_library = $.apirequest("/media/library");
    this.importX = function importX(nodsName, id) {
        let element = this.element;
        let fixClass = function (e) {
            e = e.replaceAll("-", "_")
            return e;
        }
        for (const cls of nodsName) element.add(fixClass(cls), $(cls, id))
        return element
    }
    this.importElement = function importElement(elements) {
        let element = this.element;
        let insert = function (elements) {
            for (const iterator of elements.classList) {
                if (!element.export(iterator)) element.add(iterator, elements);
            }
        }
        if (elements.classList) elements = [elements];
        for (const iterator of elements) {
            insert(iterator)
        }
        return elements
    }
    this.importNodes = function importNodes(name, nodes) {
        if (!this.nodes.export(name)) this.nodes.add(name, nodes);
        return nodes
    }
    this.importClass = function importClass(classList) {
        this.classList = this.classList || [];
        typeof classList == "object"
            ? lopAppend(this.classList, classList, insert)
            : insert(this.classList, classList);

        this.importX(this.classList)
    }
    this.importId = function importId(idList) {
        this.idList = this.idList || [];
        typeof idList == "object"
            ? lopAppend(this.idList, idList, insert)
            : insert(this.idList, idList);

        this.importX(this.idList, true)
    }
    this.optionThumble = function (buttton) {
        if (buttton = $("IN094-vertical")) {
            buttton.remove()
        }
        let get = this.get(), container = $.bindFunction(document.body).create("IN094-vertical");
        container.create.button("open", "Open").event.on()
        container.create.button("delete", "Delete")
        container.create.button("about", "Abouts")
        container.style.top = this.get.px("y", 0.5)
        container.style.right = this.get().side.right + 10;
        $.windows(container, e => container.remove(), false)
        console.log(this, get);
    }
    this.image_sowing_container = function (image_data, icon) {
        var load = false;
        const dataContainer = this;
        const image_containers = $.create("preview-image-container");
        const image_container = image_containers.create("preview-image");
        const image = image_container.create("image").create.img("img");
        const progress = image_container.create("image-progress")
        image_containers.progress = progress.create({
            class: "progressbar",
            role: "progressbar",
            "aria-valuemin": 0,
            "aria-valuemax": 100,
            "cssText": "--value : 0",
        });

        image_containers.set_thumbnail = function (thumbnail) {
            image.src = thumbnail;
        }
        image_containers.load_image = function () { }
        image.addEventListener("load", function () {
            if (load === false) { image_containers.load_image() }
            load = true;
        })

        image_container.create.button("option-button", icon).event.on(dataContainer.optionThumble);
        image_container.create.p("image-name").in(image_data.name);
        image_containers.set_thumbnail(image_data.thumbnail || "/media/img/empty.png")
        image_containers.data = image_data;
        image.dataset.type = image_data.type;

        // Image Select
        var action_button, selects, right_session;
        image.event.on(function () {
            image_containers.toggle("select");
            if (action_button = dataContainer.element.right_header_session.choose("action-button")) {
                action_button.remove()
            }
            selects = image_containers.parentElement.children.filter(e => e.isclass("select"));
            right_session = $("right-session");
            if (selects.length > 0) {
                action_button = dataContainer.element.right_header_session.create.button("action-button", "Action");
                action_button.event.on(function () {
                    console.log(dataContainer);
                    for (const iterator of selects) {
                        console.log(iterator.data);
                    }
                })
            }
        });

        image_containers.addEventListener("dblclick", function (e) {
            this.add("select");
            let oppner = dataContainer.isfiles(this.data.type);
            dataContainer.oppnerContainer.export(oppner)(this.data);
        });

        return image_containers
    }
    this.oppnerContainer = new $(function oppner() {
        this.video = function (a, b) {
            console.log(a);

            // Create containerfor the video and controls
            if (b = $('video-player')) {
                b.remove()
            }
            const vcontainer = $.create('video-player');
            const container = vcontainer.create("video-container");
            var header = container.create("header");
            $("session-container").in(vcontainer, 0)

            header.create.span("header-title", a.id)
            header.create.span("close-button").event.on(e => $('video-player').remove()).addIcon("ic_close")
            let isDragging = false;
            let offsetX, offsetY;

            header.addEventListener('mousedown', (e) => {
                isDragging = true;
                // Calculate the offset between the mouse position and the container's top-left corner
                offsetX = e.clientX - vcontainer.getBoundingClientRect().left;
                offsetY = e.clientY - vcontainer.getBoundingClientRect().top;
            });

            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    // Move the containerbased on the mouse position and offset
                    vcontainer.style.left = `${e.clientX - offsetX}px`;
                    vcontainer.style.top = `${e.clientY - offsetY}px`;
                }
            });

            document.addEventListener('mouseup', () => {
                isDragging = false;
            });

















            // Create video element
            const id = $.makeid(6)
            const video = container.create({
                tagName: "video",
                class: "AdvancedExample__Video-sc-14ptb85-7 lbOPpE video-js vjs-fluid vjs-big-play-centered preview-player-dimensions vjs-controls-enabled vjs-workinghover vjs-v8 vjs-mux vjs-has-started vjs-paused vjs-member-inactive",
                id: id,
                preload: "auto",
                role: "application",
                poster: a.thumbnail,
                playsinline: "playsinline",
                tabindex: "-1",
                crossorigin: "anonymous",
                role: "region",
                controls: "",
            });
            video.create({
                tagName: "source",
                src: a.src,
                type: a.type,
            })
            video.create.p("vjs-no-js", "To view this video please enable JavaScript, and consider upgrading to a web browser that").create.a({
                href: "#",
                target: "_blank",
                inner: "supports HTML5 video",
            })
            $.module("video.min", function (e) {
                const player = e(id, {
                    controls: true,
                    autoplay: false,
                    preload: 'auto',
                    enableDocumentPictureInPicture: true,
                    // Other options...
                });
                console.log(player);

                player.ready(() => {
                    var playerElement = $.bindFunction(player.el_);
                    var videoElement = playerElement.choose("video", false)
                    for (const element of [playerElement]) {
                        element.style.width = container.get.px("width")
                    }
                    // setTimeout(() => {
                    //     playerElement.choose("vjs-picture-in-picture-control").click()
                    // }, 100);
                });

            })
        }
        this.image = function nae(a, b) {

        }
        this.audio = function nae(a, b) {

        }
        this.pdf = function nae(a, b) {

        }
        this.svg = function nae(a, b) {

        }
        return this;
    })

    this.loadMediaLibrary = function loadMediaLibrary(request, page = 1) {
        if (isLoading)
            return;
        isLoading = true;
        let dataContainer = this;

        request.search.set('limit', itemsPerPage);
        request.search.set('action', "read");
        request.search.set('ref', $.makeid(5));
        this.element.IN001.style.display = "block";
        this.request_library.error = function (data) {
            console.error('Error:', error);
            isLoading = false;
        }
        this.request_library.finish = function (data) {
            var load_more_button, library_content = dataContainer.element.data_container.choose("library-content");
            if (dataContainer.element.data_container.get("data-type") != request.search.get("path")) {
                dataContainer.element.data_container.clear()
                library_content = dataContainer.element.data_container.choose("library-content") || dataContainer.element.data_container.create("library-content")
                load_more_button = dataContainer.element.data_container.create("load-more-button").create("span", "button");
                load_more_button.in("Load More")
                dataContainer.element.data_container.add("data-type", request.search.get("path"));
                load_more_button.event.on(e => dataContainer.loadMediaLibrary(request, dataContainer.currentPage))
            }
            dataContainer.element.data_container.removed("hidden");
            for (const file of data.files) {
                image = dataContainer.image_sowing_container(file, `<i class="fa-duotone fa-ellipsis-vertical"></i>`)
                library_content.in(image)
            }

            isLoading = false;
            dataContainer.currentPage++;
        }

        this.request_library.change_path("/media/library");
        this.request_library.send((request.url.search + "&page=" + page).slice(1));

        return
        $.fch('/media/library' + request.url.search + "&page=" + page, e => dataContainer.mainProgresr(e))
            .then(response => response.json())
            .then(data => {
                var load_more_button, library_content = dataContainer.element.data_container.choose("library-content");

                if (dataContainer.element.data_container.get("data-type") != request.search.get("path")) {
                    dataContainer.element.data_container.clear()
                    library_content = dataContainer.element.data_container.choose("library-content") || dataContainer.element.data_container.create("library-content")
                    load_more_button = dataContainer.element.data_container.create("load-more-button").create("span", "button");
                    load_more_button.in("Load More")
                    dataContainer.element.data_container.add("data-type", request.search.get("path"));
                    load_more_button.event.on(e => dataContainer.loadMediaLibrary(request, dataContainer.currentPage))
                }
                dataContainer.element.data_container.removed("hidden");
                for (const file of data.files) {
                    image = dataContainer.image_sowing_container(file, `<i class="fa-duotone fa-ellipsis-vertical"></i>`)
                    library_content.in(image)
                }

                isLoading = false;
                dataContainer.currentPage++;
            })
            .catch(error => {
                console.error('Error:', error);
                isLoading = false;
            });
    }
    this.mainProgresr = function (progresr) {
        this.element.IN001.style.display = "block";
        this.element.IN001.style.width = progresr + "%";
        if (progresr == 100) {
            setTimeout(() => {
                this.element.IN001.style.display = "none";
            }, 2000);
        }
    }
    return this;
});

dataContainer.add("previewImages", function previewImages() {
    const files = dataContainer.element.file_upload.files;
    dataContainer.element.preview.innerHTML = '';
    console.log("previewImages");

    if (files.length > 0) {
        dataContainer.element.uploader.add("hidden")
    }

    function getVideoThumbnail(e, thumbnail) {
        const video = document.createElement('video');
        video.src = e.target.result;

        video.addEventListener('loadeddata', function () {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = video.videowidth;
            canvas.height = video.videoHeight;

            // Seek to a specific time (e.g., 1 second)
            video.currentTime = 1;

            video.addEventListener('seeked', function () {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                // thumbnail.src = canvas.toDataURL('image/png');
                thumbnail(canvas.toDataURL('image/png'));
            });
        });
    }



    const otter = new $(function otter(a) {
        this.image = function (a, b, c) {

        }
        this.video = function (a, b, c) {

        }
        this.audio = function (a, b, c) {

        }
        this.pdf = function (a, b, c) {

        }
    });

    function onload(image_data, file) {
        var image_containers = dataContainer.image_sowing_container(image_data, `<i class="fa-duotone fa-ellipsis-vertical"></i>`)
        console.log(image_containers);
        image_containers.load_image = function () {
            dataContainer.uplodeFile(file, image_containers);
            return
            uploadImages(file, image_containers)
        }
        dataContainer.element.preview.appendChild(image_containers);
    }

    for (const file of files) onload({
        name: file.name,
        type: file.type,
        size: (file.size / 1024).toFixed(2) + " KB",
        fileType: dataContainer.isfiles(file.type)
    }, file)

})

dataContainer.add("uplodeFile", function uplodeFile(file, element) {
    const formData = new FormData();
    formData.append('files', file);
    this.request_library.change_path("/media/upload");
    console.log(this.request_library);

    this.request_library.progress = function (e) {
        element.progress.p.style.display = "flex"
        element.progress.style.cssText = "--value :" + e;
        // if (e == 100) {element.progress.style.width = 0;}
        console.log(e);
    }
    this.request_library.send(formData);


    // if (data.error) {
    //     console.log(data.error);
    // }
    // else {
    //     data = new $.array(data);
    //     element.progress.p.style.display = "none"
    //     element.set_thumbnail(data.is("thumbnail"));
    // }

})





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

const request = new $.request();

dataContainer.importClass([
    "uploader",
    "IN002",
    "right-IN038"
])
dataContainer.importId([
    "preview",
    "file-upload",
    "upload-btn",
    "data-container",
])

// document.getElementById('insert-url-btn').addEventListener('click', insertFromUrl);
// document.querySelectorAll('.menu-btn').forEach(btn => btn.addEventListener('click', filterMediaLibrary));

console.log(dataContainer);
dataContainer.element.file_upload.addEventListener('change', dataContainer.previewImages);

$.event("media-group", function (e) {
    const request = new $.request();
    dataContainer.importClass(["title", "session-container"]);
    dataContainer.importNodes("media_group", e.weres("list"))
    dataContainer.importElement(e.p.choose("indector"));

    var upload;
    $.weres("list").filter(e => e.get("aria-label") == "upload").for(e => upload = e);

    upload.event.on(function () {
        request.search.set("path", "upload");
        dataContainer.element.uploader.removed("hidden"), dataContainer.element.right_header_session.clear(), dataContainer.element.preview.clear()
    })

    console.log(dataContainer.nodes.media_group);
    dataContainer.nodes.media_group.for(e => e.event.on(function () {
        dataContainer.currentPage = 1;
        request.search.set("path", e.get("aria-label"))
    }))


    request.functions = function () {
        var button_position, path = this.search.get("path");
        if (!path) { request.search.set("path", "all_media") }

        $.weres("a", false).filter(e => e.get("aria-label") == path).for(e => button_position = e.get())
        dataContainer.element.title.in(button_position.target.innerHTML)
        button_position.target.p.append(dataContainer.element.indector)
        button_position.set_preant()
        dataContainer.element.indector.style.top = button_position.to_top + "px"

        if (path != "upload") {
            // Initial load
            dataContainer.loadMediaLibrary(request, dataContainer.currentPage);
        }


        dataContainer.element.session_container.children.for(function (item) {
            item.get("data-type") == path
                ? item.removed("hidden")
                : item.add("hidden")
        })
    }

    request.functions()
}, true)


