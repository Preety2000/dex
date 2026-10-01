



const analyticsData = {
    v: 2,
    tid: 'G-QDRYX34JP5',
    gtm: '45je45t0v9167914159za200',
    _p: 1717386781820,
    gcd: '13l3l3l3l1',
    npa: 0,
    dma: 0,
    cid: '1635073819.1698674239',
    ul: 'en-us',
    sr: '1536x864',
    uaa: 'x86',
    uab: 64,
    uafvl: 'Google%2520Chrome%3B125.0.6422.113%7CChromium%3B125.0.6422.113%7CNot.A%252FBrand%3B24.0.0.0',
    uamb: 0,
    uam: '',
    uap: 'Windows',
    uapv: '15.0.0',
    _s: 1,
    sid: 1717386300,
    sct: 47,
    seg: 1,
    dl: encodeURIComponent(window.location.href),
    dr: encodeURIComponent(document.referrer),
    dt: encodeURIComponent(window.document.title),
    en: 'page_view',
    _ee: 1,
    tfd: 5667
};



if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
        function (position) {
            console.log('Latitude:', position.coords.latitude);
            console.log('Longitude:', position.coords.longitude);
        },
        function (error) {
            console.error('Error Code = ' + error.code + ' - ' + error.message);
        }
    );
} else {
    console.log("Geolocation is not available");
}



analyticsData.sr = window.outerwidth + "x" + window.outerHeight
window.onscroll = function (e) {
    console.log(e);
    if (analyticsData.en != "scroll") {
        analyticsData.en = "scroll";
        analyticsData.scroll= window.scrollY
        set_function = !0
    }
}









// Your analytics endpoint
const endpoint = 'http://127.0.0.1:4040/api/analytics/collect';
var set_function = !0

setInterval(() => {
    if (set_function === !0) {
        set_function = !1
        let queryString = new URLSearchParams(analyticsData).toString();
        let url = `${endpoint}?${queryString}`;

        // Send the GET request
        fetch(url, { method: 'GET' }).then(response => {
            if (response.ok) { console.log('Analytics data sent successfully'); } else { console.error('Error sending analytics data:', response.statusText); }
        }).catch(error => { console.error('Fetch error:', error); });
    }

}, 1000);
