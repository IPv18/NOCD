function replaceNavNotifications(response) {
    var newNotificationContainer = $(response).filter('#nav-notifications');
    $('#nav-notifications').replaceWith(newNotificationContainer);

    var newNotificationsCount = $(response).filter('#notifications-count');
    $('#notifications-count').replaceWith(newNotificationsCount);
}

function longNavPollNotifications() {
    $.ajax({
        url: '/notifications/get_nav/',
        type: 'GET',
        success: (function (response) {
            if (response) {
                replaceNavNotifications(response);
            }

            longNavPollNotifications();
        }),
        error: function (error) {
            console.log(error);
            longNavPollNotifications();
        }
    });
};

function initializeNotifications() {
    $.ajax({
        url: '/notifications/nav/',
        type: 'GET',
        success: (function (response) {
            if (response) {
                replaceNavNotifications(response);
            }
        }),
        error: function (error) {
            console.log(error);
        }
    });
};

$(document).ready(function () {
    initializeNotifications();
    longNavPollNotifications();
});
