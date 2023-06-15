function switchTablePolicy(rule_id, csrfToken) {
    var xhr = new XMLHttpRequest();
    var url = '/firewall/rule/' + rule_id + '/';
    xhr.open('PATCH', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', csrfToken);
    xhr.onload = function() {
        var response = JSON.parse(xhr.responseText);
        var id = response.id;
        var homeUrl = '/firewall/?id=' + id;
        window.location.href = homeUrl;
    }
    xhr.send(JSON.stringify({}));
}

document.addEventListener("DOMContentLoaded", function () {
    const URL_PARAMS = new URLSearchParams(window.location.search);
    const ID = URL_PARAMS.get("id");
    if (ID === "4") {
        document.getElementById('pills-IPv6-Outbound-tab').click();
    } else if (ID === "3") {
        document.getElementById('pills-IPv6-Inbound-tab').click();
    } else if (ID === "2") {
        document.getElementById('pills-IPv4-Outbound-tab').click();
    } else if (ID === "1") {
        document.getElementById('pills-IPv4-Inbound-tab').click();
    }

    // Get the alert message element
    var alertMessage = document.getElementById('alert-message');

    // If the alert message element exists, add an event listener to the close button
    if (alertMessage) {
        var closeButton = alertMessage.querySelector('.btn-close');
        closeButton.addEventListener('click', function() {
            // When the close button is clicked, remove the alert message from the session storage
            sessionStorage.removeItem('alert-message');
        });
    }

    // Check if the alert message is in the session storage
    var sessionMessage = sessionStorage.getItem('alert-message');
    if (sessionMessage) {
        // If the alert message is in the session storage, display it and remove it from the session storage
        alertMessage.innerHTML = sessionMessage;
        sessionStorage.removeItem('alert-message');
    }
});
