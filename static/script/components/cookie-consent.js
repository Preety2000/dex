// Cookie Script
$.DOMContentLoaded(query => (!function (coocke, bind) {
    const { E } = $.getFunction();
    var bt
        , ac = function (query) {
            return bn.remove();
        }
        , ab = function (bn) {
            return bn.create({
                tagName: "a",
                class: "IN096 button",
                inner: "Accept"
            });
        }
        , ad = function (bt, ar) {
            ar.finish = ac;
            ar.send({ accept: "all" });
        }
        , [bn, ar] = coocke.get() == null
            ? bind($.getHtmlBody(), $.apirequest("setting/accept-cookie"))
            : [null, null]

    if (E(bn) && (bt = ab(bn))) {
        bt.event.on(e => ad(bt, ar))
    }

}($.cookie("_cf_bQ"), function (b, api, bn = b.create("IN095")) {
    bn.create({
        tagName: "p",
        inner: `We use <strong>cookies</strong> to improve your experience on our site.
                You can <a href="/privacy-policy" target="_blank" class="c-link">change your preferences</a> any time.`
    });
    return [bn, api]
})))
