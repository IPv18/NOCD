var json;
var live = true;
var interface;
var interfaces;


function renderProgramPolicy(data, type, row, meta) {
    col = meta.col;
    if (type === 'display') {
        console.log(row);
        switch (col) {
            case 2:
                return data.join(', ');
            case 11:
                return data.slice(0, 16).replace('T', ' ');

            case 12:
                return `<button class="btn btn-sm btn-primary">
                            <i class="fa fa-pencil"></i> 
                        </button>`; 
            case 13:
                return `<button class=" btn btn-sm btn-danger delete-link " data-id="${row['id']} " >
                            <i class="fas fa-trash"></i> 
                        </button>`;

        }
    }
    return data;
}
$(document).ready(function () {


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
        scrollCollapse: false,
        fixedColumns: {
            left: 1,
        }

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
                $('#interface-selector').append(optionElement);
            }
        });

    // Update the interface
    $('#interface-selector').on('change', function () {
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
        order: [[0, 'desc']],
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
            { "data": "description" },
            { "data": "created" },
            {
                "data": null,
                "defaultContent": "<button>Edit</button>"
            },
            {
                "data": null,
                "defaultContent": "<button>Delete</button>"
            }
        ],
        lengthMenu: [100, 200, 500],
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: false,
        fixedColumns: {
            left: 1,
        },
        initComplete: function () {
            $(".delete-link").on('click', function (event) {
                console.log("delete");
                event.stopPropagation();
                event.stopImmediatePropagation();
                event.preventDefault();
                row = $(this).parents('tr');
                var deleteUrl = "/traffic_control/policy/" + $(this).data("id") + "/";
                $.ajax({
                    url: deleteUrl,
                    type: "DELETE",
                    success: function () {
                        // Remove the row from the table
                        console.log(programTable);
                        $('#program-table').DataTable().ajax.reload()
                        console.log("Done deleting object!");
                    },
                    error: function () {
                        alert("Error deleting object!");
                    }
                });
            });
            $(".edit-link").on('click', function (event) {
                console.log("edit");
                event.stopPropagation();
                event.stopImmediatePropagation();
                event.preventDefault();
                row = $(this).parents('tr');

            });
        }


    })











    // --------------------------------- IP Policies ---------------------------------

    var programTable = $('#ip-table').DataTable({
        ajax: {
            url: 'ip_policy/',
            dataSrc: ''
        },

        order: [[0, 'desc']],
        "columnDefs": [{
            "defaultContent": "-",
            "targets": "_all",
        }],
        "columns": [
            { "data": "id" },
            { "data": "name" },
            { "data": "direction" },
            { "data": "transport" },
            { "data": "ip_src" },
            { "data": "sport" },
            { "data": "ip_dest" },
            { "data": "dport" },
            { "data": "rate" },
            { "data": "burst" },
            { "data": "prio" },
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
        lengthMenu: [100, 200, 500],
        scrollY: "500px",
        scrollX: true,
        scrollCollapse: false,
        fixedColumns: {
            left: 1,
            right: 2,
        }
    });



});
