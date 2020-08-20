$(function () {
  /* Interface to view the workflow status from the explorer / editor */
  $(".allocate-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        chooser: function (modal, jsonData) {
          $("form.allocation-create").on("submit", function (e) {
            e.preventDefault();
            var formdata = new FormData(this);
            $.ajax({
              url: this.action,
              type: "POST",
              data: formdata,
              processData: false,
              contentType: false,
              dataType: "text",
              success: modal.loadResponseText,
            });
            return false;
          });
        },
        allocated: function (modal, jsonData) {
          addMessage("success", "Available stock has been allocated.");
          modal.close();
        },
      },
    });
    return false;
  });

  $(".purchase-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        chooser: function (modal, jsonData) {
          $("form.purchase-order-create").on("submit", function (e) {
            e.preventDefault();
            var formdata = new FormData(this);
            console.log(formdata);
            $.ajax({
              url: this.action,
              type: "POST",
              data: formdata,
              processData: false,
              contentType: false,
              dataType: "text",
              success: modal.loadResponseText,
            });
            return false;
          });
        },
        created: function (modal, jsonData) {
          addMessage("success", "Purchase order has been created.");
          modal.close();
        },
      },
    });
  });

  $(".receive-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        chooser: function (modal, jsonData) {
          $("form.receive-create").on("submit", function (e) {
            e.preventDefault();
            var formdata = new FormData(this);
            $.ajax({
              url: this.action,
              type: "POST",
              data: formdata,
              processData: false,
              contentType: false,
              dataType: "text",
              success: modal.loadResponseText,
            });
            return false;
          });
        },
        received: function (modal, jsonData) {
          addMessage("success", "Stock has been received.");
          modal.close();
        },
      },
    });
    return false;
  });
});
