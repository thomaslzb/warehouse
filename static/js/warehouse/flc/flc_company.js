//如果有输入， 清除错误提示
$("#myModal-company").on("keyup", "#code", function () {
    console.log("code coming in ")
    $('#code_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-company").on("keyup", "#name", function () {
    console.log("name coming in ")
    $('#name_fail').html('')
})


// $("#name").bind('input propertychange', function () {
//     console.log("name coming in ")
//     $('#name_fail').html('')
// })


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
        console.log('load Company Form modal ...')
        console.log(btn.attr("data-url"))
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#myModal-company").modal("show");
            },
            success: function (data) {
                $("#myModal-company .modal-content").html(data.html_form);
            }
        })
    };

    let saveForm = function () {
        let form = $(this);
        console.log('save Company Form modal ...')
        $.ajax({
          url: form.attr("action"),
          data: form.serialize(),
          type: form.attr("method"),
          dataType: 'json',
          cache: false,
          async: false,
          success: function (data) {
              if (data.form_is_valid) {
                  //console.log('Submit Button Success and form is valid ...')
                  $("#myModal-company").modal("hide");  // <-- Close the modal

                  // 刷新表格数据
                  $('#company-table tbody').html(data.html_company_list);
                  // 正确提示
                  toastr.success('Data Save Successfully...');

              } else {
                  // 正确提示
                  toastr.warning('Data have some error ...');
                  //console.log('Submit Button Success and form is no valid ...')
                  $("#myModal-company .modal-content").html(data.html_form);
              }
          },
        });
        return false
    };
    // 建立新的公司
    $(".js_create_company").click(loadForm);
    $("#myModal-company").on("submit", ".js-company-create-form", saveForm);

    // 编辑公司
    $("#company-table").on("click", ".js-update-company", loadForm);
    $("#myModal-company").on("submit", ".js-company-update-form", saveForm);

});
    // $(".js_create_company").click(function () {
    //     //console.log('display company modal ...')
    //     $.ajax({
    //         url: '/lcl/company/create/',
    //         type: 'get',
    //         dataType: 'json',
    //         beforeSend: function () {
    //             $("#myModal-company").modal("show");
    //         },
    //
    //         success: function (data) {
    //             $("#myModal-company .modal-content").html(data.html_form);
    //         }
    //     });
    //     //console.log('display company modal finished...')
    // });

  // $("#myModal-company").on("click", ".js_save_btn", function() {
  //     //console.log('submit button as Button ...')
  //     let form = $("#create_company_form")
  //
  //     $.ajax({
  //         url: form.attr("action"),
  //         data: form.serialize(),
  //         type: form.attr("method"),
  //         dataType: 'json',
  //         cache: false,
  //         async: false,
  //         success: function (data) {
  //             if (data.form_is_valid) {
  //                 //console.log('Submit Button Success and form is valid ...')
  //                 $("#myModal-company").modal("hide");  // <-- Close the modal
  //                 // 刷新表格数据
  //                 $('#company-table tbody').html(data.html_company_list);
  //                 // 正确提示
  //                 toastr.success('Data Save Successfully...');
  //             } else {
  //                 // 正确提示
  //                 toastr.warning('Data have some error ...');
  //                 //console.log('Submit Button Success and form is no valid ...')
  //                 $("#myModal-company .modal-content").html(data.html_form);
  //             }
  //         },
  //     });
  //     return false;
  //  });


  // $("#myModal-company").on("submit",".js-company-create-form", function() {
  //     console.log('Submit Button ...')
  //     let form = $(this)
  //     $.ajax({
  //         url: form.attr("action"),
  //         data: form.serialize(),
  //         type: form.attr("method"),
  //         dataType: 'json',
  //         cache: false,
  //         async: false,
  //         success: function (data) {
  //             if (data.form_is_valid) {
  //                 console.log('Submit Button Success and form is valid ...')
  //                 // $("#myModal-company").modal("hide");  // <-- Close the modal
  //                 document.getElementById("btn-cancel").click();
  //                 // 刷新表格数据
  //                 $('#company-table tbody').html(data.html_company_list);
  //                 // 正确提示
  //                 // toastr.success('Data Save Successfully...');
  //             } else {
  //                 console.log('Submit Button Success and form is no valid ...')
  //                 $("#myModal-company .modal-content").html(data.html_form);
  //             }
  //         },
  //     });
  //     return false;
  //  });
