function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function replaceNotifications(response) {
    var newNotificationContainer = $(response).find('#notification-container');
    $('#notification-container').replaceWith(newNotificationContainer);
}

function ajaxUpdateNotifications(button, type) {
    $.ajax({
        url: button.attr("url"),
        type: type,
        beforeSend: function (xhr, settings) {
            var csrfToken = getCookie('csrftoken');
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        success: (function (response) {
            replaceNotifications(response);
            addButtonListeners();
        }),
        error: function (error) {
            console.log(error);
        }
    });
}

function addButtonListeners() {
    $(".delete-button").on('click', function () {
        ajaxUpdateNotifications($(this), 'POST');
        console.log("Notification delete request sent.");
    });
    $(".read-button").on('click', function () {
        ajaxUpdateNotifications($(this), 'POST');
        console.log("Notification read request sent.");
    });
}

$(document).ready(function () {
    setInterval(function () {
        $.ajax({
            success: (function (response) {
                replaceNotifications(response);
                addButtonListeners();
            }),
        });
        console.log("Notification reload request sent.");
    }, 5000);

    addButtonListeners();
});
