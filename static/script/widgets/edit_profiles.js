$.define(function EditProfiles(settings) {
    const { is, getString, isExtend, F } = $.getFunction();
    const { session, extend, bind } = isExtend();


    const member = settings.member;
    if (!member.name) {
        return settings.window();
    }

    extend(function getContainer(a, b) {
        return settings.each.IN091.create("edite-container")
    })

    function Form(module) {
        let img, ich, inf, imp, bex = session.getContainer();
        let form = module(settings.each.IN091);

        let website = getString("Website")
        let name = getString("Name")
        let username = getString("User Name")
        let biography = getString("Biography")
        let gender = getString("Gender")
        let description_w = getString("Editing your links is only available on mobile. Visit the MyApplication $ and edit your profile to change the websites in your biography.")
        let description_g = getString("This won't be part of your public profile.")



        form.input({
            title: website,
            disabled: "disabled",
            type: "text",
            name: "website",
            spellcheck: "true",
            placeholder: website,
            description: description_w
        });

        form.input({
            title: name,
            type: "text",
            name: "name",
            value: member.name,
            spellcheck: "true",
            placeholder: "Full Name",
        });

        form.input({
            title: username,
            type: "text",
            name: "username",
            value: member.username,
            spellcheck: "true",
            placeholder: username,
        });

        form.textarea({
            title: biography,
            type: "text",
            name: "biography",
            value: member.biography,
            spellcheck: "true",
            placeholder: biography,
        });

        form.select({
            title: gender,
            name: "gender",
            value: ["Prefer Not to Say", "Female", "Male"],
            checked: member.gender,
            addCustonValue: true,
            description: description_g
        })

        form.change = function (event, action) {
            var submitValue = action.getValue();
            var submitButton = action.getSubmitButton();
            var checkValue = function (a, b) {
                return is(a) && is(b)
                    ? a.trim() == b.trim()
                    : false;
            }
        }

        form.addCaptcha();
        form.submitButton("Submit");

        bex = bex.create("padding-twenty width DIS01", false, 0);
        img = bex.create("member-image")
        inf = bex.create("member-info");
        ich = bex.create.button("button image-change")

        imp = img.create({
            tagName: "img",
            src: member.img,
            id: "member_atr",
            alt: "User Image",
        })
        inf.create("name", member.username)
        inf.create("namea", member.name)
        ich.in("Change Image")
        settings.each(imp)
        ich.event.on(e => settings.load_image.call(imp))

        form.finish = function (query) {
            $.loader(false);
            let update = query.is("update");
            let message = query.is("message");
            message ? $.message(message) : null;
            for (const [name, value] of Object.entries(update || {})) {
                settings.member.add(name, value)
            }
            settings.window();
        }
        form.error = function (query) {
            $.loader(false);
            console.log(query);

            let inputs = form.getInputs();
            let errors = query.is("error") || {};

            let [c, t] = errors.details || [];
            if ("captcha_virification_error" == c && t) {
                $.alert(t), form.resetCaptcha();
            }

            // errors.for(function (item) {
            //     const input = inputs.find(e => e.name == item[0]);
            //     if (input && F(input.showError)) {
            //         input.showError(item[1])
            //     }
            //     if (item[0] == "captcha_virification_error") {
            //         query.alert(item[1]);
            //         form.resetCaptcha();
            //     }
            // })
        }


        form.setRequestRoot("profile/edit");

        let bodx = form.getForm();
        bodx.create.input({
            disabled: "disabled",
            type: "text",
            name: "email",
            value: member.email
        }).css({ display: "none" });
        $.loader(false)
    }

    $.require("widgets/forms", Form).css();
    return session;
})