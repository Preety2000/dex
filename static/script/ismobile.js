
$.define("mobile", function Mobile(documentbody) {
    "use strict";
    $.event("IN0103", function (slider) {
        console.log("IN0103");


        const dotsContainer = $('dots');
        const slides = $.weres('slide');
        const numSlides = slides.length;
        const scrollInterval = 3000;
        let currentIndex = 0;
        let autoScroll;

        // Create dots
        for (let i = 0; i < numSlides; i++) {
            const dot = $.create.span("dot");
            dot.dataset.index = i;
            dotsContainer.appendChild(dot);
        }

        const dots = dotsContainer.weres('dot');
        dots[0].add('active');

        // Function to update dots based on scroll position
        function updateDots() {
            const slidewidth = slider.offsetWidth;
            const index = Math.round(slider.scrollLeft / slidewidth);
            dots.forEach(dot => dot.removed('active'));
            dots[index].add('active');
            currentIndex = index;
        }

        // Scroll event listener
        slider.addEventListener('scroll', updateDots);

        // Dot click event listener
        dots.for(function (dot) {
            dot.event.on(() => {
                const index = parseInt(dot.dataset.index, 10);
                clearInterval(autoScroll);
                slider.scrollTo({
                    left: index * slider.offsetWidth,
                    behavior: 'smooth'
                });
                autoScroll = startAutoScroll();
            })
        })
        // Function to start automatic scrolling
        function startAutoScroll() {
            return setInterval(() => {
                const nextIndex = (currentIndex + 1) % numSlides;
                console.log(nextIndex);

                slider.scrollTo({
                    left: nextIndex * slider.offsetWidth,
                    // behavior: 'smooth'
                });
                currentIndex = nextIndex;
                updateDots();
            }, scrollInterval);
        }

        // Initialize automatic scrolling
        autoScroll = startAutoScroll();

        // Optionally, initialize the dots
        updateDots();

    });

    // Mobile Search 
    $.event("search", (m
        , n = !0
        , a = "IN057"
        , b = new $.request()
        , c = b.search.get("q")
        , d = $.create("button IN059")
        , s = $.create("button IN058")
        , e = m.choose("input", false)
        , f = m.choose("IN047")
        , g = function (ev) {
            documentbody.removed(a);
            d.remove();
            s.remove();
            f.removed("hidden");
        }
        , h = function () {
            m.submit()
        }
        , i = function (ev) {
            ev.preventDefault();
            d.addIcon("ic_close", true);
            s.addIcon("ice_search", true);
            if (window.innerWidth < 980 && !$("IN059")) {
                var w = $.windows(null, { container: m, functions: g, noremove: true }, m.p);
                console.log(documentbody, a, d);
                documentbody.add(a);
                f.add("hidden");
                m.in(d, 0);
                m.in(s);
                d.event.on(ev => (ev.preventDefault(), w.close(), g()));
                s.event.on(ev => h);
            }
            e.focus();
        }) => f && f.event.on(i));



    // TOC Worker 
    $.weres('toc_a', (m, a, b
        , c = false
        , d = m.get("href")
        , e = { behavior: 'smooth' }
        , f = $(d, c)
        , g = function (m) {
            m.preventDefault();
            f.scrollIntoView(e);
        }) => m.event.on(g))

    return documentbody
});


function markdownToHtml(text) {
    // Convert headings
    text = text.replace("<p></p>", '');
    text = text.replace(/##### (.+)/g, '<h5>$1</h5>');
    text = text.replace(/#### (.+)/g, '<h4>$1</h4>');
    text = text.replace(/### (.+)/g, '<h3>$1</h3>');
    text = text.replace(/## (.+)/g, '<h2>$1</h2>');

    // Convert bold text
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a rel="noopener" target="_new" href="$2">$1</a>');

    // Convert code blocks
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Convert lists
    text = text.replace(/- (.+)/g, '<ul><li>$1</li></ul>');

    // Convert paragraphs and ensure proper spacing
    text = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');

    // Wrap in paragraphs
    text = '<p>' + text.replace(/<\/ul>\s*<ul>/g, '</p><p>').replace(/<\/p>\s*<p>/g, '</p><p>') + '</p>';

    return text;
}

function typeText(element, text, speed = 50) {
    let index = 0;
    innerHTML = "";

    function type() {
        if (index < text.length) {
            innerHTML += text[index];
            index++;
            element.innerHTML = innerHTML
            setTimeout(type, speed);

        }
    }

    type();
}