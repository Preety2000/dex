isdefine("tableNav", function tablenav(was, extend, modules) {
    "use strict";

    const { is, S, N, F, B, E, A } = $.getFunction();

    const isModules = function (array) {
        return modules.is(array)
    };


    modules.add("filter", function ACANS(filter) {
        // Import the form module and PopupWindow from previously defined modules
        var form = was.export("form");
        var PopupWindow = was.export("PopupWindow");

        // Create a new popup window with the title "Filter"
        var data = filter.get("filter");
        var popupWindow = PopupWindow("Filter");

        // Initialize the form inside the popup window container
        form = form(popupWindow.container);

        data = JSON.parse(data.replaceAll("'", '"'))

        console.log(data);


        // Create a switch input holder inside the form for toggling subject options
        form.accordion({
            title: "Show data in.",
            name: [
                { name: "ase", value: "Ascending" },
                { name: "desc", value: "Descending" },
            ],
            switchValue: ["title", "id", "date"]
        });

        var pages = []
        for (let item = 1; item < data.total_pages; item++) {
            pages.push(["Page number", item])
        }
        console.log(pages);


        // Create a switch input holder inside the form for toggling subject options
        form.accordion({
            title: "List of page",  // Title of the switch
            name: "page",                    // Name attribute for the switch input
            switchValue: pages       // Values for the switch (on/off)
        });

        // Create a submit button with the label "Add Subject"
        form.submitButton("Action");

        // Override the form's submit method to handle form submission
        form.submit = function () {

            var eq, request = new $.request();
            for (const [name, value] of Object.entries(form.getValue())) {
                if (eq = request.search.get(name)) {
                    console.log(name == "asc" ? "desc" : name);

                    request.search.delete(name == "asc" ? "desc" : name, false)
                }
                if (value) { request.search.set(name, value, false) }
            }
            console.log(request, request.url.href);

            // request.updateHistory()
        };
    });

    $.weres("a", false).filter(e => e.href == "javascript:void(0)").for(function (button) {
        button.event.on(function () {
            var modules = isModules(this.get("jsname"))
            if (F(modules)) {
                modules(this)
            }
        })
    })
})
