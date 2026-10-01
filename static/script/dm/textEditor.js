// Assuming EventEmitter is an object
const EventEmitter = {};
const hedlineHendel = function (e, button, select, query, callBack) {
    e.preventDefault();

    var selectContainer = select.create("F0002");
    for (const item in query) {
        selectContainer.create("option", "button").add("value", item).in(query[item]).event.on(function () {
            this.value = this.get("value");
            button.add("jsname", item).in(query[item]);
            selectContainer.remove();
            callBack(this);
        });
    }
    return selectContainer;
}

const selectElement = function (query, container, callBack, name, selected) {
    var checked = query[selected] || "Select", button, select = container.create("select").add("name", name);
    button = select.create.button("button select-button")
        .add({ type: "button", jsname: selected })
        .in(checked).event.on(event => hedlineHendel(event, button, select, query, callBack));

    button.data = query;
    return button;
};

const inputElement = function (attributes, labelText, context) {
    if (!attributes.name) attributes.name = $.makeid(16);
    var inputWrapper = (context || $).create("F0011 " + attributes.type).create.input("input");
    inputWrapper.p.create.label("label", labelText).add("for", attributes.name);

    for (const name in attributes) {
        inputWrapper.add(name, attributes[name]);
    }
    return inputWrapper;
};

const actionGroup = $(function actionGroup() {
    return this
});

const button = function (a, b, c) { };
const Session = function (option, editor) {
    this.value = editor.container.value;
    for (const [name, value] of Object.entries(option)) {
        this[name] = value;
    }
    // this.change = function () {}
    return this;
}

