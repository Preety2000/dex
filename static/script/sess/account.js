

$.define(function Account(a, b, u = $.create("IN081 dialog")) {
    u.create("IN082").create.span("IN083", "@{{auth_session.username}}").p.create.span("icon button dialog-close", `{{ svg.ic_close | safe }}`).event.on(e => a.close());
    u.create("IN086").create({
        tagName: "img",
        src: "{{auth_session.img or 'icon/member.png'}}?size=200x200",
        alt: "User"
    });
    u.create("IN084 ", "{{function.utc('Hello')}}, <strong>{{ auth_session.name }}</strong>");
    u.create("IN085 ").create({
        tagName: "a",
        class: "button manage",
        href: "/settings/profiles/edit",
        title: "{{function.utc('Edit Account')}}",
        inner: "{{function.utc('Edit Account')}}"
    }).p.create.button("button logout", "{{function.utc('Logout')}}").event.on(e => a.logout(e, "{{ auth_session.device|length }}")).p.create({
        tagName: "a",
        class: "IN087",
        href: "/exam/dashboard",
        title: "{{ function.utc('Test List') }}",
        inner: `<span>{{ function.utc('Test List') }}</span>`,
        icon: "ic_link"
    }).p.create({
        tagName: "a",
        class: "IN087",
        href: "/exam/r/dashboard",
        title: "{{ function.utc('Test dashboard') }}",
        inner: `<span>{{ function.utc('Test dashboard') }}</span>`,
        icon: "ic_link"
    }).p.create({
        tagName: "a",
        class: "IN087",
        href: "/liked-questions",
        title: "{{ function.utc('Liked Questions') }}",
        inner: `<span>{{ function.utc('Liked Questions') }}</span>`,
        icon: "ic_link"
    });
    return u
});

