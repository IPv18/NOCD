var json;
var live = true;
var interface;
var interfaces;


function program_table_sort(){
    // Workaround for header bug in DataTables
    // where headers are scratched on page load
    document.querySelector("#program-table_wrapper > div.row.dt-row > div > div > div.dataTables_scrollHead > div > table > thead > tr > th.sorting.sorting_asc").click();
}

function ip_table_sort(){
    // Workaround for header bug in DataTables
    // where headers are scratched on page load
    document.querySelector("#ip-table_wrapper > div.row.dt-row > div > div > div.dataTables_scrollHead > div > table > thead > tr > th.sorting.sorting_asc").click();
}


function deleteProgramPolicy(btn) {
    console.log("delete");
    console.log(btn);
    var deleteUrl = "/traffic_control/policy/" + btn.getAttribute("data-id") + "/";
    $.ajax({
        url: deleteUrl,
        type: "DELETE",
        success: function () {
            // Remove the row from the table
            $('#program-table').DataTable().ajax.reload()
            console.log("Done deleting object!");
        },
        error: function () {
            alert("Error deleting object!");
        }
    });
}


function renderProgramPolicy(data, type, row, meta) {
    col = meta.col;
    if (type === 'display') {
        console.log(row);
        switch (col) {
            case 11:
                return `<button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#info-modal" data-bs-info='${JSON.stringify(row["description"])}'>
                            <i class="fas fa-info-circle"></i>
                        </button>
            `;
            case 10:
                return data.slice(0, 16).replace('T', ' ');

            case 12:
                return `<button type="button" class="btn btn-sm btn-primary"
                            data-bs-toggle="modal"
                            data-bs-target="#program-modal"
                            data-bs-action="edit"
                            data-bs-row='${JSON.stringify(row)}'>
                            <i class="fa fa-pencil"></i> 
                        </button>`;
            case 13:
                return `<button class=" btn btn-sm btn-danger delete-link " data-id="${row['id']}" onclick="deleteProgramPolicy(this)">
                            <i class="fas fa-trash"></i> 
                        </button>`;

        }
    }

    return data;
}



function deleteIpPolicy(btn) {
    console.log("delete");
    console.log(btn);
    var deleteUrl = "/traffic_control/policy/" + btn.getAttribute("data-id") + "/";
    $.ajax({
        url: deleteUrl,
        type: "DELETE",
        success: function () {
            // Remove the row from the table
            $('#ip-table').DataTable().ajax.reload()
            console.log("Done deleting object!");
        },
        error: function () {
            alert("Error deleting object!");
        }
    });
}


function renderIpPolicy(data, type, row, meta) {
    col = meta.col;
    if (type === 'display') {
        console.log(row);
        switch (col) {
            case 15:
                return `<button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#info-modal" data-bs-info='${JSON.stringify(row["description"])}'>
                            <i class="fas fa-info-circle"></i>
                        </button>`;
            case 14:
                return data.slice(0, 16).replace('T', ' ');

            case 16:
                return `<button type="button" class="btn btn-sm btn-primary"
                            data-bs-toggle="modal"
                            data-bs-target="#ip-modal"
                            data-bs-action="edit"
                            data-bs-row='${JSON.stringify(row)}'>
                            <i class="fa fa-pencil"></i> 
                        </button>`;
            case 17:
                return `<button class=" btn btn-sm btn-danger delete-link " data-id="${row['id']}" onclick="deleteIpPolicy(this)">
                            <i class="fas fa-trash"></i> 
                        </button>`;

        }
    }

    return data;
}