const bind = function (editor) {
    var selection;
    const createActionButton = function (attributes, container, iconClass, action) {
        const button = container.create.button("button option-button");
        attributes.type = "button"
        actionGroup.add(attributes.id, button);
        for (const [attribut, value] of Object.entries(attributes)) {
            button.add(attribut, value);
        }
        button.action = action;
        button.container = container;
        button.event.on(toggleButtonAction);
        button.create("icon", "fa-solid fa-" + iconClass);
        return button;
    };

    const toggleButtonAction = function (event) {
        event.preventDefault();
        let command = this.isclass("active");
        this.container.children.for(e => e.removed("active"))
        modifyText(this.id, command, null);
        !command && this.action === true ? this.add("active") : null;
        console.log(this);

    };

    const getOrCreateActionButton = function (actionId, actionCommand, container, iconClass, action) {
        return actionGroup[actionId] || createActionButton({ id: actionId, jsname: actionCommand }, container || actionGroup.header, iconClass, action);
    };

    const getOrCreateSelectButton = function (actionId, options, container, selectedValue) {
        actionGroup[actionId] = actionGroup[actionId] || selectElement(options, container, e => modifyText(actionId, false, e.value), actionId, selectedValue);
        actionGroup[actionId].active = selectedValue;
        return actionGroup[actionId];
    };

    const insertNodeAtSelection = function (node, selectionRange) {
        selectionRange = selectionRange || editor.getSelection();
        if (selectionRange.rangeCount > 0) {
            const range = selectionRange.getRangeAt(0);
            range.deleteContents();
            range.insertNode(node);
        }
    };

    // Function to remove all text alignment
    const clearTextAlignment = function (node, selectionRange) {
        selectionRange = selectionRange || editor.getSelection();
        console.log(selectionRange);

        if (selectionRange.rangeCount > 0) {
            const range = selectionRange.getRangeAt(0);
            const container = range.commonAncestorContainer.parentElement;
            if (container.nodeType === Node.ELEMENT_NODE) {
                container.style.textAlign = '';
            }
        }
    }

    const createLinkDialog = function (selectionText, actionId) {

        var selectedText = selectionText.toString();
        var linkContainer = $.create("link-container");
        var container = (editor.container.p.choose("create-link") || editor.container.p.create("fixed create-link"));
        var closeContainer = function () {
            actionGroup.export("link").removed("active");
            container.remove();
        }

        var titleInput = inputElement({ type: "text", value: selectedText }, "Text to display", linkContainer);
        var urlInput = inputElement({ type: "text", placeholder: "Enter URL" }, "Paste or search for a link", linkContainer);
        var targetCheckbox = inputElement({ type: "checkbox" }, "Open this link in a new window", linkContainer);
        var nofollowCheckbox = inputElement({ type: "checkbox" }, "Add 'rel=nofollow' attribute (Learn more)", linkContainer);

        var footer = linkContainer.create("footer");
        container.in(linkContainer);
        footer.create.button("button").add("type", "button").in("Cancle").event.on(closeContainer)
        footer.create.button("button").add("type", "button").in("Apply").event.on(function () {
            actionGroup.export("link").add("active");
            var linkElement = $.create.a("link");
            var title = titleInput.value || selectedText;
            var url = urlInput.value;

            if (targetCheckbox.checked) linkElement.add("target", "_blank");
            if (nofollowCheckbox.checked) linkElement.add("rel", "nofollow");

            if (url) {
                linkElement.add("href", url).in(selectedText).add("title", title);
                insertNodeAtSelection(linkElement);
                container.remove();
            } else {
                urlInput.addClass("error_value");
            }
        });

        container.create("close").add("type", "button").event.on(closeContainer);
    };

    const modifyText = (command, showUI, value) => {
        if (!editor.document) return;

        console.log("modifyText", command, showUI, value);

        const selection = editor.getSelection();
        const executeCommand = (cmd, ui, val) => {
            const alignment = new this.alignment();
            if (ui === true && Object.entries(alignment).filter(([e,]) => e == cmd).length == 1) {
                alignment.clearValue()
            }
            else { editor.document.execCommand(cmd, ui, val) }

        };

        if (command === "link" && selection.rangeCount > 0) { createLinkDialog(selection, command) }
        else if (command === "strong") {
            showUI == true
                ? executeCommand("bold", showUI, value)
                : insertNodeAtSelection($.c("strong").in(selection.toString()));
        }
        else { executeCommand(command, showUI, value); }
    };

    bind.prototype.container = function (context) {
        var formatBlock = new this.formatBlock();
        for (const blockTag in formatBlock.block) {
            if (context.target.nodeName.toLowerCase() === blockTag.toLowerCase()) {
                formatBlock.button.add("jsname", context.target.nodeName).in(formatBlock.block[blockTag]);
            }

        }

        for (const [, element] of actionGroup) {
            let target = context.target;
            let isMatch = false;

            for (let i = 0; i < 4 && target; i++) {
                if (target.nodeName.toLowerCase() === element.get("jsname")) {
                    isMatch = true;
                    break;
                }
                target = target.parentElement;
            }

            isMatch ? element.add("active") : element.removed("active");
        }

    };

    bind.prototype.modifyText = modifyText;
    this.undoRedo = function (context) {
        this.undo = getOrCreateActionButton("undo", false, context, "rotate-left");
        this.redo = getOrCreateActionButton("redo", false, context, "rotate-right");
        return this;
    };

    this.formatBlock = function (context) {
        this.block = {
            H1: "Major Heading",
            H2: "Heading",
            H3: "Subheading",
            H4: "Minor Heading",
            H5: "Small Heading",
            p: "Paragraph",
            div: "Normal"
        };
        this.button = getOrCreateSelectButton("formatBlock", this.block, context, "p");
        return this;
    };

    this.format = function (context) {
        this.strong = getOrCreateActionButton("strong", 'strong', context, "strong", true);
        this.bold = getOrCreateActionButton("bold", 'b', context, "bold", true);
        this.italic = getOrCreateActionButton("italic", 'i', context, "italic", true);
        this.underline = getOrCreateActionButton("underline", 'u', context, "underline", true);
        this.strikethrough = getOrCreateActionButton("strikethrough", 'strike', context, "strikethrough", true);
        return this;
    };

    this.script = function (context) {
        this.superscript = getOrCreateActionButton("superscript", 'sup', context, "superscript", true);
        this.subscript = getOrCreateActionButton("subscript", 'sub', context, "subscript", true);
        return this;
    };

    this.list = function (context) {
        this.orderedList = getOrCreateActionButton("insertOrderedList", false, context, "list-ol");
        this.unorderedList = getOrCreateActionButton("insertUnorderedList", false, context, "list");
        return this;
    };

    this.link = function (context) {
        this.link = getOrCreateActionButton("link", 'a', context, "link");
        this.unlink = getOrCreateActionButton("unlink", false, context, "unlink");
        return this;
    };

    this.alignment = function (context) {
        this.justifyLeft = getOrCreateActionButton("justifyLeft", false, context, "align-left", true);
        this.justifyCenter = getOrCreateActionButton("justifyCenter", false, context, "align-center", true);
        this.justifyRight = getOrCreateActionButton("justifyRight", false, context, "align-right", true);
        this.justifyFull = getOrCreateActionButton("justifyFull", false, context, "align-justify", true);
        this.clearValue = clearTextAlignment
        return this;
    };

    this.spacing = function (context) {
        this.indent = getOrCreateActionButton("indent", false, context, "indent");
        this.outdent = getOrCreateActionButton("outdent", false, context, "outdent");
        return this;
    };

    return this;
};

