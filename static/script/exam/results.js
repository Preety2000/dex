// © 2025 Your MyApplication. All rights reserved.
// This script is licensed under the MIT License.
$(function results(_, a, b, c, d, e, f, g, h, i, j, k, l, T, U) {
    "use strict";

    // Helper to get query string parameters
    function getQueryParam(key, defaultValue) {
        const url = new URL(window.location.href);
        return url.searchParams.get(key) || defaultValue;
    }

    const {
        FlEXMAP, SEOPES, F, S, N, B, A, E, I, script
    } = $.getFunction();

    $.loader(true)
    const utils = $.req(() => false);
    const actionMap = FlEXMAP({ eventLogger: true });
    const apiRequest = $.apirequest("auth/r");

    let isActionHandling = false;

    function handleInitialAction() {
        if (isActionHandling) return false;

        const queryParam = getQueryParam('q');
        const pw = getQueryParam('pw');

        if (pw === 'add_student') {
            // Handle adding student if needed
        }

        if (Number(queryParam)) {
            // Some logic based on `q`
        }

        return true;
    }

    function get_watermark(container = $("container")) {
        var text = '';
        for (let index = 0; index < 500; index++) {
            text += `   STUDYHUB TRAINING INSTITUTE`
        }
        var css = $.create({
            tagName: "style",
            inner: `.container::before { content: "${text}";display:none;}`
        })
        document.body.append(css);

    }

    function sendApiRequest(payload = null, fallbackHandler = () => { }) {
        if (!handleInitialAction() || apiRequest.getResponceCount > 0) return;

        apiRequest.progress = function (count) {
            // Optional: handle progress count
        };

        apiRequest.send(payload, function (response, raw) {
            apiRequest.getResponceCount++;

            console.log("ok");


            const params = response.getParams();
            const boundHandler = actionMap.get(params.__ac);

            if (params.jump) {
                utils.navigate(params.jump);
                return;
            }

            if (F(boundHandler)) {
                boundHandler(params, raw);
            } else {
                fallbackHandler.call(this, params, raw);
            }

            $.loader(false);
        });

        return apiRequest;
    }

    function registerAction(key, handler) {
        return actionMap.add(key, handler);
    }

    registerAction(301, function result(query) {
        const result_dg = $("result_dg ", true);

        console.log(result_dg);


        const [
            [result_no, exam_name, category, published, result_year],
            [total_questions, incorrect_count, correct_count, skipped_count, attempt_questions],
            list_in_paper,
            [total_marks, total_obtained_marks, percentage, marks_in_word, total_grade, result],
            [sname, roll_number, ragistration_number],
            [examinant, instructor]
        ] = query;

        const templateRow = result_dg.choose('list_on_paper');
        const template = templateRow.innerHTML;

        templateRow.innerHTML = list_in_paper.map(
            ([paper_name, m, [
                paper_total_marks,
                paper_obtained_marks,
                percentage,
                marks_in_word,
                paper_grade,
                result
            ]]) => {

                const placeholders = {
                    paper_name,
                    paper_obtained_marks: String(paper_obtained_marks),
                    paper_total_marks,
                    marks_in_word,
                    paper_grade,
                    percentage,
                    result
                };

                return template.replace(
                    /\{\{(.*?)\}\}/g,
                    (_, key) => placeholders[key.trim()] ?? ''
                );
            }
        ).join('');

        // Replace main placeholders
        const placeholders = {
            result_no, exam_name, examinant, published, result_year, instructor,
            total_questions, attempt_questions, result,
            total_marks, total_obtained_marks, percentage, total_grade,
            sname, roll_number, ragistration_number
        };
        const empty = []
        result_dg.innerHTML = result_dg.innerHTML.replace(
            /\{\{(.*?)\}\}/g,
            (_, key) => placeholders[key.trim()] ?? (empty.push(key.trim()), '')
        );
        for (const i of empty) {
            result_dg.choose(i)?.remove()
        }
        const instructor_img = result_dg.choose("instructor_img");
        instructor_img && (instructor_img.src = instructor);
        result_dg.css({ display: "block" });

        get_watermark();
    })

    registerAction(302, function message(query) {
        const __result = $("__result");
        __result.css({ margin: 40 })
        __result.create("h2", "title").in($.title)

        for (const i of query.desc) {
            __result.create("p", "desc").in(i)
        }

    })

    function triggerActionByKey(key, callback = () => { }) {
        sendApiRequest(null, function handleAction(params) {
            const action = params.get("__ac");
            if (action && Array.isArray(action) && action.length === 2) {
                const [code, data] = action;
                const handler = actionMap.get(code);
                if (typeof handler === "function") {
                    handler(data);
                }
            }
            console.log("Action Params:", action, actionMap);
        }
        );
    }

    utils.onChange(() => triggerActionByKey(800));
    triggerActionByKey(800);
});