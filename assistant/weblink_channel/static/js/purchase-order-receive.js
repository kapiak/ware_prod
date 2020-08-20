$(function () {
  $(".receive-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),
      onload: {
        chooser: function (modal, jsonData) {
          $("form.purchase-receive", modal.body).on("submit", function (e) {
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
        invalid: function (modal, jsonData) {
          addMessage("error", "More than requested.");
          $("form.purchase-receive", modal.body).on("submit", function (e) {
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
        marked: function (modal, jsonData) {
          addMessage("success", "Quantity updated");
          modal.close();
        },
      },
    });
  });
});
