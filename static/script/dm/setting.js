var loader = function (a = $) {
    return a.create("img", "loader").add("src", "/static/icon/loading.gif")
}

// This code defines a function `option_container` that sets up a UI component for selecting and managing options.
// It provides a session for tooltips, option groups, and handles edit/save functionality.
const option_container = function OptionContainer(choose = $, option) {

    // Declare variables, including the currently active database (activedatabese), and the session structure.
    let activedatabese,
        session = choose.create("choose-session"), // Create the main session element.
        tolltip = session.create("tolltip"),           // Create a tooltip element inside the session.
        group = session.create("IN0104");               // Create a group element inside the session.

    // Define the 'save' function, which adds the "active" class to the group and updates the button with "save".
    let save = function (button) {
        group.add("active");  // Add 'active' class to the group.
        button.in("save");    // Set the button text to 'save'.
    };

    // Define the 'edit' function, which handles editing logic.
    let edit = function (button) {
        button.clear();          // Reset the button state.
        loader(button);         // Display a loader on the button.

        // Retrieve value from the provided option function using the active database.
        let value = option.function(activedatabese);
        if (value) {
            // If a value is returned, update the tooltip with the active database's title.
            tolltip.choose("optioner").in(activedatabese.title);
            group.removed("active");  // Remove 'active' class from the group.
            button.in("edit");        // Set the button text to 'edit'.
        } else {
            // If no value is returned, show an alert that the database is not set and call save.
            window.alert("Sorry DataBase Not Set");
            save(button);
        }
    };

    // Loop through the provided option items to create option buttons.
    for (const item of option.option) {
        let list = group.create.button("option-list", item.title); // Create a button for each option in the group.

        // Attach event to handle button clicks.
        list.add(item).event.on(function () {
            this.active();         // Mark the clicked button as active.
            activedatabese = item; // Set the clicked item as the active database.
        });

        // Define a method to handle marking the active button.
        list.active = function () {
            group.childrens.for(e => e.removed("active")); // Remove 'active' class from all children.
            list.add("active");                            // Add 'active' class to the clicked list.
        };

        // If the current option's value matches the initial value, set it as active.
        if (option.value == item.value) {
            activedatabese = item;
            list.active();  // Mark the corresponding list item as active.
        }
    }

    // Create the left tooltip, displaying the option title and active database title.
    tolltip.create("tolltip-left")
        .create.span("title-session", option.title)
        .p.create.span("optioner", activedatabese.title);

    // Create the right tooltip with an edit link, handling the click event for edit/save actions.
    tolltip.create("tolltip-right")
        .create.a("link", "edit")
        .event.on(function () {
            group.isclass("active")  // If the group has the 'active' class...
                ? edit(this)         // Call the 'edit' function if active.
                : save(this);        // Call the 'save' function if not active.
        });
}

$.define("dm/setting", function adminSetting(was, database, c) {
    console.log("AdminSetting js");
    option_container(database, {
        title: "DataBase",
        value: "database1",
        function: function (e) {
            console.log(e);
            return true
        },
        option: [
            { "title": "DataBase Hindi", "name": "database1", "value": "database1" },
            { "title": "DataBase English", "name": "database2", "value": "database2" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
            { "title": "DataBase Sankrit", "name": "database3", "value": "database3" },
        ]
    })

})
