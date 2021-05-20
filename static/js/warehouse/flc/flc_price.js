//如果有输入， 清除错误提示
$("#myModal-flc-price").on("keyup", "#destination", function () {
    $('#destination_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-flc-price").on("keyup", "#begin_date", function () {
    $('#begin_date_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-flc-price").on("keyup", "#expire_date", function () {
    $('#expire_date_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-flc-price").on("keyup", "#price", function () {
    $('#price_fail').html('')
})

$(function () {
    // 设置弹出提示框属性
    toastr.options = {
        closeButton: true,
        debug: true,
        progressBar: true,
        positionClass: "toast-top-center",
        onclick: null,
        showDuration: "1000",
        hideDuration: "5000",
        timeOut: "2000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut"
    };

    let loadForm = function() {
        let btn = $(this);
        console.log('load flc price modal ...')
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#myModal-flc-price").modal("show");
            },
            success: function (data) {
                $("#myModal-flc-price .modal-content").html(data.html_form);
            }
        })
    };

    let saveForm = function () {
        let form = $(this);
        console.log('save flc price Form modal ...')
        $.ajax({
          url: form.attr("action"),
          data: form.serialize(),
          type: form.attr("method"),
          dataType: 'json',
          cache: false,
          async: false,

          success: function (data) {
              if (data.form_is_valid) {
                  console.log('Submit Button Success and form is valid ...')
                  $("#myModal-flc-price").modal("hide");  // <-- Close the modal
                  // 刷新表格数据
                  // $('#flc-price-table tbody').html(data.html_flc_price_list);
                  document.getElementById("btn_reset").click();
                  // console.log("abc***********************" + abc)
                  // 正确提示
                  toastr.success('Data Save Successfully...');

              } else {
                  // 不正确提示
                  toastr.warning('Data have some error ...');
                  //console.log('Submit Button Success and form is no valid ...')
                  $("#myModal-flc-price .modal-content").html(data.html_form);
              }
          },
        });
        return false
    };
    // 建立新的价格
    $(".js-flc-price-create-form").click(loadForm);
    $("#myModal-flc-price").on("submit", ".js-flc-price-create-form", saveForm);

    // 编辑flc 价格
    $("#flc-price-table").on("click", ".js-update-flc-price", loadForm);
    $("#myModal-flc-price").on("submit", ".js-flc_price-update-form", saveForm);

});
