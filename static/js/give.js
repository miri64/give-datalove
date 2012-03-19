$(document).ready(function() {
    // AJAX Login
    $("#login_box").submit(function(event) {
        var form = $(this);
        var data = form.serialize();
        var action = form.find("input[name=ajax_action]").val();
        var next = form.find("input[name=next]").val();

        $.post(action, data, function(data) {
            if (data.errors) {
                form.find("ul").remove();
                form.find("ul#login-all-errors").remove();
                for (var field in data.errors) {
                    if (field == 'all') {
                        form.append(data.errors[field]);
                    } else {
                        form.find("input#id_login-"+field+"+br")
                                .after(data.errors[field]);
                    }
                }
            } else {
                window.location = next;
            }
        }).error(function(response) {
            if (response.status == 404) {
                window.location = action;
            } else {
                content = response.responseText;
                window.document.write(content);
                window.history.pushState(content,document.title,action)
            }
        });

        return false;
    })
})
