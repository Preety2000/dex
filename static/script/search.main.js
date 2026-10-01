// function s(e) { return document.querySelector('.' + e); }
function suggestionsRemove() { $.event('suggestions-items', e => e.remove()), inputBox.add('array-fill', false) }

function suggestionsAdd(val) {
    suggestionsRemove();
    var suggestions = [
        'how to create html website',
        'how to create website in html css',
        'how to create sidebar in html css',
        'how to make menu in html css',
        'how to make card in html css',
        'how to create an $',
        'how to create google forms',
        'how to create website using html css and javascript',
        'how to create website on blogger',
        'blogger theme',
        'how to add theme on bloger',
        'how to create login forms in html css',
        'login form in html css',
        'codewithar',
        'make website',
        'blogger website design',
        'blogger website kaise banaye',
        'blogger website ko google search me kaise laye',
        'blogger website adsense approval',
        'blogger website kaise banaye mobile se',
        'login form in html and css',
        'login form in html and css with source code',
        'login form in php and mysql',
        'login form in react js',
        'login form in html',
        'login form in php',
        'login form in angular',
        'login form in angular with validation',
        'login form in asp.net',
        'login form in android studio',
        'login form in java netbeans with database',
    ]
    
    if ((suggestions.length > 1) && val) {
        var count = 0;
        inputBox.add('array-fill', true);
        a = inputBox.create("suggestions-items");
        
        for (i = 0; i < suggestions.length; i++) {
            // matching letters
            m = suggestions[i].substr(0, val.length);
            /*check if the item starts with the same letters as the text field value:*/
            if (m.toUpperCase() == val.toUpperCase()) {
                count++
                /*create a DIV element for each matching element:*/
                b = $.create("list", "suggestions")

                /*make the matching letters bold:*/
                b.innerHTML = `<span class="one"> <strong>${m}</strong>${suggestions[i].substr(val.length)}</span>`;
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + suggestions[i] + "'>";
                b.innerHTML += '<svg focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"></path></svg>';
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.event.on(function (e) {
                    /*insert the value for the autocomplete text field:*/
                    sinput.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    suggestionsRemove();
                })

                a.appendChild(b);
                if (count > 6) { break; }
            }
        }
    }
}



var sinput = $('sinput');
var inputBox = $('contenar-inp');
var error = '!$&^:';

sinput.event.focusin(function () { suggestionsAdd(this.value), inputBox.add('focus') })
sinput.event.focusout(function () {
    inputBox.removed('focus'), suggestionsRemove();
})
sinput.event.input(function () {
    var val = this.value;
    suggestionsAdd(val);
    val ? (function () {
        var clear = $('clear-value');
        clear.event.on(function () {
            sinput.value = null;
            sinput.removeAttribute('value');
            inputBox.add('array-fill', false);
            suggestionsRemove();
        })
    }()) : inputBox.add('array-fill', false);
    sinput.add('value', val);
})


