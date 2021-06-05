// put all the global variables here
let url_string = window.location.href
let url = new URL(url_string);
let ipsearchurl = `https://ipapi.co/${ip}/json/`
let latitude = ''
let longitude = ''
let map = ''//complex object of type OpenLayers.Map
let dict = {};

let state = {}


locationiq.key = 'pk.959200a41370341f608a91b67be6e8eb';


function GetIp() {
    $.ajax(ipsearchurl, {

        success: function (data) {
            latitude = data.latitude
            longitude = data.longitude
        },
        error: function (data) {
            $.ajax('/v2/getlocation', {
                success: function (data) {
                    latitude = data.latitude
                    longitude = data.longitude
                    $('#lat').val(latitude)
                    $('#lng').val(longitude)
                }
            })
        }
    })
}

function setupLatLng() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            console.log(position);
            latitude = position.coords.latitude
            longitude = position.coords.longitude
            $('#lat').val(latitude)
            $('#lng').val(longitude)
        }, function () {
            GetIp()
        });

    } else {
        GetIp()
    }
}

$(document).ready(function () {
    $('[data-toggle="popover"]').popover();
});

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

function addToast(title, text) {

    toast_container = document.getElementById('toastContainer')

    const no = Math.random().toString(36).substring(7);
    var toastChild = htmlToElement(
        `<div id="${no}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header text-center" >
                <strong class="me-auto">${title}</strong>
                <small class="text-muted"></small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
            ${text}

            </div>
        </div>
        `)


    toast_container.append(toastChild)
    console.log(no)

    $(`#${no}`).toast('show')
}