Editor = function Editor(renderer, session, options) {
    this.container = $(renderer);
    var $session = new Session(session, this);
    var editor = this
        , Event = function (a) {
            // Update the editor container's innerHTML with the target's innerHTML
            $session.value = a.target.innerHTML;
            editor.container.innerHTML = $session.value;
            // Set the target to the editor container
            this.target = editor.container;

            // Safely copy properties from the target's prototype if necessary
            for (const name in Object.getPrototypeOf(this.target)) {
                if (!this.hasOwnProperty(name)) {
                    this[name] = this.target[name];
                }
            }

            return this;
        }
        , bind_item = new bind(editor);
    if (!actionGroup.header) {
        actionGroup.header = $session.toolbar || this.container.p.create({ class: "ed_toolbar", id: "ed_toolbar" })
    }

    for (const n in bind_item) {
        if (Object.hasOwnProperty.call(bind_item, n)) {
            new bind_item[n](actionGroup.header.create("button-container").add("id=container_" + n))
        }
    }

    this.setSession($session || options && options.$session);
    this.document = this.container.p.c("iframe.editor-area[id=text_editor|src=about:blank]").css({ height: this.container.get.px('height'), width: this.container.get.px('width') }).contentDocument
    this.document.open();
    // this.document.write(`<head><style>body{padding:4px 8px !important;font-size: 13pt!important;}</style><link rel="stylesheet" id="main_style" href="/css/article.css"></head><body class="article-content" role="textbox" contenteditable="true">${$session.value || ""}</body>`);
    this.document.write(`<head><style>body{padding:4px 8px !important;font-size: 13pt!important;}</style><link rel="stylesheet" id="main_style" href="/css/index.css"><link rel="stylesheet" id="main_style" href="/css/article.css"></head><body class="article-content" role="textbox" contenteditable="true">${$session.value || ""}</body>`);
    this.document.close();
    this.document.body.addEventListener("mousedown", function (e) {
        $session.cursor = e;
        $session.target = e.target;
        bind_item.container($session);
    });

    this.document.addEventListener("input", function (e) {
        if (e.target.innerHTML.length <= 1 && !editor.document.queryCommandValue('formatBlock')) {
            bind_item.modifyText('formatBlock', false, 'p')
        }
        $session.change(new Event(e))
        // $session.change( EventEmitter(e))
    });

    actionGroup.header.css({ display: "block" })
    this.container.css({ display: "none" });
}


Editor.prototype.setSession = function (session) {
    this.session = session;
    EventEmitter.addEventListener = function (eventName, callback, capturing = false) {
        // Initialize the event registry if it doesn't exist
        this._eventRegistry = this._eventRegistry || {};

        // Get the listeners for the event name, or create an empty array if none exist
        var listeners = this._eventRegistry[eventName] || (this._eventRegistry[eventName] = []);

        // Add the callback to the list if it hasn't been added already
        if (listeners.indexOf(callback) === -1) {
            // Add to the beginning if capturing, otherwise to the end
            listeners[capturing ? "unshift" : "push"](callback);
        }

        // Return the callback for reference
        return callback;
    };
};
Editor.prototype.getSession = function () {
    return this.session;
};
Editor.prototype.setValue = function (val, cursorPos) {
    this.session.doc.setValue(val);
    if (!cursorPos)
        this.selectAll();
    else if (cursorPos == 1)
        this.navigateFileEnd();
    else if (cursorPos == -1)
        this.navigateFileStart();
    return val;
};
Editor.prototype.getValue = function () {
    return this.session.getValue();
};
Editor.prototype.getSelection = function () {
    return this.document.getSelection();
};
Editor.prototype.session = function () {
    return this.session;
};

if (typeof $ != "undefined") {

    var ed_toolbar = new Editor("editor-area", {
        toolbar: $("ed_toolbar", true),
        updateValue: true
    });

    var weres = $.weres("button")
    $.buttonAnimation(weres);

    console.log(ed_toolbar);

    ed_toolbar.session.change = function (e) {
        console.log(ed_toolbar.session, e);
    }
}