$(document).ready(function () {


    // --------------------------------- Common ---------------------------------




    const infoModal = document.getElementById('info-modal')
    infoModal.addEventListener('show.bs.modal', event => {
        // Button that triggered the modal
        const button = event.relatedTarget
        // Extract info from data-bs-* attributes
        const info = button.getAttribute('data-bs-info')
        // update the modal's content
        const modalBody = infoModal.querySelector('.modal-body')
        modalBody.textContent = info
    })


    // --------------------------------- Program  ---------------------------------
    const programModal = document.getElementById('program-modal')
    programModal.addEventListener('show.bs.modal', event => {
        // Button that triggered the modal
        const button = event.relatedTarget
        if (button.getAttribute('data-bs-action') == 'edit') {
            // Extract info from data-bs-* attributes
            const row = JSON.parse(button.getAttribute('data-bs-row'))
            // update the modal's content
            $("#program-policy-name").val(row['name']);
            $("#program-policy-programs").val(row['programs']);
            $("#program-policy-rate").val(row['rate']);
            $("#program-policy-burst").val(row['burst']);
            $("#program-policy-prio").val(row['prio']);
            $("#program-policy-description").val(row['description']);

            $("#program-policy-direction option[value='" + row['direction'] + "']").prop('selected', true)
            $("#modal-interface-selector option[value='" + row['interface'] + "']").prop('selected', true)
            $("#program-policy-enabled").prop('checked', row['enabled']);
            $("#program-policy-startup").prop('checked', row['startup']);
            $("#program-policy-id").val(row['id']);


            //const modalBodyInput = programModal.querySelector('.modal-body input')

            
            const modalTitle = programModal.querySelector('.modal-title')
            //const modalBodyInput = programModal.querySelector('.modal-body input')
            console.log(row);
            modalTitle.textContent = `Edit program policy ID:${row['id']}`
            //modalBodyInput.value = recipient
        }
        else {
            $("#program-policy-name").val('');
            $("#program-policy-programs").val('');
            $("#program-policy-rate").val('');
            $("#program-policy-burst").val('');
            $("#program-policy-prio").val('');
            $("#program-policy-description").val('');
            $("#program-policy-direction option[value='1']").prop('selected', true)
            $("#modal-interface-selector option[value='1']").prop('selected', true)
            $("#program-policy-enabled").prop('checked', true);
            $("#program-policy-startup").prop('checked', true);
            $("#program-policy-id").val('');
            const modalTitle = programModal.querySelector('.modal-title')
            modalTitle.textContent = `Add program policy`
        }
    })


    $("#program-policy-form").on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var id = $("#program-policy-id").val();
        var data = form.serialize();
        console.log(data);
        if (id != '') {
            url = url + id + '/';
            method = 'PUT';
            console.log(url);
        }
        else {
            method = 'POST';
        }

        $.ajax({
            type: method,
            url: url,
            data: data,
            success: function (data) {
                console.log(data);
                $('#program-table').DataTable().ajax.reload()
                $('#program-modal').modal('hide');
            },
            error: function (err) {
                console.log(err);
                alert('Error: ' + err.responseText);
            }
        });
    });



    // --------------------------------- IP  ---------------------------------


    const ipModal = document.getElementById('ip-modal')
    ipModal.addEventListener('show.bs.modal', event => {
        // Button that triggered the modal
        const button = event.relatedTarget
        if (button.getAttribute('data-bs-action') == 'edit') {
            // Extract info from data-bs-* attributes
            const row = JSON.parse(button.getAttribute('data-bs-row'))
            // update the modal's content
            $("#ip-policy-name").val(row['name']);

            $("#ip-policy-rate").val(row['rate']);
            $("#ip-policy-burst").val(row['burst']);
            $("#ip-policy-prio").val(row['prio']);
            $("#ip-policy-description").val(row['description']);

            $("#ip-policy-direction option[value='" + row['direction'] + "']").prop('selected', true)
            $("#modal-interface-selector option[value='" + row['interface'] + "']").prop('selected', true)
            $("#ip-policy-enabled").prop('checked', row['enabled']);
            $("#ip-policy-startup").prop('checked', row['startup']);
            $("#ip-policy-id").val(row['id']);



            
            const modalTitle = ipModal.querySelector('.modal-title')
            console.log(row);
            modalTitle.textContent = `Edit ip policy ID:${row['id']}`
        }        
        else {
            $("#ip-policy-name").val('');

            $("#ip-policy-rate").val('');
            $("#ip-policy-burst").val('');
            $("#ip-policy-prio").val('');
            $("#ip-policy-description").val('');

            $("#ip-policy-direction option[value='0']").prop('selected', true)
            $("#modal-interface-selector option[value='0']").prop('selected', true)
            $("#ip-policy-enabled").prop('checked', true);
            $("#ip-policy-startup").prop('checked', true);
            $("#ip-policy-id").val('');
            const modalTitle = ipModal.querySelector('.modal-title')
            modalTitle.textContent = `Add ip policy`
        }
    })


    $("#ip-policy-form").on('submit', function (e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var id = $("#ip-policy-id").val();
        var data = form.serialize();
        console.log(data);
        if (id != '') {
            url = url + id + '/';
            method = 'PUT';
            console.log(url);
        }
        else {
            method = 'POST';
        }

        $.ajax({
            type: method,
            url: url,
            data: data,
            success: function (data) {
                console.log(data);
                $('#ip-table').DataTable().ajax.reload()
                $('#ip-modal').modal('hide');
            },
            error: function (err) {
                console.log(err);
                alert('Error: ' + err.responseText);
            }
        });
    });



    // --------------------------------- Overview ---------------------------------

    // Initialize the DataTable with empty data
    var overviewTable = $('#overview-table').DataTable({
        order: [[0, 'desc']],
        "columnDefs": [{
            "defaultContent": "-",
            "targets": "_all",
        }],
        "columns": [
            { "data": "timestamp" },
            { "data": "program" },
            { "data": "protocol" },
            { "data": "direction" },
            { "data": "ip_src" },
            { "data": "port_src" },
            { "data": "ip_dest" },
            { "data": "port_dest" },
            { "data": "length" },
            { "data": "pkt_count" }
        ],
        lengthMenu: [100, 200, 500],
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: false

    });


    // Interface selector
    fetch('interfaces/')
        .then(response => response.json())
        .then(data => {
            // do something with the data
            console.log(data);
            interfaces = data;
        })
        .catch(error => {
            // handle the error
            console.error(error);
        }).then(() => {

            for (const interface of interfaces) {
                const optionElement = document.createElement('option');
                optionElement.textContent = interface;
                optionElement.value = interface;
                $('#overview-interface-selector, #modal-interface-selector').append(optionElement);
            }
        });

    // Update the interface
    $('#overview-interface-selector').on('change', function () {
        // Clear the previous xhr object if it exists
        if (xhr) {
            console.log('aborting previous request');
            xhr.abort();
        }
        overviewTable.rows().remove().draw();

        interface = this.value;
        console.log(interface);
        // Start the HTTP stream
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'interface_metrics/?interface=' + interface);
        xhr.setRequestHeader('Cache-Control', 'no-cache');
        xhr.send();

        // Parse the response as it arrives and update the DataTable
        var old = 0;
        xhr.onprogress = function () {
            if (xhr.responseURL.endsWith(interface) == false) {
                xhr.abort();
                return;
            }
            length = xhr.responseText.length;
            var n = length - old;
            old = xhr.responseText.length;
            // wait for 1s  
            setTimeout(function () { }, 1000);

            if (live == true) {
                overviewTable.rows().remove();
            }

            json = JSON.parse(xhr.responseText.slice(-n));
            console.log(json);
            overviewTable.rows.add(json).draw();

            setTimeout(function () { }, 1000);

        };

    });

    // --------------------------------- Program Policies  ---------------------------------
    var programTable = $('#program-table').DataTable({
        ajax: {
            url: 'program_policy/',
            dataSrc: ''
        },
        lengthMenu: [100, 200, 500],
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: false,
        "columnDefs": [{
            "defaultContent": "-",
            "targets": "_all",
            "render": renderProgramPolicy
        }],
        "columns": [
            { "data": "id" },
            { "data": "name" },
            { "data": "programs" },
            { "data": "rate" },
            { "data": "burst" },
            { "data": "prio" },
            { "data": "direction" },
            { "data": "interface" },
            { "data": "enabled" },
            { "data": "startup" },
            { "data": "created" },
            { "data": "description" },
            {
                "data": null,
                "defaultContent": "<button>Edit</button>"
            },
            {
                "data": null,
                "defaultContent": "<button>Delete</button>"
            }
        ]
    })


    // --------------------------------- IP Policies ---------------------------------

    var ipTable = $('#ip-table').DataTable({
        ajax: {
            url: 'ip_policy/',
            dataSrc: ''
        },
        lengthMenu: [100, 200, 500],
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: false,

        "columnDefs": [{
            "defaultContent": "-",
            "targets": "_all",
            "render": renderIpPolicy
        }],
        "columns": [
            { "data": "id" },
            { "data": "name" },
            { "data": "transport" },
            { "data": "ip_src" },
            { "data": "sport" },
            { "data": "ip_dest" },
            { "data": "dport" },
            { "data": "rate" },
            { "data": "burst" },
            { "data": "prio" },
            { "data": "direction" },
            { "data": "interface" },
            { "data": "enabled" },
            { "data": "startup" },
            { "data": "created" },
            { "data": "description" },
            {
                "data": null,
                "defaultContent": "<button>Edit</button>"
            },
            {
                "data": null,
                "defaultContent": "<button>Delete</button>"
            }
        ],
    });




});
