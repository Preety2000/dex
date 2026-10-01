

// cif
function createInputField(options, parent = $, ps) {
    const {
        F0012,
        name,
        title,
        description,
        desc,
        type,
        tagName = "input",
        ...attrs
    } = options;

    // Wrapper
    const wrapper = title
        ? parent.create("block")
        : parent;


    // Label
    const label = $.create({ tagName: "label", for: name, });
    const ti = title && label.create("F0019", getString(title));
    desc && label.create.p("F0020", getString(desc));
    attrs.required && ti && ti.create.span(null, "*");


    // Input element
    const g = { tagName, name, id: name, type: type || "text", ...attrs }
    const input = ["img", "file"].includes(type)
        ? fileInput($, g)
        : $.create(g);


    F0012
        ? (wrapper.add("F0012"), wrapper.append(input, label))
        : wrapper.append(label, input)

    input.event.input(e => body.change(e, form));

    // Bottom description
    description && wrapper.create.p("description", getString(description));

    // Error handler
    input.showError = function (message) {
        let errorBox =
            wrapper.choose(input_error) ||
            $.create.p(input_error);

        errorBox.in(message);
        wrapper.add("IN0101");
        wrapper.insertBefore(errorBox, input);
    };

    // Metadata
    input.wrapper = wrapper;
    input.header = wrapper;

    allInputs.add(input);


    const re = input.remove;
    input.remove = function (a, b) {
        const m = ps || parent, { p, childrens } = m, pos = [...p.children].indexOf(m);
        re.call(this, a, b); allInputs.delete(input); m.remove();
        input.reStore = () => {
            p.in(m, pos);
            for (const i of childrens) m.append(i);
            m.append(input); allInputs.add(input)
        }
    };


    return input;
}