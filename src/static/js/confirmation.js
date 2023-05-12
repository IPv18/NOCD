function deleteRule(rule_id, csrf_token) {
    var xhr = new XMLHttpRequest();
    var url = '/firewall/rule/' + rule_id + '/';
    xhr.open('DELETE', url);
    xhr.setRequestHeader('X-CSRFToken', csrf_token);
    xhr.onload = function() {
        var response = JSON.parse(xhr.responseText);
        if (xhr.status == 200 && response.success) {
            var id = response.id;
            var homeUrl = '/firewall/?id=' + id;
            window.location.href = homeUrl;
        }
    };
    xhr.send();
}
